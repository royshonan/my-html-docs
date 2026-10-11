#!/usr/bin/env python3
"""
メニューバー最適化ツール
MacBookのメニューバー常駐アプリを分析し、最適化提案を行う
"""

import csv
import os
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Tuple
import json

class MenuBarOptimizer:
    def __init__(self, csv_file: str = "mac_app_inventory.csv"):
        self.csv_file = csv_file
        self.apps = []
        self.menu_bar_apps = []
        self.load_data()

    def load_data(self):
        """CSVファイルからデータを読み込み"""
        if not os.path.exists(self.csv_file):
            print(f"エラー: {self.csv_file} が見つかりません。")
            print("先に mac_app_inventory.py を実行してください。")
            sys.exit(1)

        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.apps = list(reader)
            
        # メニューバー常駐アプリを抽出
        self.menu_bar_apps = [app for app in self.apps if app['is_menu_bar_app'] == 'True']
        
        print(f"総アプリ数: {len(self.apps)}")
        print(f"メニューバー常駐アプリ数: {len(self.menu_bar_apps)}")

    def analyze_menu_bar_apps(self):
        """メニューバー常駐アプリの詳細分析"""
        print("\n" + "="*60)
        print("メニューバー常駐アプリ詳細分析")
        print("="*60)
        
        # カテゴリ別分析
        category_analysis = {}
        for app in self.menu_bar_apps:
            category = app['category']
            if category not in category_analysis:
                category_analysis[category] = {
                    'count': 0,
                    'total_size': 0,
                    'apps': []
                }
            category_analysis[category]['count'] += 1
            category_analysis[category]['total_size'] += float(app['size_mb'])
            category_analysis[category]['apps'].append(app)
        
        # カテゴリ別表示
        for category, data in sorted(category_analysis.items(), key=lambda x: x[1]['count'], reverse=True):
            print(f"\n【{category}】({data['count']}個, {data['total_size']:.2f} MB)")
            for app in data['apps']:
                print(f"  • {app['app_name']} - {app['size_mb']} MB")
                print(f"    バンドルID: {app['bundle_id']}")
                print(f"    バージョン: {app['version']}")
                print(f"    パス: {app['app_path']}")
                print()

    def check_running_processes(self):
        """現在実行中のプロセスをチェック"""
        print("\n" + "="*60)
        print("現在実行中のメニューバー関連プロセス")
        print("="*60)
        
        try:
            # psコマンドでプロセス一覧を取得
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            processes = result.stdout.split('\n')
            
            running_menu_bar_apps = []
            for app in self.menu_bar_apps:
                app_name = app['app_name']
                bundle_id = app['bundle_id']
                
                for process in processes:
                    if (app_name.lower() in process.lower() or 
                        bundle_id in process or
                        any(keyword in process.lower() for keyword in ['menu', 'bar', 'status', 'tray'])):
                        running_menu_bar_apps.append((app, process))
                        break
            
            if running_menu_bar_apps:
                for app, process in running_menu_bar_apps:
                    print(f"実行中: {app['app_name']}")
                    print(f"  プロセス: {process.strip()}")
                    print()
            else:
                print("メニューバー関連の実行中プロセスは見つかりませんでした。")
                
        except Exception as e:
            print(f"プロセス確認中にエラーが発生しました: {e}")

    def analyze_system_resources(self):
        """システムリソース使用状況を分析"""
        print("\n" + "="*60)
        print("システムリソース分析")
        print("="*60)
        
        try:
            # メモリ使用量
            result = subprocess.run(['vm_stat'], capture_output=True, text=True)
            if result.returncode == 0:
                print("メモリ使用状況:")
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        print(f"  {line.strip()}")
            
            print()
            
            # CPU使用率（簡易版）
            result = subprocess.run(['top', '-l', '1', '-n', '0'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines[:10]:  # 最初の10行のみ表示
                    if line.strip():
                        print(f"  {line}")
                        
        except Exception as e:
            print(f"システムリソース分析中にエラーが発生しました: {e}")

    def generate_optimization_recommendations(self):
        """最適化提案を生成"""
        print("\n" + "="*60)
        print("メニューバー最適化提案")
        print("="*60)
        
        # サイズが大きいメニューバーアプリを特定
        large_apps = [app for app in self.menu_bar_apps if float(app['size_mb']) > 10]
        if large_apps:
            print("【注意】サイズが大きいメニューバーアプリ:")
            for app in sorted(large_apps, key=lambda x: float(x['size_mb']), reverse=True):
                print(f"  • {app['app_name']}: {app['size_mb']} MB")
                print(f"    パス: {app['app_path']}")
                print(f"    推奨: 不要であればアンインストールを検討")
                print()
        
        # Apple純正以外のメニューバーアプリ
        non_apple_apps = [app for app in self.menu_bar_apps if app['category'] != 'Apple']
        if non_apple_apps:
            print("【確認推奨】Apple純正以外のメニューバーアプリ:")
            for app in non_apple_apps:
                print(f"  • {app['app_name']} ({app['category']})")
                print(f"    バンドルID: {app['bundle_id']}")
                print(f"    サイズ: {app['size_mb']} MB")
                print(f"    推奨: 使用頻度を確認し、不要であれば無効化を検討")
                print()
        
        # メニューバーアプリの総数による推奨
        total_menu_bar = len(self.menu_bar_apps)
        if total_menu_bar > 20:
            print(f"【最適化推奨】メニューバーアプリが{total_menu_bar}個と多すぎます。")
            print("推奨アクション:")
            print("  1. 使用頻度の低いアプリを特定")
            print("  2. アプリの設定でメニューバー表示を無効化")
            print("  3. 不要なアプリをアンインストール")
            print("  4. 類似機能のアプリを統合")
        elif total_menu_bar > 10:
            print(f"【注意】メニューバーアプリが{total_menu_bar}個あります。")
            print("推奨アクション:")
            print("  1. 各アプリの使用頻度を確認")
            print("  2. 不要なアプリの設定を調整")
        else:
            print(f"【良好】メニューバーアプリ数({total_menu_bar}個)は適切です。")

    def export_menu_bar_report(self, filename: str = "menu_bar_report.csv"):
        """メニューバーアプリ専用レポートをエクスポート"""
        print(f"\nメニューバー専用レポートをエクスポート中: {filename}")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                "app_name", "bundle_id", "version", "developer", 
                "size_mb", "last_modified", "is_menu_bar_app", "is_mas_app",
                "category", "app_path", "optimization_priority"
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for app in self.menu_bar_apps:
                # 最適化優先度を計算
                priority = "Low"
                size_mb = float(app['size_mb'])
                if size_mb > 50:
                    priority = "High"
                elif size_mb > 10:
                    priority = "Medium"
                elif app['category'] != 'Apple':
                    priority = "Medium"
                
                row = {**app, "optimization_priority": priority}
                writer.writerow(row)

    def run_optimization_analysis(self):
        """最適化分析を実行"""
        print("メニューバー最適化分析を開始します...")
        
        self.analyze_menu_bar_apps()
        self.check_running_processes()
        self.analyze_system_resources()
        self.generate_optimization_recommendations()
        self.export_menu_bar_report()
        
        print(f"\n詳細なメニューバーレポートは 'menu_bar_report.csv' に保存されました。")

if __name__ == "__main__":
    optimizer = MenuBarOptimizer()
    optimizer.run_optimization_analysis()
