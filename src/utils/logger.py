# 豆苗プランター - ログ設定

"""
ログシステムの設定と管理
"""

import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path


def setup_logging():
    """ログシステムを設定"""
    
    # ログディレクトリを作成
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # ログレベルを環境変数から取得
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # ログフォーマット
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # 既存のハンドラーをクリア
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # ファイルハンドラー（日別ローテーション）
    log_file = log_dir / f"bean_sprout_planter_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, log_level))
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # エラーログ用のハンドラー
    error_log_file = log_dir / f"error_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # アプリケーション開始ログ
    logger = logging.getLogger(__name__)
    logger.info("🌱 豆苗プランター - ログシステム初期化完了")
    logger.info(f"📝 ログレベル: {log_level}")
    logger.info(f"📁 ログファイル: {log_file}")
    logger.info(f"❌ エラーログファイル: {error_log_file}")


def get_logger(name: str) -> logging.Logger:
    """指定された名前のロガーを取得"""
    return logging.getLogger(name)


def log_sensor_data(sensor_data: dict):
    """センサーデータをログに記録"""
    logger = get_logger("sensor")
    logger.info(f"📊 センサーデータ: 温度={sensor_data.get('temperature', 'N/A')}°C, "
                f"湿度={sensor_data.get('humidity', 'N/A')}%, "
                f"土壌水分={sensor_data.get('soil_moisture', 'N/A')}")


def log_watering_event(amount: int, success: bool):
    """給水イベントをログに記録"""
    logger = get_logger("watering")
    status = "成功" if success else "失敗"
    logger.info(f"💧 給水実行: {amount}ml - {status}")


def log_camera_capture(camera_id: str, layer: int, success: bool):
    """カメラ撮影イベントをログに記録"""
    logger = get_logger("camera")
    status = "成功" if success else "失敗"
    logger.info(f"📷 カメラ撮影: {camera_id} (階層{layer}) - {status}")


def log_ai_consultation(question: str, tag: str, success: bool):
    """AI相談イベントをログに記録"""
    logger = get_logger("ai")
    status = "成功" if success else "失敗"
    logger.info(f"🤖 AI相談: [{tag}] {question[:50]}... - {status}")


def log_system_event(event: str, details: str = ""):
    """システムイベントをログに記録"""
    logger = get_logger("system")
    if details:
        logger.info(f"⚙️ システム: {event} - {details}")
    else:
        logger.info(f"⚙️ システム: {event}")


def log_error(error: Exception, context: str = ""):
    """エラーをログに記録"""
    logger = get_logger("error")
    if context:
        logger.error(f"❌ エラー [{context}]: {str(error)}", exc_info=True)
    else:
        logger.error(f"❌ エラー: {str(error)}", exc_info=True)
