import streamlit as st
import json
import os
import random
from datetime import datetime

DATA_FILE = "data.json"

# -----------------------------
# 데이터 로드
# -----------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        data = {
            "balance": 10_000_000,
            "positions": {},
            "trades": [],
            "price_history": {}
        }
        save_data(data)
        return data

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    data.setdefault("balance", 10_000_000)
    data.setdefault("positions", {})
    data.setdefault("trades", [])
    data.setdefault("price_history", {})

    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -----------------------------
# 실시간 가격
# -----------------------------
def get_prices():
    return {
        "삼성전자": 337000 + random.randint(-3000, 3000),
        "SK하이닉스": 2288000 + random.randint(-15000, 15000),
        "삼성전기": 1999000 + random.randint(-12000, 12000),
        "LG CNS": 118400 + random.randint(-1200, 1200),
    }


# -----------------------------
# RSI 계산
# -----------------------------
def calc_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50

    gains = 0
    losses = 0

    for i in range(-period, 0):
        diff = prices[i] - prices[i - 1]
        if diff > 0:
            gains += diff
        else:
            losses -= diff

    if losses == 0:
        return 100

    rs = gains / losses
    rsi = 100 - (100 / (1 + rs))
    return rsi


# -----------------------------
# 자동매매 (RSI 기반)
# -----------------------------
def auto_trade(data, prices):
    for stock, price in prices.items():

        # 히스토리 저장
        if stock not in data["price_history"]:
            data["price_history"][stock] = []

        data["price_history"][stock].append(price)

        # 최대 50개 유지
        if len(data["price_history"][stock]) > 50:
            data["price_history"][stock].pop(0)

        rsi = calc_rsi(data["price_history"][stock])

        qty = data["positions"].get(stock, 0)

        # 📉 RSI < 30 → 매수 (과매도)
        if rsi < 30 and data["balance"] > price:
            data["balance"] -= price
            data["positions"][stock] = qty + 1

            data["trades"].append({
                "type": "BUY",
                "stock": stock,
                "price": price,
                "rsi": round(rsi, 2),
                "time": str(datetime.now())
            })

        # 📈 RSI > 70 → 매도 (과매수)
        if rsi > 70 and qty > 0:
            data["positions"][stock] = qty - 1
            data["balance"] += price

            data["trades"].append({
                "type": "SELL",
                "stock": stock,
                "price": price,
                "rsi": round(rsi, 2),
                "time": str(datetime.now())
            })


# -----------------------------
# 포트폴리오 계산
# -----------------------------
def calc_portfolio(data, prices):
    portfolio = []
    total = data["balance"]

    for stock, qty in data["positions"].items():
        price = prices.get(stock, 0)
        value = qty * price
        total += value

        portfolio.append({
            "stock": stock,
            "qty": qty,
            "price": price,
            "value": value
        })

    return portfolio, total


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="Auto Trading Dashboard", layout="wide")

st.title("📊 Auto Trading Dashboard 🤖")

data = load_data()
prices = get_prices()

# 🤖 자동매매 실행
auto_trade(data, prices)
save_data(data)

# -----------------------------
# 가격
# -----------------------------
st.subheader("📈 실시간 가격")

cols = st.columns(len(prices))

for i, (name, price) in enumerate(prices.items()):
    with cols[i]:
        st.metric(name, f"{price:,}원")


# -----------------------------
# 포트폴리오
# -----------------------------
portfolio, total = calc_portfolio(data, prices)

st.subheader("💰 계좌")
st.write(f"현금: {data['balance']:,}원")
st.write(f"총 자산: {total:,}원")

st.subheader("📦 보유 종목")

if portfolio:
    for p in portfolio:
        st.write(
            f"{p['stock']} | {p['qty']}주 | "
            f"{p['price']:,}원 | 평가금 {p['value']:,}원"
        )
else:
    st.write("보유 없음")


# -----------------------------
# 거래 내역
# -----------------------------
st.subheader("🧾 거래 내역")

for t in data["trades"][-20:]:
    rsi = t.get("rsi", "-")
    st.write(f"{t['time']} | {t['type']} | {t['stock']} | {t['price']:,}원 | RSI {rsi}")


# -----------------------------
# 상태
# -----------------------------
st.subheader("💾 상태")
st.json(data)
