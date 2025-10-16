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
    
    # テスト用APIエンドポイントを登録
    api.add_resource(HealthCheckResource, '/health')
    api.add_resource(SystemStatusResource, '/status')
    
    print("✅ APIブループリントを登録しました")
