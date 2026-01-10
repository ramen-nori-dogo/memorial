#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py - メモリアルサイト静的生成スクリプト

このスクリプトは以下の処理を行います：
1. Google スプレッドシートからCSVデータを取得
2. raw_images/ 内の画像をリサイズして static/images/ に出力
3. Jinja2 テンプレートを使用して HTML を生成

Usage:
    python build.py [--csv-url URL]
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import json

import pandas as pd
import markdown
import requests
from jinja2 import Environment, FileSystemLoader
from PIL import Image

# =============================================================================
# 設定
# =============================================================================

# プロジェクトのルートディレクトリ
BASE_DIR = Path(__file__).parent.resolve()

# 各種ディレクトリパス
TEMPLATES_DIR = BASE_DIR / "templates"
CONTENT_DIR = BASE_DIR / "content"
DATA_DIR = BASE_DIR / "data"
RAW_IMAGES_DIR = BASE_DIR / "raw_images"
STATIC_DIR = BASE_DIR / "static"
OUTPUT_IMAGES_DIR = STATIC_DIR / "images"
PUBLIC_DIR = BASE_DIR / "public"
CONFIG_FILE = BASE_DIR / "config.json"

# 画像処理設定
MAX_IMAGE_WIDTH = 1200  # 最大幅（ピクセル）
MAX_IMAGE_HEIGHT = 800  # 最大高さ（ピクセル）
IMAGE_QUALITY = 85      # JPEG/WebP品質（1-100）
OUTPUT_FORMAT = "webp"  # 出力フォーマット（webp または jpg）

# Google スプレッドシートの公開CSV URL
# 環境変数 CSV_URL で設定するか、コマンドライン引数 --csv-url で指定してください
DEFAULT_CSV_URL = os.environ.get("CSV_URL", "")


# =============================================================================
# ユーティリティ関数
# =============================================================================

def ensure_directories():
    """
    必要なディレクトリが存在することを確認し、なければ作成します。
    """
    directories = [DATA_DIR, OUTPUT_IMAGES_DIR, PUBLIC_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ ディレクトリ確認: {directory}")


def load_config() -> dict:
    """
    設定ファイル（config.json）を読み込みます。
    
    Returns:
        dict: 設定情報の辞書
    """
    if not CONFIG_FILE.exists():
        print(f"⚠️ 設定ファイルが見つかりません: {CONFIG_FILE}")
        print("   デフォルト設定を使用します")
        return {}
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"⚠️ 設定ファイルの読み込みに失敗: {e}")
        print("   デフォルト設定を使用します")
        return {}


def fetch_csv_data(csv_url: str) -> pd.DataFrame:
    """
    Google スプレッドシートからCSVデータを取得します。
    
    Args:
        csv_url: CSV形式で公開されたスプレッドシートのURL
    
    Returns:
        pandas.DataFrame: 取得したデータ
    """
    print(f"\n📥 CSVデータを取得中: {csv_url[:50]}...")
    
    try:
        # URLからCSVを取得
        response = requests.get(csv_url, timeout=30)
        response.raise_for_status()
        
        # レスポンスのエンコーディングをUTF-8に設定
        response.encoding = 'utf-8'
        
        # CSVをDataFrameに変換
        from io import StringIO
        df = pd.read_csv(StringIO(response.text), encoding='utf-8')
        
        # ローカルにキャッシュとして保存
        cache_path = DATA_DIR / "comments.csv"
        df.to_csv(cache_path, index=False, encoding="utf-8")
        print(f"✓ CSVデータを保存: {cache_path}")
        print(f"  → {len(df)} 件のコメントを取得しました")
        
        return df
        
    except requests.RequestException as e:
        print(f"⚠️ CSVの取得に失敗しました: {e}")
        
        # キャッシュファイルがあれば使用
        cache_path = DATA_DIR / "comments.csv"
        if cache_path.exists():
            print(f"  → キャッシュファイルを使用します: {cache_path}")
            return pd.read_csv(cache_path, encoding='utf-8')
        
        # キャッシュもなければ空のDataFrameを返す
        print("  → 空のDataFrameを使用します")
        return pd.DataFrame()


def load_local_csv() -> pd.DataFrame:
    """
    ローカルのキャッシュCSVを読み込みます。
    
    Returns:
        pandas.DataFrame: 読み込んだデータ（ファイルがなければ空のDataFrame）
    """
    cache_path = DATA_DIR / "comments.csv"
    if cache_path.exists():
        return pd.read_csv(cache_path, encoding='utf-8')
    return pd.DataFrame()


def download_image_from_google_drive(url: str, output_path: Path) -> bool:
    """
    Google DriveのURLから画像をダウンロードします。
    
    Args:
        url: Google DriveのURL
        output_path: 保存先のパス
    
    Returns:
        bool: 成功したらTrue
    """
    try:
        # Google DriveのURL形式を変換
        # https://drive.google.com/open?id=FILE_ID
        # または https://drive.google.com/file/d/FILE_ID/view
        # → https://drive.google.com/uc?export=download&id=FILE_ID
        
        file_id = None
        if "id=" in url:
            file_id = url.split("id=")[1].split("&")[0]
        elif "/d/" in url:
            file_id = url.split("/d/")[1].split("/")[0]
        
        if not file_id:
            print(f"  ✗ URLからファイルIDを抽出できませんでした: {url}")
            return False
        
        # ダウンロード用URLを構築
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        # 画像をダウンロード
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()
        
        # ファイルに保存
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return True
        
    except Exception as e:
        print(f"  ✗ ダウンロード失敗: {e}")
        return False


def download_images_from_csv(df: pd.DataFrame) -> int:
    """
    CSVに含まれるGoogle Drive URLから画像をダウンロードします。
    
    Args:
        df: コメントデータのDataFrame
    
    Returns:
        int: ダウンロードした画像の数
    """
    if df.empty:
        return 0
    
    print(f"\n📥 CSV内の画像をダウンロード中...")
    
    RAW_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    downloaded_count = 0
    
    for idx, row in df.iterrows():
        # 5列目（インデックス4）が写真URL
        if len(row) <= 4:
            continue
        
        photo_url = row.iloc[4]
        
        # URLが空でない場合
        if pd.notna(photo_url) and str(photo_url).strip() and str(photo_url) != "nan":
            # ファイル名を生成（タイムスタンプ + 行番号）
            timestamp = row.iloc[0] if len(row) > 0 else ""
            safe_timestamp = str(timestamp).replace("/", "").replace(":", "").replace(" ", "_")
            filename = f"photo_{safe_timestamp}_{idx}.jpg"
            output_path = RAW_IMAGES_DIR / filename
            
            # 既にダウンロード済みならスキップ
            if output_path.exists():
                print(f"  ⊙ スキップ（既存）: {filename}")
                continue
            
            print(f"  ⬇ ダウンロード中: {filename}")
            if download_image_from_google_drive(str(photo_url), output_path):
                print(f"  ✓ 保存完了: {filename}")
                downloaded_count += 1
    
    if downloaded_count > 0:
        print(f"  → {downloaded_count} 件の画像をダウンロードしました")
    else:
        print(f"  → ダウンロードする新しい画像はありませんでした")
    
    return downloaded_count


def process_images() -> list:
    """
    raw_images/ 内の画像をリサイズして static/images/ に出力します。
    
    Returns:
        list: 処理された画像ファイル名のリスト
    """
    print(f"\n🖼️ 画像を処理中...")
    
    # 対応する画像形式
    supported_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
    processed_images = []
    
    if not RAW_IMAGES_DIR.exists():
        print(f"  → raw_images/ ディレクトリが見つかりません")
        return processed_images
    
    # raw_images/ 内のすべての画像を処理
    for image_path in RAW_IMAGES_DIR.iterdir():
        if image_path.suffix.lower() not in supported_extensions:
            continue
        
        try:
            # 画像を開く
            with Image.open(image_path) as img:
                # RGBAの場合はRGBに変換（WebP/JPEG用）
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # アスペクト比を維持してリサイズ
                img.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.Resampling.LANCZOS)
                
                # 出力ファイル名を決定
                output_filename = f"{image_path.stem}.{OUTPUT_FORMAT}"
                output_path = OUTPUT_IMAGES_DIR / output_filename
                
                # 保存
                if OUTPUT_FORMAT == "webp":
                    img.save(output_path, "WEBP", quality=IMAGE_QUALITY)
                else:
                    img.save(output_path, "JPEG", quality=IMAGE_QUALITY)
                
                processed_images.append(output_filename)
                print(f"  ✓ {image_path.name} → {output_filename}")
                
        except Exception as e:
            print(f"  ✗ {image_path.name} の処理に失敗: {e}")
    
    print(f"  → {len(processed_images)} 件の画像を処理しました")
    return sorted(processed_images)


def load_markdown_content(filename: str) -> str:
    """
    Markdownファイルを読み込んでHTMLに変換します。
    
    Args:
        filename: content/ ディレクトリ内のファイル名
    
    Returns:
        str: HTMLに変換された内容
    """
    filepath = CONTENT_DIR / filename
    
    if not filepath.exists():
        print(f"⚠️ {filepath} が見つかりません")
        return ""
    
    with open(filepath, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    # MarkdownをHTMLに変換（拡張機能付き）
    html_content = markdown.markdown(
        md_content,
        extensions=["extra", "nl2br", "sane_lists"]
    )
    
    return html_content


def extract_store_history(about_html: str) -> tuple:
    """
    店舗の変遷情報をHTMLから抽出します。
    
    Args:
        about_html: about.mdから変換されたHTML
    
    Returns:
        tuple: (店舗変遷を除いたHTML, 店舗変遷のリスト)
    """
    import re
    
    # 「店舗の変遷」セクションを抽出
    history_pattern = r'<h2>店舗の変遷</h2>(.*?)<hr\s*/>'
    match = re.search(history_pattern, about_html, re.DOTALL)
    
    if not match:
        return about_html, []
    
    history_section = match.group(1)
    about_without_history = about_html.replace(match.group(0), '<hr />')
    
    # 各店舗の情報を抽出（h3とimgを別々に）
    stores = []
    
    # h3タグを探す
    h3_pattern = r'<h3>(.*?)</h3>'
    img_pattern = r'<img\s+alt="(.*?)"\s+src="(.*?)"\s*/>'
    
    h3_matches = list(re.finditer(h3_pattern, history_section))
    img_matches = list(re.finditer(img_pattern, history_section))
    
    # h3とimgを順番にマッチング
    for idx, (h3_match, img_match) in enumerate(zip(h3_matches, img_matches)):
        title = h3_match.group(1)
        alt_text = img_match.group(1)
        image_url = img_match.group(2)
        
        stores.append({
            'id': f'store{idx}',
            'title': title,
            'alt': alt_text,
            'image': image_url
        })
    
    return about_without_history, stores


def prepare_comments_data(df: pd.DataFrame) -> list:
    """
    DataFrameをテンプレート用の辞書リストに変換します。
    
    Args:
        df: コメントデータのDataFrame
    
    Returns:
        list: コメントの辞書リスト
    """
    comments = []
    
    # データが空の場合は空のリストを返す
    if df.empty:
        return comments
    
    # Googleフォームの列は以下の順序:
    # 0: タイムスタンプ
    # 1: 店主様やラーメンNORIにまつわる思い出を教えて下さい（必須）
    # 2: 公開可能なお名前（ニックネーム、任意）
    # 3: 好きだったメニューを教えて下さい（複数可、任意）
    # 4: 思い出の写真（1枚/1MBまで、任意）
    
    for idx, row in df.iterrows():
        # 列インデックスで直接アクセス
        timestamp = row.iloc[0] if len(row) > 0 else ""
        content = row.iloc[1] if len(row) > 1 else ""
        name = row.iloc[2] if len(row) > 2 else "匿名"
        menu = row.iloc[3] if len(row) > 3 else ""
        photo_url = row.iloc[4] if len(row) > 4 else ""
        
        # 写真のローカルパスを特定（ダウンロード済みの画像）
        photo_filename = None
        if pd.notna(photo_url) and str(photo_url).strip() and str(photo_url) != "nan":
            # タイムスタンプベースのファイル名を生成
            safe_timestamp = str(timestamp).replace("/", "").replace(":", "").replace(" ", "_")
            photo_filename = f"photo_{safe_timestamp}_{idx}.webp"
        
        comment = {
            "timestamp": timestamp,
            "content": str(content),
            "menu": str(menu),
            "photo_url": str(photo_url),
            "photo_filename": photo_filename,  # ローカル画像ファイル名を追加
            "name": str(name)
        }
        
        # 名前が空の場合は「匿名」に
        if pd.isna(comment["name"]) or comment["name"].strip() == "" or comment["name"] == "nan":
            comment["name"] = "匿名"
        
        # メニュー情報をコンテンツに追加
        if comment.get("menu") and not pd.isna(comment["menu"]) and comment["menu"].strip() and comment["menu"] != "nan":
            menu_text = f"\n\n【好きだったメニュー】\n{comment['menu']}"
            comment["content"] = comment["content"] + menu_text
        
        # コメントが空でない場合のみ追加
        if not pd.isna(comment["content"]) and comment["content"].strip() and comment["content"] != "nan":
            comments.append(comment)
    
    # 新しい順にソート（Timestampがある場合）
    if comments and comments[0].get("timestamp"):
        try:
            comments.sort(key=lambda x: x["timestamp"], reverse=True)
        except:
            pass
    
    return comments


def generate_html(comments: list, images: list, about_html: str, config: dict, store_history: list = None):
    """
    Jinja2テンプレートを使用してHTMLを生成します。
    
    Args:
        comments: コメントの辞書リスト
        images: 画像ファイル名のリスト
        about_html: 「店主について」のHTML
        config: 設定情報の辞書
        store_history: 店舗変遷データのリスト
    """
    print(f"\n📝 HTMLを生成中...")
    
    # Jinja2環境を設定
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=True
    )
    
    # テンプレートを読み込み
    template = env.get_template("index.html")
    
    # テンプレートに渡すデータ
    context = {
        "site_title": config.get("site", {}).get("title", "想い出のラーメン - メモリアルサイト"),
        "site_description": config.get("site", {}).get("description", "故人を偲ぶメモリアルサイト"),
        "shop_name": config.get("site", {}).get("shop_name", "想い出のラーメン"),
        "hero": config.get("hero", {}),
        "navigation": config.get("navigation", {}),
        "sections": config.get("sections", {}),
        "footer": config.get("footer", {}),
        "ui": config.get("ui", {}),
        "comments": comments,
        "images": images,
        "about_html": about_html,
        "store_history": store_history or [],
        "generated_at": datetime.now().strftime("%Y年%m月%d日 %H:%M"),
        "comment_count": len(comments),
        "image_count": len(images),
    }
    
    # HTMLを生成
    html_output = template.render(**context)
    
    # index.html を public/ に出力
    output_path = PUBLIC_DIR / "index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_output)
    print(f"✓ HTMLを出力: {output_path}")
    
    # static/ ディレクトリを public/ にコピー
    copy_static_files()


def copy_static_files():
    """
    static/ ディレクトリの内容を public/ にコピーします。
    """
    import shutil
    
    # CSS をコピー
    css_src = STATIC_DIR / "css"
    css_dst = PUBLIC_DIR / "static" / "css"
    if css_src.exists():
        css_dst.mkdir(parents=True, exist_ok=True)
        for css_file in css_src.glob("*.css"):
            shutil.copy2(css_file, css_dst / css_file.name)
            print(f"✓ CSSをコピー: {css_file.name}")
    
    # 画像をコピー
    img_src = OUTPUT_IMAGES_DIR
    img_dst = PUBLIC_DIR / "static" / "images"
    if img_src.exists():
        img_dst.mkdir(parents=True, exist_ok=True)
        for img_file in img_src.iterdir():
            if img_file.is_file():
                shutil.copy2(img_file, img_dst / img_file.name)
        print(f"✓ 画像をコピー: {len(list(img_src.iterdir()))} ファイル")


# =============================================================================
# メイン処理
# =============================================================================

def main():
    """
    メインのビルド処理を実行します。
    """
    parser = argparse.ArgumentParser(
        description="メモリアルサイト静的生成スクリプト"
    )
    parser.add_argument(
        "--csv-url",
        type=str,
        default=DEFAULT_CSV_URL,
        help="Google スプレッドシートのCSV公開URL"
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="CSVの取得をスキップし、ローカルキャッシュを使用"
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="画像のダウンロードをスキップ"
    )
    args = parser.parse_args()
    
    print("=" * 60)
    print("🍜 メモリアルサイト ビルドスクリプト")
    print("=" * 60)
    
    # 1. ディレクトリ構成を確認
    ensure_directories()
    
    # 2. 設定ファイルを読み込み
    config = load_config()
    
    # 3. CSVデータを取得（またはローカルキャッシュを使用）
    if args.skip_fetch:
        df = load_local_csv()
        print(f"\n📂 ローカルキャッシュを使用: {len(df)} 件")
    else:
        # CSV URLが設定されているか確認
        if not args.csv_url:
            print("\n⚠️ エラー: CSV URLが設定されていません")
            print("   以下のいずれかの方法で設定してください:")
            print("   1. 環境変数: export CSV_URL='https://docs.google.com/...'")
            print("   2. コマンドライン: python build.py --csv-url 'https://docs.google.com/...'")
            print("   3. ローカルキャッシュを使用: python build.py --skip-fetch")
            sys.exit(1)
        
        df = fetch_csv_data(args.csv_url)
    
    # 4. CSV内の画像をダウンロード（オプション）
    if not args.skip_download:
        download_images_from_csv(df)
    
    # 5. 画像を処理
    images = process_images()
    
    # 6. Markdownコンテンツを読み込み
    about_html = load_markdown_content("about.md")
    
    # 7. 店舗変遷を抽出
    about_html, store_history = extract_store_history(about_html)
    
    # 8. コメントデータを準備
    comments = prepare_comments_data(df)
    
    # 9. HTMLを生成
    generate_html(comments, images, about_html, config, store_history)
    
    print("\n" + "=" * 60)
    print("✨ ビルド完了!")
    print(f"   コメント: {len(comments)} 件")
    print(f"   画像: {len(images)} 件")
    print(f"   出力先: {PUBLIC_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
