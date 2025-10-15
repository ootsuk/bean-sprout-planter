#!/bin/bash
# 豆苗プランター - Raspberry Pi環境構築スクリプト

set -e

echo "🌱 豆苗プランター - Raspberry Pi環境構築を開始します..."

# システム更新
echo "📦 システムを更新しています..."
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git

# プロジェクトディレクトリの作成
echo "📁 プロジェクトディレクトリを作成しています..."
mkdir -p /home/pi/projects
cd /home/pi/projects

# プロジェクトのクローン（実際のリポジトリURLに置き換え）
echo "📥 プロジェクトをクローンしています..."
# git clone https://github.com/your-org/bean-sprout-planter.git
# cd bean-sprout-planter

# 仮想環境の作成
echo "🐍 Python仮想環境を作成しています..."
python3.11 -m venv venv
source venv/bin/activate

# pipのアップグレード
echo "⬆️ pipをアップグレードしています..."
pip install --upgrade pip

# 依存関係のインストール
echo "📚 依存関係をインストールしています..."
pip install -r requirements.txt

# 環境変数ファイルの設定
echo "⚙️ 環境変数ファイルを設定しています..."
cp .env.raspberrypi .env
echo "⚠️  .envファイルを編集してAPIキーを設定してください"

# USBストレージのマウント設定
echo "💾 USBストレージのマウント設定を行っています..."
sudo mkdir -p /mnt/usb-storage
sudo chown pi:pi /mnt/usb-storage

# GPIO権限の設定
echo "🔌 GPIO権限を設定しています..."
sudo usermod -a -G gpio pi
sudo usermod -a -G i2c pi
sudo usermod -a -G spi pi

# udevルールの設定
echo "📋 udevルールを設定しています..."
sudo tee /etc/udev/rules.d/99-gpio.rules > /dev/null << 'EOF'
SUBSYSTEM=="gpio", GROUP="gpio", MODE="0664"
SUBSYSTEM=="gpio*", PROGRAM="/bin/sh -c 'chown -R root:gpio /sys/class/gpio && chmod -R 775 /sys/class/gpio; chown -R root:gpio /sys/devices/virtual/gpio && chmod -R 775 /sys/devices/virtual/gpio'"
EOF

# systemdサービスの設定
echo "🔧 systemdサービスを設定しています..."
sudo cp bean-sprout-planter.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bean-sprout-planter

# cronジョブの設定
echo "⏰ cronジョブを設定しています..."
(crontab -l 2>/dev/null; echo "# 豆苗プランター自動撮影"; echo "0 6 * * * cd /home/pi/projects/bean-sprout-planter && /home/pi/projects/bean-sprout-planter/venv/bin/python -c \"from src.camera.multi_camera_manager import MultiCameraManager; MultiCameraManager().capture_all_layers()\""; echo "# 豆苗プランターセンサーデータ取得"; echo "0 * * * * cd /home/pi/projects/bean-sprout-planter && /home/pi/projects/bean-sprout-planter/venv/bin/python -c \"from src.sensors.sensor_manager import SensorManager; SensorManager().read_all_sensors()\"") | crontab -

echo "✅ 環境構築が完了しました！"
echo ""
echo "📋 次のステップ:"
echo "1. .envファイルを編集してAPIキーを設定"
echo "2. USBストレージを接続してマウント"
echo "3. センサーとアクチュエータを接続"
echo "4. sudo systemctl start bean-sprout-planter でサービス開始"
echo "5. http://localhost:8080 でWeb UIにアクセス"
echo ""
echo "🔧 トラブルシューティング:"
echo "- ログ確認: sudo journalctl -u bean-sprout-planter -f"
echo "- サービス状態: sudo systemctl status bean-sprout-planter"
echo "- サービス再起動: sudo systemctl restart bean-sprout-planter"
