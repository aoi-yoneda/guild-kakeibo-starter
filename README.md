# 家計簿アプリ（AI駆動開発ギルドのスターター）

AI駆動開発ギルドの作品づくり「家計簿アプリの土台をつくる」（ダンジョン 1〜3）のスターターです。
ダンジョンの区切りごとにタグを置いているので、どのダンジョンからでも始められます。

いまのタグは `kakeibo-base-01-start`（ダンジョン 1 を始める前）です。まだアプリは入っていません。
ダンジョン 1 の「準備: 家計簿のフォルダと Streamlit」から進めてください。

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
