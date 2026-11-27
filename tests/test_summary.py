from summary import summarize
from test_storage import SAMPLE


def test_empty_is_all_zero():
    assert summarize([]) == (0, 0, 0)


def test_totals_by_kind():
    assert summarize(SAMPLE) == (200000, 5000, 195000)


def test_balance_can_be_negative():
    records = [{"日付": "2026-11-21", "区分": "支出", "金額": 1200, "メモ": "ランチ"}]
    assert summarize(records) == (0, 1200, -1200)
