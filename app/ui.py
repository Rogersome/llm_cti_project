import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from app.main import ask

st.set_page_config(page_title="Cybersecurity AI Assistant")

st.title("🔐 Cybersecurity AI Assistant")

st.write("輸入攻擊描述，系統會自動分析並提供建議")

question = st.text_input("請輸入問題 / 攻擊描述")

if st.button("分析"):
    if question.strip() == "":
        st.warning("請輸入內容")
    else:
        with st.spinner("分析中..."):
            result = ask(question)

        st.subheader("📊 分析結果")
        st.write(result)