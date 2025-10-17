# 豆苗プランター - システムアーキテクチャ説明書

## 📋 概要
このドキュメントでは、豆苗栽培に特化した自動植物育成システムの各ファイルの役割、連携方法、主要な関数について説明します。

---

## 🏗️ 全体アーキテクチャ

```
┌─────────────────────────────────────────────────┐
│  ユーザー（ブラウザ）                            │
└─────────────────────────────────────────────────┘
                    ↓ HTTP
┌─────────────────────────────────────────────────┐
│  main.py                                        │
│  - アプリケーションのエントリーポイント          │
│  - サーバー起動                                 │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  src/app/app.py                                 │
│  - Flaskアプリ作成                              │
│  - 画面表示ルート定義（HTML返す）               │
└─────────────────────────────────────────────────┘
                    ↓
        ┌──────────┴──────────┐
        ↓                     ↓
┌──────────────┐      ┌──────────────────┐
│ 画面表示     │      │ API (JSON返す)    │
│ templates/   │      │ src/api/         │
└──────────────┘      └──────────────────┘
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ センサー     │      │ カメラ       │      │ 給水制御     │
│ src/sensors/ │      │ src/camera/  │      │ src/watering/│
└──────────────┘      └──────────────┘      └──────────────┘
                              ↓
                    ┌──────────────────┐
                    │ AI判断機能       │
                    │ src/ai/         │
                    └──────────────────┘
```

---

## 📁 ファイル別の役割と連携

### 🔹 **1. main.py**（エントリーポイント）

**役割:**
- アプリケーションの起動
- ログシステムの初期化
- Flaskアプリの作成と実行

**主要な関数:**
```python
def main():
    """メイン実行関数"""
    # 1. ログ設定
    setup_logging()  # src/utils/logger.py から
    
    # 2. Flaskアプリ作成
    app = create_app()  # src/app/app.py から
    
    # 3. APIブループリント登録
    register_api_blueprints(app)  # src/api/api_blueprint.py から
    
    # 4. サーバー起動
    app.run(host='0.0.0.0', port=8080)
```

**連携先:**
- `src/app/app.py` - Flaskアプリ作成
- `src/api/api_blueprint.py` - API登録
- `src/utils/logger.py` - ログ設定

---

### 🔹 **2. src/app/app.py**（Flaskアプリケーション）

**役割:**
- Flaskアプリのインスタンス作成
- 画面表示ルートの定義のみ（シンプル）
- エラーハンドリング

**主要な関数:**
```python
def create_app():
    """Flaskアプリケーションを作成"""
    app = Flask(__name__)
    
    # ルート定義（画面表示のみ）
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/settings')
    def settings():
        return render_template('settings.html')
    
    @app.route('/ai-consultation')
    def ai_consultation():
        return render_template('ai_consultation.html')
    
    return app
```

**連携先:**
- `src/web/templates/` - HTMLテンプレート
- `src/web/static/` - CSS/JavaScript

**重要:** APIエンドポイントは定義しない（src/api/に分離）

---

### 🔹 **3. src/api/api_blueprint.py**（API統合管理）

**役割:**
- 全てのAPIブループリントを統合
- Flaskアプリに一括登録

**主要な関数:**
```python
def register_api_blueprints(app: Flask):
    """APIブループリントをFlaskアプリに登録"""
    
    # 各APIを登録
    app.register_blueprint(sensors_bp)      # センサーAPI
    app.register_blueprint(watering_bp)     # 給水API
    app.register_blueprint(camera_bp)       # カメラAPI
    app.register_blueprint(notifications_bp) # 通知API
    app.register_blueprint(settings_bp)     # 設定API
    app.register_blueprint(ai_bp)           # AI相談API（新規）
```

**連携先:**
- `src/api/sensors_api.py`
- `src/api/watering_api.py`
- `src/api/camera_api.py`
- `src/api/notifications_api.py`
- `src/api/settings_api.py`
- `src/api/ai_api.py`（新規）

---

### 🔹 **4. src/ai/ai_consultation.py**（AI判断機能）

**役割:**
- マルチモーダルAI（Visionモデル）APIとの連携
- 画像とセンサーデータを組み合わせた高度な状況判断
- 収穫判断、病気診断、調理例などを構造化データ（JSON）で提供

**主要なクラス:**
```python
class AIConsultationManager:
    def __init__(self):
        """AI相談マネージャーの初期化"""
        # APIクライアントを初期化 (OpenAI, Anthropic, Google AI)
        self._initialize_clients()

    def get_harvest_judgment(self, image_path: str, sensor_data: dict):
        """収穫判断を実行"""
        # 1. 画像をエンコード
        # 2. Visionモデルに画像とセンサーデータを送信
        # 3. AIからのJSON応答をパースして返す
        
        return {
            'harvest_ready': True,
            'confidence': 0.95,
            'recommendation': '葉の色も濃く、収穫に最適な状態です。',
            'days_remaining': 0
        }
    
    def diagnose_disease(self, image_path: str, symptoms: list):
        """病気診断を実行"""
        # 1. 画像をエンコード
        # 2. Visionモデルに画像と症状を送信
        # 3. AIからのJSON応答をパースして返す
        
        return {
            'disease_detected': '健康',
            'confidence': 0.98,
            'treatment': '現在のところ対処の必要はありません。',
            'prevention': '引き続き通気性を確保してください。'
        }
    
    def get_cooking_suggestions(self, harvest_data: dict):
        """調理例を提供"""
        # 1. LLMに収穫データを送信
        # 2. AIからのJSON応答をパースして返す
        
        return {
            'recommended_dishes': ['豆苗と豚肉の炒め物', '豆苗のナムル'],
            'cooking_tips': 'シャキシャキ感を残すため、加熱は短時間で。',
            'nutrition_info': 'ビタミンK、ビタミンA、葉酸が豊富です。'
        }
```

**連携先:**
- `src/api/ai_api.py` - AI相談API

---

### 🔹 **5. src/api/ai_api.py**（AI相談API）

**役割:**
- AI相談機能のRESTful API提供
- カメラ、センサーモジュールと連携し、リアルタイムデータでAIを呼び出し

**APIエンドポイント:**
```
POST /api/ai/consultation       - 一般相談（画像付き対応）
POST /api/ai/harvest-judgment   - 収穫判断（画像・センサーデータ連携）
POST /api/ai/disease-check      - 病気診断
POST /api/ai/cooking-tips       - 調理例提案
GET  /api/ai/tags              - 相談タグ一覧取得
GET  /api/ai/history           - 相談履歴取得
```

**主要なクラス:**
```python
class AIConsultationResource(Resource):
    def post(self):
        """AI相談を実行"""
        data = request.get_json()
        question = data.get('question')
        tag = data.get('tag', 'general')
        
        # AI相談マネージャーに問い合わせ
        result = ai_manager.consult(question, tag)
        
        return {
            'status': 'success',
            'answer': result['answer'],
            'confidence': result['confidence'],
            'tag': tag
        }

class HarvestJudgmentResource(Resource):
    def post(self):
        """収穫判断を実行"""
        # 最新の画像とセンサーデータを取得
        image_path = camera_manager.get_latest_image()
        sensor_data = sensor_manager.get_latest_data()
        
        # AI判断を実行
        judgment = ai_manager.get_harvest_judgment(image_path, sensor_data)
        
        return {
            'status': 'success',
            'harvest_ready': judgment['harvest_ready'],
            'confidence': judgment['confidence'],
            'recommendation': judgment['recommendation']
        }
```

**連携先:**
- `src/ai/ai_consultation.py` - AI判断ロジック

---

### 🔹 **6. src/camera/multi_camera_manager.py**（多層化カメラ管理）

**役割:**
- 複数カメラの管理
- 階層別撮影制御

**主要なクラス:**
```python
class MultiCameraManager:
    def __init__(self):
        """多層化カメラマネージャーの初期化"""
        self.cameras = {}
        self.camera_configs = self._load_camera_configs()
    
    def add_camera(self, camera_id: str, camera_index: int, layer: int):
        """カメラを追加"""
        self.cameras[camera_id] = {
            'index': camera_index,
            'layer': layer,
            'enabled': True,
            'last_capture': None
        }
    
    def capture_layer(self, layer: int):
        """指定階層の撮影を実行"""
        layer_cameras = [cam for cam in self.cameras.values() if cam['layer'] == layer]
        
        results = []
        for camera_id, config in layer_cameras.items():
            if config['enabled']:
                result = self._capture_single_camera(camera_id, config)
                results.append(result)
        
        return results
    
    def schedule_capture(self, schedule_config: dict):
        """撮影スケジュールを設定"""
        # 各階層の撮影時刻を設定
        # cronジョブとして登録
        
        return {
            'status': 'success',
            'schedule_id': 'schedule_001',
            'layers': schedule_config['layers']
        }
```

**連携先:**
- `src/api/camera_api.py` - カメラAPI
- `src/settings/settings_manager.py` - 設定管理

---

### 🔹 **7. src/watering/water_tank_manager.py**（給水タンク管理）

**役割:**
- 給水タンク残量の計算と管理
- ユーザー入力による初期設定

**主要なクラス:**
```python
class WaterTankManager:
    def __init__(self):
        """給水タンクマネージャーの初期化"""
        self.tank_capacity = 2000  # ml
        self.current_volume = 2000  # ml
        self.water_usage_history = []
    
    def set_initial_volume(self, volume: int):
        """初期水量を設定"""
        self.current_volume = min(volume, self.tank_capacity)
        self._save_tank_status()
    
    def calculate_remaining_volume(self, watering_amount: int):
        """給水後の残量を計算"""
        self.current_volume -= watering_amount
        self.current_volume = max(0, self.current_volume)
        
        # 使用履歴を記録
        self.water_usage_history.append({
            'timestamp': datetime.now(),
            'amount': watering_amount,
            'remaining': self.current_volume
        })
        
        self._save_tank_status()
        return self.current_volume
    
    def get_tank_status(self):
        """タンク状態を取得"""
        percentage = (self.current_volume / self.tank_capacity) * 100
        
        return {
            'current_volume': self.current_volume,
            'capacity': self.tank_capacity,
            'percentage': percentage,
            'status': 'low' if percentage < 20 else 'normal',
            'last_refill': self._get_last_refill_date()
        }
    
    def refill_tank(self, amount: int):
        """タンクに水を補充"""
        self.current_volume += amount
        self.current_volume = min(self.current_volume, self.tank_capacity)
        self._save_tank_status()
```

**連携先:**
- `src/api/watering_api.py` - 給水API
- `src/sensors/float_switch.py` - フロートスイッチ

---

## 🔄 **データフロー例**

### **例1: AI収穫判断**

```
1. ブラウザ（dashboard.html）
   ↓ 収穫判断ボタンクリック
   
2. main.js
   └── checkHarvestReadiness()
   ↓ POST /api/ai/harvest-judgment

3. src/api/ai_api.py
   ├── HarvestJudgmentResource.post()
   │   ├── camera_manager.get_latest_image_path()  <- 最新画像取得
   │   └── sensor_manager.get_all_sensors_data() <- 最新センサーデータ取得
   └── ai_manager.get_harvest_judgment()
   ↓

4. src/ai/ai_consultation.py
   ├── VisionモデルAPI呼び出し（画像＋センサーデータ）
   └── JSON応答をパース
   ↓

5. ブラウザに結果表示
   └── 収穫推奨度、信頼度、推奨事項
```

### **例2: 多層化撮影**

```
1. ブラウザ（settings.html）
   ↓ 撮影スケジュール設定
   
2. settings.js
   └── saveCaptureSchedule()
   ↓ POST /api/camera/schedule

3. src/api/camera_api.py
   ├── CameraScheduleResource.post()
   └── multi_camera_manager.schedule_capture()
   ↓

4. src/camera/multi_camera_manager.py
   ├── 各階層の撮影時刻設定
   ├── cronジョブ登録
   └── スケジュール保存
   ↓

5. 指定時刻に自動撮影実行
   └── 各階層のカメラで順次撮影
```

---

## 📊 **モジュール間の依存関係**

```
main.py
  ├─ depends on: src/app/app.py
  ├─ depends on: src/api/api_blueprint.py
  └─ depends on: src/utils/logger.py

src/api/api_blueprint.py
  ├─ depends on: src/api/sensors_api.py
  ├─ depends on: src/api/watering_api.py
  ├─ depends on: src/api/camera_api.py
  ├─ depends on: src/api/notifications_api.py
  ├─ depends on: src/api/settings_api.py
  └─ depends on: src/api/ai_api.py

src/api/ai_api.py
  ├─ depends on: src/ai/ai_consultation.py
  ├─ depends on: src/camera/multi_camera_manager.py
  └─ depends on: src/sensors/sensor_manager.py

src/ai/ai_consultation.py
  └─ depends on: Vision Model APIs (External)

src/camera/multi_camera_manager.py
  └─ depends on: src/settings/settings_manager.py

src/watering/water_tank_manager.py
  └─ depends on: src/sensors/float_switch.py
```

---

## 🎯 **重要なポイント**

### **1. レイヤー分離:**
- **プレゼンテーション層:** app.py（画面）
- **API層:** src/api/（JSONレスポンス）
- **ビジネスロジック層:** src/sensors/, src/camera/, src/ai/など
- **データ層:** config/settings.json, CSVファイル

### **2. AI機能統合:**
- LLM API連携による豆苗栽培支援
- 画像解析とセンサーデータの組み合わせ
- タグ別相談機能（収穫判断、病気、調理例）

### **3. 多層化対応:**
- 複数カメラの管理システム
- 階層別撮影制御
- スケジュール管理

### **4. 拡張性:**
- 新しいセンサー追加: BaseSensorを継承
- 新しいAPI追加: Blueprintで登録
- 新しい画面追加: app.pyにルート追加
- AI機能拡張: 新しいタグとロジック追加

---

**作成日**: 2025年10月15日  
**バージョン**: 1.0  
**ブランチ**: bean-sprout-planter



