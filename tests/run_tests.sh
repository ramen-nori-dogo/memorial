#!/bin/bash
# メニュー集計機能のテストを実行するスクリプト

cd "$(dirname "$0")/.."

echo "=========================================="
echo "メニュー集計機能のテストを実行します"
echo "=========================================="
echo ""

# Pythonのバージョンを確認
python3 --version

echo ""
echo "テストを実行中..."
echo ""

# unittestで実行
python3 -m unittest tests.test_menu_aggregation -v

echo ""
echo "=========================================="
echo "テスト完了"
echo "=========================================="
