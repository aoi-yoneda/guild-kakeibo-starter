from pathlib import Path

from streamlit.testing.v1 import AppTest

import storage
from test_storage import SAMPLE

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def run_app():
    at = AppTest.from_file(APP)
    at.run()
    assert not at.exception
    return at


def metrics(at):
    return {m.label: m.value for m in at.metric}


def add(at, kind, amount, memo):
    at.radio[0].set_value(kind)
    at.number_input[0].set_value(amount)
    at.text_input[0].set_value(memo)
    at.button[0].click().run()
    assert not at.exception


def test_inputs_follow_the_rules():
    at = run_app()
    assert at.title[0].value == "家計簿"
    assert at.date_input[0].label == "日付"
    assert at.radio[0].options == ["収入", "支出"]
    assert at.number_input[0].min == 1
    assert at.number_input[0].step == 1
    assert at.text_input[0].label == "メモ"


def test_starts_empty_without_csv(csv_path):
    at = run_app()
    assert metrics(at) == {"収入": "0 円", "支出": "0 円", "残高": "0 円"}
    assert len(at.dataframe[0].value) == 0
    assert not csv_path.exists()


def test_totals_match_hand_calculation():
    storage.save_records(SAMPLE)
    at = run_app()
    assert metrics(at) == {"収入": "200,000 円", "支出": "5,000 円", "残高": "195,000 円"}
    add(at, "支出", 500, "コーヒー")
    assert metrics(at) == {"収入": "200,000 円", "支出": "5,500 円", "残高": "194,500 円"}
    add(at, "収入", 3000, "フリマ")
    assert metrics(at) == {"収入": "203,000 円", "支出": "5,500 円", "残高": "197,500 円"}


def test_added_rows_survive_restart(csv_path):
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
    assert len(csv_path.read_text(encoding="utf-8").splitlines()) == 3
