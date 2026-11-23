import streamlit as st

from storage import load_records, save_records


def summarize(records):
    income = 0
    expense = 0
    for r in records:
        if r["区分"] == "収入":
            income += r["金額"]
        else:
            expense += r["金額"]
    return income, expense, income - expense


st.title("家計簿")
st.write("収支を入れて、一覧と合計で見るアプリです")

# kakeibo.csv があれば読む。無ければ空の一覧から始める
if "records" not in st.session_state:
    st.session_state["records"] = load_records()

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
    st.session_state["records"].append(
        {"日付": day.isoformat(), "区分": kind, "金額": int(amount), "メモ": memo}
    )
    save_records(st.session_state["records"])

records = st.session_state["records"]
income, expense, balance = summarize(records)

col1, col2, col3 = st.columns(3)
col1.metric("収入", f"{income:,} 円")
col2.metric("支出", f"{expense:,} 円")
col3.metric("残高", f"{balance:,} 円")

st.subheader("一覧")
st.dataframe(records)
