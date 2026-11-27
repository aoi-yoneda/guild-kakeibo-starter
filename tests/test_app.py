from datetime import date
from pathlib import Path

from streamlit.testing.v1 import AppTest

import holidays
import rates
import storage
from test_storage import add_sample

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def run_app():
    # 初回は import に時間がかかるので、待つ時間を長めにする
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    assert not at.exception
    return at


def metrics(at):
    return {m.label: m.value for m in at.metric}


def add(at, kind, amount, memo):
    # 入力欄の 0 番目は、いちばん上の「追加」のフォーム
    at.radio[0].set_value(kind)
    at.number_input[0].set_value(amount)
    at.text_input[0].set_value(memo)
    at.button(key="FormSubmitter:entry-追加").click().run()
    assert not at.exception


def edit_button(at, label):
    return at.button(key=f"FormSubmitter:edit-{label}")


def test_inputs_follow_the_rules():
    at = run_app()
    assert at.title[0].value == "家計簿"
    assert at.date_input[0].label == "日付"
    assert at.radio[0].options == ["収入", "支出"]
    assert at.number_input[0].min == 1
    assert at.number_input[0].step == 1
    assert at.text_input[0].label == "メモ"
    assert at.selectbox[0].label == "カテゴリ"
    assert at.selectbox[0].options == storage.CATEGORIES


def test_starts_empty_without_db(db_path):
    at = run_app()
    assert metrics(at) == {"収入": "0 円", "支出": "0 円", "残高": "0 円"}
    assert len(at.dataframe[0].value) == 0
    assert db_path.exists()


def test_totals_match_hand_calculation():
    add_sample()
    at = run_app()
    assert metrics(at) == {"収入": "200,000 円", "支出": "5,000 円", "残高": "195,000 円"}
    add(at, "支出", 500, "コーヒー")
    assert metrics(at) == {"収入": "200,000 円", "支出": "5,500 円", "残高": "194,500 円"}
    add(at, "収入", 3000, "フリマ")
    assert metrics(at) == {"収入": "203,000 円", "支出": "5,500 円", "残高": "197,500 円"}


def test_added_rows_survive_restart():
    at = run_app()
    add(at, "支出", 1200, "ランチ")
    add(at, "収入", 3000, "フリマ")
    assert len(at.dataframe[0].value) == 2

    # 止めて起動し直す（新しいセッション）
    again = run_app()
    assert metrics(again) == {"収入": "3,000 円", "支出": "1,200 円", "残高": "1,800 円"}
    df = again.dataframe[0].value
    # 同じ日付なら、あとから入れた行が上
    assert df["メモ"].tolist() == ["フリマ", "ランチ"]
    assert df["金額"].tolist() == [3000, 1200]


def test_edit_changes_only_the_chosen_row():
    add_sample()
    at = run_app()
    at.selectbox(key="target").set_value(2).run()
    at.number_input(key="a2").set_value(1500)
    edit_button(at, "直す").click().run()
    assert not at.exception
    assert metrics(at) == {"収入": "200,000 円", "支出": "5,300 円", "残高": "194,700 円"}
    assert [r["金額"] for r in storage.load_records()] == [3800, 1500, 200000]


def test_delete_removes_only_the_chosen_row():
    add_sample()
    at = run_app()
    at.selectbox(key="target").set_value(3).run()
    edit_button(at, "消す").click().run()
    assert not at.exception
    assert [r["メモ"] for r in storage.load_records()] == ["ランチ", "給料"]
    assert metrics(at) == {"収入": "200,000 円", "支出": "1,200 円", "残高": "198,800 円"}


def test_broken_csv_shows_error_instead_of_crashing(csv_path, db_path):
    csv_path.write_text("日付,区分,金額\n2026-11-20,収入,abc\n", encoding="utf-8")
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    assert not at.exception
    assert "kakeibo.csv の 2 行目を読めませんでした" in at.error[0].value
    assert not db_path.exists()


def add_foreign(at, currency, amount, memo):
    at.selectbox(key="f_currency").set_value(currency)
    at.number_input(key="f_amount").set_value(amount)
    at.text_input(key="f_memo").set_value(memo)
    at.button(key="FormSubmitter:foreign-円にして追加").click().run()
    assert not at.exception


def test_without_network_the_screen_still_works():
    # conftest で外のネットを塞いでいる。為替も祝日も取れない
    at = run_app()
    assert "祝日の印を付けられませんでした" in at.warning[0].value
    add_foreign(at, "USD", 12.5, "本")
    assert "上の欄に円で入れてください" in at.error[0].value
    assert storage.load_records() == []
    # 円の欄からは入れられる
    add(at, "支出", 1940, "本")
    assert metrics(at) == {"収入": "0 円", "支出": "1,940 円", "残高": "-1,940 円"}


def test_foreign_amount_is_saved_in_yen(monkeypatch):
    calls = []

    def fake_rate(currency, day):
        calls.append((currency, day))
        return 155.12, "2026-11-20"

    monkeypatch.setattr(rates, "fetch_rate", fake_rate)
    at = run_app()
    add_foreign(at, "USD", 12.5, "本")
    record = storage.load_records()[0]
    assert record["金額"] == 1939
    assert record["区分"] == "支出"
    assert record["メモ"] == "本（12.50 USD・2026-11-20 のレート 155.12）"
    # 同じ通貨・日付は覚えておき、呼び直さない
    add_foreign(at, "USD", 3, "コーヒー")
    assert len(calls) == 1


def test_holidays_are_marked_in_the_list(monkeypatch):
    monkeypatch.setattr(
        holidays, "fetch_holidays", lambda year: {"2026-11-23": "勤労感謝の日"}
    )
    storage.init_db()
    storage.add_record("2026-11-23", "支出", 800, "ランチ")
    storage.add_record("2026-11-24", "支出", 300, "コーヒー")
    at = run_app()
    assert not at.warning
    assert at.dataframe[0].value["祝日"].tolist() == ["", "勤労感謝の日"]


def test_amount_below_one_yen_is_not_saved_and_edit_still_opens(monkeypatch):
    monkeypatch.setattr(rates, "fetch_rate", lambda currency, day: (0.1047, "2026-11-20"))
    storage.init_db()
    storage.add_record("2026-11-20", "支出", 500, "ランチ")
    at = run_app()
    add_foreign(at, "KRW", 3, "ガム")
    assert "1 円より少ない" in at.error[0].value
    assert [r["メモ"] for r in storage.load_records()] == ["ランチ"]
    # 一覧と「直す・消す」はそのまま開く
    again = run_app()
    assert again.number_input(key="a1").value == 500


def test_failed_holiday_year_is_not_called_again_but_this_month_is_shown(monkeypatch):
    this_year = date.today().year
    calls = []

    def fake_holidays(year):
        calls.append(year)
        if year != this_year:
            raise holidays.HolidayError(f"{year} 年の祝日を取れませんでした（404）")
        return {}

    monkeypatch.setattr(holidays, "fetch_holidays", fake_holidays)
    storage.init_db()
    storage.add_record("2015-01-01", "支出", 800, "初詣")
    at = run_app()
    assert "2015 年の祝日を取れませんでした" in at.warning[0].value
    assert at.caption[-1].value == "今月の祝日: なし"
    add(at, "支出", 300, "コーヒー")
    assert calls.count(2015) == 1


def test_month_filter_narrows_totals_and_list():
    add_sample()
    storage.add_record("2026-10-31", "支出", 500, "本")
    at = run_app()
    assert at.selectbox(key="month").options == ["すべて", "2026-11", "2026-10"]
    assert metrics(at)["支出"] == "5,500 円"
    at.selectbox(key="month").set_value("2026-10").run()
    assert not at.exception
    assert metrics(at) == {"収入": "0 円", "支出": "500 円", "残高": "-500 円"}
    assert at.dataframe[0].value["メモ"].tolist() == ["本"]
