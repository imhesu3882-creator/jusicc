import streamlit as st
import json
import os
import random
from datetime import datetime

DATA_FILE = "data.json"

# ----------------------------
# 데이터 로드 / 초기화
# ----------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        data = {
            "balance": 10_000_000,
            "positions": {},
            "trades": [],
            "history": []
        }
        save_data(data)
        return data

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 🔥 구조 방어 (옛날 데이터 자동 복구)
    if not isinstance(data.get("positions"), dict):
        data["positions"] = {}

    if "balance" not in data:
        data["balance"] = 10_000_000

    if "trades" not in data:
        data["trades"] = []

    if "history" not in data:
        data["history"] = []

    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ----------------------------
# 가짜 실시간 가격 (나중에 API 연결 가능)
# ----------------------------
def get_prices():
    return {
        "삼성전자": 337000 + random.randint(-2000, 2000),
        "SK하이닉스": 2288000 + random.randint(-10000, 10000),
        "삼성전기": 1999000 + random.randint(-8000, 8000),
        "LG CNS": 118400 + random.randint(-1000, 1000),
    }


# ----------------------------
# 거래 로직
# ----------------------------
def buy(data, stock, price):
    qty = 1
    cost = price * qty

    if data["balance"] >= cost:
        data["balance"] -= cost
        data["positions"][stock] = data["positions"].get(stock, 0) + qty

        data["trades"].append({
            "type": "BUY",
            "stock": stock,
            "price": price,
            "time": str(datetime.now())
        })


def sell(data, stock, price):
    if data["positions"].get(stock, 0) > 0:
        data["positions"][stock] -= 1
        data["balance"] += price

        data["trades"].append({
            "type": "SELL",
            "stock": stock,
            "price": price,
            "time": str(datetime.now())
        })


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title="Auto Trading Dashboard", layout="wide")

st.title("📊 Auto Trading Dashboard 🤖")

data = load_data()
prices = get_prices()

# ----------------------------
# 가격 영역
# ----------------------------
st.subheader("📈 실시간 가격")

cols = st.columns(4)

for i, (name, price) in enumerate(prices.items()):
    with cols[i]:
        st.metric(name, f"{price:,}원")

        if st.button(f"{name} 매수"):
            buy(data, name, price)
            save_data(data)
            st.rerun()

        if st.button(f"{name} 매도"):
            sell(data, name, price)
            save_data(data)
            st.rerun()


# ----------------------------
# 계좌 정보
# ----------------------------
st.subheader("💰 계좌")

total_asset = data["balance"]

for stock, qty in data["positions"].items():
    total_asset += qty * prices.get(stock, 0)

st.write(f"현금: {data['balance']:,}원")
st.write(f"총 자산: {total_asset:,}원")

st.subheader("📦 보유 종목")
st.json(data["positions"])


# ----------------------------
# 거래 로그
# ----------------------------
st.subheader("🧾 거래 내역")

st.dataframe(data["trades"][-20:])


# ----------------------------
# 저장 상태
# ----------------------------
st.subheader("💾 상태 파일")

st.json(data)
