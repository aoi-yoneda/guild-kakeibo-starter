import csv
from pathlib import Path

PATH = Path(__file__).resolve().parent / "kakeibo.csv"
FIELDS = ["日付", "区分", "金額", "メモ"]


def load_records():
    if not PATH.exists():
        return []
    with open(PATH, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["金額"] = int(r["金額"])
    return rows


def save_records(records):
    # 1 行だけでなく、全部の行を書き直す
    with open(PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(records)
