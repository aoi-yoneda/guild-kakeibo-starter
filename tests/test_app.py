from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def run_app():
    at = AppTest.from_file(APP)
    at.run()
    assert not at.exception
    return at


def test_title():
    at = run_app()
    assert at.title[0].value == "家計簿"


def test_inputs_follow_the_rules():
    at = run_app()
    assert at.date_input[0].label == "日付"
    assert at.radio[0].options == ["収入", "支出"]
    amount = at.number_input[0]
    assert amount.label == "金額（円）"
    assert amount.min == 1
    assert amount.step == 1
    assert at.text_input[0].label == "メモ"


def test_list_has_three_sample_rows_with_number_amounts():
    at = run_app()
    df = at.dataframe[0].value
    assert list(df.columns) == ["日付", "区分", "金額", "メモ"]
    assert len(df) == 3
    assert df["金額"].tolist() == [200000, 1200, 3800]
    assert set(df["区分"]) <= {"収入", "支出"}


def test_submit_shows_the_entered_values():
    at = run_app()
    at.number_input[0].set_value(1200)
    at.radio[0].set_value("支出")
    at.text_input[0].set_value("ランチ")
    at.button[0].click().run()
    assert not at.exception
    shown = " ".join(str(m.value) for m in at.markdown)
    assert "1200" in shown
    assert "ランチ" in shown
