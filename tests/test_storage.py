import storage

SAMPLE = [
    {"日付": "2026-11-20", "区分": "収入", "金額": 200000, "メモ": "給料"},
    {"日付": "2026-11-21", "区分": "支出", "金額": 1200, "メモ": "ランチ"},
    {"日付": "2026-11-22", "区分": "支出", "金額": 3800, "メモ": "日用品"},
]


def test_no_file_returns_empty(csv_path):
    assert not csv_path.exists()
    assert storage.load_records() == []


def test_save_then_load_keeps_all_rows_and_number_amounts(csv_path):
    storage.save_records(SAMPLE)
    loaded = storage.load_records()
    assert loaded == SAMPLE
    assert all(isinstance(r["金額"], int) for r in loaded)


def test_saving_again_keeps_previous_rows(csv_path):
    records = SAMPLE[:1]
    storage.save_records(records)
    records = storage.load_records() + [SAMPLE[1]]
    storage.save_records(records)
    assert len(storage.load_records()) == 2


def test_csv_header_and_encoding(csv_path):
    storage.save_records(SAMPLE[:1])
    text = csv_path.read_text(encoding="utf-8")
    assert text.splitlines()[0] == "日付,区分,金額,メモ"
    assert "給料" in text
