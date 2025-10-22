"""
センサー統合管理モジュール
全センサーの監視と管理を行う
"""

import threading
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from .temperature_humidity import AHT25Sensor
from .soil_moisture import SEN0193Sensor
from .float_switch import FloatSwitch


class SensorManager:
    """センサー管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger("sensor_manager")
        self.sensors = {}
        self.data_cache = {}
        self.running = False
        self.threads = {}
        
        # センサー初期化
        self._initialize_sensors()
        
    def _initialize_sensors(self):
        """センサーを初期化"""
        try:
            # 温湿度センサー
            self.sensors['temperature_humidity'] = AHT25Sensor()
            self.sensors['temperature_humidity'].initialize()
            
            # 土壌水分センサー
            self.sensors['soil_moisture'] = SEN0193Sensor(channel=0, vref=3.3)
            self.sensors['soil_moisture'].initialize()
            
            # フロートスイッチ
            self.sensors['water_level'] = FloatSwitch(pin=18)
            self.sensors['water_level'].initialize()
            
            self.logger.info("全センサー初期化完了")
            
        except Exception as e:
            self.logger.error(f"センサー初期化エラー: {str(e)}")
    
    def start_monitoring(self):
        """センサー監視開始"""
        if self.running:
            self.logger.warning("センサー監視は既に実行中です")
            return
        
        self.running = True
        self.logger.info("センサー監視を開始します")
        
        # 各センサーの監視スレッドを開始
        self.threads['monitor'] = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.threads['monitor'].start()
    
    def stop_monitoring(self):
        """センサー監視停止"""
        self.running = False
        self.logger.info("センサー監視を停止します")
        
        # スレッドの終了を待つ
        for thread_name, thread in self.threads.items():
            if thread.is_alive():
                thread.join(timeout=2.0)
    
    def _monitoring_loop(self):
        """センサー監視ループ"""
        while self.running:
            try:
                # 全センサーのデータを取得
                self.read_all_sensors()
                
                # 60秒待機
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"監視ループエラー: {str(e)}")
                time.sleep(10)
    
    def read_all_sensors_once(self) -> Dict[str, Any]:
        """全センサーのデータを一度だけ読み取る（スケジューラー用）"""
        try:
            results = {}
            
            for sensor_name, sensor in self.sensors.items():
                if sensor.is_enabled:
                    data = sensor.read_data()
                    results[sensor_name] = data
                    
                    # キャッシュに保存
                    self.data_cache[sensor_name] = {
                        'data': data,
                        'timestamp': time.time()
                    }
            
            # データベースに保存
            self._save_sensor_data_to_db(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"センサー読み取りエラー: {str(e)}")
            return {}
    
    def read_temperature_humidity_once(self) -> Dict[str, Any]:
        """温湿度センサーのみを読み取る（スケジューラー用）"""
        try:
            if 'temperature_humidity' in self.sensors:
                sensor = self.sensors['temperature_humidity']
                if sensor.is_enabled:
                    data = sensor.read_data()
                    self.data_cache['temperature_humidity'] = {
                        'data': data,
                        'timestamp': time.time()
                    }
                    
                    # データベースに保存
                    self._save_sensor_data_to_db({'temperature_humidity': data})
                    
                    return data
            
            return {}
            
        except Exception as e:
            self.logger.error(f"温湿度センサー読み取りエラー: {str(e)}")
            return {}
    
    def read_soil_moisture_once(self) -> Dict[str, Any]:
        """土壌水分センサーのみを読み取る（スケジューラー用）"""
        try:
            if 'soil_moisture' in self.sensors:
                sensor = self.sensors['soil_moisture']
                if sensor.is_enabled:
                    data = sensor.read_data()
                    self.data_cache['soil_moisture'] = {
                        'data': data,
                        'timestamp': time.time()
                    }
                    
                    # データベースに保存
                    self._save_sensor_data_to_db({'soil_moisture': data})
                    
                    return data
            
            return {}
            
        except Exception as e:
            self.logger.error(f"土壌水分センサー読み取りエラー: {str(e)}")
            return {}
    
    def _save_sensor_data_to_db(self, sensor_data: Dict[str, Any]):
        """センサーデータをデータベースに保存"""
        try:
            from src.data.data_manager import data_manager
            
            # 統合データを作成
            integrated_data = {
                'timestamp': datetime.now().isoformat(),
                'temperature': None,
                'humidity': None,
                'soil_moisture': None,
                'tank_level': None,
                'sensor_status': 'active'
            }
            
            # 各センサーのデータを統合
            for sensor_name, data in sensor_data.items():
                if sensor_name == 'temperature_humidity':
                    integrated_data['temperature'] = data.get('temperature')
                    integrated_data['humidity'] = data.get('humidity')
                elif sensor_name == 'soil_moisture':
                    integrated_data['soil_moisture'] = data.get('soil_moisture')
                elif sensor_name == 'water_level':
                    integrated_data['tank_level'] = data.get('tank_level')
            
            # データベースに保存
            data_manager.save_sensor_data(integrated_data)
            
        except Exception as e:
            self.logger.error(f"センサーデータ保存エラー: {str(e)}")
    
    def get_sensor_data(self, sensor_name: str = None) -> Optional[Dict[str, Any]]:
        """センサーデータを取得（キャッシュから）"""
        if sensor_name:
            return self.data_cache.get(sensor_name, {}).get('data')
        else:
            # 全センサーのデータを返す
            return {name: cache.get('data') for name, cache in self.data_cache.items()}
    
    def get_all_sensor_status(self) -> Dict[str, Any]:
        """全センサーの状態を取得"""
        status = {}
        for sensor_name, sensor in self.sensors.items():
            status[sensor_name] = sensor.get_status()
        return status
    
    def force_read(self, sensor_name: str) -> Dict[str, Any]:
        """指定センサーの強制読み取り"""
        if sensor_name in self.sensors:
            return self.sensors[sensor_name].read_data()
        return {"error": "センサーが見つかりません"}
    
    def get_latest_data(self) -> Dict[str, Any]:
        """最新のセンサーデータを統合して取得"""
        # 温湿度データ
        temp_hum_data = self.get_sensor_data('temperature_humidity') or {}
        
        # 土壌水分データ
        soil_data = self.get_sensor_data('soil_moisture') or {}
        
        # 水位データ
        water_data = self.get_sensor_data('water_level') or {}
        
        # 統合データ
        return {
            'temperature': temp_hum_data.get('temperature'),
            'humidity': temp_hum_data.get('humidity'),
            'soil_moisture': soil_data.get('raw_value'),
            'soil_moisture_percentage': soil_data.get('moisture_percentage'),
            'water_present': water_data.get('water_present'),
            'water_level': water_data.get('level'),
            'timestamp': time.time()
        }
    # グローバルインスタンス
sensor_manager = SensorManager()