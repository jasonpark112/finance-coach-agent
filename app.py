import sys
import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

sys.path.insert(0, "src")
from tools import (
    get_transactions, analyze_spending,
    get_stock_price, MOCK_STOCKS,
)
from agent_loop import run_agent

load_dotenv()

# ──────────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="개인 재무 코치",
    page_icon="💰",
    layout="wide",
)

# ──────────────────────────────────────────────
# 사이드바: 조회 설정
# ──────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 설정")
    user_id = st.text_input("사용자 ID", value="u001")
    period  = st.selectbox("조회 기간", ["2026-04", "2026-03"])
    risk    = st.selectbox("리스크 성향", ["mid", "low", "high"],
                           format_func=lambda x: {"low": "안정형", "mid": "중립형", "high": "공격형"}[x])
    st.divider()
    watchlist = st.multiselect(
        "관심 종목",
        list(MOCK_STOCKS.keys()),
        default=["TIGER 미국S&P500", "005930", "TIGER 미국나스닥100"],
    )

# ──────────────────────────────────────────────
# 데이터 로드
# ──────────────────────────────────────────────
tx_result  = get_transactions(user_id, period)
txs        = tx_result["data"] if tx_result["ok"] else []
ana_result = analyze_spending(txs) if txs else {"ok": False}
ana        = ana_result["data"] if ana_result["ok"] else {}

# ──────────────────────────────────────────────
# 헤더
# ──────────────────────────────────────────────
st.title("💰 개인 재무 코치 Agent")
st.caption(f"기간: {period}  |  사용자: {user_id}  |  성향: {risk}")
st.divider()

# ──────────────────────────────────────────────
# 섹션 1: 지표 카드
# ──────────────────────────────────────────────
if ana:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 지출",   f"{ana['total']:,}원")
    c2.metric("고정비",    f"{ana['fixed']:,}원")
    c3.metric("변동비",    f"{ana['variable']:,}원")
    c4.metric("💸 여유 자금", f"{ana['surplus']:,}원",
              delta=f"월 소득 {ana['monthly_income']:,}원 기준")
else:
    st.warning(f"거래 내역을 불러올 수 없습니다. (user={user_id}, period={period})")

st.divider()

# ──────────────────────────────────────────────
# 섹션 2: 차트 + 종목 시세
# ──────────────────────────────────────────────
col_chart, col_stock = st.columns([3, 2])

with col_chart:
    st.subheader("📊 카테고리별 지출")
    if ana.get("breakdown"):
        bd = ana["breakdown"]
        fig = px.bar(
            x=list(bd.keys()),
            y=list(bd.values()),
            labels={"x": "카테고리", "y": "금액 (원)"},
            color=list(bd.values()),
            color_continuous_scale="Blues",
        )
        fig.update_layout(
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=30, b=0),
            height=300,
        )
        fig.update_traces(
            hovertemplate="%{x}<br>%{y:,}원<extra></extra>"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("데이터 없음")

with col_stock:
    st.subheader("📈 관심 종목 시세")
    for symbol in watchlist:
        res = get_stock_price(symbol)
        if res["ok"]:
            d = res["data"]
            delta_color = "normal" if d["change_pct"] >= 0 else "inverse"
            st.metric(
                label=d["name"],
                value=f"{d['price']:,}원",
                delta=f"{d['change_pct']:+.2f}%",
                delta_color=delta_color,
            )
        else:
            st.warning(f"{symbol} 조회 실패")

st.divider()

# ──────────────────────────────────────────────
# 섹션 3: Agent 채팅 + 실행 흐름
# ──────────────────────────────────────────────
col_chat, col_trace = st.columns([3, 2])

# 세션 상태
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_metadata" not in st.session_state:
    st.session_state.last_metadata = None

with col_chat:
    st.subheader("💬 Agent와 대화")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("질문하세요. 예) 이번 달 지출 분석해줘, 삼성전자 지금 살 만해?"):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
            st.stop()

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        trace_events: list[dict] = []

        with col_trace:
            st.subheader("🔍 실행 흐름")
            trace_box = st.empty()

        def on_step(event: dict):
            trace_events.append(event)
            rows = []
            for e in trace_events:
                if e["type"] == "action":
                    rows.append(f"**Step {e['step']}** 🔧 `{e['tool']}`")
                elif e["type"] == "observation":
                    icon = "✅" if e["ok"] else "❌"
                    rows.append(f"{icon} 결과 수신")
            trace_box.markdown("\n\n".join(rows))

        with st.chat_message("assistant"):
            with st.spinner("Agent 실행 중..."):
                result = run_agent(prompt, on_step=on_step)
            st.markdown(result["answer"])

        st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
        st.session_state.last_metadata = result["metadata"]
        st.rerun()

with col_trace:
    st.subheader("🔍 실행 흐름")
    if st.session_state.last_metadata:
        meta = st.session_state.last_metadata
        c1, c2 = st.columns(2)
        c1.metric("총 스텝", meta["total_steps"])
        c2.metric("Fallback", "발생" if meta["fallback_occurred"] else "없음")
        st.caption(f"출처: `{meta['data_source']}` | {meta['generated_at'][:19]}")
        st.markdown("**호출된 Tool 순서**")
        for i, name in enumerate(meta["tool_sequence"], 1):
            st.markdown(f"`{i}.` {name}")
        with st.expander("상세 보기"):
            for call in meta["tool_calls"]:
                icon = "✅" if call["ok"] else "❌"
                st.markdown(f"{icon} **{call['tool']}**")
                st.json(call["input"])
    else:
        st.info("아직 Agent를 실행하지 않았습니다.")
