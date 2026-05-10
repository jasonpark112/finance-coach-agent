import json
import os
import sys
from datetime import datetime
from pathlib import Path
import anthropic
from tools import TOOL_FUNCTIONS
from prompts import SYSTEM_PROMPT

# 로그 파일 경로: 프로젝트 루트의 logs/ 디렉터리
LOGS_DIR = Path(__file__).parent.parent / "logs"

# ──────────────────────────────────────────────
# Claude에게 넘길 Tool 스키마 정의
# ──────────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "get_transactions",
        "description": (
            "지정한 사용자와 기간의 지출 내역을 조회합니다. "
            "소비 분석 또는 투자 추천 요청 시 가장 먼저 호출합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "사용자 ID (예: u001)"},
                "period":  {"type": "string", "description": "조회 기간 YYYY-MM (예: 2026-04)"},
            },
            "required": ["user_id", "period"],
        },
    },
    {
        "name": "analyze_spending",
        "description": (
            "지출 내역을 카테고리별로 분류하고 고정비·변동비를 구분하여 여유 자금을 계산합니다. "
            "get_transactions 결과가 있을 때 호출합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "transactions": {
                    "type": "array",
                    "description": "get_transactions에서 반환된 거래 내역 리스트",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date":     {"type": "string"},
                            "category": {"type": "string"},
                            "amount":   {"type": "integer"},
                            "merchant": {"type": "string"},
                        },
                    },
                }
            },
            "required": ["transactions"],
        },
    },
    {
        "name": "get_stock_price",
        "description": (
            "종목 또는 ETF의 현재 시세와 등락률을 조회합니다. "
            "종목 리서치 또는 투자 추천 시 사용합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "종목 코드 또는 ETF 이름 (예: 005930, TIGER 미국S&P500)",
                }
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "get_news_summary",
        "description": (
            "종목 또는 키워드 관련 최신 뉴스 3~5건을 요약합니다. "
            "종목 판단 보조 정보가 필요할 때 사용합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "검색 키워드 (예: 삼성전자, S&P500)"},
                "limit": {"type": "integer", "description": "반환할 뉴스 개수 (기본값: 3)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "generate_recommendation",
        "description": (
            "여유 자금과 리스크 성향, 시장 데이터를 기반으로 투자 추천을 생성합니다. "
            "지출 분석과 시세 조회가 모두 완료된 후 마지막에 호출합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "surplus":     {"type": "integer", "description": "추정 여유 자금 (원)"},
                "risk":        {"type": "string",  "enum": ["low", "mid", "high"],
                                "description": "리스크 성향: low(안정형) / mid(중립형) / high(공격형)"},
                "market_data": {"type": "object",  "description": "수집된 시세 및 뉴스 데이터"},
            },
            "required": ["surplus", "risk", "market_data"],
        },
    },
]

MAX_STEPS = 15
LOOP_DETECT_THRESHOLD = 3  # 동일 Tool·인자 반복 횟수 초과 시 중단


# ──────────────────────────────────────────────
# 유틸
# ──────────────────────────────────────────────

_log_file = None  # run_agent 실행 시 초기화


def _log(tag: str, content: str) -> None:
    line = f"\n[{tag}] {content}"
    print(line)
    if _log_file:
        _log_file.write(line + "\n")


def _call_key(tool_name: str, tool_input: dict) -> str:
    return f"{tool_name}:{json.dumps(tool_input, sort_keys=True, ensure_ascii=False)}"


def _execute_tool(tool_name: str, tool_input: dict) -> dict:
    fn = TOOL_FUNCTIONS.get(tool_name)
    if fn is None:
        return {
            "ok": False, "data": None,
            "error": {"code": "UNKNOWN_TOOL", "message": f"알 수 없는 Tool: {tool_name}"},
        }
    try:
        return fn(**tool_input)
    except Exception as e:
        return {
            "ok": False, "data": None,
            "error": {"code": "EXECUTION_ERROR", "message": str(e)},
        }


# ──────────────────────────────────────────────
# ReAct Agent 루프
# ──────────────────────────────────────────────

def run_agent(user_message: str, on_step=None) -> dict:
    """
    반환값:
        {
            "answer": str,          최종 답변 텍스트
            "metadata": {
                "tool_sequence":  [str],   호출된 Tool 이름 순서
                "tool_calls":     [dict],  Tool별 입력·결과·성공 여부
                "data_source":    str,     "mock" | "api"
                "generated_at":   str,     응답 생성 시각 (ISO 8601)
                "total_steps":    int,     총 스텝 수
                "fallback_occurred": bool, fallback·재시도 발생 여부
            }
        }
    """
    global _log_file

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # 로그 파일 초기화
    LOGS_DIR.mkdir(exist_ok=True)
    run_ts = datetime.now()
    log_path = LOGS_DIR / f"{run_ts.strftime('%Y%m%d_%H%M%S')}_run.txt"
    _log_file = open(log_path, "w", encoding="utf-8")

    messages = [{"role": "user", "content": user_message}]
    call_counter: dict[str, int] = {}
    step = 0

    # 메타데이터 수집
    tool_sequence: list[str] = []
    tool_calls: list[dict] = []
    fallback_occurred = False

    header = f"\n{'='*60}\n사용자: {user_message}\n{'='*60}"
    print(header)
    _log_file.write(header + "\n")

    while step < MAX_STEPS:
        step += 1
        _log(f"Step {step}", "Claude 호출 중...")

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        # ── 종료: 최종 답변 ──────────────────────
        if response.stop_reason == "end_turn":
            final = "".join(
                block.text for block in response.content if hasattr(block, "text")
            )
            metadata = {
                "tool_sequence":     tool_sequence,
                "tool_calls":        tool_calls,
                "data_source":       "mock",
                "generated_at":      datetime.now().isoformat(),
                "total_steps":       step,
                "fallback_occurred": fallback_occurred,
            }

            footer = (
                f"\n{'='*60}\n최종 답변:\n{'='*60}\n{final}"
                f"\n\n[메타데이터]\n{json.dumps(metadata, ensure_ascii=False, indent=2)}"
            )
            print(footer)
            if _log_file:
                _log_file.write(footer + "\n")
                _log_file.close()
                print(f"\n[로그 저장] {log_path}")

            return {"answer": final, "metadata": metadata}

        # ── Tool 호출 처리 ───────────────────────
        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type != "tool_use":
                    continue

                tool_name  = block.name
                tool_input = block.input
                called_at  = datetime.now().isoformat()

                _log("Action", f"{tool_name}({json.dumps(tool_input, ensure_ascii=False)})")
                if on_step:
                    on_step({"type": "action", "step": step, "tool": tool_name, "input": tool_input})

                # 루프 감지
                key = _call_key(tool_name, tool_input)
                call_counter[key] = call_counter.get(key, 0) + 1
                if call_counter[key] >= LOOP_DETECT_THRESHOLD:
                    msg = f"동일 Tool 반복 호출 감지 ({tool_name}). Agent를 중단합니다."
                    _log("WARN", msg)
                    if _log_file:
                        _log_file.close()
                    return {"answer": msg, "metadata": {
                        "tool_sequence": tool_sequence,
                        "tool_calls": tool_calls,
                        "data_source": "mock",
                        "generated_at": datetime.now().isoformat(),
                        "total_steps": step,
                        "fallback_occurred": fallback_occurred,
                    }}

                # Tool 실행
                result = _execute_tool(tool_name, tool_input)
                ok = result.get("ok", False)

                # fallback 감지: 실패 후 같은 스텝에서 다른 Tool 시도 시
                if not ok:
                    fallback_occurred = True

                _log("Observation", json.dumps(result, ensure_ascii=False, indent=2))
                if on_step:
                    on_step({"type": "observation", "step": step, "tool": tool_name, "ok": ok, "result": result})

                # 메타데이터 기록
                tool_sequence.append(tool_name)
                tool_calls.append({
                    "tool":       tool_name,
                    "input":      tool_input,
                    "ok":         ok,
                    "called_at":  called_at,
                })

                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     json.dumps(result, ensure_ascii=False),
                })

            messages.append({"role": "user", "content": tool_results})

    # ── 종료: max_steps 초과 ─────────────────────
    msg = f"최대 스텝 수({MAX_STEPS})를 초과하여 중단합니다."
    _log("WARN", msg)
    if _log_file:
        _log_file.close()
        print(f"\n[로그 저장] {log_path}")
    return {"answer": msg, "metadata": {
        "tool_sequence": tool_sequence,
        "tool_calls": tool_calls,
        "data_source": "mock",
        "generated_at": datetime.now().isoformat(),
        "total_steps": step,
        "fallback_occurred": fallback_occurred,
    }}
