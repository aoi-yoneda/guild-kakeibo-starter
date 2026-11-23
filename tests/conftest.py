import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import storage  # noqa: E402


@pytest.fixture(autouse=True)
def csv_path(tmp_path, monkeypatch):
    """テストでは本物の kakeibo.csv を使わず、一時フォルダの CSV に読み書きする"""
    path = tmp_path / "kakeibo.csv"
    monkeypatch.setattr(storage, "PATH", path)
    return path
