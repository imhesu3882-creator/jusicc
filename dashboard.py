import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime

# =========================
# 설정
# =========================
STOCKS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "삼성전기": "009150.KS",
    "LG CNS": "064400.KS"
}

INITIAL_BALANCE = 10_000_000

# =========================
# 초기 상태
# =========================
if "data" not in st.session_state:
    st.session_state.data = {
        "balance": INITIAL_BALANCE,
        "positions": {},   # {name: qty}
        "trades": [],
        "price_history": {name: [] for name in STOCKS.keys()}
    }

data = st.session_state.data

# =========================
# 가격 가져오기
# =========================
@st.cache_data(ttl=5)
def get_price(ticker):
    try:
        df = yf.download(ticker, period="5d", interval="1m", progress=False)
        if df.empty:
            return None
        return float(df["Close"].iloc[-1])
    except:
        return None


def get_all_prices():
    prices = {}
    for name, code in STOCKS.items():
        price = get_price(code)
        if price:
            prices[name] = price
            data["price_history"][name].append(price)
            if len(data["price_history"][name]) > 200:
                data["price_history"][name].pop(0)
    return prices

# =========================
# RSI 계산
# =========================
def calc_rsi(series, period=14):
    if len(series) < period + 1:
        return 50

    delta = np.diff(series)
    gains = np.where(delta > 0, delta, 0)
    losses = np.where(delta < 0, -delta, 0)

    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# =========================
# 자동매매
# =========================
def auto_trade(prices):
    for name, price in prices.items():
        history = data["price_history"][name]
        rsi = calc_rsi(history)

        qty = data["positions"].get(name, 0)

        # 매수 조건
        if rsi < 30 and data["balance"] > price:
            buy_qty = int(data["balance"] // price * 0.1)
            if buy_qty > 0:
                cost = buy_qty * price
                data["balance"] -= cost
                data["positions"][name] = qty + buy_qty

                data["trades"].append({
                    "time": str(datetime.now()),
                    "type": "BUY",
                    "name": name,
                    "price": price,
                    "qty": buy_qty
                })

        # 매도 조건
        elif rsi > 70 and qty > 0:
            sell_qty = int(qty * 0.5)
            if sell_qty > 0:
                revenue = sell_qty * price
                data["balance"] += revenue
                data["positions"][name] = qty - sell_qty

                data["trades"].append({
                    "time": str(datetime.now()),
                    "type": "SELL",
                    "name": name,
                    "price": price,
                    "qty": sell_qty
                })

# =========================
# UI
# =========================
st.title("📊 Auto Trading Dashboard 🤖")

prices = get_all_prices()
auto_trade(prices)

# -------------------------
# 실시간 가격
# -------------------------
st.subheader("📈 실시간 가격")

for name, price in prices.items():
    st.write(f"**{name}** : {int(price):,}원")

# -------------------------
# 계좌
# -------------------------
st.subheader("💰 계좌")

portfolio_value = sum(
    data["positions"].get(name, 0) * prices.get(name, 0)
    for name in STOCKS.keys()
)

total_asset = data["balance"] + portfolio_value
profit = total_asset - INITIAL_BALANCE

st.write(f"현금: {int(data['balance']):,}원")
st.write(f"총 자산: {int(total_asset):,}원")
st.write(f"손익: {int(profit):,}원")

# -------------------------
# 보유 종목
# -------------------------
st.subheader("📦 보유 종목")

if not data["positions"]:
    st.write("보유 없음")
else:
    for name, qty in data["positions"].items():
        st.write(f"{name}: {qty}주")

# -------------------------
# 거래 내역
# -------------------------
st.subheader("🧾 거래 내역")

for t in data["trades"][-10:][::-1]:
    st.write(t)

# -------------------------
# 상태 JSON
# -------------------------
st.subheader("💾 상태")
st.json(data)

time.sleep(3)
st.rerun()
