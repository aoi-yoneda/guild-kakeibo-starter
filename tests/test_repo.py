import shutil
from pathlib import Path

import storage

ROOT = Path(__file__).resolve().parent.parent


def test_gitignore_keeps_out_venv_and_real_data():
    lines = (ROOT / ".gitignore").read_text(encoding="utf-8").split()
    for name in [".venv/", "kakeibo.csv", "kakeibo.db", "__pycache__/"]:
        assert name in lines


def test_requirements_are_only_what_the_app_uses():
    lines = (ROOT / "requirements.txt").read_text(encoding="utf-8").split()
    assert lines == ["streamlit", "pandas", "requests"]


def test_sample_csv_is_imported_into_new_db(csv_path):
    shutil.copy(ROOT / "sample.csv", csv_path)
    storage.init_db()
    records = storage.load_records()
    assert len(records) == 3
    assert [r["金額"] for r in records] == [3800, 1200, 200000]


def test_agents_md_is_short_and_names_the_rules():
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) <= 40
    for rule in ["storage.py", "python -m pytest", "kakeibo.db"]:
        assert rule in text


def test_review_md_lists_the_checks():
    text = (ROOT / "REVIEW.md").read_text(encoding="utf-8")
    for word in ["符号", "?", "kakeibo.db", "API", "pytest"]:
        assert word in text
