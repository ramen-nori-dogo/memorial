この仕様を、ChatGPT (o1/4o) や Claude 3.5 Sonnet などの開発に強いAIに入力すれば、そのまま動くコードと手順が出力されるように構成した「開発指示プロンプト（要件定義書）」を作成しました。

このテキストをコピーして、開発用のAIチャットに貼り付けてください。

---

## 開発用AIへの指示プロンプト

あなたは経験豊富なPython開発者兼DevOpsエンジニアです。
以下の要件に基づき、故人（ラーメン店主）のためのメモリアルサイトを構築するための「ソースコード」「ディレクトリ構成」「セットアップ手順」を作成してください。

### 1. プロジェクト概要

* **目的:** 故人のラーメン店主を偲ぶメモリアルサイトの構築。
* **ホスティング:** GitHub Pages (静的サイト)。
* **主要機能:**
* Googleフォームで集めた「ファンの声（コメント）」の掲載。
* 故人やラーメンの「写真」の掲載（管理者が選別）。
* サイト生成の自動化（Pythonスクリプト）。



### 2. システム要件 & アーキテクチャ

#### データソース

* **テキスト:** Googleフォームの回答が蓄積されるGoogleスプレッドシート。
* 項目: `Timestamp` (自動), `コメント` (必須), `お名前` (任意), `好きだったメニュー` (任意), `写真` (任意/Google Drive URL)。
* 取得方法: スプレッドシートを「Webに公開 (CSV)」し、そのURLからPythonで取得する。
* **セキュリティ:** CSV URLは環境変数（`.env.local`）で管理し、Gitにコミットしない。


* **画像:**
* **自動ダウンロード:** CSV内のGoogle Drive URLから画像を自動ダウンロードして `raw_images/` に保存。
* **管理者による追加:** 管理者が選定した店舗写真などを `raw_images/` ディレクトリに配置。
* **自動最適化:** すべての画像を自動的にWebP形式に変換し、`static/images/` に出力（ファイルサイズ削減）。
* 注意: 不適切な画像を除外するため、管理者の手動フィルタリング（配置作業）を挟む運用とする。



#### 技術スタック

* **言語:** Python 3.x
* **ライブラリ:**
* `pandas`: CSV処理
* `jinja2`: HTMLテンプレートエンジン
* `markdown`: 固定ページの変換
* `Pillow`: 画像の最適化・リサイズ・WebP変換
* `requests`: CSV・画像のダウンロード


* **フロントエンド:**
* Bootstrap 5: レスポンシブデザイン
* Bootstrap Icons: アイコン表示

* **自動化:** GitHub Actions (定期実行および手動トリガー)

### 3. ディレクトリ構成案

以下の構成を前提にコードを作成してください。

```text
memorial-site/
├── .github/
│   └── workflows/
│       └── build_deploy.yml  # GitHub Actions設定
├── content/
│   └── about.md              # 店主についての固定ページ（Markdown）
├── data/
│   └── comments.csv          # (Cache用) スプレッドシートから取得したデータ
├── raw_images/               # 【入力】オリジナル画像（管理者配置+自動ダウンロード）
├── static/
│   ├── css/
│   │   └── style.css         # カスタムCSS
│   └── images/               # 【出力】WebPに最適化された画像
├── templates/
│   ├── base.html             # ベーステンプレート
│   └── index.html            # メインページ（タイムライン・タブ・ギャラリー）
├── public/                   # 【出力】生成された静的サイト
├── build.py                  # サイト生成のメインスクリプト
├── config.json               # UI設定ファイル（テキスト・ラベル等）
├── requirements.txt          # Python依存ライブラリ
├── Makefile                  # 操作コマンド定義
├── .env.local                # ローカル環境変数（CSV URL等）※Gitignore対象
├── env.sample                # 環境変数のサンプルファイル
├── .gitignore
└── README.md

```

### 4. 実装詳細要件

#### A. ビルドスクリプト (`build.py`) の挙動

1. **環境設定読み込み:**
* `.env.local` から CSV_URL を読み込む（環境変数またはコマンドライン引数）。
* `config.json` からUI設定（テキスト・ラベル・アイコン等）を読み込む。

2. **データ取得:** 
* 指定されたCSV URLからデータを取得し、`data/comments.csv` に保存（または更新）。
* 文字エンコーディングを明示的にUTF-8で処理。

3. **画像処理:**
* **自動ダウンロード:** CSV内の「写真」列にあるGoogle Drive URLから画像を自動ダウンロードし、`raw_images/` に保存。
* **WebP変換:** `raw_images/` 内のすべての画像（JPG/PNG/JPEG）をWebP形式に変換し、`static/images/` に出力。
* **ファイルサイズ削減:** 画質を維持しながらファイルサイズを大幅に削減（通常70-90%削減）。
* **コメントとの紐付け:** タイムスタンプベースのファイル名で、コメントと写真を紐付け。
* 名前欄が入力されていない人は「匿名」として表示すること。
* 写真を投稿した人はコメントの下に「写真」を表示すること。

---
### 追加仕様
* コメント投稿フォーム（CSV_URL）と、写真投稿フォーム（PHOTO_URL）を分けた。
  * コメント投稿フォームはログインなし、写真投稿はログインあり（その旨記載）
* 投稿コメント、写真は、共に一覧にリストすること

---ここまでで一旦終了--
<!-- * コメント、写真一覧はSNSライクなUIにすること -->
<!-- * ギャラリーに掲載された写真をクリックすると、投稿者とコメントが見えるようにすること -->

1. **店舗変遷の抽出:**
* `content/about.md` から「店舗の変遷」セクションを抽出し、タブ表示用のデータ構造に変換。

1. **HTML生成:**
* `content/about.md` をHTMLに変換（店舗変遷セクションは別処理）。
* `data/comments.csv` の内容をリスト化。
* `config.json` の設定を読み込み。
* `jinja2` テンプレートに上記データを渡し、最終的な `index.html` を `public/` に出力。
* CSSと画像を `public/static/` にコピー。



#### B. Makefile のコマンド定義

以下のコマンドを実装してください。

* `make setup`: Python仮想環境（venv）のセットアップ。
* `make install`: 依存ライブラリのインストール。
* `make build`: `build.py` を実行し、静的ファイルを生成（.env.local から環境変数を読み込む）。
* `make build-local`: ローカル開発用ビルド（CSVダウンロードスキップ可能）。
* `make preview`: 生成されたディレクトリをルートとしてローカルサーバー (`python -m http.server`) を起動。
  * **ポート競合対策:** ポート8000を使用中のプロセスを自動的にkillしてから起動。
* `make publish`: 変更を git commit & push する（mainブランチへ）。
* `make clean`: 生成ファイル（public/）を削除。
* `make clean-all`: 生成ファイル、キャッシュ、仮想環境をすべて削除。

#### C. GitHub Actions (`build_deploy.yml`)

* トリガー: `main` ブランチへの push、および スケジュール実行（例: 毎日0時）。
* 処理:
1. 環境構築 (`pip install`)
2. **環境変数設定:** GitHub Secretsから `CSV_URL` と `PHOTO_URL`（オプション）を読み込む。
3. ビルド実行 (`python build.py`) ※コメントと写真投稿の両方のCSVを自動取得・マージ、画像の自動ダウンロードを含む
4. 生成されたHTMLを `gh-pages` ブランチにデプロイ（`peaceiris/actions-gh-pages` などを使用）。

* **GitHub Pages設定:**
* リポジトリ設定で「GitHub Actions」をソースとして選択。
* ワークフローに必要な権限（contents: write, pages: write）を付与。
* GitHub Secretsに `CSV_URL`（必須）と `PHOTO_URL`（オプション）を設定。


#### D. 設定ファイル (`config.json`)

すべてのUI要素（テキスト・ラベル・アイコン等）を外部化し、コード変更なしでカスタマイズ可能に。

* **含まれる設定:**
* サイトタイトル・説明文
* ヒーローセクションのテキスト
* ナビゲーションラベル
* セクションタイトル・説明文
* フッターテキスト
* アイコン（Bootstrap Icons）
* 空メッセージ等

#### E. UIデザインとユーザー体験

* **レスポンシブデザイン:** スマホ・タブレット・PCすべてに対応。
* **店舗の変遷:** Bootstrapのタブ機能で各時代の店舗写真を切り替え表示。
* **ヘッダー背景:** 印象的な背景画像（`ramen_nori_bg.webp`）をヒーローセクションに設定。
* **SNSスタイルの投稿ボタン:**
  * ヒーローセクションに大きなCTAボタン
  * 画面右下にフローティングアクションボタン（FAB）
  * パルスアニメーションで視認性向上
* **タイムライン表示:** コメントをタイムライン形式で美しく表示。
* **画像モーダル:** クリックで画像を拡大表示。
* **スムーススクロール:** ナビゲーションリンクでスムーズにスクロール。



### 5. 成果物

以下のファイルの中身を出力してください。

1. `requirements.txt` - Python依存ライブラリ
2. `build.py` - 詳細なコメント付きメインスクリプト
3. `templates/base.html` - ベーステンプレート
4. `templates/index.html` - メインページテンプレート（Bootstrap 5使用）
5. `static/css/style.css` - カスタムCSS
6. `config.json` - UI設定ファイル
7. `Makefile` - ビルド・プレビューコマンド
8. `.github/workflows/build_deploy.yml` - GitHub Actions設定
9. `env.sample` - 環境変数サンプル
10. `.gitignore` - Git除外設定

---

### 6. セットアップ手順

1. **リポジトリの準備:**
```bash
git clone <repository-url>
cd memorial-site
```

2. **Python環境のセットアップ:**
```bash
make setup      # 仮想環境作成
make install    # 依存ライブラリインストール
```

3. **環境変数の設定:**
```bash
cp env.sample .env.local
# .env.local を編集してCSV_URLを設定
```

4. **Googleフォームとスプレッドシートの準備:**
* Googleフォームを作成（想い出投稿用）
* スプレッドシートを「Webに公開 (CSV)」
* CSV URLを `.env.local` に設定

5. **ローカルビルド＆プレビュー:**
```bash
make build      # サイト生成
make preview    # http://localhost:8000 でプレビュー
```

6. **GitHub Pagesへのデプロイ:**
* GitHub Secretsに `CSV_URL` を設定
* リポジトリ設定で GitHub Pages を有効化（ソース: GitHub Actions）
* `main` ブランチにpushすると自動デプロイ

---

### 7. カスタマイズ方法

* **テキスト変更:** `config.json` を編集（コード変更不要）
* **店主情報:** `content/about.md` を編集
* **店舗写真追加:** `raw_images/` に画像を配置して `make build`
* **デザイン変更:** `static/css/style.css` を編集
* **ヘッダー背景:** `raw_images/ramen_nori_bg.webp` を配置

---

### 8. 技術的な特徴

* **自動化:** CSV更新、画像ダウンロード、WebP変換、デプロイがすべて自動
* **最適化:** WebP変換でファイルサイズを70-90%削減
* **セキュリティ:** CSV URLなどの機密情報は環境変数で管理
* **保守性:** UI要素をconfig.jsonで外部化し、コード変更不要
* **レスポンシブ:** すべてのデバイスで美しく表示
* **ユーザビリティ:** SNSスタイルの投稿ボタンで直感的な操作
* **パフォーマンス:** 静的サイトで高速表示

これで、ご希望通りの「想いのこもった、メンテナンスフリーなメモリアルサイト」が完成します。