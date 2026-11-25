import sqlite3
from contextlib import closing

import pytest

import storage

SAMPLE = [
    {"日付": "2026-11-20", "区分": "収入", "金額": 200000, "メモ": "給料"},
    {"日付": "2026-11-21", "区分": "支出", "金額": 1200, "メモ": "ランチ"},
    {"日付": "2026-11-22", "区分": "支出", "金額": 3800, "メモ": "日用品"},
]


def add_sample():
    storage.init_db()
    for r in SAMPLE:
        storage.add_record(r["日付"], r["区分"], r["金額"], r["メモ"])


def without_id(records):
    return [{k: v for k, v in r.items() if k != "id"} for r in records]


def test_init_creates_empty_table(db_path):
    assert not db_path.exists()
    storage.init_db()
    assert db_path.exists()
    assert storage.load_records() == []


def test_init_twice_keeps_rows():
    add_sample()
    storage.init_db()
    assert len(storage.load_records()) == 3


def test_add_then_load_keeps_number_amounts_and_default_category():
    add_sample()
    loaded = storage.load_records()
    assert without_id(loaded) == [dict(r, カテゴリ="未分類") for r in SAMPLE]
    assert all(isinstance(r["金額"], int) for r in loaded)
    assert [r["id"] for r in loaded] == [1, 2, 3]


def test_quote_in_memo_is_saved_as_is():
    storage.init_db()
    storage.add_record("2026-11-23", "支出", 600, "It's カフェ'); DROP TABLE records; --")
    assert storage.load_records()[0]["メモ"] == "It's カフェ'); DROP TABLE records; --"


def test_update_changes_only_one_row():
    add_sample()
    assert storage.count_by_id(2) == 1
    assert storage.update_record(2, "2026-11-21", "支出", 1500, "ランチ", "食費") == 1
    records = storage.load_records()
    assert [r["金額"] for r in records] == [200000, 1500, 3800]
    assert [r["カテゴリ"] for r in records] == ["未分類", "食費", "未分類"]


def test_delete_removes_only_one_row():
    add_sample()
    assert storage.delete_record(3) == 1
    assert [r["メモ"] for r in storage.load_records()] == ["給料", "ランチ"]


def test_missing_id_counts_zero_and_changes_nothing():
    add_sample()
    assert storage.count_by_id(99) == 0
    assert storage.delete_record(99) == 0
    assert len(storage.load_records()) == 3


def test_csv_is_imported_only_when_db_is_new(csv_path):
    csv_path.write_text(
        "日付,区分,金額,メモ\n2026-11-20,収入,200000,給料\n2026-11-21,支出,1200,ランチ\n",
        encoding="utf-8",
    )
    storage.init_db()
    assert [r["メモ"] for r in storage.load_records()] == ["給料", "ランチ"]

    # 起動し直しても、また取り込まない
    storage.init_db()
    assert len(storage.load_records()) == 2

    # 全部消してから起動し直しても、また取り込まない
    storage.delete_record(1)
    storage.delete_record(2)
    storage.init_db()
    assert storage.load_records() == []


def test_old_table_gets_category_column_with_default(db_path):
    # カテゴリ列を足す前の kakeibo.db
    with closing(sqlite3.connect(db_path)) as conn, conn:
        conn.execute(
            "CREATE TABLE records (id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " date TEXT NOT NULL, kind TEXT NOT NULL, amount INTEGER NOT NULL,"
            " memo TEXT NOT NULL DEFAULT '')"
        )
        conn.execute(
            "INSERT INTO records (date, kind, amount, memo) VALUES (?, ?, ?, ?)",
            ("2026-11-21", "支出", 1200, "ランチ"),
        )
    storage.init_db()
    records = storage.load_records()
    assert records[0]["メモ"] == "ランチ"
    assert records[0]["カテゴリ"] == "未分類"
    storage.add_record("2026-11-22", "支出", 3800, "日用品", "日用品")
    assert [r["カテゴリ"] for r in storage.load_records()] == ["未分類", "日用品"]


def test_csv_saved_with_bom_is_imported(csv_path):
    csv_path.write_text(
        "日付,区分,金額,メモ\n2026-11-20,収入,200000,給料\n", encoding="utf-8-sig"
    )
    storage.init_db()
    assert [r["メモ"] for r in storage.load_records()] == ["給料"]


def test_broken_csv_leaves_no_db_and_can_be_retried(db_path, csv_path):
    csv_path.write_text(
        "日付,区分,金額,メモ\n2026-11-20,収入,200000,給料\n2026-11-21,支出,千円,ランチ\n",
        encoding="utf-8",
    )
    with pytest.raises(storage.CsvImportError):
        storage.init_db()
    assert not db_path.exists()

    # 直してから起動し直すと、取り込める
    csv_path.write_text(
        "日付,区分,金額,メモ\n2026-11-20,収入,200000,給料\n2026-11-21,支出,1000,ランチ\n",
        encoding="utf-8",
    )
    storage.init_db()
    assert [r["金額"] for r in storage.load_records()] == [200000, 1000]


def test_shift_jis_csv_stops_without_leaving_db(db_path, csv_path):
    csv_path.write_bytes("日付,区分,金額,メモ\n2026-11-20,収入,200000,給料\n".encode("cp932"))
    with pytest.raises(storage.CsvImportError, match="utf-8 で保存し直して"):
        storage.init_db()
    assert not db_path.exists()


@pytest.mark.parametrize(
    "row, message",
    [
        ("2026/11/20,収入,200000,給料", "2 行目を読めませんでした"),
        ("2026-11-20,入金,200000,給料", "2 行目の区分"),
    ],
)
def test_bad_date_or_kind_stops_without_leaving_db(db_path, csv_path, row, message):
    csv_path.write_text(f"日付,区分,金額,メモ\n{row}\n", encoding="utf-8")
    with pytest.raises(storage.CsvImportError, match=message):
        storage.init_db()
    assert not db_path.exists()
