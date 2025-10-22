# 豆苗プランター - メインアプリケーション

"""
豆苗栽培に特化した自動植物育成システム
メインエントリーポイント
"""

import os
import sys
import logging
import signal
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.app.app import create_app
from src.api.api_blueprint import register_api_blueprints
from src.utils.logger import setup_logging
from src.utils.scheduler import scheduler_manager
from src.data.data_manager import data_manager
from src.sensors.sensor_manager import sensor_manager
from src.watering.water_tank_manager import water_tank_manager
from src.camera.single_camera_manager import single_camera_manager


def signal_handler(signum, frame):
    """シグナルハンドラー"""
    logger = logging.getLogger(__name__)
    logger.info(f"シグナル {signum} を受信しました。アプリケーションを終了します...")
    
    # スケジューラーを停止
    scheduler_manager.shutdown()
    
    sys.exit(0)


def main():
    """メイン実行関数"""
    
    # ログ設定
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🌱 豆苗プランター起動中...")
        
        # シグナルハンドラーを設定
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 各マネージャーを初期化
        logger.info("📊 データマネージャーを初期化中...")
        # data_managerは既に初期化済み
        
        logger.info("🌡️ センサーマネージャーを初期化中...")
        # sensor_managerは既に初期化済み
        
        logger.info("💧 給水マネージャーを初期化中...")
        water_tank_manager.initialize(data_manager)
        
        logger.info("📷 カメラマネージャーを初期化中...")
        single_camera_manager.initialize(data_manager)
        
        # スケジューラーを初期化
        logger.info("⏰ スケジューラーを初期化中...")
        scheduler_manager.initialize(
            data_manager=data_manager,
            sensor_manager=sensor_manager,
            watering_manager=water_tank_manager,
            camera_manager=single_camera_manager
        )
        
        # Flaskアプリケーション作成
        logger.info("🌐 Flaskアプリケーションを作成中...")
        app = create_app()
        
        # APIブループリントを登録
        logger.info("🔌 APIブループリントを登録中...")
        register_api_blueprints(app)
        
        logger.info("✅ 初期化完了！")
        logger.info("📱 Webインターフェース: http://0.0.0.0:8080")
        logger.info("⏰ スケジューラー: 動作中")
        
        # アプリケーション実行
        app.run(
            host='0.0.0.0',
            port=8080,
            debug=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("⏹️ アプリケーション停止")
    except Exception as e:
        logger.error(f"❌ アプリケーションエラー: {str(e)}")
        sys.exit(1)
    finally:
        # クリーンアップ
        logger.info("🧹 クリーンアップ中...")
        scheduler_manager.shutdown()


if __name__ == "__main__":
    main()



