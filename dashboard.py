import streamlit as st
import json
import os
import random
from datetime import datetime

DATA_FILE = "data.json"

# -----------------------------
# 데이터 로드/초기화 (완전 안전버전)
# -----------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        data = {
            "balance": 10_000_000,
            "positions": {},
            "trades": []
        }
        save_data(data)
        return data

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 구조 보정
    data.setdefault("balance", 10_000_000)
    data.setdefault("positions", {})
    data.setdefault("trades", [])

    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -----------------------------
# 실시간 가격 (시뮬)
# -----------------------------
def get_prices():
    return {
        "삼성전자": 337000 + random.randint(-2000, 2000),
        "SK하이닉스": 2288000 + random.randint(-10000, 10000),
        "삼성전기": 1999000 + random.randint(-8000, 8000),
        "LG CNS": 118400 + random.randint(-1000, 1000),
    }


# -----------------------------
# 자동매매 엔진 (핵심)
# -----------------------------
def auto_trade(data, prices):
    for stock, price in prices.items():

        qty = data["positions"].get(stock, 0)

        # 🎯 매수 조건 (단순 시뮬 전략)
        if price % 9 == 0 and data["balance"] > price:
            data["balance"] -= price
            data["positions"][stock] = qty + 1

            data["trades"].append({
                "type": "BUY",
                "stock": stock,
                "price": price,
                "time": str(datetime.now())
            })

        # 🎯 매도 조건 (익절/손절 시뮬)
        if qty > 0 and price % 13 == 0:
            data["positions"][stock] = qty - 1
            data["balance"] += price

            data["trades"].append({
                "type": "SELL",
                "stock": stock,
                "price": price,
                "time": str(datetime.now())
            })


# -----------------------------
# 포트폴리오 계산
# -----------------------------
def calc_portfolio(data, prices):
    portfolio = []
    total_asset = data["balance"]

    for stock, qty in data["positions"].items():
        price = prices.get(stock, 0)
        value = qty * price
        total_asset += value

        portfolio.append({
            "stock": stock,
            "qty": qty,
            "price": price,
            "value": value
        })

    return portfolio, total_asset


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="Auto Trading Dashboard", layout="wide")

st.title("📊 Auto Trading Dashboard 🤖")

data = load_data()
prices = get_prices()

# 자동매매 실행 (핵심)
auto_trade(data, prices)
save_data(data)

# -----------------------------
# 실시간 가격
# -----------------------------
st.subheader("📈 실시간 가격")

cols = st.columns(len(prices))

for i, (name, price) in enumerate(prices.items()):
    with cols[i]:
        st.metric(name, f"{price:,}원")


# -----------------------------
# 포트폴리오
# -----------------------------
portfolio, total_asset = calc_portfolio(data, prices)

st.subheader("💰 계좌 정보")
st.write(f"현금: {data['balance']:,}원")
st.write(f"총 자산: {total_asset:,}원")

st.subheader("📦 보유 종목")

if len(portfolio) == 0:
    st.write("보유 종목 없음")
else:
    for p in portfolio:
        st.write(
            f"{p['stock']} | 수량 {p['qty']} | "
            f"현재가 {p['price']:,}원 | 평가금 {p['value']:,}원"
        )


# -----------------------------
# 거래 내역
# -----------------------------
st.subheader("🧾 거래 내역")

for t in data["trades"][-15:]:
    st.write(f"{t['time']} | {t['type']} | {t['stock']} | {t['price']:,}원")


# -----------------------------
# 상태 JSON
# -----------------------------
st.subheader("💾 상태 데이터")
st.json(data)
