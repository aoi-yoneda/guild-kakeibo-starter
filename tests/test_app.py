from pathlib import Path

from streamlit.testing.v1 import AppTest

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
    assert df["メモ"].tolist() == ["ランチ", "フリマ"]
    assert df["金額"].tolist() == [1200, 3000]


def test_edit_changes_only_the_chosen_row():
    add_sample()
    at = run_app()
    at.selectbox[1].set_value(2).run()
    at.number_input[1].set_value(1500)
    edit_button(at, "直す").click().run()
    assert not at.exception
    assert metrics(at) == {"収入": "200,000 円", "支出": "5,300 円", "残高": "194,700 円"}
    assert [r["金額"] for r in storage.load_records()] == [200000, 1500, 3800]


def test_delete_removes_only_the_chosen_row():
    add_sample()
    at = run_app()
    at.selectbox[1].set_value(3).run()
    edit_button(at, "消す").click().run()
    assert not at.exception
    assert [r["メモ"] for r in storage.load_records()] == ["給料", "ランチ"]
    assert metrics(at) == {"収入": "200,000 円", "支出": "1,200 円", "残高": "198,800 円"}


def test_broken_csv_shows_error_instead_of_crashing(csv_path, db_path):
    csv_path.write_text("日付,区分,金額\n2026-11-20,収入,abc\n", encoding="utf-8")
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    assert not at.exception
    assert "kakeibo.csv の 2 行目を読めませんでした" in at.error[0].value
    assert not db_path.exists()
