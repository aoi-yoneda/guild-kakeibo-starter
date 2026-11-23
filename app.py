import streamlit as st

st.title("家計簿")
st.write("収支を入れて、一覧で見るアプリです")

with st.form("entry"):
    col1, col2 = st.columns(2)
    with col1:
        day = st.date_input("日付")
    with col2:
        kind = st.radio("区分", ["収入", "支出"])
    col3, col4 = st.columns(2)
    with col3:
        amount = st.number_input("金額（円）", min_value=1, step=1)
    with col4:
        memo = st.text_input("メモ")
    submitted = st.form_submit_button("追加")

if submitted:
    st.write(day.isoformat(), kind, amount, memo)

# 見本の 3 行。金額は数で持ち、カンマは出すときに付ける
records = [
    {"日付": "2026-11-20", "区分": "収入", "金額": 200000, "メモ": "給料"},
    {"日付": "2026-11-21", "区分": "支出", "金額": 1200, "メモ": "ランチ"},
    {"日付": "2026-11-22", "区分": "支出", "金額": 3800, "メモ": "日用品"},
]

st.subheader("一覧")
st.dataframe(records)
