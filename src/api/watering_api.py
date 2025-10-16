# 豆苗プランター - 給水API

"""
給水制御API
- 給水タンク管理
- 手動給水
- 自動給水設定
- 給水履歴
"""

from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api
import logging
from datetime import datetime

# 給水管理モジュールのインポート
from src.watering.water_tank_manager import WaterTankManager
from src.data.data_manager import data_manager
from src.notifications.notification_manager import notification_manager

watering_bp = Blueprint('watering', __name__)
api = Api(watering_bp)
logger = logging.getLogger(__name__)

# 給水タンクマネージャーのインスタンス化
water_tank_manager = WaterTankManager()
logger.info("給水タンクマネージャー初期化成功")


class WateringStatusResource(Resource):
    """給水状態取得"""
    
    def get(self):
        try:
            status = water_tank_manager.get_tank_status()
            return {
                "status": "success",
                "data": status
            }, 200
        except Exception as e:
            logger.error(f"給水状態取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class WateringManualResource(Resource):
    """手動給水"""
    
    def post(self):
        try:
            data = request.get_json() or {}
            amount = data.get('amount', 100)  # デフォルト100ml
            duration = data.get('duration', 5)  # デフォルト5秒
            
            # 給水実行
            result = water_tank_manager.water_plants(amount, duration)
            
            # 給水履歴を保存
            data_manager.save_watering_history({
                'timestamp': datetime.now().isoformat(),
                'amount': amount,
                'duration': duration,
                'success': result['success'],
                'reason': result.get('reason', '')
            })
            
            if result['success']:
                # 通知送信
                remaining = water_tank_manager.get_current_volume()
                notification_manager.notify_watering(amount, remaining)
                
                return {
                    "status": "success",
                    "data": {
                        "amount": amount,
                        "duration": duration,
                        "remaining_volume": remaining,
                        "message": "給水が完了しました"
                    }
                }, 200
            else:
                return {"status": "error", "message": result['error']}, 400
                
        except Exception as e:
            logger.error(f"手動給水エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class WateringAutoResource(Resource):
    """自動給水設定"""
    
    def get(self):
        try:
            config = water_tank_manager.get_auto_watering_config()
            return {
                "status": "success",
                "data": config
            }, 200
        except Exception as e:
            logger.error(f"自動給水設定取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500
    
    def post(self):
        try:
            data = request.get_json()
            
            # 設定更新
            result = water_tank_manager.update_auto_watering_config(data)
            
            if result['success']:
                return {
                    "status": "success",
                    "message": "自動給水設定を更新しました"
                }, 200
            else:
                return {"status": "error", "message": result['error']}, 400
                
        except Exception as e:
            logger.error(f"自動給水設定更新エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class WateringHistoryResource(Resource):
    """給水履歴取得"""
    
    def get(self):
        try:
            days = request.args.get('days', 7, type=int)
            history = data_manager.get_watering_history(days)
            
            return {
                "status": "success",
                "data": {
                    "history": history,
                    "total_count": len(history)
                }
            }, 200
        except Exception as e:
            logger.error(f"給水履歴取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class WateringTankRefillResource(Resource):
    """タンク補充"""
    
    def post(self):
        try:
            data = request.get_json() or {}
            amount = data.get('amount', 500)  # デフォルト500ml
            
            # タンク補充
            result = water_tank_manager.refill_tank(amount)
            
            if result['success']:
                return {
                    "status": "success",
                    "data": {
                        "refill_amount": amount,
                        "current_volume": result['current_volume'],
                        "message": "タンクを補充しました"
                    }
                }, 200
            else:
                return {"status": "error", "message": result['error']}, 400
                
        except Exception as e:
            logger.error(f"タンク補充エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class WateringTankConfigResource(Resource):
    """タンク設定"""
    
    def get(self):
        try:
            config = water_tank_manager.get_tank_config()
            return {
                "status": "success",
                "data": config
            }, 200
        except Exception as e:
            logger.error(f"タンク設定取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500
    
    def post(self):
        try:
            data = request.get_json()
            
            # 設定更新
            result = water_tank_manager.update_tank_config(data)
            
            if result['success']:
                return {
                    "status": "success",
                    "message": "タンク設定を更新しました"
                }, 200
            else:
                return {"status": "error", "message": result['error']}, 400
                
        except Exception as e:
            logger.error(f"タンク設定更新エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class WateringStatisticsResource(Resource):
    """給水統計"""
    
    def get(self):
        try:
            days = request.args.get('days', 7, type=int)
            stats = data_manager.get_statistics(days)
            
            watering_stats = stats.get('watering', {})
            
            return {
                "status": "success",
                "data": {
                    "period_days": days,
                    "total_amount": watering_stats.get('total_amount', 0),
                    "total_count": watering_stats.get('total_count', 0),
                    "successful_count": watering_stats.get('successful_count', 0),
                    "success_rate": watering_stats.get('success_rate', 0),
                    "average_amount": watering_stats.get('total_amount', 0) / max(watering_stats.get('total_count', 1), 1)
                }
            }, 200
        except Exception as e:
            logger.error(f"給水統計取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class WateringCheckResource(Resource):
    """給水必要性チェック"""
    
    def post(self):
        try:
            # 土壌水分センサーから現在の値を取得
            from src.sensors.sensor_manager import sensor_manager
            
            sensor_data = sensor_manager.read_all_sensors()
            current_moisture = sensor_data.soil_moisture
            
            # 給水が必要かチェック
            result = water_tank_manager.check_watering_needed(current_moisture)
            
            return {
                "status": "success",
                "data": {
                    "current_moisture": current_moisture,
                    "watering_needed": result['needed'],
                    "reason": result.get('reason', ''),
                    "recommended_amount": result.get('recommended_amount', 0)
                }
            }, 200
        except Exception as e:
            logger.error(f"給水必要性チェックエラー: {e}")
            return {"status": "error", "message": str(e)}, 500


# APIエンドポイントの登録
api.add_resource(WateringStatusResource, '/status')
api.add_resource(WateringManualResource, '/manual')
api.add_resource(WateringAutoResource, '/auto')
api.add_resource(WateringHistoryResource, '/history')
api.add_resource(WateringTankRefillResource, '/refill')
api.add_resource(WateringTankConfigResource, '/config')
api.add_resource(WateringStatisticsResource, '/statistics')
api.add_resource(WateringCheckResource, '/check')
