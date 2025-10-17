# 豆苗プランター - APIブループリント統合管理

"""
全てのAPIブループリントを統合してFlaskアプリに登録
"""

from flask import Flask
from flask_restful import Api
from flask_cors import CORS

# APIブループリントのインポート
from src.api.ai_api import ai_bp
from src.api.sensors_api import sensors_bp
from src.api.watering_api import watering_bp
from src.api.camera_api import camera_bp
from src.api.settings_api import settings_bp


def register_api_blueprints(app: Flask):
    """APIブループリントをFlaskアプリに登録"""
    
    # CORS設定
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 各APIブループリントを登録
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(sensors_bp, url_prefix='/api/sensors')
    app.register_blueprint(watering_bp, url_prefix='/api/watering')
    app.register_blueprint(camera_bp, url_prefix='/api/camera')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    
    # 一時的なテスト用APIエンドポイント
    from flask_restful import Resource, Api
    
    # APIインスタンス作成
    api = Api(app, prefix='/api')
    
    class HealthCheckResource(Resource):
        """ヘルスチェックAPI"""
        def get(self):
            return {
                'status': 'healthy',
                'message': '豆苗プランターAPI稼働中',
                'version': '1.0.0'
            }
    
    class SystemStatusResource(Resource):
        """システム状態API"""
        def get(self):
            return {
                'status': 'running',
                'components': {
                    'ai_consultation': 'available',
                    'multi_camera': 'available',
                    'water_tank': 'available',
                    'sensors': 'not_implemented',
                    'notifications': 'not_implemented',
                    'api_layer': 'partial'
                },
                'environment': 'development'
            }

    class SensorsCurrentResource(Resource):
        """現在のセンサーデータAPI"""
        def get(self):
            import random
            return {
                'status': 'success',
                'data': {
                    'temperature': round(20 + random.random() * 10, 1),
                    'humidity': round(50 + random.random() * 30, 1),
                    'tank_level': round(60 + random.random() * 40, 1)
                }
            }

    class SensorsHistoryResource(Resource):
        """センサー履歴データAPI"""
        def get(self):
            import random
            from datetime import datetime, timedelta
            
            history = []
            now = datetime.now()
            
            for i in range(24):
                time = now - timedelta(hours=23-i)
                history.append({
                    'timestamp': time.isoformat(),
                    'temperature': round(20 + random.random() * 10, 1),
                    'humidity': round(50 + random.random() * 30, 1)
                })
            
            return {
                'status': 'success',
                'history': history
            }

    class AIHarvestJudgmentResource(Resource):
        """AI収穫判断API"""
        def post(self):
            import random
            return {
                'status': 'success',
                'harvest_ready': random.choice([True, False]),
                'confidence': round(0.6 + random.random() * 0.4, 2),
                'recommendation': '適度な水やりと日光浴を続けてください。',
                'days_remaining': random.randint(1, 7)
            }

    class CameraLatestResource(Resource):
        """最新画像API"""
        def get(self):
            return {
                'status': 'success',
                'image_url': '/static/images/placeholder.jpg'
            }
    
    # テスト用APIエンドポイントを登録
    api.add_resource(HealthCheckResource, '/health')
    api.add_resource(SystemStatusResource, '/status')
    api.add_resource(AIHarvestJudgmentResource, '/ai/harvest-judgment')
    api.add_resource(CameraLatestResource, '/camera/latest')
    
    print("✅ APIブループリントを登録しました")
