import streamlit as st
import json
import threading
import time

DATA_FILE = "data.json"

# -------------------------
# 자동매매 엔진
# -------------------------
def trading_engine():
    while True:
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)

            # 🔥 여기서 매매 로직 (임시)
            data["balance"] *= 1.0002  # 아주 작은 수익 시뮬레이션

            with open(DATA_FILE, "w") as f:
                json.dump(data, f)

            time.sleep(5)

        except Exception as e:
            print("engine error:", e)
            time.sleep(5)

# -------------------------
# 백그라운드 실행
# -------------------------
threading.Thread(target=trading_engine, daemon=True).start()

# -------------------------
# 웹 UI
# -------------------------
st.title("Auto Trading Dashboard")

with open(DATA_FILE, "r") as f:
    data = json.load(f)

st.metric("총 자산", f"{data['balance']:,}원")
