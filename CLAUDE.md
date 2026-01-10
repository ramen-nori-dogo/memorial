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
* 項目: `Timestamp` (自動), `コメント` (必須), `写真` (任意/Google Drive URL), `お名前` (任意)。
* 取得方法: スプレッドシートを「Webに公開 (CSV)」し、そのURLからPythonで取得する。


* **画像:**
* 運用: 管理者がGoogleフォームのアップロード先（Google Drive）から手動でダウンロードし、ローカルリポジトリの `raw_images/` ディレクトリに配置する。
* 注意: 不適切な画像を除外するため、管理者の手動フィルタリング（配置作業）を挟む運用とする。



#### 技術スタック

* **言語:** Python 3.x
* **ライブラリ:**
* `pandas`: CSV処理
* `jinja2`: HTMLテンプレートエンジン
* `markdown`: 固定ページの変換
* `Pillow`: 画像の最適化・リサイズ


* **自動化:** GitHub Actions (定期実行および手動トリガー)

### 3. ディレクトリ構成案

以下の構成を前提にコードを作成してください。

```text
memorial-site/
├── .github/
│   └── workflows/
│       └── build_deploy.yml  # GitHub Actions設定
├── content/
│   └── about.md              # 店主についての固定ページ
├── data/
│   └── comments.csv          # (Cache用) スプレッドシートから取得したデータ
├── raw_images/               # 【入力】管理者が手動で置くオリジナル画像
├── static/
│   ├── css/
│   │   └── style.css
│   └── images/               # 【出力】スクリプトによりリサイズ・生成された画像
├── templates/
│   ├── base.html
│   └── index.html            # タイムライン形式でコメントと画像を表示
├── build.py                  # サイト生成のメインスクリプト
├── requirements.txt
└── Makefile                  # 操作コマンド定義

```

### 4. 実装詳細要件

#### A. ビルドスクリプト (`build.py`) の挙動

1. **データ取得:** 指定されたCSV URLからデータを取得し、`data/comments.csv` に保存（または更新）。
2. **画像処理:**
* CSV内の「写真」列にURLがある行を特定する。
* **紐付けロジック:** 今回は簡易化のため、`raw_images/` 内にあるファイル名と、CSVの「行番号」または「投稿日時」などを紐付ける、あるいは単純に「画像ギャラリー」としてコメントとは切り離して表示する形式でも可。
* ※今回は**「raw_images内の画像をすべて WebP または JPG にリサイズして static/images/ に出力し、ファイル名リストをHTMLに渡す」**というギャラリー方式で実装してください。
* 名前欄が入力ない人は「匿名」として表示すること。
* 写真投稿した人はコメントの下に「写真」を表示すること。


3. **HTML生成:**
* `content/about.md` をHTMLに変換。
* `data/comments.csv` の内容をリスト化。
* `jinja2` テンプレートに上記データを渡し、最終的な `index.html` をルートディレクトリ（または `public/`）に出力。



#### B. Makefile のコマンド定義

以下のコマンドを実装してください。

* `make install`: 依存ライブラリのインストール。
* `make build`: `build.py` を実行し、静的ファイルを生成。
* `make preview`: 生成されたディレクトリをルートとしてローカルサーバー (`python -m http.server`) を起動。
* `make publish`: 変更を git commit & push する（mainブランチへ）。

#### C. GitHub Actions (`build_deploy.yml`)

* トリガー: `main` ブランチへの push、および スケジュール実行（例: 毎日0時）。
* 処理:
1. 環境構築 (`pip install`)
2. ビルド実行 (`python build.py`) ※CSVの最新化を含む
3. 生成されたHTMLを `gh-pages` ブランチにデプロイ（`peaceiris/actions-gh-pages` などを使用）。



### 5. 成果物

以下のファイルの中身を出力してください。

1. `requirements.txt`
2. `build.py` (詳細なコメント付きで)
3. `templates/index.html` (BootstrapなどCDNを使ったシンプルなデザインで)
4. `Makefile`
5. `.github/workflows/build_deploy.yml`

---

### 補足：この後の流れ

1. 上記のプロンプトをAIに投げると、コードが出力されます。
2. ご自身のPC（VS Codeなど）でフォルダを作り、出力されたコードをファイルとして保存します。
3. Googleフォームとスプレッドシートを用意し、CSVのURLを取得して、`build.py` 内のURL部分を書き換えます。
4. `make build` → `make preview` で動作確認します。

これで、ご希望通りの「想いのこもった、メンテナンスフリーなサイト」の土台が出来上がります。