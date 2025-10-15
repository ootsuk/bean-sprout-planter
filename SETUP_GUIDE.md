# 豆苗プランター - 環境構築手順書

## 📋 概要
豆苗栽培に特化した自動植物育成システムの環境構築手順書

## 🎯 構築目標
- Raspberry Pi 5上での動作環境構築
- Python仮想環境の設定
- 必要なライブラリのインストール
- 設定ファイルの準備
- 初回起動テスト

## 🛠️ 必要な環境

### ハードウェア
- Raspberry Pi 5
- microSDカード（32GB以上推奨）
- USBカメラ（複数台対応）
- センサー類（AHT25, SEN0193, フロートスイッチ）
- リレーモジュール（AE-G5V-DRV）
- 水中ポンプ（12V DC）

### ソフトウェア
- Raspberry Pi OS (64-bit)
- Python 3.11.x
- Git

## 🔧 構築手順

### Step 1: Raspberry Pi OS のセットアップ

#### 1.1 OSイメージの書き込み
```bash
# Raspberry Pi Imagerを使用してOSイメージを書き込み
# 設定項目：
# - SSH有効化
# - ユーザー名・パスワード設定
# - WiFi設定（必要に応じて）
```

#### 1.2 システム更新
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git
```

### Step 2: プロジェクトのクローン

#### 2.1 プロジェクトディレクトリの作成
```bash
mkdir -p /home/pi/projects
cd /home/pi/projects
```

#### 2.2 プロジェクトのクローン
```bash
# GitHubからクローン（実際のリポジトリURLに置き換え）
git clone https://github.com/your-org/bean-sprout-planter.git
cd bean-sprout-planter
```

### Step 3: Python仮想環境の構築

#### 3.1 仮想環境の作成
```bash
python3.11 -m venv venv
source venv/bin/activate
```

#### 3.2 pipのアップグレード
```bash
pip install --upgrade pip
```

#### 3.3 依存関係のインストール
```bash
pip install -r requirements.txt
```

### Step 4: 設定ファイルの準備

#### 4.1 環境変数ファイルの作成
```bash
cp .env.example .env
nano .env
```

#### 4.2 .envファイルの設定
```bash
# Flask設定
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=False

# データベース設定
DATA_BASE_PATH=/mnt/usb-storage

# センサー設定
SENSOR_CHECK_INTERVAL=60
TEMPERATURE_HUMIDITY_INTERVAL=1800
SOIL_MOISTURE_INTERVAL=300

# 給水設定
SOIL_MOISTURE_THRESHOLD=159
WATERING_INTERVAL_HOURS=12
WATERING_DURATION_SECONDS=5
WATER_AMOUNT_ML=100

# カメラ設定
CAMERA_RESOLUTION_WIDTH=1280
CAMERA_RESOLUTION_HEIGHT=720
AUTO_CAPTURE_TIME=06:00

# LINE通知設定
LINE_NOTIFY_TOKEN=your-line-notify-token
LINE_NOTIFY_API_URL=https://notify-api.line.me/api/notify

# AI設定
OPENAI_API_KEY=your-openai-api-key
AI_MODEL=gpt-4
AI_MAX_TOKENS=1000

# ログ設定
LOG_LEVEL=INFO
LOG_FILE_PATH=/mnt/usb-storage/logs
```

### Step 5: USBストレージのマウント

#### 5.1 USBストレージの接続
```bash
# USBストレージを接続後、デバイスを確認
lsblk
```

#### 5.2 マウントポイントの作成
```bash
sudo mkdir -p /mnt/usb-storage
sudo chown pi:pi /mnt/usb-storage
```

#### 5.3 マウント設定
```bash
# /etc/fstabに追加（デバイス名は実際のものに置き換え）
echo "/dev/sda1 /mnt/usb-storage ext4 defaults,uid=pi,gid=pi 0 0" | sudo tee -a /etc/fstab
```

#### 5.4 マウントの実行
```bash
sudo mount -a
```

### Step 6: GPIO権限の設定

#### 6.1 piユーザーをgpioグループに追加
```bash
sudo usermod -a -G gpio pi
sudo usermod -a -G i2c pi
sudo usermod -a -G spi pi
```

#### 6.2 udevルールの設定
```bash
sudo nano /etc/udev/rules.d/99-gpio.rules
```

```bash
# GPIO権限設定
SUBSYSTEM=="gpio", GROUP="gpio", MODE="0664"
SUBSYSTEM=="gpio*", PROGRAM="/bin/sh -c 'chown -R root:gpio /sys/class/gpio && chmod -R 775 /sys/class/gpio; chown -R root:gpio /sys/devices/virtual/gpio && chmod -R 775 /sys/devices/virtual/gpio'"
```

### Step 7: システムサービスの設定

#### 7.1 systemdサービスファイルの作成
```bash
sudo nano /etc/systemd/system/bean-sprout-planter.service
```

```ini
[Unit]
Description=Bean Sprout Planter Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/projects/bean-sprout-planter
Environment=PATH=/home/pi/projects/bean-sprout-planter/venv/bin
ExecStart=/home/pi/projects/bean-sprout-planter/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 7.2 サービスの有効化
```bash
sudo systemctl daemon-reload
sudo systemctl enable bean-sprout-planter
sudo systemctl start bean-sprout-planter
```

### Step 8: 初回起動テスト

#### 8.1 サービス状態の確認
```bash
sudo systemctl status bean-sprout-planter
```

#### 8.2 ログの確認
```bash
sudo journalctl -u bean-sprout-planter -f
```

#### 8.3 Web UIアクセステスト
```bash
# ブラウザでアクセス
http://localhost:8080
http://localhost:8080/dashboard
http://localhost:8080/settings
http://localhost:8080/ai-consultation
```

### Step 9: 自動起動設定

#### 9.1 cronジョブの設定
```bash
crontab -e
```

```bash
# 毎日午前6時に自動撮影
0 6 * * * cd /home/pi/projects/bean-sprout-planter && /home/pi/projects/bean-sprout-planter/venv/bin/python -c "from src.camera.multi_camera_manager import MultiCameraManager; MultiCameraManager().capture_all_layers()"

# 毎時センサーデータ取得
0 * * * * cd /home/pi/projects/bean-sprout-planter && /home/pi/projects/bean-sprout-planter/venv/bin/python -c "from src.sensors.sensor_manager import SensorManager; SensorManager().read_all_sensors()"
```

## 🧪 動作確認テスト

### テスト1: センサー動作確認
```bash
cd /home/pi/projects/bean-sprout-planter
source venv/bin/activate
python -c "from src.sensors.sensor_manager import SensorManager; sm = SensorManager(); print(sm.get_latest_data())"
```

### テスト2: カメラ動作確認
```bash
python -c "from src.camera.multi_camera_manager import MultiCameraManager; mcm = MultiCameraManager(); print(mcm.get_camera_status())"
```

### テスト3: AI機能確認
```bash
python -c "from src.ai.ai_consultation import AIConsultationManager; ai = AIConsultationManager(); print(ai.consult('豆苗の育て方を教えて', 'general'))"
```

### テスト4: LINE通知確認
```bash
python -c "from src.notifications.line_notify import LineNotify; ln = LineNotify(); print(ln.send_message('テスト通知です'))"
```

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 問題1: GPIO権限エラー
```bash
# 解決方法
sudo usermod -a -G gpio pi
sudo reboot
```

#### 問題2: USBストレージがマウントされない
```bash
# 解決方法
sudo dmesg | grep -i usb
sudo fdisk -l
sudo mkfs.ext4 /dev/sda1  # フォーマット（データが消えるので注意）
```

#### 問題3: カメラが認識されない
```bash
# 解決方法
lsusb
sudo modprobe uvcvideo
v4l2-ctl --list-devices
```

#### 問題4: AI API接続エラー
```bash
# 解決方法
# .envファイルのAPIキーを確認
# インターネット接続を確認
curl -I https://api.openai.com
```

## 📊 構築完了チェックリスト

- [ ] Raspberry Pi OS インストール完了
- [ ] Python 3.11 インストール完了
- [ ] 仮想環境構築完了
- [ ] 依存関係インストール完了
- [ ] 設定ファイル作成完了
- [ ] USBストレージマウント完了
- [ ] GPIO権限設定完了
- [ ] システムサービス設定完了
- [ ] 初回起動テスト完了
- [ ] 自動起動設定完了
- [ ] 全機能動作確認完了

## 🎯 次のステップ

1. **ハードウェア接続**: センサーとアクチュエータの接続
2. **設定調整**: 豆苗栽培に最適なパラメータ設定
3. **AI学習**: 豆苗特有のデータでのAI学習
4. **運用開始**: 実際の豆苗栽培での運用開始

---

**作成日**: 2025年10月15日  
**バージョン**: 1.0  
**ブランチ**: bean-sprout-planter

