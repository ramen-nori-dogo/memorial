# =============================================================================
# Memorial Site - Makefile
# メモリアルサイト構築用のコマンド定義
# =============================================================================

# Python 実行環境（仮想環境を使用）
VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# ディレクトリ
PUBLIC_DIR := public
PORT := 8000

# デフォルトターゲット
.PHONY: help
help:
	@echo "=============================================="
	@echo "🍜 メモリアルサイト - コマンド一覧"
	@echo "=============================================="
	@echo ""
	@echo "  make setup     - 初期セットアップ（venv作成 + インストール）"
	@echo "  make install   - 依存ライブラリをインストール"
	@echo "  make build     - サイトをビルド（CSVを取得して静的ファイル生成）"
	@echo "  make build-local - サイトをビルド（ローカルキャッシュを使用）"
	@echo "  make preview   - ローカルサーバーを起動してプレビュー"
	@echo "  make publish   - 変更をコミットしてプッシュ"
	@echo "  make clean     - 生成ファイルを削除"
	@echo ""

# 仮想環境の作成
$(VENV)/bin/activate:
	@echo "🐍 仮想環境を作成中..."
	python3 -m venv $(VENV)
	@echo "✅ 仮想環境を作成しました"

# 初期セットアップ（venv作成 + インストール）
.PHONY: setup
setup: $(VENV)/bin/activate install
	@echo "✅ セットアップ完了"
	@echo "   次は 'make build' でビルドしてください"

# 依存ライブラリのインストール
.PHONY: install
install: $(VENV)/bin/activate
	@echo "📦 依存ライブラリをインストール中..."
	$(PIP) install -r requirements.txt
	@echo "✅ インストール完了"

# サイトのビルド（CSV取得あり）
.PHONY: build
build: $(VENV)/bin/activate
	@echo "🔨 サイトをビルド中..."
	@if [ -f .env.local ]; then \
		echo "📝 環境変数を .env.local から読み込み中..."; \
		export $$(cat .env.local | grep -v '^#' | xargs) && $(PYTHON) build.py; \
	else \
		$(PYTHON) build.py; \
	fi
	@echo "✅ ビルド完了"

# サイトのビルド（ローカルキャッシュを使用）
.PHONY: build-local
build-local: $(VENV)/bin/activate
	@echo "🔨 サイトをビルド中（ローカルキャッシュ使用）..."
	$(PYTHON) build.py --skip-fetch
	@echo "✅ ビルド完了"

# ローカルプレビューサーバーの起動
.PHONY: preview
preview:
	@echo "🌐 ローカルサーバーを起動中..."
	@# 既存のhttp.serverプロセスをKILL
	@if pgrep -f "http.server $(PORT)" > /dev/null 2>&1; then \
		echo "⚠️ ポート $(PORT) で実行中のプロセスを停止中..."; \
		pkill -f "http.server $(PORT)" || true; \
		sleep 1; \
		echo "✅ 既存プロセスを停止しました"; \
	fi
	@echo "   URL: http://localhost:$(PORT)"
	@echo "   終了するには Ctrl+C を押してください"
	@cd $(PUBLIC_DIR) && python3 -m http.server $(PORT)

# 変更をコミットしてプッシュ
.PHONY: publish
publish:
	@echo "📤 変更をコミット & プッシュ中..."
	git add .
	git commit -m "Update memorial site - $$(date '+%Y-%m-%d %H:%M:%S')" || true
	git push origin main
	@echo "✅ プッシュ完了"

# 生成ファイルの削除
.PHONY: clean
clean:
	@echo "🧹 生成ファイルを削除中..."
	rm -rf $(PUBLIC_DIR)
	rm -rf static/images/*
	@echo "✅ クリーン完了"

# 完全クリーン（venvも削除）
.PHONY: clean-all
clean-all: clean
	@echo "🧹 仮想環境も削除中..."
	rm -rf $(VENV)
	@echo "✅ 完全クリーン完了"
