import streamlit as st
import json
import time

st.title("자동매매 대시보드")

placeholder = st.empty()

while True:
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        with placeholder.container():
            st.write("시간:", data["time"])
            st.write("현금:", data["cash"])
            st.write("상태:", data["note"])

    except:
        st.write("데이터 없음")

    time.sleep(5)
