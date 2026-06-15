import streamlit as st
import yfinance as yf
import os
import json

st.title("Auto Trading Dashboard")

DATA_FILE = "data.json"

# ✅ 파일 없으면 자동 생성
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

# ✅ 데이터 로드
with open(DATA_FILE, "r") as f:
    try:
        data = json.load(f)
    except:
        data = {}

# =========================
# 📊 관심 종목
# =========================
stocks = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "삼성전기": "009150.KS",
    "LG CNS": "003550.KS"
}

st.subheader("📈 실시간 가격")

for name, ticker in stocks.items():
    try:
        price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
        st.write(f"{name}: {price:,.0f}원")
    except:
        st.write(f"{name}: 데이터 오류")

# =========================
# 💾 상태 저장
# =========================
st.subheader("💾 저장 상태")
st.json(data)

# =========================
# 🧠 테스트 버튼
# =========================
if st.button("테스트 저장"):
    data["test"] = "ok"
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)
    st.success("저장 완료")
import time
import pandas as pd

st.subheader("🤖 자동매매 시뮬레이터")

capital = 10_000_000
positions = {}

buy_threshold = -1.5   # -1.5% 떨어지면 매수
sell_threshold = 2.0   # +2% 오르면 매도
