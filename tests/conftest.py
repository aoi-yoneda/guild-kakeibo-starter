import sys
from pathlib import Path

import pytest
import requests
import streamlit as st

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


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """テストは外のネットに出ない。呼ぶとつながらなかったことにする"""

    def blocked(*args, **kwargs):
        raise requests.ConnectionError("テストではネットを使わない")

    monkeypatch.setattr(requests, "get", blocked)
    # 前のテストで覚えたレート・祝日を持ち越さない
    st.cache_data.clear()
    yield
    st.cache_data.clear()
