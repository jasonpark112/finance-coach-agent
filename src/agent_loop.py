#  cli 진입점(main.py)이 호출하는 실제 AI 에이전트의 핵심 비즈니스 로직이다.
import copy
import hashlib
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
                    "description": "get_transactions 결과의 data.resTrHistoryList를 그대로 전달",
                    "items": {
                        "type": "object",
                        "properties": {
                            "resAccountTrDate":    {"type": "string"},
                            "resAccountTrTime":    {"type": "string"},
                            "resAccountOut":       {"type": "string"},
                            "resAccountIn":        {"type": "string"},
                            "resAccountDesc1":     {"type": "string"},
                            "resAccountDesc2":     {"type": "string"},
                            "resAccountDesc3":     {"type": "string"},
                            "resAccountDesc4":     {"type": "string"},
                            "resAfterTranBalance": {"type": "string"},
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
# AI 가 도구를 사용하고 생각하는 단계를 최대 15번으로 제한한다.
LOOP_DETECT_THRESHOLD = 3  # 동일 Tool·인자 반복 횟수 초과 시 중단, 똑같은 인자로 똑같은 도구를 3번 이상 연속 호출하면, 에이전트가 길을 잃었다고 판단하고 강제 중단
MODEL_ID = "claude-sonnet-4-6"


# ──────────────────────────────────────────────
# 유틸
# ──────────────────────────────────────────────

_log_file = None  # run_agent 실행 시 초기화


# 콘솔 창에 진행 상황을 실시간으로 출력하는 동시에, logs/ 폴더 안의 텍스트 파일에 타임스탬프와 함께 기록 남김
# -> None 이거는 return 값이 없다는 뜻
def _log(tag: str, content: str) -> None:
    line = f"\n[{tag}] {content}"
    print(line)
    if _log_file:
        _log_file.write(line + "\n")

# 루프(ai가 똑같은 행동을 무한히 반복하면서 해매는 렉걸린 상태) 감지를 위해 도구 이름과 인자 값을 직렬화(JSON)하여 고유한 키로 변환합니다.
def _call_key(tool_name: str, tool_input: dict) -> str:
    return f"{tool_name}:{json.dumps(tool_input, sort_keys=True, ensure_ascii=False)}"

# ──────────────────────────────────────────────
# 민감정보 마스킹
# ──────────────────────────────────────────────

# trace 저장 시 제거할 금융 잔액 필드
_SENSITIVE_KEYS = {"resAfterTranBalance", "resAccountBalance", "resWithdrawalAmt"}


def _mask_input(tool_name: str, tool_input: dict) -> dict:
    """Tool 입력에서 민감정보를 마스킹 (원본 변경 없음)"""
    masked = dict(tool_input)

    # user_id: 첫 글자만 남기고 나머지 마스킹
    if "user_id" in masked:
        uid = str(masked["user_id"])
        masked["user_id"] = uid[0] + "***" if len(uid) > 1 else "***"

    # analyze_spending의 transactions 배열: 건수만 남기고 내용 제거
    if tool_name == "analyze_spending" and "transactions" in masked:
        count = len(masked["transactions"]) if isinstance(masked["transactions"], list) else "?"
        masked["transactions"] = f"[{count} items omitted]"

    return masked


def _mask_result(tool_name: str, result: dict) -> dict:
    """Tool 결과에서 민감정보를 마스킹 (원본 변경 없음)"""
    r = copy.deepcopy(result)
    data = r.get("data")
    if not isinstance(data, dict):
        return r

    # get_transactions: 잔액 필드 제거 + 거래 목록은 건수로 대체
    if tool_name == "get_transactions":
        for key in _SENSITIVE_KEYS:
            data.pop(key, None)
        tx_list = data.get("resTrHistoryList")
        if isinstance(tx_list, list):
            data["resTrHistoryList"] = f"[{len(tx_list)} items omitted]"

    return r


def _save_trace(path: Path, trace: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trace, f, ensure_ascii=False, indent=2)


# 미리 정의된 TOOL_FUNCTIONS 맵에서 실제 파이썬 함수를 찾아 실행한다. 만약 함수 실행 중 에러가 나면 프로그램이 튕기지 않도록 try-except로 감싸 에러 메시지를 안전하게 딕셔너리 형태로 반환한다/
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

# user_message는 사용자가 입력한 질문, on_step은 각 스텝마다 외부로 상태를 전달하는 콜백함수이다. (없으면 None). 반환값은 dict
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
    # global 은 함수 밖에 선언된 변수를 이 함수 안에서 수정하겠다는 선언
    global _log_file
    # os.environ에서 API 키를 읽어 온다. 코드에 직접 키를 적지 않고 환경변수로 관리하는 게 보안상 안전
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # 로그 폴더가 없으면 만들고, 현재 시각으로 run_id를 만든다.
    # 같은 run_id로 _run.txt 와 _trace.json 두 파일을 묶어 한 실행 단위로 관리한다.
    LOGS_DIR.mkdir(exist_ok=True)
    run_ts        = datetime.now()
    run_id        = run_ts.strftime("%Y%m%d_%H%M%S")
    started_at    = run_ts.isoformat()
    log_path      = LOGS_DIR / f"{run_id}_run.txt"
    trace_path    = LOGS_DIR / f"{run_id}_trace.json"
    prompt_version = "v:" + hashlib.md5(SYSTEM_PROMPT.encode()).hexdigest()[:8]
    _log_file     = open(log_path, "w", encoding="utf-8")

    # 변수 초기화이다. message는 Claude와 주고받는 대화 기록 전체이고, 처음엔 사용자 메시지 하나만 들어 있다. 나머지는 루프 돌면서 채워진다.
    messages = [{"role": "user", "content": user_message}]
    call_counter: dict[str, int] = {}
    step = 0
    tool_sequence: list[str]  = []
    tool_calls:    list[dict] = []
    steps_trace:   list[dict] = []  # step별로 그룹화된 trace
    fallback_occurred = False
    total_input_tokens  = 0  # 전체 스텝 누산 input token
    total_output_tokens = 0  # 전체 스텝 누산 output token

    header = f"\n{'='*60}\n사용자: {user_message}\n{'='*60}"
    print(header)
    _log_file.write(header + "\n")

    # ── 공통 종료 처리 ───────────────────────────
    # 종료 경로가 4개(end_turn / max_tokens / loop_detected / max_steps)인데
    # 어떤 경로로 끝나든 trace를 항상 저장하기 위해 하나의 함수로 묶었다.
    def _finish(stop_reason: str, final_answer: str) -> dict:
        global _log_file
        finished_at = datetime.now().isoformat()

        metadata = {
            "tool_sequence":     tool_sequence,
            "tool_calls":        tool_calls,
            "data_source":       "mock",
            "generated_at":      finished_at,
            "total_steps":       step,
            "fallback_occurred": fallback_occurred,
            "stop_reason":       stop_reason,
        }

        total_latency_ms = int((datetime.now() - run_ts).total_seconds() * 1000)

        trace = {
            "run_id":            run_id,
            "user_message":      user_message,
            "started_at":        started_at,
            "finished_at":       finished_at,
            "total_latency_ms":  total_latency_ms,
            "stop_reason":       stop_reason,
            "total_steps":       step,
            "fallback_occurred": fallback_occurred,
            "data_source":       "mock",
            "model": {
                "provider": "anthropic",
                "name":     MODEL_ID,
            },
            "prompt": {
                "version": prompt_version,
            },
            "safety": {
                "masked_fields":   ["user_id", "resTrHistoryList", "resAfterTranBalance", "resAccountBalance", "resWithdrawalAmt"],
                "excluded_fields": ["transactions (analyze_spending input)"],
            },
            # claude-sonnet-4-6 단가: input $3/M tokens, output $15/M tokens
            "usage": {
                "input_tokens":        total_input_tokens,
                "output_tokens":       total_output_tokens,
                "total_tokens":        total_input_tokens + total_output_tokens,
                "estimated_cost_usd":  round(
                    total_input_tokens  * 3  / 1_000_000 +
                    total_output_tokens * 15 / 1_000_000,
                    6
                ),
            },
            "steps":             steps_trace,
            "final_answer":      final_answer,
        }
        _save_trace(trace_path, trace)

        if _log_file:
            _log_file.close()
            _log_file = None

        print(f"\n[로그 저장]    {log_path}")
        print(f"[트레이스 저장] {trace_path}")

        return {"answer": final_answer, "metadata": metadata}

# 매 루프마다 step을 1 올리고 Claude를 호출한다. messages에는 지금까지의 대화 기록이 전부 담겨있어서 Claude가 이전 맥락을 기억할 수 있습니다.
# 응답이 오면 즉시 messages에 추가해서 다음 루프에서도 Claude가 자신이 뭘 했는지 알 수 있게 한다.
    while step < MAX_STEPS:
        step += 1
        _log(f"Step {step}", "Claude 호출 중...")

        # Claude에게 요청 / 응답
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        # 매 스텝 token 사용량 누산 (여러 스텝에 걸친 총 사용량을 _finish에서 집계)
        total_input_tokens  += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        # Claude가 응답을 생성하다가 8192토큰을 넘으면 응답이 잘린 채로 끝난다. 잘린 응답을 그냥 쓰면 불완전한 답변이 나오니까 즉시 종료하고 메시지를 반환한다.
        # ── 종료: 출력 토큰 한도 초과 ───────────
        if response.stop_reason == "max_tokens":
            msg = "응답 생성 중 토큰 한도를 초과했습니다. 요청을 더 단순하게 나눠서 시도해 주세요."
            _log("WARN", msg)
            return _finish("max_tokens", msg)
        

        # Claude가 Tool을 더 쓸 필요 없이 최종 답변을 냈을 때이다. response.content 안에는 여러 블록이 섞여 있을 수 있어서, hasattr(block, "text")로 텍스트 블록만 골라서 하나로 합칩니다.
        # ── 종료: 최종 답변 ──────────────────────
        if response.stop_reason == "end_turn":
            final = "".join(
                block.text for block in response.content if hasattr(block, "text")
            )
            footer = f"\n{'='*60}\n최종 답변:\n{'='*60}\n{final}"
            print(footer)
            if _log_file:
                _log_file.write(footer + "\n")
            return _finish("end_turn", final)

        # ── Tool 호출 처리 ───────────────────────
        if response.stop_reason == "tool_use":
            tool_results = []
            step_calls: list[dict] = []  # 이번 step의 tool call 목록 (trace용)

        # Claude가 Tool을 써야겠다고 판단했을 때이다. 응답 안에 Tool 호출 블록이 여러 개일 수 있어서 for로 순회한다. tool_use 타입이 아닌 블록은 건너뛴다.
            for block in response.content:
                if block.type != "tool_use":
                    continue

                tool_name  = block.name
                tool_input = block.input
                call_start = datetime.now()
                called_at  = call_start.isoformat()

                _log("Action", f"{tool_name}({json.dumps(tool_input, ensure_ascii=False)})")

                # on_step 이 있으면 현재 상태를 외부로 전달한다. 예를 들어 웹 UI에서 현재 몇 번째 스텝, 어떤 Tool 실행 중을 실시간으로 보여줄 때 씀
                if on_step:
                    on_step({"type": "action", "step": step, "tool": tool_name, "input": tool_input})

                # 루프 감지
                key = _call_key(tool_name, tool_input)
                call_counter[key] = call_counter.get(key, 0) + 1
                if call_counter[key] >= LOOP_DETECT_THRESHOLD:
                    msg = f"동일 Tool 반복 호출 감지 ({tool_name}). Agent를 중단합니다."
                    _log("WARN", msg)
                    return _finish("loop_detected", msg)

                # Tool 실행하고 성공 여부를 확인한다.
                result     = _execute_tool(tool_name, tool_input)
                ok         = result.get("ok", False)
                latency_ms = int((datetime.now() - call_start).total_seconds() * 1000)

                # fallback 감지: 실패하면 True로 바꾼다.
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

                # trace 기록: 이름·인자·결과·에러를 step_calls에 누적 (마스킹 적용)
                step_calls.append({
                    "tool":       tool_name,
                    "input":      _mask_input(tool_name, tool_input),
                    "ok":         ok,
                    "result":     _mask_result(tool_name, result),
                    "error":      result.get("error"),
                    "called_at":  called_at,
                    "latency_ms": latency_ms,
                })

                # Tool 결과를 tool_results 리스트에 담습니다. tool_use_id가 중요한데, Claude가 내가 요청한 그 Tool의 결과가 이거구나를 매칭하는 데 씀
                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     json.dumps(result, ensure_ascii=False),
                })

            # 이번 step의 tool call들을 steps_trace에 추가 (step 단위로 그룹화)
            steps_trace.append({"step": step, "tool_calls": step_calls})

            # Tool 결과를 messages에 추가하고 다음 루프로 넘어간다. Claude API 규칙상 Tool 결과는 role:"user" 로 전달해야 한다.
            messages.append({"role": "user", "content": tool_results})

    # ── 종료: max_steps 초과 ─────────────────────
    # while 루프를 정상적으로 빠져나왔다는 건 15번 다 썼는데도 end_turn이 안 나왔다는 뜻이다. 이때 강제로 종료하고 안내 메시지를 반환한다.
    msg = f"최대 스텝 수({MAX_STEPS})를 초과하여 중단합니다."
    _log("WARN", msg)
    return _finish("max_steps", msg)
