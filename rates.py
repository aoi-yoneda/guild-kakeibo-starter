import requests

# Frankfurter（キー不要・無料の為替 API）。providers=ECB で欧州中央銀行の参考レートに絞る
URL = "https://api.frankfurter.dev/v2/rates"
CURRENCIES = ["USD", "EUR", "GBP", "KRW"]
TIMEOUT = 5


class RateError(Exception):
    """レートを取れなかったとき。画面では理由を出し、円で入れてもらう"""


def fetch_rate(currency, day):
    """1 currency が何円かを返す。返り値は (レート, レートの日付)

    土日・休みの日を頼むと、その前の営業日のレートが返る（日付も前の営業日になる）
    """
    params = {"base": currency, "quotes": "JPY", "date": day, "providers": "ECB"}
    try:
        res = requests.get(URL, params=params, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise RateError(f"為替の API につながりませんでした（{type(e).__name__}）") from e
    if res.status_code != 200:
        raise RateError(f"レートを取れませんでした（{res.status_code}）")
    try:
        data = res.json()
    except ValueError as e:
        raise RateError("レートの返事が JSON ではありませんでした") from e
    # 成功すると [{"date": ..., "base": ..., "quote": "JPY", "rate": ...}] のリスト
    if not data:
        raise RateError(f"{day} の {currency} のレートがありませんでした")
    return data[0]["rate"], data[0]["date"]


def to_yen(amount, rate):
    return round(amount * rate)
