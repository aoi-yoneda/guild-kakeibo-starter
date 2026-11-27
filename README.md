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
- 「外貨の支出を入れる」で、ドルなどの金額をその日の為替レートで円にして足す
- 一覧の日付に祝日の印を付け、今月の祝日を出す
- 閉じて開き直しても、収支が残る

為替と祝日はネットの API から取ります（どちらも登録・キーは要りません）。取れないときも画面は止まらず、円の欄から入れられます。

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

## 使っている API

| 用途 | API | 呼ぶ URL の例 |
| --- | --- | --- |
| 為替レート（rates.py） | [Frankfurter](https://frankfurter.dev/)（欧州中央銀行の参考レート。無料・キー不要） | `https://api.frankfurter.dev/v2/rates?base=USD&quotes=JPY&date=2026-11-20&providers=ECB` |
| 祝日（holidays.py） | [holidays-jp](https://holidays-jp.github.io/)（日本の祝日。無料・キー不要） | `https://holidays-jp.github.io/api/v1/2026/date.json` |

- 為替は、土日などレートの出ない日を頼むと、その前の営業日のレートが返ります。メモに使ったレートの日付を残します
- 同じ通貨・日付のレートは 1 時間、祝日は 1 日、覚えておいて呼び直しません
- レートは参考の値です。カードの明細の円の金額とは少しずれます
- 円にすると 1 円より少ない金額（少しの韓国ウォンなど）は入れません
- 祝日を取れなかった年は、画面を開いている間は呼び直しません。起動し直すと、もう一度試します
- 為替の返事が思っていた形でないとき（リストの中に rate が無いなど）の備えは、まだ入れていません。品質とリファクタのトラック（品質のダンジョン 4）で、偽物の通信を使うテストと一緒に足します

## 作るときの決まり

何を作るかは SPEC.md、AI に作業を頼むときの決まり（SQL は storage.py だけ・確かめ方は `python -m pytest`・kakeibo.db は上げない など）は AGENTS.md に書いています。

## 確かめ方

1. 支出 1200 ランチ を追加する
2. 収入 3000 フリマ を追加する
3. 「直す・消す」でランチの行の id を選び、金額を 1500 にして「直す」を押す
4. ターミナルで Ctrl + C で止め、`streamlit run app.py` で起動し直す
5. 2 行が残り、ランチが 1500 円になっていて、合計が手で計算した数と同じなら OK
6. 「外貨の支出を入れる」で 12.50 USD を足し、メモのレートを掛けた円の金額で一覧に入れば OK。祝日の日付の行には「祝日」の列に名前が出る

## テスト

`.venv` を有効にしたまま、pytest を入れて回します。Windows では `pytest` だけだとアプリ制御で止められることがあるので、`python -m pytest` で回します。

```bash
pip install pytest
python -m pytest
```

tests/ のテストは、Streamlit の AppTest で app.py を動かし、入力欄の決まり・合計が手計算と合うこと・開き直しても収支が残ること・選んだ 1 行だけが直る・消えることを確かめます。
storage.py では、' の入ったメモもそのまま入ること、kakeibo.csv の取り込みが 1 回だけなこと・読めない CSV では kakeibo.db を残さないこと、カテゴリ列の無い古い kakeibo.db に列が足されることも確かめます。上げないファイルが .gitignore にあることも確かめます。
為替と祝日は、ネットにつながらないときに画面が止まらず円で入れられること、レートを取れたら円にして保存すること、祝日の印と今月分への絞り込みを確かめます。
テストは一時フォルダの kakeibo.db を使うので、自分の kakeibo.db は書き換えません。テストは外のネットに出ません（requests.get を塞いでいます）。
Python 3.10・3.12・3.14 で確かめました（Streamlit 1.65〜1.67）。

## このリポジトリについて（ギルドのスターター）

AI駆動開発ギルドの作品づくり「家計簿アプリをつくる」のスターターです。「家計簿アプリの土台をつくる」（ダンジョン 1〜3）と、その続きの「データと外部連携」（ダンジョン 1・2）・「チームの開発の型」（ダンジョン 1〜5）のタグがあります。
ダンジョンの区切りごとにタグを置いているので、どのダンジョンからでも始められます。
main と `team-01-done`（チームの開発の型 ダンジョン 1 の完成形）は同じ中身です。

### タグの一覧

| タグ | 地点 | 入っているもの |
| --- | --- | --- |
| `kakeibo-base-01-start` | ダンジョン 1 を始める前 | README.md・LICENSE だけ |
| `kakeibo-base-01-done` | ダンジョン 1 の完成形（入力欄と一覧の画面） | app.py・tests/ |
| `kakeibo-base-02-done` | ダンジョン 2 の完成形（追加・合計・CSV に保存） | app.py・storage.py・tests/ |
| `kakeibo-base-03-done` | ダンジョン 3 の完成形（GitHub に上げる形） | 上に加えて requirements.txt・.gitignore・sample.csv |
| `data-01-done` | データと外部連携 ダンジョン 1 の完成形（保存先を SQLite に。追加・一覧・直す・消す・カテゴリ） | storage.py が SQLite（kakeibo.db の records 表）。.gitignore に kakeibo.db |
| `data-02-done` | データと外部連携 ダンジョン 2 の完成形（外貨を円にして保存・祝日の印） | 上に加えて rates.py・holidays.py。requirements.txt に requests |
| `team-01-done` | チームの開発の型 ダンジョン 1 の完成形（作るものを言葉にする） | 上に加えて SPEC.md・AGENTS.md・summary.py（合計の計算を app.py から分けた） |

### 始めるダンジョンと使うタグ

| 始めるダンジョン | 使うタグ |
| --- | --- |
| ダンジョン 1「家計簿の画面を作る」 | `kakeibo-base-01-start` |
| ダンジョン 2「家計簿を動く形にする」 | `kakeibo-base-01-done` |
| ダンジョン 3「家計簿を GitHub に上げる」 | `kakeibo-base-02-done` |
| データと外部連携 ダンジョン 1「データを残す SQLite と CRUD」 | `kakeibo-base-03-done` |
| データと外部連携 ダンジョン 2「外の API からデータを取る」 | `data-01-done` |
| チームの開発の型 ダンジョン 1「作るものを言葉にする」 | `data-02-done` |

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
データと外部連携・チームの開発の型から入るときは、clone したフォルダを自分の GitHub の空のリポジトリ kakeibo に上げてから始めます（上げ方は「家計簿アプリの土台をつくる」のダンジョン 3）。
Git を使わずに取るなら、GitHub の画面でタグを選び、Code → Download ZIP でも同じものが手に入ります。

### 自分のコードと比べる

ダンジョンを終えたら、そのダンジョンの完成形のタグと見比べられます。ダンジョンの間の差分は GitHub の比較の画面で見られます。

- ダンジョン 1: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/kakeibo-base-01-start...kakeibo-base-01-done
- ダンジョン 2: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/kakeibo-base-01-done...kakeibo-base-02-done
- ダンジョン 3: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/kakeibo-base-02-done...kakeibo-base-03-done
- データと外部連携 ダンジョン 1: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/kakeibo-base-03-done...data-01-done
- データと外部連携 ダンジョン 2: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/data-01-done...data-02-done
- チームの開発の型 ダンジョン 1: https://github.com/aoi-yoneda/guild-kakeibo-starter/compare/data-02-done...team-01-done

完成形はひとつの答えの例です。自分のコードが違っていても、ダンジョンのクリア条件を満たしていれば大丈夫です。
