# 豆苗プランター - データ管理モジュール

"""
データ管理機能
- センサーデータの永続化
- 設定データの管理
- 統計データの計算
- データのエクスポート・インポート
"""

import json
import csv
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class DataPoint:
    """データポイント"""
    timestamp: str
    data_type: str
    value: Union[float, int, str, bool]
    metadata: Optional[Dict] = None


class DataManager:
    """データ管理クラス"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # データベースファイル
        self.db_path = self.data_dir / "bean_sprout_data.db"
        
        # 設定ファイル
        self.config_path = self.data_dir / "config.json"
        
        # データベース初期化
        self._init_database()
        
        # 設定読み込み
        self.config = self._load_config()
    
    def _init_database(self):
        """データベースの初期化"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # センサーデータテーブル
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sensor_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        temperature REAL,
                        humidity REAL,
                        soil_moisture INTEGER,
                        tank_level BOOLEAN,
                        sensor_status TEXT
                    )
                """)
                
                # 給水履歴テーブル
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS watering_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        amount INTEGER,
                        duration INTEGER,
                        success BOOLEAN,
                        reason TEXT
                    )
                """)
                
                # カメラ撮影履歴テーブル
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS camera_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        camera_id TEXT,
                        layer INTEGER,
                        file_path TEXT,
                        success BOOLEAN
                    )
                """)
                
                # AI相談履歴テーブル
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_consultation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        question TEXT,
                        answer TEXT,
                        tag TEXT,
                        confidence REAL,
                        model TEXT
                    )
                """)
                
                # 通知履歴テーブル
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notification_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        type TEXT,
                        title TEXT,
                        message TEXT,
                        channel TEXT,
                        success BOOLEAN
                    )
                """)
                
                conn.commit()
                logger.info("データベース初期化完了")
                
        except Exception as e:
            logger.error(f"データベース初期化エラー: {e}")
    
    def _load_config(self) -> Dict:
        """設定ファイルの読み込み"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # デフォルト設定
                default_config = {
                    "sensors": {
                        "check_interval": 60,
                        "temperature_humidity_interval": 1800,
                        "soil_moisture_interval": 300
                    },
                    "watering": {
                        "soil_moisture_threshold": 159,
                        "watering_interval_hours": 12,
                        "watering_duration_seconds": 5,
                        "water_amount_ml": 100
                    },
                    "camera": {
                        "resolution_width": 1280,
                        "resolution_height": 720,
                        "auto_capture_time": "06:00"
                    },
                    "ai": {
                        "model": "gpt-4",
                        "max_tokens": 1000
                    },
                    "notifications": {
                        "line_notify_enabled": False,
                        "email_enabled": False
                    }
                }
                self._save_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"設定読み込みエラー: {e}")
            return {}
    
    def _save_config(self, config: Dict):
        """設定ファイルの保存"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"設定保存エラー: {e}")
    
    def save_sensor_data(self, data: Dict):
        """センサーデータの保存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sensor_data 
                    (timestamp, temperature, humidity, soil_moisture, tank_level, sensor_status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    data.get('timestamp'),
                    data.get('temperature'),
                    data.get('humidity'),
                    data.get('soil_moisture'),
                    data.get('tank_level'),
                    json.dumps(data.get('sensor_status', {}))
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"センサーデータ保存エラー: {e}")
    
    def save_watering_history(self, data: Dict):
        """給水履歴の保存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO watering_history 
                    (timestamp, amount, duration, success, reason)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    data.get('timestamp'),
                    data.get('amount'),
                    data.get('duration'),
                    data.get('success'),
                    data.get('reason')
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"給水履歴保存エラー: {e}")
    
    def save_camera_history(self, data: Dict):
        """カメラ撮影履歴の保存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO camera_history 
                    (timestamp, camera_id, layer, file_path, success)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    data.get('timestamp'),
                    data.get('camera_id'),
                    data.get('layer'),
                    data.get('file_path'),
                    data.get('success')
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"カメラ履歴保存エラー: {e}")
    
    def save_ai_consultation_history(self, data: Dict):
        """AI相談履歴の保存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ai_consultation_history 
                    (timestamp, question, answer, tag, confidence, model)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    data.get('timestamp'),
                    data.get('question'),
                    data.get('answer'),
                    data.get('tag'),
                    data.get('confidence'),
                    data.get('model')
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"AI相談履歴保存エラー: {e}")
    
    def save_notification_history(self, data: Dict):
        """通知履歴の保存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO notification_history 
                    (timestamp, type, title, message, channel, success)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    data.get('timestamp'),
                    data.get('type'),
                    data.get('title'),
                    data.get('message'),
                    data.get('channel'),
                    data.get('success')
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"通知履歴保存エラー: {e}")
    
    def get_sensor_data(self, hours: int = 24) -> List[Dict]:
        """センサーデータの取得"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
                
                cursor.execute("""
                    SELECT * FROM sensor_data 
                    WHERE timestamp >= ? 
                    ORDER BY timestamp DESC
                """, (cutoff_time,))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"センサーデータ取得エラー: {e}")
            return []
    
    def get_watering_history(self, days: int = 7) -> List[Dict]:
        """給水履歴の取得"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
                
                cursor.execute("""
                    SELECT * FROM watering_history 
                    WHERE timestamp >= ? 
                    ORDER BY timestamp DESC
                """, (cutoff_time,))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"給水履歴取得エラー: {e}")
            return []
    
    def get_camera_history(self, days: int = 7) -> List[Dict]:
        """カメラ撮影履歴の取得"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
                
                cursor.execute("""
                    SELECT * FROM camera_history 
                    WHERE timestamp >= ? 
                    ORDER BY timestamp DESC
                """, (cutoff_time,))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"カメラ履歴取得エラー: {e}")
            return []
    
    def get_ai_consultation_history(self, days: int = 7) -> List[Dict]:
        """AI相談履歴の取得"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
                
                cursor.execute("""
                    SELECT * FROM ai_consultation_history 
                    WHERE timestamp >= ? 
                    ORDER BY timestamp DESC
                """, (cutoff_time,))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"AI相談履歴取得エラー: {e}")
            return []
    
    def get_statistics(self, days: int = 7) -> Dict:
        """統計データの計算"""
        try:
            stats = {}
            
            # センサーデータ統計
            sensor_data = self.get_sensor_data(hours=days*24)
            if sensor_data:
                temperatures = [d['temperature'] for d in sensor_data if d['temperature']]
                humidities = [d['humidity'] for d in sensor_data if d['humidity']]
                soil_moistures = [d['soil_moisture'] for d in sensor_data if d['soil_moisture']]
                
                stats['sensors'] = {
                    'temperature': {
                        'avg': sum(temperatures) / len(temperatures) if temperatures else 0,
                        'min': min(temperatures) if temperatures else 0,
                        'max': max(temperatures) if temperatures else 0
                    },
                    'humidity': {
                        'avg': sum(humidities) / len(humidities) if humidities else 0,
                        'min': min(humidities) if humidities else 0,
                        'max': max(humidities) if humidities else 0
                    },
                    'soil_moisture': {
                        'avg': sum(soil_moistures) / len(soil_moistures) if soil_moistures else 0,
                        'min': min(soil_moistures) if soil_moistures else 0,
                        'max': max(soil_moistures) if soil_moistures else 0
                    }
                }
            
            # 給水統計
            watering_data = self.get_watering_history(days)
            if watering_data:
                total_amount = sum(d['amount'] for d in watering_data if d['amount'])
                successful_waterings = sum(1 for d in watering_data if d['success'])
                
                stats['watering'] = {
                    'total_amount': total_amount,
                    'total_count': len(watering_data),
                    'successful_count': successful_waterings,
                    'success_rate': successful_waterings / len(watering_data) if watering_data else 0
                }
            
            # カメラ統計
            camera_data = self.get_camera_history(days)
            if camera_data:
                successful_captures = sum(1 for d in camera_data if d['success'])
                
                stats['camera'] = {
                    'total_captures': len(camera_data),
                    'successful_captures': successful_captures,
                    'success_rate': successful_captures / len(camera_data) if camera_data else 0
                }
            
            # AI相談統計
            ai_data = self.get_ai_consultation_history(days)
            if ai_data:
                stats['ai_consultation'] = {
                    'total_consultations': len(ai_data),
                    'avg_confidence': sum(d['confidence'] for d in ai_data if d['confidence']) / len(ai_data) if ai_data else 0
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"統計データ計算エラー: {e}")
            return {}
    
    def export_data(self, file_path: str, data_type: str = "all", days: int = 30):
        """データのエクスポート"""
        try:
            export_data = {}
            
            if data_type in ["all", "sensors"]:
                export_data["sensor_data"] = self.get_sensor_data(hours=days*24)
            
            if data_type in ["all", "watering"]:
                export_data["watering_history"] = self.get_watering_history(days)
            
            if data_type in ["all", "camera"]:
                export_data["camera_history"] = self.get_camera_history(days)
            
            if data_type in ["all", "ai"]:
                export_data["ai_consultation_history"] = self.get_ai_consultation_history(days)
            
            if data_type in ["all", "config"]:
                export_data["config"] = self.config
            
            # ファイルに保存
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"データエクスポート完了: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"データエクスポートエラー: {e}")
            return False
    
    def import_data(self, file_path: str) -> bool:
        """データのインポート"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 設定のインポート
            if "config" in import_data:
                self.config.update(import_data["config"])
                self._save_config(self.config)
            
            # その他のデータは個別に処理
            # 実際の実装では、データの整合性チェックが必要
            
            logger.info(f"データインポート完了: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"データインポートエラー: {e}")
            return False
    
    def get_config(self) -> Dict:
        """設定の取得"""
        return self.config.copy()
    
    def update_config(self, new_config: Dict):
        """設定の更新"""
        self.config.update(new_config)
        self._save_config(self.config)
        logger.info("設定を更新しました")
    
    def cleanup_old_data(self, days: int = 90):
        """古いデータの削除"""
        try:
            cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 各テーブルから古いデータを削除
                tables = [
                    "sensor_data",
                    "watering_history", 
                    "camera_history",
                    "ai_consultation_history",
                    "notification_history"
                ]
                
                for table in tables:
                    cursor.execute(f"DELETE FROM {table} WHERE timestamp < ?", (cutoff_time,))
                
                conn.commit()
            
            logger.info(f"{days}日以前のデータを削除しました")
            
        except Exception as e:
            logger.error(f"データクリーンアップエラー: {e}")


# グローバルインスタンス
data_manager = DataManager()
