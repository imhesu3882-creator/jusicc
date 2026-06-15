import streamlit as st
import yfinance as yf
import json
import os
from datetime import datetime

DATA_FILE = "data.json"

# =========================
# 초기 데이터 자동 생성
# =========================
def load_data():
    if not os.path.exists(DATA_FILE):
        data = {
            "balance": 10000000,
            "positions": {},
            "trades": [],
            "history": []
        }
        save_data(data)
        return data

    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# =========================
# 종목 매핑 (한국주식)
# =========================
TICKERS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "삼성전기": "009150.KS",
    "LG CNS": "064400.KS"
}

# =========================
# 가격 가져오기
# =========================
def get_price(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if df is None or df.empty:
            return None
        return float(df["Close"].iloc[-1])
    except:
        return None

# =========================
# UI 시작
# =========================
st.set_page_config(page_title="Auto Trading Dashboard", layout="wide")
st.title("📊 Auto Trading Dashboard")

data = load_data()

# =========================
# 가격 영역
# =========================
st.subheader("📈 실시간 가격")

prices = {}

for name, ticker in TICKERS.items():
    price = get_price(ticker)
    prices[name] = price

    if price is None:
        st.error(f"{name}: 데이터 오류")
    else:
        st.write(f"{name}: {price:,.0f}원")

# =========================
# 포트폴리오 계산
# =========================
total_value = data["balance"]

for name, pos in data["positions"].items():
    if name in prices and prices[name]:
        total_value += prices[name] * pos

# =========================
# 자동 기록
# =========================
data["history"].append({
    "time": str(datetime.now()),
    "balance": total_value
})

if len(data["history"]) > 200:
    data["history"] = data["history"][-200:]

save_data(data)

# =========================
# 자산 영역
# =========================
st.subheader("💰 자산 현황")

col1, col2, col3 = st.columns(3)

col1.metric("현금", f"{data['balance']:,.0f}원")
col2.metric("총자산", f"{total_value:,.0f}원")
col3.metric("포지션 수", len(data["positions"]))

# =========================
# 매매 패널
# =========================
st.subheader("🤖 자동매매")

selected = st.selectbox("종목 선택", list(TICKERS.keys()))

col1, col2 = st.columns(2)

if col1.button("매수"):
    if prices[selected]:
        data["balance"] -= prices[selected]
        data["positions"][selected] = data["positions"].get(selected, 0) + 1
        data["trades"].append({
            "type": "BUY",
            "name": selected,
            "price": prices[selected],
            "time": str(datetime.now())
        })
        save_data(data)
        st.rerun()

if col2.button("매도"):
    if data["positions"].get(selected, 0) > 0 and prices[selected]:
        data["balance"] += prices[selected]
        data["positions"][selected] -= 1

        data["trades"].append({
            "type": "SELL",
            "name": selected,
            "price": prices[selected],
            "time": str(datetime.now())
        })
        save_data(data)
        st.rerun()

# =========================
# 그래프
# =========================
st.subheader("📉 자산 그래프")

if len(data["history"]) > 1:
    st.line_chart([h["balance"] for h in data["history"]])

# =========================
# 거래 로그
# =========================
st.subheader("📜 거래 로그")

st.dataframe(data["trades"][-20:])
