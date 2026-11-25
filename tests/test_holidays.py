import pytest

import holidays
import rates

HOLIDAYS_2026 = {
    "2026-01-01": "元日",
    "2026-05-06": "憲法記念日 振替休日",
    "2026-11-03": "文化の日",
    "2026-11-23": "勤労感謝の日",
}


def test_in_month_keeps_only_that_month():
    assert holidays.in_month(HOLIDAYS_2026, 2026, 11) == {
        "2026-11-03": "文化の日",
        "2026-11-23": "勤労感謝の日",
    }


def test_month_without_holidays_is_empty():
    assert holidays.in_month(HOLIDAYS_2026, 2026, 6) == {}


def test_mark_returns_empty_for_ordinary_day():
    assert holidays.mark("2026-11-23", HOLIDAYS_2026) == "勤労感謝の日"
    assert holidays.mark("2026-11-24", HOLIDAYS_2026) == ""


def test_to_yen_rounds_to_whole_yen():
    assert rates.to_yen(12.5, 155.12) == 1939
    assert rates.to_yen(10, 0.1047) == 1


class FakeResponse:
    status_code = 200

    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


def test_unexpected_shape_becomes_holiday_error(monkeypatch):
    monkeypatch.setattr(holidays.requests, "get", lambda *a, **k: FakeResponse(["2026-11-03"]))
    with pytest.raises(holidays.HolidayError):
        holidays.fetch_holidays(2026)
