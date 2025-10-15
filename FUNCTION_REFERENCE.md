# 豆苗プランター - 関数リファレンス

## 📋 主要な関数・メソッド一覧

このドキュメントでは、豆苗栽培に特化した各モジュールの主要な関数について詳しく説明します。

---

## 🔹 **main.py**

### `main()`
**説明:** アプリケーションのメインエントリーポイント  
**引数:** なし  
**戻り値:** なし  
**処理フロー:**
```python
1. setup_logging()でログシステム初期化
2. create_app()でFlaskアプリ作成
3. register_api_blueprints(app)でAPI登録
4. app.run()でサーバー起動
```

---

## 🔹 **src/app/app.py**

### `create_app()`
**説明:** Flaskアプリケーションを作成して返す  
**引数:** なし  
**戻り値:** `Flask` - Flaskアプリインスタンス  
**処理:**
```python
- テンプレートとスタティックディレクトリを指定
- SECRET_KEYを環境変数から取得
- ルート定義（/, /dashboard, /settings, /ai-consultation, /logs）
- エラーハンドラー定義（404, 500）
```

---

## 🔹 **src/api/api_blueprint.py**

### `register_api_blueprints(app: Flask)`
**説明:** 全てのAPIブループリントをFlaskアプリに登録  
**引数:**
- `app` (Flask): Flaskアプリインスタンス
**戻り値:** なし  
**登録するAPI:**
```python
- sensors_bp      → /api/sensors/*
- watering_bp     → /api/watering/*
- camera_bp       → /api/camera/*
- notifications_bp → /api/notifications/*
- settings_bp     → /api/settings/*
- ai_bp           → /api/ai/*（新規）
```

---

## 🔹 **src/ai/ai_consultation.py**

### `AIConsultationManager.__init__()`
**説明:** AI相談マネージャーの初期化  
**処理:**
```python
1. OpenAI APIクライアント初期化
2. 相談履歴リスト初期化
3. タグ別プロンプトテンプレート読み込み
4. 設定値の初期化
```

### `AIConsultationManager.get_harvest_judgment(image_path: str, sensor_data: dict)`
**説明:** 豆苗の収穫判断を実行  
**引数:**
- `image_path` (str): 撮影画像のパス
- `sensor_data` (dict): センサーデータ
**戻り値:** `Dict[str, Any]`
```python
{
    'harvest_ready': True/False,
    'confidence': 0.85,
    'recommendation': '収穫のタイミングです',
    'days_remaining': 2,
    'growth_stage': 'mature',
    'quality_score': 8.5
}
```
**処理:**
```python
1. 画像をBase64エンコード
2. センサーデータと組み合わせてプロンプト作成
3. OpenAI APIに問い合わせ
4. レスポンスを解析して結果を返す
```

### `AIConsultationManager.diagnose_disease(image_path: str, symptoms: list)`
**説明:** 豆苗の病気診断を実行  
**引数:**
- `image_path` (str): 撮影画像のパス
- `symptoms` (list): 症状リスト
**戻り値:** `Dict[str, Any]`
```python
{
    'disease_detected': 'うどんこ病',
    'confidence': 0.92,
    'treatment': '重曹水の散布を推奨',
    'prevention': '通風を良くする',
    'severity': 'mild',
    'affected_area': 'leaves'
}
```

### `AIConsultationManager.get_cooking_suggestions(harvest_data: dict)`
**説明:** 収穫した豆苗の調理例を提供  
**引数:**
- `harvest_data` (dict): 収穫データ
**戻り値:** `Dict[str, Any]`
```python
{
    'recommended_dishes': ['豆苗炒め', '豆苗スープ'],
    'cooking_tips': '茎の部分は火を通しすぎない',
    'nutrition_info': 'ビタミンCが豊富',
    'storage_tips': '冷蔵庫で3-4日保存可能'
}
```

### `AIConsultationManager.consult(question: str, tag: str)`
**説明:** 一般相談を実行  
**引数:**
- `question` (str): 質問内容
- `tag` (str): 相談タグ（general, harvest, disease, cooking）
**戻り値:** `Dict[str, Any]`
```python
{
    'answer': '豆苗の栽培に関する回答',
    'confidence': 0.88,
    'related_topics': ['水やり', '光量'],
    'next_steps': ['定期的な観察を続ける']
}
```

---

## 🔹 **src/api/ai_api.py**

### `AIConsultationResource.post()`
**説明:** AI相談API  
**HTTPメソッド:** POST  
**エンドポイント:** `/api/ai/consultation`  
**リクエストボディ:**
```json
{
  "question": "豆苗の育て方について教えて",
  "tag": "general"
}
```
**レスポンス（成功時）:**
```json
{
  "status": "success",
  "answer": "豆苗の栽培に関する回答",
  "confidence": 0.88,
  "tag": "general",
  "timestamp": "2025-10-15T09:30:00"
}
```

### `HarvestJudgmentResource.post()`
**説明:** 収穫判断API  
**HTTPメソッド:** POST  
**エンドポイント:** `/api/ai/harvest-judgment`  
**レスポンス:**
```json
{
  "status": "success",
  "harvest_ready": true,
  "confidence": 0.85,
  "recommendation": "収穫のタイミングです",
  "days_remaining": 2,
  "growth_stage": "mature"
}
```

### `DiseaseCheckResource.post()`
**説明:** 病気診断API  
**HTTPメソッド:** POST  
**エンドポイント:** `/api/ai/disease-check`  
**リクエストボディ:**
```json
{
  "symptoms": ["葉が白い", "成長が遅い"],
  "image_analysis": true
}
```

### `CookingTipsResource.post()`
**説明:** 調理例API  
**HTTPメソッド:** POST  
**エンドポイント:** `/api/ai/cooking-tips`  
**リクエストボディ:**
```json
{
  "harvest_amount": 200,
  "harvest_quality": "excellent",
  "preferences": ["炒め物", "スープ"]
}
```

---

## 🔹 **src/camera/multi_camera_manager.py**

### `MultiCameraManager.__init__()`
**説明:** 多層化カメラマネージャーの初期化  
**処理:**
```python
1. カメラ辞書初期化
2. カメラ設定読み込み
3. 撮影スケジュール初期化
4. 各カメラの状態確認
```

### `MultiCameraManager.add_camera(camera_id: str, camera_index: int, layer: int)`
**説明:** カメラをシステムに追加  
**引数:**
- `camera_id` (str): カメラID
- `camera_index` (int): カメラインデックス
- `layer` (int): 階層番号
**戻り値:** `bool` - 成功/失敗

### `MultiCameraManager.capture_layer(layer: int)`
**説明:** 指定階層の撮影を実行  
**引数:**
- `layer` (int): 階層番号
**戻り値:** `List[Dict[str, Any]]` - 撮影結果リスト
```python
[
    {
        'camera_id': 'camera_001',
        'layer': 1,
        'image_path': '/path/to/image.jpg',
        'timestamp': '2025-10-15T09:30:00',
        'success': True
    }
]
```

### `MultiCameraManager.schedule_capture(schedule_config: dict)`
**説明:** 撮影スケジュールを設定  
**引数:**
- `schedule_config` (dict): スケジュール設定
**戻り値:** `Dict[str, Any]`
```python
{
    'status': 'success',
    'schedule_id': 'schedule_001',
    'layers': [1, 2, 3],
    'times': ['06:00', '12:00', '18:00']
}
```

### `MultiCameraManager.get_camera_status()`
**説明:** 全カメラの状態を取得  
**戻り値:** `Dict[str, Any]`
```python
{
    'total_cameras': 3,
    'active_cameras': 2,
    'cameras': [
        {
            'camera_id': 'camera_001',
            'layer': 1,
            'status': 'active',
            'last_capture': '2025-10-15T09:30:00'
        }
    ]
}
```

---

## 🔹 **src/watering/water_tank_manager.py**

### `WaterTankManager.__init__()`
**説明:** 給水タンクマネージャーの初期化  
**処理:**
```python
1. タンク容量設定（デフォルト2000ml）
2. 現在水量初期化
3. 使用履歴リスト初期化
4. 設定ファイル読み込み
```

### `WaterTankManager.set_initial_volume(volume: int)`
**説明:** 初期水量を設定  
**引数:**
- `volume` (int): 初期水量（ml）
**戻り値:** `bool` - 成功/失敗
**処理:**
```python
1. 容量上限チェック
2. 現在水量を更新
3. 設定ファイルに保存
4. ログ出力
```

### `WaterTankManager.calculate_remaining_volume(watering_amount: int)`
**説明:** 給水後の残量を計算  
**引数:**
- `watering_amount` (int): 給水量（ml）
**戻り値:** `int` - 残量（ml）
**処理:**
```python
1. 現在水量から給水量を減算
2. 0以下にならないよう調整
3. 使用履歴に記録
4. 設定ファイル更新
5. 残量を返す
```

### `WaterTankManager.get_tank_status()`
**説明:** タンク状態を取得  
**戻り値:** `Dict[str, Any]`
```python
{
    'current_volume': 1500,
    'capacity': 2000,
    'percentage': 75.0,
    'status': 'normal',
    'last_refill': '2025-10-10T10:00:00',
    'estimated_days_remaining': 5
}
```

### `WaterTankManager.refill_tank(amount: int)`
**説明:** タンクに水を補充  
**引数:**
- `amount` (int): 補充量（ml）
**戻り値:** `Dict[str, Any]`
```python
{
    'success': True,
    'previous_volume': 500,
    'new_volume': 2000,
    'refill_amount': 1500,
    'timestamp': '2025-10-15T09:30:00'
}
```

### `WaterTankManager.get_usage_statistics(days: int)`
**説明:** 使用統計を取得  
**引数:**
- `days` (int): 統計期間（日数）
**戻り値:** `Dict[str, Any]`
```python
{
    'total_usage': 3000,
    'average_daily': 100,
    'peak_usage': 200,
    'refill_count': 2,
    'efficiency_score': 8.5
}
```

---

## 🔹 **src/api/camera_api.py**

### `CameraScheduleResource.post()`
**説明:** 撮影スケジュール設定API  
**HTTPメソッド:** POST  
**エンドポイント:** `/api/camera/schedule`  
**リクエストボディ:**
```json
{
  "layers": [1, 2, 3],
  "times": ["06:00", "12:00", "18:00"],
  "enabled": true
}
```
**レスポンス:**
```json
{
  "status": "success",
  "schedule_id": "schedule_001",
  "message": "撮影スケジュールを設定しました"
}
```

### `MultiCameraStatusResource.get()`
**説明:** 多層化カメラ状態取得API  
**HTTPメソッド:** GET  
**エンドポイント:** `/api/camera/status`  
**レスポンス:**
```json
{
  "status": "success",
  "data": {
    "total_cameras": 3,
    "active_cameras": 2,
    "cameras": [...]
  }
}
```

---

## 🔹 **src/web/static/js/ai-consultation.js**

### `AIConsultationManager.initialize()`
**説明:** AI相談マネージャーの初期化（フロントエンド）  
**引数:** なし  
**戻り値:** なし  
**処理:**
```javascript
1. 相談履歴初期化
2. タグ選択UI初期化
3. 質問フォーム設定
4. 結果表示エリア準備
```

### `AIConsultationManager.submitQuestion(question, tag)`
**説明:** AI相談を送信  
**引数:**
- `question` (string): 質問内容
- `tag` (string): 相談タグ
**戻り値:** `Promise<Object>`  
**処理:**
```javascript
1. POST /api/ai/consultation を呼び出し
2. レスポンス解析
3. 結果表示
4. 履歴に追加
```

### `AIConsultationManager.checkHarvestReadiness()`
**説明:** 収穫判断を実行  
**引数:** なし  
**戻り値:** `Promise<Object>`  
**処理:**
```javascript
1. POST /api/ai/harvest-judgment を呼び出し
2. 結果を視覚的に表示
3. 推奨事項を表示
```

### `AIConsultationManager.diagnoseDisease(symptoms)`
**説明:** 病気診断を実行  
**引数:**
- `symptoms` (array): 症状リスト
**戻り値:** `Promise<Object>`  
**処理:**
```javascript
1. POST /api/ai/disease-check を呼び出し
2. 診断結果表示
3. 対処法を表示
```

---

## 🔹 **src/web/static/js/multi-camera.js**

### `MultiCameraManager.initialize()`
**説明:** 多層化カメラマネージャーの初期化  
**引数:** なし  
**戻り値:** なし  
**処理:**
```javascript
1. カメラ状態取得
2. 階層別UI初期化
3. 撮影ボタン設定
4. スケジュール設定UI準備
```

### `MultiCameraManager.captureLayer(layer)`
**説明:** 指定階層の撮影を実行  
**引数:**
- `layer` (number): 階層番号
**戻り値:** `Promise<Object>`  
**処理:**
```javascript
1. POST /api/camera/capture-layer を呼び出し
2. 撮影結果表示
3. 画像プレビュー表示
```

### `MultiCameraManager.setSchedule(scheduleConfig)`
**説明:** 撮影スケジュールを設定  
**引数:**
- `scheduleConfig` (object): スケジュール設定
**戻り値:** `Promise<Object>`  
**処理:**
```javascript
1. POST /api/camera/schedule を呼び出し
2. 設定結果表示
3. スケジュール一覧更新
```

---

**作成日**: 2025年10月15日  
**バージョン**: 1.0  
**ブランチ**: bean-sprout-planter

