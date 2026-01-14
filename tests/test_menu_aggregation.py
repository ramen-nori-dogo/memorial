#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_menu_aggregation.py - メニュー集計機能のユニットテスト

「好きだったメニュー」の集計機能をテストします。
- カンマ区切り（,）
- 全角カンマ（、）
- 全角カンマ（，）
- 複数区切り文字の混在
- 空欄の処理
"""

import unittest
import sys
from pathlib import Path
import pandas as pd

# プロジェクトルートをパスに追加
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from build import aggregate_menu_items, normalize_form_df


class TestMenuAggregation(unittest.TestCase):
    """メニュー集計機能のテストクラス"""
    
    @classmethod
    def setUpClass(cls):
        """テストクラス全体のセットアップ"""
        cls.test_data_dir = PROJECT_ROOT / "tests" / "data"
        cls.test_csv_path = cls.test_data_dir / "comments.csv"
    
    def setUp(self):
        """各テストメソッドの前に実行されるセットアップ"""
        pass
    
    def test_load_test_data(self):
        """テストデータが正しく読み込めることを確認"""
        self.assertTrue(
            self.test_csv_path.exists(),
            f"テストデータファイルが見つかりません: {self.test_csv_path}"
        )
        
        df = pd.read_csv(self.test_csv_path, encoding='utf-8')
        self.assertFalse(df.empty, "テストデータが空です")
        print(f"\n✓ テストデータ読み込み成功: {len(df)} 件")
    
    def test_aggregate_with_normalized_dataframe(self):
        """正規化済みDataFrameでの集計テスト"""
        # テストデータを読み込み
        df = pd.read_csv(self.test_csv_path, encoding='utf-8')
        
        # 正規化
        df_normalized = normalize_form_df(df, "comments")
        
        # 集計実行
        menu_stats = aggregate_menu_items(df_normalized)
        
        # 結果が辞書であることを確認
        self.assertIsInstance(menu_stats, dict)
        self.assertGreater(len(menu_stats), 0, "集計結果が空です")
        
        # 降順ソートされていることを確認
        values = list(menu_stats.values())
        self.assertEqual(values, sorted(values, reverse=True), "降順ソートされていません")
        
        print(f"\n✓ 集計結果: {len(menu_stats)} 種類のメニュー")
        for menu, count in list(menu_stats.items())[:10]:
            print(f"  - {menu}: {count}票")
    
    def test_aggregate_with_raw_dataframe(self):
        """生のDataFrame（正規化前）での集計テスト"""
        # テストデータを読み込み（正規化しない）
        df = pd.read_csv(self.test_csv_path, encoding='utf-8')
        
        # 集計実行（正規化前のDataFrameでも動作することを確認）
        menu_stats = aggregate_menu_items(df)
        
        # 結果が辞書であることを確認
        self.assertIsInstance(menu_stats, dict)
        self.assertGreater(len(menu_stats), 0, "集計結果が空です")
        
        print(f"\n✓ 生データからの集計成功: {len(menu_stats)} 種類のメニュー")
    
    def test_comma_separated_menus(self):
        """カンマ区切りのメニューを正しく分割できることを確認"""
        # カンマ区切りのテストデータを作成
        test_data = {
            "timestamp": ["2026/01/11 8:00:00"],
            "comment": ["テストコメント"],
            "name": ["テストユーザー"],
            "menu": ["塩ラーメン, 焦がしガーリック, わさび塩"],
            "photo": [""]
        }
        df = pd.DataFrame(test_data)
        
        menu_stats = aggregate_menu_items(df)
        
        # 3つのメニューがそれぞれ1回ずつカウントされていることを確認
        self.assertEqual(menu_stats.get("塩ラーメン", 0), 1)
        self.assertEqual(menu_stats.get("焦がしガーリック", 0), 1)
        self.assertEqual(menu_stats.get("わさび塩", 0), 1)
        self.assertEqual(len(menu_stats), 3)
    
    def test_fullwidth_comma_separated_menus(self):
        """全角カンマ（、）区切りのメニューを正しく分割できることを確認"""
        # 全角カンマ区切りのテストデータを作成
        test_data = {
            "timestamp": ["2026/01/11 8:00:00"],
            "comment": ["テストコメント"],
            "name": ["テストユーザー"],
            "menu": ["レモン塩、柚子胡椒"],
            "photo": [""]
        }
        df = pd.DataFrame(test_data)
        
        menu_stats = aggregate_menu_items(df)
        
        # 2つのメニューがそれぞれ1回ずつカウントされていることを確認
        self.assertEqual(menu_stats.get("レモン塩", 0), 1)
        self.assertEqual(menu_stats.get("柚子胡椒", 0), 1)
        self.assertEqual(len(menu_stats), 2)
    
    def test_mixed_separators(self):
        """複数の区切り文字が混在している場合のテスト"""
        # カンマと全角カンマが混在するテストデータ
        test_data = {
            "timestamp": ["2026/01/11 8:00:00"],
            "comment": ["テストコメント"],
            "name": ["テストユーザー"],
            "menu": ["塩ラーメン, 焦がしガーリック、わさび塩"],
            "photo": [""]
        }
        df = pd.DataFrame(test_data)
        
        menu_stats = aggregate_menu_items(df)
        
        # 3つのメニューがそれぞれ1回ずつカウントされていることを確認
        self.assertEqual(menu_stats.get("塩ラーメン", 0), 1)
        self.assertEqual(menu_stats.get("焦がしガーリック", 0), 1)
        self.assertEqual(menu_stats.get("わさび塩", 0), 1)
        self.assertEqual(len(menu_stats), 3)
    
    def test_empty_menu_field(self):
        """空のメニュー欄を正しく処理できることを確認"""
        # 空のメニュー欄を含むテストデータ
        test_data = {
            "timestamp": ["2026/01/11 8:00:00", "2026/01/11 9:00:00"],
            "comment": ["テストコメント1", "テストコメント2"],
            "name": ["テストユーザー1", "テストユーザー2"],
            "menu": ["塩ラーメン", ""],
            "photo": ["", ""]
        }
        df = pd.DataFrame(test_data)
        
        menu_stats = aggregate_menu_items(df)
        
        # 空のメニューはカウントされず、塩ラーメンのみが1回カウントされることを確認
        self.assertEqual(menu_stats.get("塩ラーメン", 0), 1)
        self.assertEqual(len(menu_stats), 1)
    
    def test_single_menu(self):
        """単一メニューの場合のテスト"""
        test_data = {
            "timestamp": ["2026/01/11 8:00:00"],
            "comment": ["テストコメント"],
            "name": ["テストユーザー"],
            "menu": ["裏メニュー"],
            "photo": [""]
        }
        df = pd.DataFrame(test_data)
        
        menu_stats = aggregate_menu_items(df)
        
        # 1つのメニューが1回カウントされていることを確認
        self.assertEqual(menu_stats.get("裏メニュー", 0), 1)
        self.assertEqual(len(menu_stats), 1)
    
    def test_multiple_occurrences(self):
        """同じメニューが複数回出現する場合の集計テスト"""
        test_data = {
            "timestamp": ["2026/01/11 8:00:00", "2026/01/11 9:00:00", "2026/01/11 10:00:00"],
            "comment": ["コメント1", "コメント2", "コメント3"],
            "name": ["ユーザー1", "ユーザー2", "ユーザー3"],
            "menu": ["焦がしガーリック", "焦がしガーリック, わさび塩", "焦がしガーリック"],
            "photo": ["", "", ""]
        }
        df = pd.DataFrame(test_data)
        
        menu_stats = aggregate_menu_items(df)
        
        # 焦がしガーリックが3回、わさび塩が1回カウントされていることを確認
        self.assertEqual(menu_stats.get("焦がしガーリック", 0), 3)
        self.assertEqual(menu_stats.get("わさび塩", 0), 1)
        # 降順ソートされていることを確認（焦がしガーリックが最初）
        first_menu = list(menu_stats.keys())[0]
        self.assertEqual(first_menu, "焦がしガーリック")
    
    def test_whitespace_handling(self):
        """空白文字の処理を確認"""
        test_data = {
            "timestamp": ["2026/01/11 8:00:00"],
            "comment": ["テストコメント"],
            "name": ["テストユーザー"],
            "menu": [" 塩ラーメン , 焦がしガーリック , わさび塩 "],
            "photo": [""]
        }
        df = pd.DataFrame(test_data)
        
        menu_stats = aggregate_menu_items(df)
        
        # 前後の空白が削除されていることを確認
        self.assertEqual(menu_stats.get("塩ラーメン", 0), 1)
        self.assertEqual(menu_stats.get("焦がしガーリック", 0), 1)
        self.assertEqual(menu_stats.get("わさび塩", 0), 1)
        # 空白のみの項目は含まれていないことを確認
        self.assertNotIn(" ", menu_stats)
        self.assertNotIn("", menu_stats)
    
    def test_empty_dataframe(self):
        """空のDataFrameを処理できることを確認"""
        df = pd.DataFrame(columns=["timestamp", "comment", "name", "menu", "photo"])
        
        menu_stats = aggregate_menu_items(df)
        
        # 空の辞書が返されることを確認
        self.assertIsInstance(menu_stats, dict)
        self.assertEqual(len(menu_stats), 0)
    
    def test_real_test_data_aggregation(self):
        """実際のテストデータでの集計結果を確認"""
        # テストデータを読み込み
        df = pd.read_csv(self.test_csv_path, encoding='utf-8')
        
        # 正規化
        df_normalized = normalize_form_df(df, "comments")
        
        # 集計実行
        menu_stats = aggregate_menu_items(df_normalized)
        
        # 期待されるメニューが含まれていることを確認
        # テストデータから確認できる主要なメニュー
        expected_menus = ["裏メニュー", "焦がしガーリック", "塩ラーメン", "わさび塩"]
        
        for menu in expected_menus:
            self.assertIn(menu, menu_stats, f"期待されるメニュー '{menu}' が集計結果に含まれていません")
            self.assertGreater(menu_stats[menu], 0, f"メニュー '{menu}' のカウントが0です")
        
        print(f"\n✓ 実際のテストデータでの集計成功")
        print(f"  総メニュー数: {len(menu_stats)}")
        print(f"  トップ5:")
        for i, (menu, count) in enumerate(list(menu_stats.items())[:5], 1):
            print(f"    {i}. {menu}: {count}票")
    
    def test_garlic_count_in_test_data(self):
        """テストデータでの「焦がしガーリック」の集計件数が正しいことを確認"""
        # テストデータを読み込み
        df = pd.read_csv(self.test_csv_path, encoding='utf-8')
        
        # 正規化
        df_normalized = normalize_form_df(df, "comments")
        
        # 集計実行
        menu_stats = aggregate_menu_items(df_normalized)
        
        # 「焦がしガーリック」が集計結果に含まれていることを確認
        self.assertIn("焦がしガーリック", menu_stats, 
                     "「焦がしガーリック」が集計結果に含まれていません")
        
        # 「焦がしガーリック」の件数が6件であることを確認
        garlic_count = menu_stats.get("焦がしガーリック", 0)
        self.assertEqual(
            garlic_count, 6,
            f"「焦がしガーリック」の集計件数が正しくありません。期待値: 6件, 実際: {garlic_count}件"
        )
        
        print(f"\n✓ 「焦がしガーリック」の集計件数確認成功: {garlic_count}件")


if __name__ == "__main__":
    # テストを実行
    unittest.main(verbosity=2)
