# MacBook アプリケーション完全棚卸しツール

MacBookにインストールされている全アプリケーションの詳細な棚卸しを行い、メニューバー最適化のための分析ツールです。

## 機能

### 1. アプリケーション棚卸し (`mac_app_inventory.py`)
- **スキャン対象ディレクトリ**:
  - `/Applications`
  - `~/Applications`
  - `/System/Applications`
  - `/System/Library/CoreServices`

- **収集情報**:
  - アプリ名、バンドルID、バージョン、開発者
  - ファイルサイズ（MB）、最終更新日
  - メニューバー常駐アプリかどうか（LSUIElement、LaunchAgentsをチェック）
  - Mac App Storeアプリかどうか（_MASReceiptで判定）
  - カテゴリ分類（Apple、Development、Design、Productivity等）

- **出力**:
  - CSV形式で詳細レポート出力
  - メニューバー常駐アプリを最優先でソート
  - 統計サマリー表示

### 2. メニューバー最適化分析 (`menu_bar_optimizer.py`)
- **詳細分析**:
  - メニューバー常駐アプリのカテゴリ別分析
  - 現在実行中のプロセス確認
  - システムリソース使用状況分析

- **最適化提案**:
  - サイズが大きいアプリの特定
  - Apple純正以外のアプリの確認推奨
  - メニューバーアプリ数の最適化推奨
  - 最適化優先度の自動計算

## 使用方法

### 1. アプリケーション棚卸しの実行
```bash
python3 mac_app_inventory.py
```

### 2. メニューバー最適化分析の実行
```bash
python3 menu_bar_optimizer.py
```

## 出力ファイル

- `mac_app_inventory.csv`: 全アプリケーションの詳細情報
- `menu_bar_report.csv`: メニューバー常駐アプリ専用レポート（最適化優先度付き）

## 分析結果の例

### 発見されたアプリケーション
- **総アプリケーション数**: 180個
- **メニューバー常駐アプリ**: 85個
- **Mac App Storeアプリ**: 8個
- **総サイズ**: 22,478.94 MB

### カテゴリ別統計
- **Apple**: 158個 (10,257.80 MB)
- **Browser**: 1個 (1,160.29 MB)
- **Communication**: 1個 (748.94 MB)
- **Other**: 16個 (5,508.58 MB)
- **Productivity**: 4個 (4,803.33 MB)

### メニューバー最適化のポイント
1. **サイズが大きいアプリ**:
   - Raycast: 127.92 MB
   - MTLReplayer: 43.28 MB
   - Alfred: 27.53 MB

2. **Apple純正以外のメニューバーアプリ**:
   - Alfred (Other)
   - Karabiner-VirtualHIDDevice-Manager (Other)
   - Raycast (Other)

3. **最適化推奨**:
   - メニューバーアプリが85個と多すぎる
   - 使用頻度の低いアプリの特定と無効化を推奨

## 要件

- Python 3.6以上
- macOS（plistlib、subprocess使用）

## 注意事項

- システムアプリケーションの一部は削除できないため、最適化提案は参考程度に留めてください
- アプリの削除や無効化を行う前に、必ずバックアップを取ってください
- 一部のプロセス検出は近似値のため、実際の使用状況と異なる場合があります