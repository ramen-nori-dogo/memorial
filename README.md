# memorial
ラーメンNORI メモリアルサイト 🍜

故人のラーメン店主を偲ぶメモリアルサイトです。Googleフォームで集めた「ファンの声」と「思い出の写真」を掲載します。

## ✨ 特徴

* **2つの投稿フォーム:**
  * **想い出投稿フォーム:** ログインなしで誰でも気軽にコメント投稿可能
  * **写真投稿フォーム:** Googleログインが必要（不適切な投稿を防ぐため）
* **自動マージ:** 両方のフォームからの投稿を自動的に一覧表示
* **WebP最適化:** 画像を自動的にWebP形式に変換し、70-90%ファイルサイズ削減
* **SNSスタイルUI:** 直感的な投稿ボタンとタイムライン表示
* **完全自動化:** GitHub Actionsで自動ビルド＆デプロイ

## 🚀 セットアップ

### 1. 初期セットアップ

```bash
# 仮想環境の作成と依存ライブラリのインストール
make setup
```

### 2. サイトのビルド

```bash
# CSVを取得してビルド
make build

# ローカルキャッシュを使用してビルド（オフライン時）
make build-local
```

### 3. プレビュー

```bash
make preview
# ブラウザで http://localhost:8000 を開く
```

### 4. デプロイ

```bash
make publish
```

---

## ⚙️ 設定項目

### 1. Google スプレッドシートの CSV URL（重要）

CSV URLは**環境変数**で管理します（非公開情報のため）。

#### ローカル開発環境での設定

`.env.local` ファイルを作成して、CSV URLを設定してください：

```bash
# コメント投稿フォーム用（必須）
CSV_URL=https://docs.google.com/spreadsheets/d/e/YOUR_SPREADSHEET_ID/pub?output=csv

# 写真投稿フォーム用（オプション）
# ※写真投稿フォームはGoogleログインが必要
PHOTO_URL=https://docs.google.com/spreadsheets/d/e/YOUR_PHOTO_SPREADSHEET_ID/pub?output=csv
```
# env.sample をコピーして .env.local を作成
cp env.sample .env.local

# .env.local を編集
CSV_URL=https://docs.google.com/spreadsheets/d/e/YOUR_SPREADSHEET_ID/pub?output=csv
```

`.env.local` は `.gitignore` に含まれているため、Gitには追跡されません。

#### GitHub Actions での設定

1. GitHubリポジトリの **Settings** → **Secrets and variables** → **Actions** を開く
2. **New repository secret** をクリック
3. 以下の情報を入力：
   - **Name**: `CSV_URL`
   - **Secret**: コメント投稿フォームのスプレッドシートCSV URL
4. （オプション）写真投稿フォームを使用する場合は、同様に追加：
   - **Name**: `PHOTO_URL`
   - **Secret**: 写真投稿フォームのスプレッドシートCSV URL
   - **Secret**: `https://docs.google.com/spreadsheets/d/e/YOUR_SPREADSHEET_ID/pub?output=csv`
4. **Add secret** をクリック

#### コマンドライン引数での設定（オプション）

環境変数を使わない場合は、コマンドライン引数で指定できます：

```bash
python build.py --csv-url "https://docs.google.com/spreadsheets/d/e/YOUR_SPREADSHEET_ID/pub?output=csv"
```

**CSV URL の取得方法:**
1. Google スプレッドシートを開く
2. 「ファイル」→「共有」→「ウェブに公開」
3. 「ドキュメント全体」を選択し、形式を「カンマ区切り形式（.csv）」に
4. 「公開」ボタンをクリック
5. 表示されたURLをコピーして設定

**スプレッドシートの列構成:**

| 列名 | 説明 | 必須 |
|------|------|------|
| Timestamp | 投稿日時（Googleフォームが自動生成） | ○ |
| コメント | ファンからのメッセージ | ○ |
| 写真 | Google Drive URL（任意） | - |
| お名前 | 投稿者名（未入力時は「匿名」） | - |

---

### 2. 画像処理設定

`build.py` の以下の設定を変更できます：

```python
# build.py 28-32行目
MAX_IMAGE_WIDTH = 1200   # 最大幅（ピクセル）
MAX_IMAGE_HEIGHT = 800   # 最大高さ（ピクセル）
IMAGE_QUALITY = 85       # JPEG/WebP品質（1-100）
OUTPUT_FORMAT = "webp"   # 出力フォーマット（webp または jpg）
```

---

### 3. 店主についてのページ

`content/about.md` を編集して、店主についての紹介文を記載してください：

```markdown
# 店主について

ここに故人のラーメン店主についての紹介文を記載...

## 思い出

- いつも笑顔で迎えてくれました
- こだわりのスープは絶品でした
...
```

---

### 4. 画像の追加

`raw_images/` ディレクトリに画像ファイルを配置してください。

**対応形式:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`

ビルド時に自動でリサイズされ、`static/images/` に出力されます。

---

### 5. GitHub Pages の設定

1. GitHub リポジトリの **Settings** → **Pages** を開く
2. **Source** を「**GitHub Actions**」に設定
3. 保存

これで `main` ブランチへのプッシュ時に自動デプロイされます。

---

### 6. GitHub Actions のスケジュール設定

`.github/workflows/build_deploy.yml` でスケジュールを変更できます：

```yaml
# 毎日 UTC 0:00 (JST 9:00) に実行
schedule:
  - cron: '0 0 * * *'

# 例: 毎日 UTC 15:00 (JST 0:00) に実行
schedule:
  - cron: '0 15 * * *'
```

---

### 7. サイトのテキスト設定

`config.json` でサイトに表示されるテキストをカスタマイズできます：

```json
{
  "site": {
    "title": "想い出のラーメン - メモリアルサイト",
    "description": "故人を偲ぶメモリアルサイト - 皆様の想い出とともに",
    "shop_name": "想い出のラーメン"
  },
  "hero": {
    "title": "想い出のラーメン",
    "subtitle": "故人を偲び、皆様の想い出を集めたメモリアルサイトです",
    "icon": "bi-flower1"
  },
  "sections": {
    "about": {
      "title": "店主について"
    },
    "comments": {
      "title": "ファンの声",
      "description": "皆様から寄せられた、心温まる想い出の数々です"
    }
  }
}
```

詳細は `config.json` を参照してください。

---

## 📁 ディレクトリ構成

```
memorial/
├── .github/workflows/     # GitHub Actions 設定
├── content/               # Markdownコンテンツ
│   └── about.md          # 店主についてのページ
├── data/                  # CSVキャッシュ
├── public/                # 生成された静的サイト
├── raw_images/            # オリジナル画像（手動配置）
├── static/                # 静的ファイル
│   ├── css/style.css     # カスタムスタイル
│   └── images/           # リサイズ済み画像
├── templates/             # HTMLテンプレート
├── build.py              # ビルドスクリプト
├── Makefile              # コマンド定義
└── requirements.txt      # 依存ライブラリ
```

---

## 🛠️ コマンド一覧

| コマンド | 説明 |
|---------|------|
| `make setup` | 初期セットアップ（venv作成 + インストール） |
| `make install` | 依存ライブラリをインストール |
| `make build` | サイトをビルド（CSV取得あり） |
| `make build-local` | サイトをビルド（ローカルキャッシュ使用） |
| `make preview` | ローカルサーバーを起動（ポート8000） |
| `make publish` | 変更をコミット & プッシュ |
| `make clean` | 生成ファイルを削除 |
| `make clean-all` | 生成ファイル + venvを削除 |

---

## 📝 ライセンス

このプロジェクトは故人を偲ぶ目的で作成されました。
