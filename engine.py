import yfinance as yf
import random
import time

STOCKS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "삼성전기": "009150.KS",
    "LG CNS": "003550.KS"
}


def get_prices():
    prices = {}
    for name, code in STOCKS.items():
        try:
            data = yf.download(code, period="1d", interval="1m", progress=False)
            price = float(data["Close"].iloc[-1])
            prices[name] = price
        except:
            prices[name] = None
    return prices


def init_state():
    return {
        "balance": 10_000_000,
        "positions": {},   # {종목: {qty, avg_price}}
        "trades": [],
        "history": []
    }


def buy(state, stock, price, qty):
    cost = price * qty
    if state["balance"] < cost:
        return state

    state["balance"] -= cost

    if stock not in state["positions"]:
        state["positions"][stock] = {"qty": 0, "avg": 0}

    pos = state["positions"][stock]
    new_qty = pos["qty"] + qty
    pos["avg"] = (pos["avg"] * pos["qty"] + price * qty) / new_qty
    pos["qty"] = new_qty

    state["trades"].append(f"BUY {stock} {qty} @ {price:.0f}")
    return state


def sell(state, stock, price, qty):
    if stock not in state["positions"]:
        return state

    pos = state["positions"][stock]
    if pos["qty"] < qty:
        qty = pos["qty"]

    state["balance"] += price * qty
    pos["qty"] -= qty

    pnl = (price - pos["avg"]) * qty
    state["trades"].append(f"SELL {stock} {qty} @ {price:.0f} PNL {pnl:.0f}")

    if pos["qty"] == 0:
        del state["positions"][stock]

    return state


def auto_trade(state, prices):
    for stock, price in prices.items():
        if price is None:
            continue

        r = random.random()

        # 🔥 아주 단순 RSI 흉내 전략 (너 나중에 바꾸면 됨)
        if r < 0.03:
            state = buy(state, stock, price, 5)

        elif r > 0.97:
            state = sell(state, stock, price, 5)

    return state


def total_asset(state, prices):
    asset = state["balance"]

    for stock, pos in state["positions"].items():
        price = prices.get(stock)
        if price:
            asset += pos["qty"] * price

    return asset


def run_engine(state):
    prices = get_prices()
    state = auto_trade(state, prices)
    state["history"].append(total_asset(state, prices))

    return state, prices
