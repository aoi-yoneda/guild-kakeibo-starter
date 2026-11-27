import csv
import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
PATH = HERE / "kakeibo.db"
CSV_PATH = HERE / "kakeibo.csv"
CATEGORIES = ["未分類", "食費", "日用品", "交通", "住まい", "給料", "その他"]


class CsvImportError(Exception):
    """kakeibo.csv を取り込めなかったとき。kakeibo.db は作らずに止める"""


def _connect():
    # closing で必ず閉じる。書き込みは with conn: の中で行い、抜けるときに commit される
    return closing(sqlite3.connect(PATH))


def init_db():
    """表が無ければ作る。kakeibo.db を初めて作るときだけ kakeibo.csv を取り込む"""
    first_time = not PATH.exists()
    try:
        _create_table(first_time)
    except CsvImportError:
        # 途中で落ちた kakeibo.db を残すと、次から取り込まなくなる。消して、直してから起動し直してもらう
        if first_time and PATH.exists():
            PATH.unlink()
        raise


def _create_table(first_time):
    with _connect() as conn, conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                kind TEXT NOT NULL,
                amount INTEGER NOT NULL,
                memo TEXT NOT NULL DEFAULT ''
            )
            """
        )
        # あとから足した列。CREATE TABLE IF NOT EXISTS は、もうある表には列を足さない
        columns = [row[1] for row in conn.execute("PRAGMA table_info(records)")]
        if "category" not in columns:
            conn.execute(
                "ALTER TABLE records ADD COLUMN category TEXT NOT NULL DEFAULT '未分類'"
            )
        if first_time and CSV_PATH.exists():
            _import_csv(conn)


def _import_csv(conn):
    # utf-8-sig: Excel の「CSV UTF-8」で保存した CSV の先頭に付く BOM を外して読む
    try:
        with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    except UnicodeDecodeError as e:
        raise CsvImportError("kakeibo.csv を utf-8 で読めませんでした。utf-8 で保存し直してください") from e
    values = []
    for line, r in enumerate(rows, start=2):
        try:
            day = date.fromisoformat(r["日付"]).isoformat()
            kind = r["区分"]
            amount = int(r["金額"])
            values.append((day, kind, amount, r["メモ"] or ""))
        except (KeyError, TypeError, ValueError) as e:
            raise CsvImportError(f"kakeibo.csv の {line} 行目を読めませんでした（{e!r}）") from e
        if kind not in ("収入", "支出"):
            raise CsvImportError(f"kakeibo.csv の {line} 行目の区分が「収入」「支出」ではありません")
        if amount < 1:
            raise CsvImportError(f"kakeibo.csv の {line} 行目の金額が 1 円より少ないです")
    conn.executemany(
        "INSERT INTO records (date, kind, amount, memo) VALUES (?, ?, ?, ?)", values
    )


def load_records():
    with _connect() as conn:
        # 新しい日付が上。同じ日付なら、あとから入れた行が上
        rows = conn.execute(
            "SELECT id, date, kind, amount, memo, category FROM records"
            " ORDER BY date DESC, id DESC"
        ).fetchall()
    return [
        {"id": r[0], "日付": r[1], "区分": r[2], "金額": r[3], "メモ": r[4], "カテゴリ": r[5]}
        for r in rows
    ]


def add_record(day, kind, amount, memo, category="未分類"):
    with _connect() as conn, conn:
        conn.execute(
            "INSERT INTO records (date, kind, amount, memo, category) VALUES (?, ?, ?, ?, ?)",
            (day, kind, amount, memo, category),
        )


def count_by_id(record_id):
    """直す・消す前に、同じ WHERE で何行に効くかを数える"""
    with _connect() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM records WHERE id = ?", (record_id,)
        ).fetchone()[0]


def update_record(record_id, day, kind, amount, memo, category):
    with _connect() as conn, conn:
        cur = conn.execute(
            "UPDATE records SET date = ?, kind = ?, amount = ?, memo = ?, category = ?"
            " WHERE id = ?",
            (day, kind, amount, memo, category, record_id),
        )
        return cur.rowcount


def delete_record(record_id):
    with _connect() as conn, conn:
        cur = conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
        return cur.rowcount
