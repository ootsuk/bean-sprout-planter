# 豆苗プランター - センサーAPI

"""
センサー制御API
- センサーデータ取得
- センサー状態管理
- センサー設定
"""

from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api
import logging
from datetime import datetime

# センサー管理モジュールのインポート
from src.sensors.sensor_manager import SensorManager
from src.data.data_manager import data_manager

# センサーマネージャーのインスタンス化
sensor_manager = SensorManager()

sensors_bp = Blueprint('sensors', __name__)
api = Api(sensors_bp)
logger = logging.getLogger(__name__)


class SensorsDataResource(Resource):
    """センサーデータ取得"""
    
    def get(self):
        try:
            # 最新のセンサーデータを取得
            sensor_data = sensor_manager.get_latest_data()
            
            return {
                "status": "success",
                "data": sensor_data
            }, 200
        except Exception as e:
            logger.error(f"センサーデータ取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class SensorsHistoryResource(Resource):
    """センサーデータ履歴取得"""
    
    def get(self):
        try:
            hours = request.args.get('hours', 24, type=int)
            sensor_type = request.args.get('type')  # temperature, humidity, soil_moisture
            
            # データベースから履歴を取得
            history = data_manager.get_sensor_data(hours)
            
            # 特定のセンサータイプでフィルタリング
            if sensor_type:
                filtered_history = []
                for record in history:
                    if sensor_type in record and record[sensor_type] is not None:
                        filtered_history.append({
                            'timestamp': record['timestamp'],
                            'value': record[sensor_type]
                        })
                history = filtered_history
            
            return {
                "status": "success",
                "history": history,
                "total_count": len(history),
                "period_hours": hours
            }, 200
        except Exception as e:
            logger.error(f"センサーデータ履歴取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class SensorsStatusResource(Resource):
    """センサー状態取得"""
    
    def get(self):
        try:
            status = sensor_manager.get_all_sensor_status()
            
            return {
                "status": "success",
                "data": {
                    "sensors": status,
                    "total_sensors": len(status),
                    "active_sensors": len([s for s in status.values() if s.get('enabled', False)])
                }
            }, 200
        except Exception as e:
            logger.error(f"センサー状態取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class SensorsControlResource(Resource):
    """センサー制御"""
    
    def post(self):
        try:
            data = request.get_json()
            sensor_name = data.get('sensor_name')
            action = data.get('action')  # enable, disable
            
            if not sensor_name or not action:
                return {"status": "error", "message": "sensor_nameとactionが必要です"}, 400
            
            if action == 'enable':
                if sensor_name in sensor_manager.sensors:
                    sensor_manager.sensors[sensor_name].enable()
                    success = True
                else:
                    success = False
            elif action == 'disable':
                if sensor_name in sensor_manager.sensors:
                    sensor_manager.sensors[sensor_name].disable()
                    success = True
                else:
                    success = False
            else:
                return {"status": "error", "message": "actionはenableまたはdisableである必要があります"}, 400
            
            if success:
                return {
                    "status": "success",
                    "message": f"センサー {sensor_name} を{action}しました"
                }, 200
            else:
                return {"status": "error", "message": f"センサー {sensor_name} の制御に失敗しました"}, 400
                
        except Exception as e:
            logger.error(f"センサー制御エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class SensorsStatisticsResource(Resource):
    """センサー統計"""
    
    def get(self):
        try:
            days = request.args.get('days', 7, type=int)
            stats = data_manager.get_statistics(days)
            
            sensor_stats = stats.get('sensors', {})
            
            return {
                "status": "success",
                "data": {
                    "period_days": days,
                    "temperature": sensor_stats.get('temperature', {}),
                    "humidity": sensor_stats.get('humidity', {}),
                    "soil_moisture": sensor_stats.get('soil_moisture', {})
                }
            }, 200
        except Exception as e:
            logger.error(f"センサー統計取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class SensorsTestResource(Resource):
    """センサーテスト"""
    
    def post(self):
        try:
            data = request.get_json() or {}
            sensor_name = data.get('sensor_name')
            
            if sensor_name:
                # 特定のセンサーをテスト
                if sensor_name in sensor_manager.sensors:
                    sensor_data = sensor_manager.sensors[sensor_name].read_data()
                    result = {
                        'sensor': sensor_name,
                        'data': sensor_data,
                        'status': 'ok' if 'error' not in sensor_data else 'error'
                    }
                else:
                    return {"status": "error", "message": f"未知のセンサー: {sensor_name}"}, 400
            else:
                # 全センサーをテスト
                sensor_data = sensor_manager.get_latest_data()
                result = {
                    'all_sensors': True,
                    'data': sensor_data,
                    'status': 'ok'
                }
            
            return {
                "status": "success",
                "data": result
            }, 200
        except Exception as e:
            logger.error(f"センサーテストエラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class SensorsCalibrationResource(Resource):
    """センサーキャリブレーション"""
    
    def post(self):
        try:
            data = request.get_json()
            sensor_name = data.get('sensor_name')
            calibration_data = data.get('calibration_data', {})
            
            if not sensor_name:
                return {"status": "error", "message": "sensor_nameが必要です"}, 400
            
            # キャリブレーションデータの保存
            # 実際の実装では、キャリブレーションデータを設定ファイルに保存
            config = data_manager.get_config()
            if 'sensor_calibration' not in config:
                config['sensor_calibration'] = {}
            
            config['sensor_calibration'][sensor_name] = {
                'calibration_data': calibration_data,
                'calibrated_at': datetime.now().isoformat()
            }
            
            data_manager.update_config(config)
            
            return {
                "status": "success",
                "message": f"センサー {sensor_name} のキャリブレーションを完了しました"
            }, 200
        except Exception as e:
            logger.error(f"センサーキャリブレーションエラー: {e}")
            return {"status": "error", "message": str(e)}, 500


# APIエンドポイントの登録
api.add_resource(SensorsDataResource, '/data')
api.add_resource(SensorsHistoryResource, '/history')
api.add_resource(SensorsStatusResource, '/status')
api.add_resource(SensorsControlResource, '/control')
api.add_resource(SensorsStatisticsResource, '/statistics')
api.add_resource(SensorsTestResource, '/test')
api.add_resource(SensorsCalibrationResource, '/calibration')
