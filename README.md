# 豆苗プランター - Bean Sprout Planter

## 🌱 プロジェクト概要
豆苗栽培に特化した自動植物育成システム

## 🎯 主な機能
- 豆苗専用の給水循環システム
- 多層化対応カメラ撮影
- AI判断による収穫タイミング判定
- 豆苗栽培に最適化されたセンサー監視
- LINE通知による栽培状況報告
- Web UI による遠隔操作とAI相談

## 🛠️ 技術スタック
- **ハードウェア**: Raspberry Pi 5
- **センサー**: AHT25 (温湿度), SEN0193 (土壌水分), フロートスイッチ
- **バックエンド**: Python 3.11, Flask 2.3.3
- **フロントエンド**: HTML5, CSS3, JavaScript
- **AI**: OpenAI GPT-4 / Claude / Gemini
- **通知**: LINE Notify API

## 📁 プロジェクト構成
```
bean-sprout-planter/
├── src/                    # ソースコード
│   ├── app/               # Flaskアプリケーション
│   ├── sensors/           # センサー制御
│   ├── watering/          # 給水制御
│   ├── camera/            # カメラ制御（多層化対応）
│   ├── notifications/     # 通知機能
│   ├── data/              # データ管理
│   ├── api/               # REST API
│   ├── utils/             # ユーティリティ
│   ├── web/               # Webフロントエンド
│   └── ai/                # AI判断機能
├── tests/                 # テストコード
├── docs/                  # ドキュメント
├── scripts/               # スクリプト
├── logs/                  # ログファイル
├── data/                  # データファイル
├── config/                # 設定ファイル
└── plant_images/          # 撮影画像
```

## 🚀 クイックスタート

### 1. 環境構築
```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt
```

### 2. 設定
```bash
# 環境変数設定
cp .env.example .env
# .envファイルを編集してLINE NotifyトークンとAI APIキーを設定
```

### 3. 実行
```bash
# アプリケーション起動
python main.py
```

### 4. アクセス
- Web UI: http://localhost:8080
- ダッシュボード: http://localhost:8080/dashboard
- 設定画面: http://localhost:8080/settings
- AI相談: http://localhost:8080/ai-consultation

## 🌐 API エンドポイント

### センサーAPI
- `GET /api/sensors/` - 全センサーデータ取得
- `GET /api/sensors/history` - センサー履歴取得
- `GET /api/sensors/water-level` - 水位データ取得

### 給水API
- `POST /api/watering/` - 手動給水実行
- `GET /api/watering/history` - 給水履歴取得
- `POST /api/watering/stop` - 緊急停止

### カメラAPI（多層化対応）
- `POST /api/camera/capture` - 写真撮影
- `GET /api/camera/images` - 画像リスト取得
- `POST /api/camera/schedule` - 撮影スケジュール設定

### AI相談API
- `POST /api/ai/consultation` - AI相談
- `GET /api/ai/tags` - 相談タグ一覧取得
- `POST /api/ai/harvest-judgment` - 収穫判断

### 設定API
- `GET/POST /api/settings/` - 設定取得・保存
- `POST /api/settings/reset` - 設定リセット

### 通知API
- `POST /api/notifications/test` - テスト通知送信
- `POST /api/notifications/alert` - アラート送信
- `GET /api/notifications/history` - 通知履歴取得

## 📚 ドキュメント

### 📖 システム設計書
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - システム全体のアーキテクチャと連携図
- **[FUNCTION_REFERENCE.md](FUNCTION_REFERENCE.md)** - 全関数・メソッドの詳細リファレンス
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - 環境構築手順
- **[INTEGRATION_TEST.md](INTEGRATION_TEST.md)** - 統合テスト手順

### 📂 モジュール別ガイド
- [センサーモジュール](src/sensors/INTEGRATED_GUIDE.md)
- [給水制御モジュール](src/watering/INTEGRATED_GUIDE.md)
- [カメラモジュール](docs/CAMERA_GUIDE.md)
- [AI判断モジュール](src/ai/INTEGRATED_GUIDE.md)
- [データ管理](src/data/INTEGRATED_GUIDE.md)
- [LINE通知](src/notifications/INTEGRATED_GUIDE.md)
- [Web UI](docs/WEB_GUIDE.md)
- [API](src/api/INTEGRATED_GUIDE.md)

## 🧪 テスト
```bash
# 全テスト実行
python -m pytest tests/

# 個別テスト実行
python tests/test_sensors.py
python tests/test_watering.py
python tests/test_ai.py
python tests/test_integration.py
```

## 🔧 開発

### コード品質
- PEP 8 に準拠
- 型ヒントを使用
- ドキュメント文字列を記述

### コミット規約
- feat: 新機能
- fix: バグ修正
- docs: ドキュメント更新
- test: テスト追加・修正
- refactor: リファクタリング

## 📞 サポート
- 問題報告: GitHub Issues
- 質問: チーム内Slack

## 📄 ライセンス
MIT License

## 👥 チーム
- **リーダー**: 野下
- **サブリーダー**: 大塚
- **メンバー**: 網中、川渕、檜室

## 🔀 ブランチ戦略

### メインブランチ
- `main` - 本番用（安定版）
- `integration/test-all-features` - 統合テスト用（最新機能）

### 機能ブランチ
- `feature-front` - フロントエンド開発
- `feature-backend` - バックエンド開発
- `feature/ai-integration` - AI機能統合
- `feature/multi-layer` - 多層化対応

### 開発の流れ
```bash
# 統合ブランチを取得
git checkout integration/test-all-features
git pull origin integration/test-all-features

# 機能開発
git checkout -b feature/your-feature
# ... 開発 ...
git commit -m "feat: ..."

# 統合ブランチにマージ
git checkout integration/test-all-features
git merge feature/your-feature

# テスト後、mainにマージ
git checkout main
git merge integration/test-all-features
```

## 📊 実装状況

### ✅ 完成済み
- [x] APIレイヤー（6ファイル、18エンドポイント）
- [x] センサーシステム（5ファイル、3種類のセンサー）
- [x] カメラ撮影機能（多層化対応）
- [x] Web UI（ダッシュボード・設定画面・AI相談）
- [x] 設定の永続化
- [x] 統合テストフレームワーク

### ⏳ 開発中
- [ ] AI判断機能（収穫判断、病気診断、調理例）
- [ ] 給水タンク残量計算機能
- [ ] 撮影スケジュール機能
- [ ] 多層化カメラ管理
- [ ] 外部アクセス機能

---

**作成日**: 2025年1月  
**最終更新**: 2025年10月15日  
**バージョン**: 1.0 (bean-sprout-planter)  
**チーム**: KEBABS



