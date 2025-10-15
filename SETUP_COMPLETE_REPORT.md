# 豆苗プランター - 環境構築完了レポート

## 📋 構築概要

**構築日時**: 2025年10月15日  
**環境**: macOS (開発環境) + Raspberry Pi (本番環境)  
**プロジェクト**: 豆苗プランター - 豆苗栽培に特化した自動植物育成システム  

## ✅ 完了した作業

### 1. Python仮想環境の構築
- ✅ Python 3.10.4仮想環境作成
- ✅ pipアップグレード完了
- ✅ macOS用依存関係インストール完了
- ✅ Raspberry Pi用requirements.txt準備

### 2. 環境設定ファイル
- ✅ `.env`ファイル作成（開発環境用）
- ✅ `.env.raspberrypi`ファイル作成（本番環境用）
- ✅ 環境変数設定完了

### 3. ディレクトリ構造
- ✅ 必要なディレクトリ作成完了
  - `config/` - 設定ファイル
  - `logs/` - ログファイル
  - `data/` - データファイル
  - `plant_images/` - 撮影画像
  - `src/web/templates/` - Web UIテンプレート
  - `src/web/static/` - 静的ファイル

### 4. API層の実装
- ✅ `src/api/api_blueprint.py` - API統合管理
- ✅ `src/api/ai_api.py` - AI相談API
- ✅ 6つのAI APIエンドポイント実装
  - `/api/ai/consultation` - 一般相談
  - `/api/ai/harvest-judgment` - 収穫判断
  - `/api/ai/disease-check` - 病気診断
  - `/api/ai/cooking-tips` - 調理例
  - `/api/ai/tags` - 相談タグ一覧
  - `/api/ai/history` - 相談履歴

### 5. Web UIテンプレート
- ✅ `dashboard.html` - ダッシュボードページ
- ✅ `ai_consultation.html` - AI相談ページ
- ✅ Bootstrap 5 + Font Awesome使用
- ✅ レスポンシブデザイン対応

### 6. Raspberry Pi環境準備
- ✅ `setup-raspberrypi.sh` - 自動セットアップスクリプト
- ✅ `bean-sprout-planter.service` - systemdサービスファイル
- ✅ GPIO権限設定スクリプト
- ✅ cronジョブ設定

### 7. 動作確認テスト
- ✅ AI相談マネージャー初期化テスト
- ✅ 多層化カメラマネージャー初期化テスト
- ✅ 給水タンクマネージャー初期化テスト
- ✅ Flaskアプリケーション作成テスト
- ✅ APIエンドポイント登録テスト

## 🎯 実装済み機能

### AI機能
- **収穫判断**: 画像とセンサーデータから収穫タイミングを判定
- **病気診断**: 症状と画像から病気を診断
- **調理例提供**: 収穫した豆苗の調理方法を提案
- **一般相談**: 豆苗栽培に関する質問に回答
- **相談履歴**: 過去の相談内容を記録・表示

### 多層化カメラ管理
- **複数カメラ管理**: 階層別カメラ制御
- **スケジュール撮影**: 自動撮影機能
- **エラー処理**: カメラ障害時の自動無効化

### 給水タンク管理
- **残量計算**: 給水後の残量管理
- **使用履歴**: 給水履歴の記録
- **統計情報**: 使用量統計の提供
- **低水位警告**: 自動警告機能

### Web UI
- **ダッシュボード**: システム状態の一覧表示
- **AI相談**: チャット形式の相談機能
- **レスポンシブ**: モバイル対応

## 📊 システム構成

```
main.py (エントリーポイント)
├── src/app/app.py (Flaskアプリケーション)
├── src/api/
│   ├── api_blueprint.py (API統合管理)
│   └── ai_api.py (AI相談API)
├── src/ai/ai_consultation.py (AI判断機能)
├── src/camera/multi_camera_manager.py (多層化カメラ管理)
├── src/watering/water_tank_manager.py (給水タンク管理)
└── src/web/templates/ (Web UIテンプレート)
```

## 🚀 起動方法

### 開発環境 (macOS)
```bash
cd /Users/ootsukayuya/wrok_space/bean-sprout-planter
source venv/bin/activate
python main.py
```

### 本番環境 (Raspberry Pi)
```bash
# 自動セットアップ
sudo ./setup-raspberrypi.sh

# 手動起動
sudo systemctl start bean-sprout-planter

# 状態確認
sudo systemctl status bean-sprout-planter
```

## 🌐 アクセス方法

- **Web UI**: http://localhost:8080
- **ダッシュボード**: http://localhost:8080/dashboard
- **AI相談**: http://localhost:8080/ai-consultation
- **API ヘルスチェック**: http://localhost:8080/api/health
- **システム状態**: http://localhost:8080/api/status

## 📝 次のステップ

### 1. 未実装機能の追加
- [ ] センサー制御モジュール (`src/sensors/`)
- [ ] 通知機能 (`src/notifications/`)
- [ ] カメラAPI (`src/api/camera_api.py`)
- [ ] 給水API (`src/api/watering_api.py`)
- [ ] 設定API (`src/api/settings_api.py`)

### 2. ハードウェア接続
- [ ] AHT25温湿度センサー接続
- [ ] SEN0193土壌水分センサー接続
- [ ] フロートスイッチ接続
- [ ] USBカメラ接続
- [ ] リレーモジュール接続
- [ ] 水中ポンプ接続

### 3. 設定調整
- [ ] APIキーの設定 (OpenAI, Anthropic, Google AI)
- [ ] LINE Notifyトークン設定
- [ ] 豆苗栽培パラメータ調整
- [ ] 撮影スケジュール設定

### 4. テスト・運用
- [ ] 統合テスト実行
- [ ] 実際の豆苗栽培での運用テスト
- [ ] パフォーマンス最適化
- [ ] ログ監視設定

## 🔧 トラブルシューティング

### よくある問題
1. **APIキー未設定**: `.env`ファイルでAPIキーを設定
2. **ポート競合**: 8080番ポートが使用中の場合は変更
3. **権限エラー**: Raspberry PiでGPIO権限を確認
4. **カメラ認識**: USBカメラの接続を確認

### ログ確認
```bash
# システムログ
sudo journalctl -u bean-sprout-planter -f

# アプリケーションログ
tail -f logs/app.log
```

## 📞 サポート

- **ドキュメント**: README.md, ARCHITECTURE.md, FUNCTION_REFERENCE.md
- **設定ガイド**: SETUP_GUIDE.md
- **問題報告**: GitHub Issues

---

**構築完了**: 2025年10月15日  
**バージョン**: 1.0  
**チーム**: KEBABS
