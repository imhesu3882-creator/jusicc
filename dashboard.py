import streamlit as st
import yfinance as yf
import os
import json

st.set_page_config(page_title="Auto Trading Dashboard", layout="wide")

st.title("Auto Trading Dashboard 🤖")

# =========================
# 📁 데이터 파일 자동 생성
# =========================
DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({
            "capital": 10000000,
            "positions": {}
        }, f)

with open(DATA_FILE, "r") as f:
    data = json.load(f)

# =========================
# 📊 종목
# =========================
stocks = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "삼성전기": "009150.KS",
    "LG CNS": "003550.KS"
}

# =========================
# 📈 가격 함수
# =========================
def get_price(ticker):
    return yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]

# =========================
# 📊 실시간 가격 표시
# =========================
st.subheader("📈 실시간 가격")

prices = {}

for name, ticker in stocks.items():
    try:
        price = get_price(ticker)
        prices[name] = price
        st.write(f"{name}: {price:,.0f}원")
    except:
        st.write(f"{name}: 데이터 오류")

# =========================
# 🤖 자동매매 파라미터
# =========================
buy_threshold = -1.5
sell_threshold = 2.0

st.subheader("🤖 자동매매 시뮬레이션")

if st.button("자동매매 실행"):
    logs = []

    if "positions" not in data:
        data["positions"] = {}

    for name, price in prices.items():

        if name not in data["positions"]:
            data["positions"][name] = price
            logs.append(f"🟢 매수 진입: {name} @ {price:,.0f}")

        else:
            entry = data["positions"][name]
            change = ((price - entry) / entry) * 100

            if change <= buy_threshold:
                logs.append(f"🟡 추가매수 신호: {name} ({change:.2f}%)")

            elif change >= sell_threshold:
                logs.append(f"🔴 매도 신호: {name} ({change:.2f}%)")
                del data["positions"][name]

            else:
                logs.append(f"⏸ 홀딩: {name} ({change:.2f}%)")

    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

    st.write(logs)

# =========================
# 💾 상태
# =========================
st.subheader("💾 포트폴리오 상태")
st.json(data)
