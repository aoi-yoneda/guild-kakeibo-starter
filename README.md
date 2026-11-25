# 家計簿

収支を入れて、一覧と合計で見る Streamlit のアプリです。

## 起動

Python 3.10 以上で動きます（ギルドの教材では 3.12 を入れます）。

Windows（PowerShell）:

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Mac（ターミナル）:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

初めて起動すると、ターミナルで Email を聞かれます。空のまま Enter を押せば進みます。
ブラウザで http://localhost:8501 が開き、「家計簿」の画面が出ます。止めるときはターミナルで Ctrl + C。
Windows で `.venv\Scripts\activate` が「スクリプトの実行が無効」で止まるときは、`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` を 1 回打ってからやり直します。
Windows で `streamlit run app.py` が止められるときは、代わりに `python -m streamlit run app.py` で起動します。

## できること

- 日付・区分（収入・支出）・金額・メモ・カテゴリを入れて「追加」で一覧に足す
- 収入・支出・残高の合計を出す
- 「直す・消す」で、id を選んだ 1 行だけを直す・消す
- 閉じて開き直しても、収支が残る

## データ

収支は app.py と同じフォルダの kakeibo.db（SQLite のデータベース）の records 表に残ります。
列は id（自動で付く番号）・date（日付）・kind（区分）・amount（金額）・memo（メモ）・category（カテゴリ。前からある行は「未分類」）です。
kakeibo.db は自分の本物のお金の記録なので、.gitignore に書いて GitHub には上げていません。無いときは起動したときに空の表を作ります。

前のダンジョンまでの kakeibo.csv（列は 日付,区分,金額,メモ）があれば、kakeibo.db を初めて作るときに 1 回だけ取り込みます。取り込んだあとの kakeibo.csv は使わないので、消してもかまいません（.gitignore にはそのまま残しています）。
kakeibo.csv に読めない行（金額が数字でない、日付が 2026-11-20 の形でない、区分が「収入」「支出」でない、列が足りない など）があると、画面に何行目かを出して止まり、kakeibo.db は作りません。直してから起動し直すと取り込みます。kakeibo.csv は utf-8 で保存します。Excel では「CSV UTF-8」で保存します（ふつうの「CSV」は Shift_JIS になり、読めずに止まります）。
kakeibo.db の中は、Cursor の拡張機能「SQLite Viewer」で開くと表で見られます。試しに消す・直す前は、kakeibo.db をコピーしておくと戻せます。

見本で試すなら、kakeibo.db が無い状態で、sample.csv（作り物の 3 行）を kakeibo.csv にコピーしてから起動します。

```powershell
Copy-Item sample.csv kakeibo.csv   # Windows
```

```bash
cp sample.csv kakeibo.csv   # Mac
```

## 確かめ方

1. 支出 1200 ランチ を追加する
2. 収入 3000 フリマ を追加する
3. 「直す・消す」でランチの行の id を選び、金額を 1500 にして「直す」を押す
4. ターミナルで Ctrl + C で止め、`streamlit run app.py` で起動し直す
5. 2 行が残り、ランチが 1500 円になっていて、合計が手で計算した数と同じなら OK

## テスト

`.venv` を有効にしたまま、pytest を入れて回します。Windows では `pytest` だけだとアプリ制御で止められることがあるので、`python -m pytest` で回します。

```bash
pip install pytest
python -m pytest
```

tests/ のテストは、Streamlit の AppTest で app.py を動かし、入力欄の決まり・合計が手計算と合うこと・開き直しても収支が残ること・選んだ 1 行だけが直る・消えることを確かめます。
storage.py では、' の入ったメモもそのまま入ること、kakeibo.csv の取り込みが 1 回だけなこと・読めない CSV では kakeibo.db を残さないこと、カテゴリ列の無い古い kakeibo.db に列が足されることも確かめます。上げないファイルが .gitignore にあることも確かめます。
テストは一時フォルダの kakeibo.db を使うので、自分の kakeibo.db は書き換えません。
Python 3.10・3.12・3.14 で確かめました（Streamlit 1.65〜1.67）。

## このリポジトリについて（ギルドのスターター）

AI駆動開発ギルドの作品づくり「家計簿アプリをつくる」のスターターです。「家計簿アプリの土台をつくる」（ダンジョン 1〜3）と、「データと外部連携」の家計簿の続き（ダンジョン 1）のタグがあります。
ダンジョンの区切りごとにタグを置いているので、どのダンジョンからでも始められます。
main と `data-01-done`（データと外部連携 ダンジョン 1 の完成形）は同じ中身です。

### タグの一覧

| タグ | 地点 | 入っているもの |
| --- | --- | --- |
| `kakeibo-base-01-start` | ダンジョン 1 を始める前 | README.md・LICENSE だけ |
| `kakeibo-base-01-done` | ダンジョン 1 の完成形（入力欄と一覧の画面） | app.py・tests/ |
| `kakeibo-base-02-done` | ダンジョン 2 の完成形（追加・合計・CSV に保存） | app.py・storage.py・tests/ |
| `kakeibo-base-03-done` | ダンジョン 3 の完成形（GitHub に上げる形） | 上に加えて requirements.txt・.gitignore・sample.csv |
| `data-01-done` | データと外部連携 ダンジョン 1 の完成形（保存先を SQLite に。追加・一覧・直す・消す・カテゴリ） | storage.py が SQLite（kakeibo.db の records 表）。.gitignore に kakeibo.db |

### 始めるダンジョンと使うタグ

| 始めるダンジョン | 使うタグ |
| --- | --- |
| ダンジョン 1「家計簿の画面を作る」 | `kakeibo-base-01-start` |
| ダンジョン 2「家計簿を動く形にする」 | `kakeibo-base-01-done` |
| ダンジョン 3「家計簿を GitHub に上げる」 | `kakeibo-base-02-done` |
| データと外部連携 ダンジョン 1「データを残す SQLite と CRUD」 | `kakeibo-base-03-done` |

### 途中から入る

使うタグを選んで、`kakeibo` という名前のフォルダに clone します。下の例はダンジョン 2 から始めるとき（`kakeibo-base-01-done`）です。

Windows（PowerShell）:

```powershell
git clone --branch kakeibo-base-01-done --depth 1 https://github.com/aoi-yoneda/guild-kakeibo-starter.git kakeibo
cd kakeibo
Remove-Item -Recurse -Force .git
```

Mac（ターミナル）:

```bash
git clone --branch kakeibo-base-01-done --depth 1 https://github.com/aoi-yoneda/guild-kakeibo-starter.git kakeibo
cd kakeibo
rm -rf .git
```

clone のときに `detached HEAD` の長い注意が出ますが、タグを取り出したときのいつもの表示なので気にしなくて大丈夫です。
`.git` を消すのは、このフォルダを自分の家計簿として育てるためです。消さないと、ダンジョン 3 で `git push` したときの上げ先がこのスターターのままになります。
データと外部連携から入るときは、clone したフォルダを自分の GitHub の空のリポジトリ kakeibo に上げてから始めます（上げ方は「家計簿アプリの土台をつくる」のダンジョン 3）。
Git を使わずに取るなら、GitHub の画面でタグを選び、Code → Download ZIP でも同じものが手に入ります。

### 自分のコードと比べる

ダンジョンを終えたら、そのダンジョンの完成形のタグと見比べられます。ダンジョンの間の差分は GitHub の比較の画面で見られます。

- ダンジョン 1: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/kakeibo-base-01-start...kakeibo-base-01-done
- ダンジョン 2: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/kakeibo-base-01-done...kakeibo-base-02-done
- ダンジョン 3: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/kakeibo-base-02-done...kakeibo-base-03-done
- データと外部連携 ダンジョン 1: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/kakeibo-base-03-done...data-01-done

完成形はひとつの答えの例です。自分のコードが違っていても、ダンジョンのクリア条件を満たしていれば大丈夫です。
