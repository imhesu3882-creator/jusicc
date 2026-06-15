import streamlit as st
from engine import init_state, run_engine

st.set_page_config(page_title="Auto Trading Dashboard", layout="wide")

# 상태 초기화
if "state" not in st.session_state:
    st.session_state.state = init_state()

st.title("📊 Auto Trading Dashboard 🤖")

state, prices = run_engine(st.session_state.state)
st.session_state.state = state


# ======================
# 📈 가격
# ======================
st.subheader("📈 실시간 가격")

for k, v in prices.items():
    st.write(f"**{k}** : {v:,.0f}원" if v else f"**{k}** : 데이터 오류")


# ======================
# 💰 계좌
# ======================
st.subheader("💰 계좌")

asset = state["balance"]
for stock, pos in state["positions"].items():
    price = prices.get(stock, 0)
    asset += pos["qty"] * (price or 0)

col1, col2 = st.columns(2)
col1.metric("현금", f"{state['balance']:,.0f}원")
col2.metric("총 자산", f"{asset:,.0f}원")


# ======================
# 📦 포지션
# ======================
st.subheader("📦 보유 종목")

if state["positions"]:
    for stock, pos in state["positions"].items():
        price = prices.get(stock, 0)
        pnl = (price - pos["avg"]) * pos["qty"] if price else 0

        st.write(f"""
        **{stock}**
        - 수량: {pos['qty']}
        - 평단: {pos['avg']:.0f}
        - 현재가: {price:,.0f}
        - 평가손익: {pnl:,.0f}
        """)
else:
    st.write("보유 없음")


# ======================
# 🧾 거래 내역
# ======================
st.subheader("🧾 거래 내역")

for t in state["trades"][-10:]:
    st.write(t)


# ======================
# 📊 자산 그래프
# ======================
st.subheader("📊 자산 그래프")

st.line_chart(state["history"])
