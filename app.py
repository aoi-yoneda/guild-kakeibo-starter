from datetime import date

import streamlit as st

import holidays
import rates
import storage
from summary import summarize


# 同じ通貨・日付なら 1 時間は呼び直さない（失敗したときは覚えないので、次にまた呼ぶ）
@st.cache_data(ttl=3600, show_spinner=False)
def cached_rate(currency, day):
    return rates.fetch_rate(currency, day)


@st.cache_data(ttl=86400, show_spinner=False)
def cached_holidays(year):
    return holidays.fetch_holidays(year)


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

with st.expander("外貨の支出を入れる（円にして保存）"):
    with st.form("foreign"):
        col1, col2 = st.columns(2)
        with col1:
            f_day = st.date_input("日付", key="f_day")
        with col2:
            f_currency = st.selectbox("通貨", rates.CURRENCIES, key="f_currency")
        col3, col4 = st.columns(2)
        with col3:
            f_amount = st.number_input(
                "金額（外貨）", min_value=0.01, value=10.00, step=0.01, format="%.2f", key="f_amount"
            )
        with col4:
            f_memo = st.text_input("メモ", key="f_memo")
        f_category = st.selectbox("カテゴリ", storage.CATEGORIES, key="f_category")
        f_submitted = st.form_submit_button("円にして追加")

if f_submitted:
    try:
        rate, rate_day = cached_rate(f_currency, f_day.isoformat())
    except rates.RateError as e:
        st.error(f"{e}。上の欄に円で入れてください")
    else:
        yen = rates.to_yen(f_amount, rate)
        if yen < 1:
            # 金額は 1 円から。0 円の行は「直す」の欄に入らない
            st.error(f"{f_amount:.2f} {f_currency} は 1 円より少ないので、入れませんでした")
        else:
            note = f"{f_amount:.2f} {f_currency}・{rate_day} のレート {rate}"
            storage.add_record(
                f_day.isoformat(), "支出", yen, f"{f_memo}（{note}）" if f_memo else note, f_category
            )
            st.success(f"{f_amount:.2f} {f_currency} を {yen:,} 円で追加しました（{rate_day} のレート）")

records = storage.load_records()

st.subheader("直す・消す")
if records:
    target = st.selectbox("直す行の id", [r["id"] for r in records], key="target")
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

# 一覧の日付に祝日の印を付ける。取れなくても一覧は出す
# 取れなかった年は覚えておき、操作のたびに呼び直さない（起動し直すと、もう一度試す）
failed_years = st.session_state.setdefault("holiday_failed_years", {})
today = date.today()
years = sorted({int(r["日付"][:4]) for r in records} | {today.year})
holiday_names = {}
got_this_year = False
for year in years:
    if year in failed_years:
        continue
    try:
        holiday_names.update(cached_holidays(year))
        got_this_year = got_this_year or year == today.year
    except holidays.HolidayError as e:
        failed_years[year] = str(e)

st.subheader("一覧")
if failed_years:
    st.warning("祝日の印を付けられませんでした: " + "／".join(failed_years.values()))
if got_this_year:
    this_month = holidays.in_month(holiday_names, today.year, today.month)
    if this_month:
        st.caption(
            "今月の祝日: " + "、".join(f"{d[5:]} {name}" for d, name in sorted(this_month.items()))
        )
    else:
        st.caption("今月の祝日: なし")
st.dataframe([dict(r, 祝日=holidays.mark(r["日付"], holiday_names)) for r in records])
