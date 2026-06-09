"""
logs/ 폴더의 _trace.json 파일을 읽어 실행 통계를 집계한다.

실행:
    python src/analyze_traces.py
"""
import json
from pathlib import Path
from collections import defaultdict

LOGS_DIR = Path(__file__).parent.parent / "logs"


def load_traces() -> list[dict]:
    files = sorted(LOGS_DIR.glob("*_trace.json"))
    traces = []
    for f in files:
        with open(f, encoding="utf-8") as fp:
            traces.append(json.load(fp))
    return traces


def analyze(traces: list[dict]) -> None:
    total_runs = len(traces)
    if total_runs == 0:
        print("trace 파일이 없습니다.")
        return

    # ── 기본 집계 ──────────────────────────────
    stop_reason_counts: dict[str, int] = defaultdict(int)
    step_counts:  list[int]   = []
    latencies_ms: list[int]   = []
    total_tokens_list: list[int] = []
    costs_usd: list[float] = []

    # tool 집계
    tool_call_total = 0
    tool_fail_total = 0
    tool_stats: dict[str, dict] = defaultdict(lambda: {"calls": 0, "failures": 0})

    for t in traces:
        stop_reason_counts[t.get("stop_reason", "unknown")] += 1
        step_counts.append(t.get("total_steps", 0))

        if "total_latency_ms" in t:
            latencies_ms.append(t["total_latency_ms"])

        usage = t.get("usage", {})
        if usage:
            total_tokens_list.append(usage.get("total_tokens", 0))
            costs_usd.append(usage.get("estimated_cost_usd", 0.0))

        for step in t.get("steps", []):
            for tc in step.get("tool_calls", []):
                tool_name = tc.get("tool", "unknown")
                ok = tc.get("ok", True)
                tool_call_total += 1
                tool_stats[tool_name]["calls"] += 1
                if not ok:
                    tool_fail_total += 1
                    tool_stats[tool_name]["failures"] += 1

    # ── 출력 ───────────────────────────────────
    print("=" * 50)
    print(f"  Agent Trace 분석 ({total_runs}건)")
    print("=" * 50)

    print("\n[종료 이유]")
    for reason, count in sorted(stop_reason_counts.items()):
        print(f"  {reason:15s} : {count}건")

    print("\n[Step 통계]")
    avg_steps = sum(step_counts) / total_runs
    print(f"  평균 step 수  : {avg_steps:.1f}")
    print(f"  최소 / 최대   : {min(step_counts)} / {max(step_counts)}")

    if latencies_ms:
        avg_lat = sum(latencies_ms) / len(latencies_ms)
        print("\n[Latency]")
        print(f"  평균           : {avg_lat:,.0f} ms")
        print(f"  최소 / 최대    : {min(latencies_ms):,} / {max(latencies_ms):,} ms")

    print("\n[Tool 호출]")
    print(f"  전체 호출 수   : {tool_call_total}건")
    if tool_call_total > 0:
        fail_rate = tool_fail_total / tool_call_total * 100
        print(f"  전체 실패 수   : {tool_fail_total}건 ({fail_rate:.1f}%)")
    print("\n  Tool별 성공/실패:")
    for tool_name, stat in sorted(tool_stats.items()):
        calls    = stat["calls"]
        failures = stat["failures"]
        rate     = failures / calls * 100 if calls else 0
        print(f"    {tool_name:30s} : {calls}건 호출, {failures}건 실패 ({rate:.0f}%)")

    if total_tokens_list:
        print("\n[Token / Cost]")
        total_tok = sum(total_tokens_list)
        total_cost = sum(costs_usd)
        print(f"  누적 token 수  : {total_tok:,}")
        print(f"  누적 비용      : ${total_cost:.6f}")
        print(f"  건당 평균 token: {total_tok // total_runs:,}")
        print(f"  건당 평균 비용 : ${total_cost / total_runs:.6f}")

    print("=" * 50)


if __name__ == "__main__":
    traces = load_traces()
    analyze(traces)
