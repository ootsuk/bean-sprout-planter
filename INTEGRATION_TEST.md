# 豆苗プランター - 統合テスト手順書

## 📋 概要
豆苗栽培に特化した自動植物育成システムの統合テスト手順書

## 🎯 テスト目標
- 全機能の統合動作確認
- 豆苗栽培シナリオでのテスト
- AI判断機能の精度確認
- 多層化カメラシステムの動作確認
- 給水タンク管理機能の動作確認

## 🛠️ テスト環境

### ハードウェア
- Raspberry Pi 5
- テスト用センサー（AHT25, SEN0193, フロートスイッチ）
- テスト用カメラ（複数台）
- テスト用給水システム
- テスト用豆苗

### ソフトウェア
- Python 3.11.x
- テスト用AI APIキー
- テスト用LINE Notifyトークン

## 🧪 テスト手順

### Phase 1: 基本機能テスト

#### テスト1.1: センサーシステム統合テスト
```bash
cd /home/pi/projects/bean-sprout-planter
source venv/bin/activate
python tests/test_sensor_integration.py
```

**期待結果:**
- 温湿度センサーから正常にデータ取得
- 土壌水分センサーから正常にデータ取得
- フロートスイッチから正常にデータ取得
- データが正しい形式で返される

#### テスト1.2: カメラシステム統合テスト
```bash
python tests/test_camera_integration.py
```

**期待結果:**
- 複数カメラが正常に認識される
- 各階層の撮影が正常に実行される
- 画像が正しい形式で保存される
- スケジュール撮影が正常に動作する

#### テスト1.3: 給水システム統合テスト
```bash
python tests/test_watering_integration.py
```

**期待結果:**
- 土壌水分値に基づく給水判定が正常に動作
- リレーモジュールが正常に制御される
- 給水履歴が正しく記録される
- 安全機能（連続給水制限）が正常に動作

### Phase 2: AI機能テスト

#### テスト2.1: AI相談機能テスト
```bash
python tests/test_ai_consultation.py
```

**テストケース:**
```python
# 一般相談テスト
def test_general_consultation():
    ai_manager = AIConsultationManager()
    result = ai_manager.consult("豆苗の育て方を教えて", "general")
    assert result['confidence'] > 0.7
    assert len(result['answer']) > 0

# 収穫判断テスト
def test_harvest_judgment():
    ai_manager = AIConsultationManager()
    # テスト用画像とセンサーデータを使用
    result = ai_manager.get_harvest_judgment("test_image.jpg", test_sensor_data)
    assert 'harvest_ready' in result
    assert 'confidence' in result
    assert result['confidence'] > 0.0

# 病気診断テスト
def test_disease_diagnosis():
    ai_manager = AIConsultationManager()
    result = ai_manager.diagnose_disease("test_image.jpg", ["葉が黄色い"])
    assert 'disease_detected' in result
    assert 'treatment' in result

# 調理例テスト
def test_cooking_suggestions():
    ai_manager = AIConsultationManager()
    result = ai_manager.get_cooking_suggestions(test_harvest_data)
    assert 'recommended_dishes' in result
    assert len(result['recommended_dishes']) > 0
```

#### テスト2.2: AI API統合テスト
```bash
python tests/test_ai_api_integration.py
```

**テストケース:**
```python
def test_ai_consultation_api():
    response = requests.post('http://localhost:8080/api/ai/consultation', 
                            json={'question': '豆苗の育て方', 'tag': 'general'})
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert 'answer' in data

def test_harvest_judgment_api():
    response = requests.post('http://localhost:8080/api/ai/harvest-judgment')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert 'harvest_ready' in data
```

### Phase 3: 多層化システムテスト

#### テスト3.1: 多層化カメラ管理テスト
```bash
python tests/test_multi_camera_system.py
```

**テストケース:**
```python
def test_camera_addition():
    mcm = MultiCameraManager()
    mcm.add_camera("camera_001", 0, 1)
    mcm.add_camera("camera_002", 1, 2)
    status = mcm.get_camera_status()
    assert status['total_cameras'] == 2
    assert status['active_cameras'] == 2

def test_layer_capture():
    mcm = MultiCameraManager()
    results = mcm.capture_layer(1)
    assert len(results) > 0
    for result in results:
        assert result['success'] == True
        assert result['layer'] == 1

def test_schedule_capture():
    mcm = MultiCameraManager()
    schedule_config = {
        'layers': [1, 2, 3],
        'times': ['06:00', '12:00', '18:00']
    }
    result = mcm.schedule_capture(schedule_config)
    assert result['status'] == 'success'
    assert 'schedule_id' in result
```

#### テスト3.2: 給水タンク管理テスト
```bash
python tests/test_water_tank_management.py
```

**テストケース:**
```python
def test_initial_volume_setting():
    wtm = WaterTankManager()
    wtm.set_initial_volume(1500)
    status = wtm.get_tank_status()
    assert status['current_volume'] == 1500
    assert status['percentage'] == 75.0

def test_volume_calculation():
    wtm = WaterTankManager()
    wtm.set_initial_volume(2000)
    remaining = wtm.calculate_remaining_volume(500)
    assert remaining == 1500
    
    status = wtm.get_tank_status()
    assert status['current_volume'] == 1500

def test_refill_function():
    wtm = WaterTankManager()
    wtm.set_initial_volume(500)
    result = wtm.refill_tank(1000)
    assert result['success'] == True
    assert result['new_volume'] == 1500
```

### Phase 4: Web UI統合テスト

#### テスト4.1: ダッシュボード機能テスト
```bash
python tests/test_web_ui_integration.py
```

**テストケース:**
```python
def test_dashboard_access():
    response = requests.get('http://localhost:8080/dashboard')
    assert response.status_code == 200
    assert 'dashboard' in response.text.lower()

def test_sensor_data_display():
    response = requests.get('http://localhost:8080/api/sensors/')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert 'data' in data

def test_ai_consultation_page():
    response = requests.get('http://localhost:8080/ai-consultation')
    assert response.status_code == 200
    assert 'ai' in response.text.lower()
```

#### テスト4.2: 設定画面テスト
```bash
python tests/test_settings_integration.py
```

**テストケース:**
```python
def test_settings_access():
    response = requests.get('http://localhost:8080/settings')
    assert response.status_code == 200

def test_settings_save():
    test_settings = {
        'watering_interval': 6,
        'camera_schedule': ['06:00', '18:00'],
        'ai_enabled': True
    }
    response = requests.post('http://localhost:8080/api/settings/', 
                           json=test_settings)
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
```

### Phase 5: 通知システムテスト

#### テスト5.1: LINE通知統合テスト
```bash
python tests/test_notification_integration.py
```

**テストケース:**
```python
def test_line_notify_connection():
    ln = LineNotify()
    result = ln.send_message("統合テスト通知です")
    assert result == True

def test_watering_notification():
    nm = NotificationManager()
    result = nm.send_watering_notification(100)
    assert result == True

def test_sensor_alert():
    nm = NotificationManager()
    result = nm.send_sensor_alert("温度異常", 35.5)
    assert result == True
```

### Phase 6: 豆苗栽培シナリオテスト

#### テスト6.1: 栽培開始シナリオ
```bash
python tests/test_bean_sprout_scenario.py
```

**シナリオテスト:**
```python
def test_planting_scenario():
    """豆苗の植え付けシナリオ"""
    # 1. 初期設定
    wtm = WaterTankManager()
    wtm.set_initial_volume(2000)
    
    # 2. センサー初期化
    sm = SensorManager()
    sm.start_monitoring()
    
    # 3. カメラ設定
    mcm = MultiCameraManager()
    mcm.add_camera("camera_001", 0, 1)
    
    # 4. 初回撮影
    results = mcm.capture_layer(1)
    assert len(results) > 0
    
    # 5. AI成長判定
    ai_manager = AIConsultationManager()
    judgment = ai_manager.get_harvest_judgment(results[0]['image_path'], 
                                              sm.get_latest_data())
    assert 'harvest_ready' in judgment

def test_growth_monitoring_scenario():
    """成長監視シナリオ"""
    # 1. 定期的なセンサーデータ取得
    sm = SensorManager()
    for i in range(5):
        data = sm.get_latest_data()
        assert 'temperature' in data
        assert 'humidity' in data
        assert 'soil_moisture' in data
        time.sleep(1)
    
    # 2. 給水判定
    wm = WateringManager()
    soil_moisture = sm.get_latest_data()['soil_moisture']
    if soil_moisture < 159:
        result = wm.start_watering(soil_moisture, True)
        assert result['success'] == True
    
    # 3. タンク残量更新
    wtm = WaterTankManager()
    remaining = wtm.calculate_remaining_volume(100)
    assert remaining >= 0

def test_harvest_scenario():
    """収穫シナリオ"""
    # 1. 収穫判断
    ai_manager = AIConsultationManager()
    judgment = ai_manager.get_harvest_judgment("test_harvest_image.jpg", 
                                             test_sensor_data)
    
    if judgment['harvest_ready']:
        # 2. 調理例取得
        cooking_tips = ai_manager.get_cooking_suggestions(test_harvest_data)
        assert 'recommended_dishes' in cooking_tips
        
        # 3. 収穫通知
        nm = NotificationManager()
        result = nm.send_harvest_notification(judgment)
        assert result == True
```

## 📊 テスト結果レポート

### テスト実行コマンド
```bash
# 全テスト実行
python -m pytest tests/ -v --tb=short

# カバレッジ付きテスト実行
python -m pytest tests/ --cov=src --cov-report=html

# 特定のテスト実行
python -m pytest tests/test_ai_integration.py -v
```

### 期待されるテスト結果
- **センサーシステム**: 100% パス
- **カメラシステム**: 100% パス
- **給水システム**: 100% パス
- **AI機能**: 95% パス（AI APIの応答時間による）
- **多層化システム**: 100% パス
- **Web UI**: 100% パス
- **通知システム**: 100% パス
- **栽培シナリオ**: 100% パス

## 🔧 トラブルシューティング

### よくあるテスト失敗と解決方法

#### 問題1: AI API接続エラー
```bash
# 解決方法
# .envファイルのAPIキーを確認
# インターネット接続を確認
curl -I https://api.openai.com
```

#### 問題2: カメラ認識エラー
```bash
# 解決方法
lsusb
sudo modprobe uvcvideo
v4l2-ctl --list-devices
```

#### 問題3: GPIO権限エラー
```bash
# 解決方法
sudo usermod -a -G gpio pi
sudo reboot
```

## 📋 テスト完了チェックリスト

- [ ] センサーシステム統合テスト完了
- [ ] カメラシステム統合テスト完了
- [ ] 給水システム統合テスト完了
- [ ] AI機能テスト完了
- [ ] 多層化システムテスト完了
- [ ] Web UI統合テスト完了
- [ ] 通知システムテスト完了
- [ ] 豆苗栽培シナリオテスト完了
- [ ] テスト結果レポート作成完了
- [ ] パフォーマンステスト完了

## 🎯 次のステップ

1. **本番環境デプロイ**: テスト環境での動作確認後、本番環境にデプロイ
2. **運用監視**: 実際の豆苗栽培での運用監視
3. **AI学習**: 実際のデータでのAI精度向上
4. **機能拡張**: ユーザーフィードバックに基づく機能拡張

---

**作成日**: 2025年10月15日  
**バージョン**: 1.0  
**ブランチ**: bean-sprout-planter

