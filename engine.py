import json
import os
import random
from datetime import datetime

DATA_FILE = "data.json"


# -----------------------------
# 데이터 로드/저장
# -----------------------------
def load_data():
    default = {
        "balance": 10_000_000,
        "positions": {},
        "trades": [],
        "price_history": []
    }

    if not os.path.exists(DATA_FILE):
        save_data(default)
        return default

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return default

    data.setdefault("balance", 10_000_000)
    data.setdefault("positions", {})
    data.setdefault("trades", [])
    data.setdefault("price_history", [])

    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -----------------------------
# 가격 데이터
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
def calc_rsi(values, period=14):
    if len(values) < period + 1:
        return 50

    gains = 0
    losses = 0

    for i in range(-period, 0):
        diff = values[i] - values[i - 1]
        if diff > 0:
            gains += diff
        else:
            losses -= diff

    if losses == 0:
        return 100

    rs = gains / losses
    return 100 - (100 / (1 + rs))


# -----------------------------
# 자동매매 엔진 (RSI)
# -----------------------------
def run_engine():
    data = load_data()
    prices = get_prices()

    for stock, price in prices.items():

        # 히스토리
        if stock not in data["price_history"]:
            data["price_history"][stock] = []

        data["price_history"][stock].append(price)

        if len(data["price_history"][stock]) > 50:
            data["price_history"][stock].pop(0)

        rsi = calc_rsi(data["price_history"][stock])

        qty = data["positions"].get(stock, 0)

        # BUY
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

        # SELL
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

    save_data(data)
    return data, prices


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
