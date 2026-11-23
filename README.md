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

- 日付・区分（収入・支出）・金額・メモを入れて「追加」で一覧に足す
- 収入・支出・残高の合計を出す
- 閉じて開き直しても、収支が残る

## データ

収支は app.py と同じフォルダの kakeibo.csv（列は 日付,区分,金額,メモ、文字コードは utf-8）に残ります。
kakeibo.csv は自分の本物のお金の記録なので、.gitignore に書いて GitHub には上げていません。無いときは空の一覧から始まります。

見本で試すなら、sample.csv（作り物の 3 行）を kakeibo.csv にコピーしてから起動します。

```powershell
Copy-Item sample.csv kakeibo.csv   # Windows
```

```bash
cp sample.csv kakeibo.csv   # Mac
```

## 確かめ方

1. 支出 1200 ランチ を追加する
2. 収入 3000 フリマ を追加する
3. ターミナルで Ctrl + C で止め、`streamlit run app.py` で起動し直す
4. 2 行が残り、合計が手で計算した数と同じなら OK

## テスト

`.venv` を有効にしたまま、pytest を入れて回します。Windows では `pytest` だけだとアプリ制御で止められることがあるので、`python -m pytest` で回します。

```bash
pip install pytest
python -m pytest
```

tests/ のテストは、Streamlit の AppTest で app.py を動かし、入力欄の決まり・合計が手計算と合うこと・開き直しても収支が残ることを確かめます。storage.py の読み書きと、上げないファイルが .gitignore にあることも確かめます。
テストは一時フォルダの CSV を使うので、自分の kakeibo.csv は書き換えません。
Python 3.10・3.12・3.14 で確かめました（Streamlit 1.65〜1.67）。

## このリポジトリについて（ギルドのスターター）

AI駆動開発ギルドの作品づくり「家計簿アプリの土台をつくる」（ダンジョン 1〜3）のスターターです。
ダンジョンの区切りごとにタグを置いているので、どのダンジョンからでも始められます。
main と `kakeibo-base-03-done`（ダンジョン 3 の完成形）は同じ中身です。

### タグの一覧

| タグ | 地点 | 入っているもの |
| --- | --- | --- |
| `kakeibo-base-01-start` | ダンジョン 1 を始める前 | README.md・LICENSE だけ |
| `kakeibo-base-01-done` | ダンジョン 1 の完成形（入力欄と一覧の画面） | app.py・tests/ |
| `kakeibo-base-02-done` | ダンジョン 2 の完成形（追加・合計・CSV に保存） | app.py・storage.py・tests/ |
| `kakeibo-base-03-done` | ダンジョン 3 の完成形（GitHub に上げる形） | 上に加えて requirements.txt・.gitignore・sample.csv |

### 始めるダンジョンと使うタグ

| 始めるダンジョン | 使うタグ |
| --- | --- |
| ダンジョン 1「家計簿の画面を作る」 | `kakeibo-base-01-start` |
| ダンジョン 2「家計簿を動く形にする」 | `kakeibo-base-01-done` |
| ダンジョン 3「家計簿を GitHub に上げる」 | `kakeibo-base-02-done` |

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
Git を使わずに取るなら、GitHub の画面でタグを選び、Code → Download ZIP でも同じものが手に入ります。

### 自分のコードと比べる

ダンジョンを終えたら、そのダンジョンの完成形のタグと見比べられます。ダンジョンの間の差分は GitHub の比較の画面で見られます。

- ダンジョン 1: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/kakeibo-base-01-start...kakeibo-base-01-done
- ダンジョン 2: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/kakeibo-base-01-done...kakeibo-base-02-done
- ダンジョン 3: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/kakeibo-base-02-done...kakeibo-base-03-done

完成形はひとつの答えの例です。自分のコードが違っていても、ダンジョンのクリア条件を満たしていれば大丈夫です。
