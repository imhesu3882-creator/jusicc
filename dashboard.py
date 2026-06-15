import streamlit as st
from engine import run_engine, calc_portfolio

st.set_page_config(page_title="Auto Trading Dashboard", layout="wide")

st.title("📊 Auto Trading Dashboard 🤖")

# =====================
# 엔진 실행
# =====================
data, prices = run_engine()
portfolio, total = calc_portfolio(data, prices)

# =====================
# 가격
# =====================
st.subheader("📈 실시간 가격")

cols = st.columns(len(prices))
for i, (name, price) in enumerate(prices.items()):
    with cols[i]:
        st.metric(name, f"{price:,}원")

# =====================
# 계좌
# =====================
st.subheader("💰 계좌")

st.write(f"현금: {data['balance']:,}원")
st.write(f"총 자산: {total:,}원")

profit = total - 10_000_000
st.write(f"손익: {profit:+,}원")

# =====================
# 보유 종목
# =====================
st.subheader("📦 보유 종목")

if len(portfolio) == 0:
    st.write("보유 없음")
else:
    for p in portfolio:
        st.write(
            f"📌 {p['stock']} | {p['qty']}주 | "
            f"{p['price']:,}원 | 평가 {p['value']:,}원"
        )

# =====================
# 거래 내역
# =====================
st.subheader("🧾 거래 내역")

for t in data["trades"][-20:]:
    st.write(
        f"{t['time']} | {t['type']} | {t['stock']} | "
        f"{t['price']:,}원 | RSI {t['rsi']}"
    )

# =====================
# 상태
# =====================
st.subheader("💾 상태")

st.json(data)
