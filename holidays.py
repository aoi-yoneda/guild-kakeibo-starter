import requests

# holidays-jp（キー不要・無料の祝日 API）。年ごとに {"2026-11-03": "文化の日", ...} が返る
URL = "https://holidays-jp.github.io/api/v1/{year}/date.json"
TIMEOUT = 5


class HolidayError(Exception):
    """祝日の一覧を取れなかったとき。印を付けずに続ける"""


def fetch_holidays(year):
    try:
        res = requests.get(URL.format(year=year), timeout=TIMEOUT)
    except requests.RequestException as e:
        raise HolidayError(f"祝日の API につながりませんでした（{type(e).__name__}）") from e
    if res.status_code != 200:
        raise HolidayError(f"{year} 年の祝日を取れませんでした（{res.status_code}）")
    try:
        data = res.json()
    except ValueError as e:
        raise HolidayError("祝日の返事が JSON ではありませんでした") from e
    # {"日付": "名前"} の辞書のはず。違う形なら印を付けない
    if not isinstance(data, dict):
        raise HolidayError(f"{year} 年の祝日の返事が、思っていた形ではありませんでした")
    return data


def in_month(holidays, year, month):
    """今月分に絞る。祝日の無い月は空の辞書"""
    prefix = f"{year:04d}-{month:02d}-"
    return {day: name for day, name in holidays.items() if day.startswith(prefix)}


def mark(day, holidays):
    # 祝日でない日は辞書に入っていないので、[] でなく get で引く
    return holidays.get(day, "")
