from summary import in_month, months, summarize
from test_storage import SAMPLE


def test_empty_is_all_zero():
    assert summarize([]) == (0, 0, 0)


def test_totals_by_kind():
    assert summarize(SAMPLE) == (200000, 5000, 195000)


def test_balance_can_be_negative():
    records = [{"日付": "2026-11-21", "区分": "支出", "金額": 1200, "メモ": "ランチ"}]
    assert summarize(records) == (0, 1200, -1200)


def test_months_are_newest_first_without_duplicates():
    records = SAMPLE + [{"日付": "2026-10-31", "区分": "支出", "金額": 500, "メモ": "本"}]
    assert months(records) == ["2026-11", "2026-10"]
    assert months([]) == []


def test_in_month_keeps_only_that_month():
    records = SAMPLE + [{"日付": "2026-10-31", "区分": "支出", "金額": 500, "メモ": "本"}]
    assert [r["メモ"] for r in in_month(records, "2026-10")] == ["本"]
    assert len(in_month(records, "2026-11")) == 3
    assert in_month(records, "2026-09") == []
