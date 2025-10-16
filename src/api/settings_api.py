# 豆苗プランター - 設定API

"""
設定管理API
- システム設定
- センサー設定
- 給水設定
- カメラ設定
- AI設定
- 通知設定
"""

from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api
import logging
import os
from datetime import datetime

# データ管理モジュールのインポート
from src.data.data_manager import data_manager
from src.notifications.notification_manager import notification_manager

settings_bp = Blueprint('settings', __name__)
api = Api(settings_bp)
logger = logging.getLogger(__name__)


class SettingsResource(Resource):
    """設定管理"""
    
    def get(self):
        try:
            config = data_manager.get_config()
            
            # 機密情報をマスク
            safe_config = config.copy()
            if 'notifications' in safe_config:
                if 'line_notify_token' in safe_config['notifications']:
                    safe_config['notifications']['line_notify_token'] = '***'
                if 'email_password' in safe_config['notifications']:
                    safe_config['notifications']['email_password'] = '***'
            
            return {
                "status": "success",
                "data": safe_config
            }, 200
        except Exception as e:
            logger.error(f"設定取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500
    
    def post(self):
        try:
            data = request.get_json()
            
            if not data:
                return {"status": "error", "message": "設定データが必要です"}, 400
            
            # 設定更新
            data_manager.update_config(data)
            
            return {
                "status": "success",
                "message": "設定を更新しました"
            }, 200
        except Exception as e:
            logger.error(f"設定更新エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class SettingsSensorsResource(Resource):
    """センサー設定"""
    
    def get(self):
        try:
            config = data_manager.get_config()
            sensor_config = config.get('sensors', {})
            
            return {
                "status": "success",
                "data": sensor_config
            }, 200
        except Exception as e:
            logger.error(f"センサー設定取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500
    
    def post(self):
        try:
            data = request.get_json()
            
            if not data:
                return {"status": "error", "message": "センサー設定データが必要です"}, 400
            
            # 設定更新
            config = data_manager.get_config()
            config['sensors'] = data
            data_manager.update_config(config)
            
            return {
                "status": "success",
                "message": "センサー設定を更新しました"
            }, 200
        except Exception as e:
            logger.error(f"センサー設定更新エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class SettingsWateringResource(Resource):
    """給水設定"""
    
    def get(self):
        try:
            config = data_manager.get_config()
            watering_config = config.get('watering', {})
            
            return {
                "status": "success",
                "data": watering_config
            }, 200
        except Exception as e:
            logger.error(f"給水設定取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500
    
    def post(self):
        try:
            data = request.get_json()
            
            if not data:
                return {"status": "error", "message": "給水設定データが必要です"}, 400
            
            # 設定更新
            config = data_manager.get_config()
            config['watering'] = data
            data_manager.update_config(config)
            
            return {
                "status": "success",
                "message": "給水設定を更新しました"
            }, 200
        except Exception as e:
            logger.error(f"給水設定更新エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class SettingsCameraResource(Resource):
    """カメラ設定"""
    
    def get(self):
        try:
            config = data_manager.get_config()
            camera_config = config.get('camera', {})
            
            return {
                "status": "success",
                "data": camera_config
            }, 200
        except Exception as e:
            logger.error(f"カメラ設定取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500
    
    def post(self):
        try:
            data = request.get_json()
            
            if not data:
                return {"status": "error", "message": "カメラ設定データが必要です"}, 400
            
            # 設定更新
            config = data_manager.get_config()
            config['camera'] = data
            data_manager.update_config(config)
            
            return {
                "status": "success",
                "message": "カメラ設定を更新しました"
            }, 200
        except Exception as e:
            logger.error(f"カメラ設定更新エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class SettingsAIResource(Resource):
    """AI設定"""
    
    def get(self):
        try:
            config = data_manager.get_config()
            ai_config = config.get('ai', {})
            
            # APIキーはマスク
            if 'api_keys' in ai_config:
                masked_keys = {}
                for key, value in ai_config['api_keys'].items():
                    if value:
                        masked_keys[key] = '***'
                    else:
                        masked_keys[key] = ''
                ai_config['api_keys'] = masked_keys
            
            return {
                "status": "success",
                "data": ai_config
            }, 200
        except Exception as e:
            logger.error(f"AI設定取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500
    
    def post(self):
        try:
            data = request.get_json()
            
            if not data:
                return {"status": "error", "message": "AI設定データが必要です"}, 400
            
            # 設定更新
            config = data_manager.get_config()
            config['ai'] = data
            data_manager.update_config(config)
            
            # 環境変数も更新
            if 'api_keys' in data:
                for key, value in data['api_keys'].items():
                    if value and value != '***':
                        os.environ[f"{key.upper()}_API_KEY"] = value
            
            return {
                "status": "success",
                "message": "AI設定を更新しました"
            }, 200
        except Exception as e:
            logger.error(f"AI設定更新エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class SettingsNotificationsResource(Resource):
    """通知設定"""
    
    def get(self):
        try:
            config = data_manager.get_config()
            notification_config = config.get('notifications', {})
            
            # 機密情報をマスク
            if 'line_notify_token' in notification_config:
                notification_config['line_notify_token'] = '***'
            if 'email_password' in notification_config:
                notification_config['email_password'] = '***'
            
            return {
                "status": "success",
                "data": notification_config
            }, 200
        except Exception as e:
            logger.error(f"通知設定取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500
    
    def post(self):
        try:
            data = request.get_json()
            
            if not data:
                return {"status": "error", "message": "通知設定データが必要です"}, 400
            
            # 設定更新
            config = data_manager.get_config()
            config['notifications'] = data
            data_manager.update_config(config)
            
            # 通知マネージャーの設定も更新
            if 'line_notify_token' in data and data['line_notify_token'] != '***':
                notification_manager.configure_line_notify(data['line_notify_token'])
            
            if 'email_enabled' in data and data['email_enabled']:
                notification_manager.configure_email(
                    smtp_server=data.get('smtp_server', ''),
                    smtp_port=data.get('smtp_port', 587),
                    username=data.get('email_username', ''),
                    password=data.get('email_password', ''),
                    from_email=data.get('from_email', ''),
                    to_emails=data.get('to_emails', [])
                )
            
            return {
                "status": "success",
                "message": "通知設定を更新しました"
            }, 200
        except Exception as e:
            logger.error(f"通知設定更新エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class SettingsExportResource(Resource):
    """設定エクスポート"""
    
    def get(self):
        try:
            config = data_manager.get_config()
            
            # エクスポートファイル名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bean_sprout_config_{timestamp}.json"
            
            return {
                "status": "success",
                "data": {
                    "config": config,
                    "filename": filename,
                    "exported_at": datetime.now().isoformat()
                }
            }, 200
        except Exception as e:
            logger.error(f"設定エクスポートエラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class SettingsImportResource(Resource):
    """設定インポート"""
    
    def post(self):
        try:
            data = request.get_json()
            
            if not data or 'config' not in data:
                return {"status": "error", "message": "設定データが必要です"}, 400
            
            # 設定インポート
            success = data_manager.import_data_from_dict(data['config'])
            
            if success:
                return {
                    "status": "success",
                    "message": "設定をインポートしました"
                }, 200
            else:
                return {"status": "error", "message": "設定のインポートに失敗しました"}, 500
                
        except Exception as e:
            logger.error(f"設定インポートエラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class SettingsResetResource(Resource):
    """設定リセット"""
    
    def post(self):
        try:
            data = request.get_json() or {}
            reset_type = data.get('type', 'all')  # 'all', 'sensors', 'watering', 'camera', 'ai', 'notifications'
            
            config = data_manager.get_config()
            
            if reset_type == 'all':
                # 全設定をリセット
                data_manager.update_config({})
            else:
                # 特定の設定をリセット
                if reset_type in config:
                    del config[reset_type]
                    data_manager.update_config(config)
            
            return {
                "status": "success",
                "message": f"{reset_type}設定をリセットしました"
            }, 200
        except Exception as e:
            logger.error(f"設定リセットエラー: {e}")
            return {"status": "error", "message": str(e)}, 500


# APIエンドポイントの登録
api.add_resource(SettingsResource, '/')
api.add_resource(SettingsSensorsResource, '/sensors')
api.add_resource(SettingsWateringResource, '/watering')
api.add_resource(SettingsCameraResource, '/camera')
api.add_resource(SettingsAIResource, '/ai')
api.add_resource(SettingsNotificationsResource, '/notifications')
api.add_resource(SettingsExportResource, '/export')
api.add_resource(SettingsImportResource, '/import')
api.add_resource(SettingsResetResource, '/reset')
