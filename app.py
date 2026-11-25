from datetime import date

import streamlit as st

import storage


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

# kakeibo.db が無ければ作る（kakeibo.csv があれば、そのときだけ取り込む）
try:
    storage.init_db()
except storage.CsvImportError as e:
    st.error(f"{e}。kakeibo.csv の列（日付,区分,金額,メモ）と金額を直してから、起動し直してください")
    st.stop()

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
    category = st.selectbox("カテゴリ", storage.CATEGORIES)
    submitted = st.form_submit_button("追加")

if submitted:
    storage.add_record(day.isoformat(), kind, int(amount), memo, category)

records = storage.load_records()

st.subheader("直す・消す")
if records:
    target = st.selectbox("直す行の id", [r["id"] for r in records])
    row = next(r for r in records if r["id"] == target)
    with st.form("edit"):
        new_day = st.date_input("日付", date.fromisoformat(row["日付"]), key=f"d{target}")
        new_kind = st.radio(
            "区分", ["収入", "支出"], index=["収入", "支出"].index(row["区分"]), key=f"k{target}"
        )
        new_amount = st.number_input(
            "金額（円）", min_value=1, step=1, value=row["金額"], key=f"a{target}"
        )
        new_memo = st.text_input("メモ", row["メモ"], key=f"m{target}")
        cats = storage.CATEGORIES
        new_category = st.selectbox(
            "カテゴリ", cats, index=cats.index(row["カテゴリ"]) if row["カテゴリ"] in cats else 0,
            key=f"c{target}",
        )
        col1, col2 = st.columns(2)
        save = col1.form_submit_button("直す")
        delete = col2.form_submit_button("消す")

    if save or delete:
        # 変える前に、同じ WHERE で何行に効くかを数える。1 行でなければ変えない
        hits = storage.count_by_id(target)
        if hits != 1:
            st.error(f"id {target} に当たる行が {hits} 件なので、変えませんでした")
        elif save:
            storage.update_record(
                target, new_day.isoformat(), new_kind, int(new_amount), new_memo, new_category
            )
            st.success(f"id {target} の 1 行を直しました")
        else:
            storage.delete_record(target)
            st.success(f"id {target} の 1 行を消しました")
        records = storage.load_records()
else:
    st.caption("まだ収支がありません")

income, expense, balance = summarize(records)

col1, col2, col3 = st.columns(3)
col1.metric("収入", f"{income:,} 円")
col2.metric("支出", f"{expense:,} 円")
col3.metric("残高", f"{balance:,} 円")

st.subheader("一覧")
st.dataframe(records)
