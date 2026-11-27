# AGENTS.md

家計簿の Streamlit アプリ。何を作るかは SPEC.md、起動のしかたは README.md。

## 使う技術

- Python 3.10 以上 / Streamlit / SQLite（標準の sqlite3）/ requests
- 足すライブラリは requirements.txt に書く。頼まれていないライブラリは足さない

## ファイルの分担

- 画面は app.py、合計の計算は summary.py
- SQL は storage.py の中だけに書く。値は ? で渡し、文字列をつないで SQL を作らない
- 為替は rates.py、祝日は holidays.py

## 触らないもの

- kakeibo.db・kakeibo.csv（本物の収支。開かない・中身を表示しない・コミットしない）
- .venv/

## 確かめ方

- `python -m pytest` がすべて通ること
- テストは一時フォルダの DB を使い、外のネットに出ない（tests/conftest.py）。このしくみは崩さない

## 作業の進め方

- 1 回の依頼で変えるのは 1 つだけ。頼まれていないファイルは直さず、気づいたことは提案だけする
- 画面の動きを変えたら、tests/ にテストを足すか直す
