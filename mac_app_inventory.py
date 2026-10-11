#!/usr/bin/env python3
"""
MacBook アプリケーション完全棚卸しスクリプト
メニューバー最適化のための詳細なアプリ情報収集
"""

import os
import csv
import plistlib
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

class MacAppInventory:
    def __init__(self):
        self.apps = []
        self.scan_directories = [
            "/Applications",
            os.path.expanduser("~/Applications"),
            "/System/Applications",
            "/System/Library/CoreServices"
        ]
        
        # カテゴリ分類のキーワード
        self.category_keywords = {
            "Apple": ["Apple Inc.", "com.apple"],
            "Development": ["Xcode", "Developer", "IDE", "Code", "Git", "Terminal", "Docker", "Node", "Python", "Java"],
            "Design": ["Adobe", "Sketch", "Figma", "Photoshop", "Illustrator", "Design", "UI", "UX"],
            "Productivity": ["Office", "Microsoft", "Google", "Notion", "Evernote", "Todo", "Calendar", "Mail"],
            "Communication": ["Slack", "Discord", "Zoom", "Teams", "WhatsApp", "Telegram", "Message"],
            "Media": ["VLC", "QuickTime", "iTunes", "Spotify", "Music", "Video", "Photo", "Image"],
            "System": ["System", "Utilities", "Console", "Activity Monitor", "Disk Utility"],
            "Security": ["Security", "Antivirus", "VPN", "Firewall", "Keychain"],
            "Browser": ["Safari", "Chrome", "Firefox", "Edge", "Opera", "Browser"]
        }

    def get_app_info(self, app_path: str) -> Optional[Dict]:
        """アプリケーションの詳細情報を取得"""
        try:
            info_plist_path = os.path.join(app_path, "Contents", "Info.plist")
            
            if not os.path.exists(info_plist_path):
                return None
                
            with open(info_plist_path, 'rb') as f:
                plist = plistlib.load(f)
            
            # 基本情報
            app_name = plist.get("CFBundleName", os.path.basename(app_path).replace(".app", ""))
            bundle_id = plist.get("CFBundleIdentifier", "Unknown")
            version = plist.get("CFBundleShortVersionString", plist.get("CFBundleVersion", "Unknown"))
            developer = plist.get("CFBundleSignature", "Unknown")
            
            # 開発者情報をより詳細に取得
            if "CFBundleSignature" in plist:
                developer = plist["CFBundleSignature"]
            elif "CFBundleDisplayName" in plist:
                developer = plist["CFBundleDisplayName"]
            
            # ファイルサイズ
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(app_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        pass
            
            size_mb = round(total_size / (1024 * 1024), 2)
            
            # 最終更新日
            mod_time = os.path.getmtime(app_path)
            last_modified = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
            
            # メニューバー常駐アプリかどうか
            is_menu_bar_app = self.check_menu_bar_app(plist, app_path)
            
            # Mac App Storeアプリかどうか
            is_mas_app = self.check_mas_app(app_path)
            
            # カテゴリ分類
            category = self.categorize_app(app_name, bundle_id, developer)
            
            return {
                "app_name": app_name,
                "bundle_id": bundle_id,
                "version": version,
                "developer": developer,
                "size_mb": size_mb,
                "last_modified": last_modified,
                "is_menu_bar_app": is_menu_bar_app,
                "is_mas_app": is_mas_app,
                "category": category,
                "app_path": app_path
            }
            
        except Exception as e:
            print(f"Error processing {app_path}: {e}")
            return None

    def check_menu_bar_app(self, plist: Dict, app_path: str) -> bool:
        """メニューバー常駐アプリかどうかを判定"""
        # LSUIElement をチェック
        if plist.get("LSUIElement", False):
            return True
            
        # LaunchAgents をチェック
        launch_agents_path = os.path.expanduser("~/Library/LaunchAgents")
        if os.path.exists(launch_agents_path):
            for plist_file in os.listdir(launch_agents_path):
                if plist_file.endswith(".plist"):
                    try:
                        with open(os.path.join(launch_agents_path, plist_file), 'rb') as f:
                            agent_plist = plistlib.load(f)
                            if agent_plist.get("ProgramArguments", [""])[0] == app_path:
                                return True
                    except:
                        pass
        
        # アプリ名からメニューバーアプリを推測
        menu_bar_keywords = ["Menu", "Bar", "Status", "Tray", "Dock", "Helper", "Agent"]
        app_name = plist.get("CFBundleName", "").lower()
        for keyword in menu_bar_keywords:
            if keyword.lower() in app_name:
                return True
                
        return False

    def check_mas_app(self, app_path: str) -> bool:
        """Mac App Storeアプリかどうかを判定"""
        # _MASReceipt の存在をチェック
        mas_receipt_path = os.path.join(app_path, "Contents", "_MASReceipt")
        if os.path.exists(mas_receipt_path):
            return True
            
        # バンドルIDから判定
        info_plist_path = os.path.join(app_path, "Contents", "Info.plist")
        try:
            with open(info_plist_path, 'rb') as f:
                plist = plistlib.load(f)
            bundle_id = plist.get("CFBundleIdentifier", "")
            if bundle_id.startswith("com.apple.") and "store" in bundle_id.lower():
                return True
        except:
            pass
            
        return False

    def categorize_app(self, app_name: str, bundle_id: str, developer: str) -> str:
        """アプリをカテゴリに分類"""
        search_text = f"{app_name} {bundle_id} {developer}".lower()
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in search_text:
                    return category
                    
        return "Other"

    def scan_applications(self):
        """指定されたディレクトリからアプリケーションをスキャン"""
        print("アプリケーションをスキャン中...")
        
        for directory in self.scan_directories:
            if not os.path.exists(directory):
                print(f"ディレクトリが存在しません: {directory}")
                continue
                
            print(f"スキャン中: {directory}")
            
            for item in os.listdir(directory):
                if item.endswith(".app"):
                    app_path = os.path.join(directory, item)
                    app_info = self.get_app_info(app_path)
                    if app_info:
                        self.apps.append(app_info)

    def sort_apps(self):
        """アプリをソート（メニューバー常駐アプリを最優先）"""
        self.apps.sort(key=lambda x: (
            not x["is_menu_bar_app"],  # メニューバーアプリを最優先
            x["category"],             # カテゴリでグループ化
            x["app_name"]              # アプリ名でソート
        ))

    def export_to_csv(self, filename: str = "mac_app_inventory.csv"):
        """CSVファイルにエクスポート"""
        print(f"CSVファイルにエクスポート中: {filename}")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                "app_name", "bundle_id", "version", "developer", 
                "size_mb", "last_modified", "is_menu_bar_app", 
                "is_mas_app", "category", "app_path"
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for app in self.apps:
                writer.writerow(app)

    def print_summary(self):
        """統計サマリーを表示"""
        print("\n" + "="*60)
        print("アプリケーション棚卸しサマリー")
        print("="*60)
        
        total_apps = len(self.apps)
        menu_bar_apps = sum(1 for app in self.apps if app["is_menu_bar_app"])
        mas_apps = sum(1 for app in self.apps if app["is_mas_app"])
        total_size = sum(app["size_mb"] for app in self.apps)
        
        print(f"総アプリケーション数: {total_apps}")
        print(f"メニューバー常駐アプリ: {menu_bar_apps}")
        print(f"Mac App Storeアプリ: {mas_apps}")
        print(f"総サイズ: {total_size:.2f} MB")
        
        print("\nカテゴリ別統計:")
        category_stats = {}
        for app in self.apps:
            category = app["category"]
            if category not in category_stats:
                category_stats[category] = {"count": 0, "size": 0}
            category_stats[category]["count"] += 1
            category_stats[category]["size"] += app["size_mb"]
        
        for category, stats in sorted(category_stats.items()):
            print(f"  {category}: {stats['count']}個 ({stats['size']:.2f} MB)")
        
        print("\nメニューバー常駐アプリ一覧:")
        menu_bar_apps_list = [app for app in self.apps if app["is_menu_bar_app"]]
        for app in menu_bar_apps_list:
            print(f"  • {app['app_name']} ({app['category']}) - {app['size_mb']} MB")
        
        if not menu_bar_apps_list:
            print("  メニューバー常駐アプリは見つかりませんでした")

    def run(self):
        """メイン実行関数"""
        print("MacBook アプリケーション完全棚卸しを開始します...")
        print(f"スキャン対象ディレクトリ: {', '.join(self.scan_directories)}")
        
        self.scan_applications()
        self.sort_apps()
        self.export_to_csv()
        self.print_summary()
        
        print(f"\n詳細な結果は 'mac_app_inventory.csv' に保存されました。")

if __name__ == "__main__":
    inventory = MacAppInventory()
    inventory.run()

