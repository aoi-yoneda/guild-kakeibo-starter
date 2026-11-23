# 家計簿アプリ（AI駆動開発ギルドのスターター）

AI駆動開発ギルドの作品づくり「家計簿アプリの土台をつくる」（ダンジョン 1〜3）のスターターです。
ダンジョンの区切りごとにタグを置いているので、どのダンジョンからでも始められます。

いまのタグは `kakeibo-base-02-done`（ダンジョン 2 の完成形）です。
「追加」で収支を一覧に足し、収入・支出・残高の合計を出します。収支は kakeibo.csv に残るので、閉じて開き直しても戻ります。
kakeibo.csv が無いときは、空の一覧から始まります。

## 起動のしかた

Python 3.10 以上で動きます（ギルドの教材では 3.12 を入れます）。

Windows（PowerShell）:

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install streamlit pandas
streamlit run app.py
```

Mac（ターミナル）:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit pandas
streamlit run app.py
```

初めて起動すると、ターミナルで Email を聞かれます。空のまま Enter を押せば進みます。
ブラウザで http://localhost:8501 が開き、「家計簿」の画面が出ます。止めるときはターミナルで Ctrl + C。
Windows で `.venv\Scripts\activate` が「スクリプトの実行が無効」で止まるときは、`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` を 1 回打ってからやり直します。
Windows で `streamlit run app.py` が止められるときは、代わりに `python -m streamlit run app.py` で起動します。

## 確かめ方

1. 支出 1200 ランチ を追加する
2. 収入 3000 フリマ を追加する
3. ターミナルで Ctrl + C で止め、`streamlit run app.py` で起動し直す
4. 一覧に 2 行が残り、収入 3,000 円・支出 1,200 円・残高 1,800 円になっていれば OK

収支は app.py と同じフォルダの kakeibo.csv（列は 日付,区分,金額,メモ、文字コードは utf-8）に残ります。最初からやり直すときは kakeibo.csv を消します。

## テスト

`.venv` を有効にしたまま、pytest を入れて回します。Windows では `pytest` だけだとアプリ制御で止められることがあるので、`python -m pytest` で回します。

```bash
pip install pytest
python -m pytest
```

tests/ のテストは、Streamlit の AppTest で app.py を動かし、入力欄の決まり・合計が手計算と合うこと・開き直しても収支が残ることを確かめます。storage.py の読み書きも確かめます。
テストは一時フォルダの CSV を使うので、自分の kakeibo.csv は書き換えません。
Python 3.10・3.12・3.14 で確かめました（Streamlit 1.65〜1.67）。
tests/ はスターターのものです。自分の GitHub に上げても、消してもかまいません。この README は、ダンジョン 3 のクエスト 2 で自分の家計簿の README に書き換えます。

## タグの一覧

| タグ | 地点 | 入っているもの |
| --- | --- | --- |
| `kakeibo-base-01-start` | ダンジョン 1 を始める前 | README.md・LICENSE だけ |
| `kakeibo-base-01-done` | ダンジョン 1 の完成形（入力欄と一覧の画面） | app.py・tests/ |
| `kakeibo-base-02-done` | ダンジョン 2 の完成形（追加・合計・CSV に保存） | app.py・storage.py・tests/ |
| `kakeibo-base-03-done` | ダンジョン 3 の完成形（GitHub に上げる形） | 上に加えて requirements.txt・.gitignore・sample.csv |

## 始めるダンジョンと使うタグ

| 始めるダンジョン | 使うタグ |
| --- | --- |
| ダンジョン 1「家計簿の画面を作る」 | `kakeibo-base-01-start` |
| ダンジョン 2「家計簿を動く形にする」 | `kakeibo-base-01-done` |
| ダンジョン 3「家計簿を GitHub に上げる」 | `kakeibo-base-02-done` |

## 途中から入る

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

## 自分のコードと比べる

ダンジョンを終えたら、そのダンジョンの完成形のタグと見比べられます。ダンジョンの間の差分は GitHub の比較の画面で見られます。

- ダンジョン 1: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/kakeibo-base-01-start...kakeibo-base-01-done
- ダンジョン 2: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/kakeibo-base-01-done...kakeibo-base-02-done
- ダンジョン 3: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/kakeibo-base-02-done...kakeibo-base-03-done

完成形はひとつの答えの例です。自分のコードが違っていても、ダンジョンのクリア条件を満たしていれば大丈夫です。
