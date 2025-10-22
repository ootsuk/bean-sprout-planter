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
        self.db_path = self.data_dir / "main.db"
        
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
                        water_pressure REAL,
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
                
                # 設定テーブル
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                conn.commit()
                logger.info("データベース初期化完了")
                
                # 設定の移行処理を実行
                self._migrate_settings_to_database()
                
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
                        "water_pressure_interval": 300
                    },
                    "watering": {
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
                    (timestamp, temperature, humidity, water_pressure, sensor_status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    data.get('timestamp'),
                    data.get('temperature'),
                    data.get('humidity'),
                    data.get('water_pressure'),
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
                water_pressures = [d['water_pressure'] for d in sensor_data if d['water_pressure']]
                
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
                    'water_pressure': {
                        'avg': sum(water_pressures) / len(water_pressures) if water_pressures else 0,
                        'min': min(water_pressures) if water_pressures else 0,
                        'max': max(water_pressures) if water_pressures else 0
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
        """設定の取得（後方互換性のため残す）"""
        return self.get_settings()
    
    def update_config(self, new_config: Dict):
        """設定の更新（後方互換性のため残す）"""
        self.update_settings(new_config)
    
    def get_settings(self) -> Dict:
        """SQLiteから設定を取得"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM settings")
                rows = cursor.fetchall()
                
                if not rows:
                    # 初回起動時はconfig.jsonから移行
                    return self._migrate_from_config_json()
                
                settings = {}
                for key, value in rows:
                    settings[key] = json.loads(value)
                
                return settings
        except Exception as e:
            logger.error(f"設定取得エラー: {e}")
            return {}
    
    def update_settings(self, new_settings: Dict):
        """SQLiteに設定を更新"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                current_time = datetime.now().isoformat()
                
                for key, value in new_settings.items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO settings (key, value, updated_at)
                        VALUES (?, ?, ?)
                    """, (key, json.dumps(value), current_time))
                
                conn.commit()
                logger.info("設定をSQLiteに更新しました")
        except Exception as e:
            logger.error(f"設定更新エラー: {e}")
    
    def get_setting_section(self, section: str) -> Dict:
        """特定のセクションの設定を取得"""
        settings = self.get_settings()
        return settings.get(section, {})
    
    def _migrate_settings_to_database(self):
        """設定をデータベースに移行"""
        try:
            # settingsテーブルが空かチェック
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM settings")
                count = cursor.fetchone()[0]
                
                if count == 0:
                    logger.info("settingsテーブルが空のため、設定を移行します")
                    self._migrate_from_config_json()
                else:
                    logger.info("settingsテーブルに既にデータが存在します")
                    
        except Exception as e:
            logger.error(f"設定移行エラー: {e}")
    
    def _migrate_from_config_json(self) -> Dict:
        """config.jsonからSQLiteに移行"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # SQLiteに保存
                self.update_settings(config)
                
                # config.jsonをバックアップ
                backup_path = self.config_path.with_suffix('.json.bak')
                self.config_path.rename(backup_path)
                
                logger.info(f"config.jsonからSQLiteに移行完了: {backup_path}")
                return config
            else:
                # デフォルト設定を作成
                default_config = {
                    "sensors": {
                        "check_interval": 60,
                        "temperature_humidity_interval": 1800,
                        "water_pressure_interval": 300
                    },
                    "watering": {
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
                self.update_settings(default_config)
                return default_config
        except Exception as e:
            logger.error(f"設定移行エラー: {e}")
            return {}
    
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
