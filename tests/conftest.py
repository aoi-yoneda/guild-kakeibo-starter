import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import storage  # noqa: E402


@pytest.fixture(autouse=True)
def db_path(tmp_path, monkeypatch):
    """テストでは本物の kakeibo.db・kakeibo.csv を使わず、一時フォルダのものに読み書きする"""
    path = tmp_path / "kakeibo.db"
    monkeypatch.setattr(storage, "PATH", path)
    monkeypatch.setattr(storage, "CSV_PATH", tmp_path / "kakeibo.csv")
    return path


@pytest.fixture
def csv_path(tmp_path):
    return tmp_path / "kakeibo.csv"
