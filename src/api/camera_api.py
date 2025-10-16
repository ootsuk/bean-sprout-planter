# 豆苗プランター - カメラAPI

"""
カメラ制御API
- 多層化カメラ管理
- 撮影制御
- 画像管理
"""

from flask import Blueprint, request, jsonify, send_file
from flask_restful import Resource, Api
import logging
import os
from datetime import datetime
from pathlib import Path

# カメラ管理モジュールのインポート
from src.camera.multi_camera_manager import MultiCameraManager
from src.data.data_manager import data_manager

camera_bp = Blueprint('camera', __name__)
api = Api(camera_bp)
logger = logging.getLogger(__name__)

# カメラマネージャーのインスタンス化
camera_manager = MultiCameraManager()
logger.info("カメラマネージャー初期化成功")


class CameraListResource(Resource):
    """カメラ一覧取得"""
    
    def get(self):
        try:
            cameras = camera_manager.get_all_cameras()
            return {
                "status": "success",
                "data": {
                    "cameras": cameras,
                    "total_count": len(cameras),
                    "active_count": len([c for c in cameras if c.get('enabled', False)])
                }
            }, 200
        except Exception as e:
            logger.error(f"カメラ一覧取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class CameraAddResource(Resource):
    """カメラ追加"""
    
    def post(self):
        try:
            data = request.get_json()
            camera_index = data.get('camera_index')
            layer = data.get('layer', 1)
            
            if camera_index is None:
                return {"status": "error", "message": "camera_indexが必要です"}, 400
            
            result = camera_manager.add_camera(camera_index, layer)
            
            if result['success']:
                return {
                    "status": "success",
                    "data": {
                        "camera_id": result['camera_id'],
                        "message": "カメラを追加しました"
                    }
                }, 201
            else:
                return {"status": "error", "message": result['error']}, 400
                
        except Exception as e:
            logger.error(f"カメラ追加エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class CameraRemoveResource(Resource):
    """カメラ削除"""
    
    def delete(self, camera_id):
        try:
            result = camera_manager.remove_camera(camera_id)
            
            if result['success']:
                return {
                    "status": "success",
                    "message": "カメラを削除しました"
                }, 200
            else:
                return {"status": "error", "message": result['error']}, 400
                
        except Exception as e:
            logger.error(f"カメラ削除エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class CameraCaptureResource(Resource):
    """カメラ撮影"""
    
    def post(self):
        try:
            data = request.get_json() or {}
            camera_id = data.get('camera_id')
            layer = data.get('layer')
            
            if camera_id:
                # 特定のカメラで撮影
                result = camera_manager.capture_by_camera_id(camera_id)
            elif layer:
                # 特定の階層で撮影
                result = camera_manager.capture_by_layer(layer)
            else:
                # 全カメラで撮影
                result = camera_manager.capture_all_layers()
            
            if result['success']:
                # 撮影履歴を保存
                for capture in result['captures']:
                    data_manager.save_camera_history({
                        'timestamp': datetime.now().isoformat(),
                        'camera_id': capture.get('camera_id'),
                        'layer': capture.get('layer'),
                        'file_path': capture.get('file_path'),
                        'success': capture.get('success', True)
                    })
                
                return {
                    "status": "success",
                    "data": {
                        "captures": result['captures'],
                        "message": "撮影が完了しました"
                    }
                }, 200
            else:
                return {"status": "error", "message": result['error']}, 400
                
        except Exception as e:
            logger.error(f"カメラ撮影エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class CameraImageResource(Resource):
    """画像取得"""
    
    def get(self, image_name):
        try:
            image_path = Path("plant_images") / image_name
            
            if not image_path.exists():
                return {"status": "error", "message": "画像が見つかりません"}, 404
            
            return send_file(str(image_path), mimetype='image/jpeg')
            
        except Exception as e:
            logger.error(f"画像取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class CameraHistoryResource(Resource):
    """撮影履歴取得"""
    
    def get(self):
        try:
            days = request.args.get('days', 7, type=int)
            camera_id = request.args.get('camera_id')
            layer = request.args.get('layer', type=int)
            
            history = data_manager.get_camera_history(days)
            
            # フィルタリング
            if camera_id:
                history = [h for h in history if h.get('camera_id') == camera_id]
            if layer:
                history = [h for h in history if h.get('layer') == layer]
            
            return {
                "status": "success",
                "data": {
                    "history": history,
                    "total_count": len(history)
                }
            }, 200
            
        except Exception as e:
            logger.error(f"撮影履歴取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class CameraScheduleResource(Resource):
    """撮影スケジュール管理"""
    
    def get(self):
        try:
            schedules = camera_manager.get_schedules()
            return {
                "status": "success",
                "data": {
                    "schedules": schedules
                }
            }, 200
        except Exception as e:
            logger.error(f"スケジュール取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500
    
    def post(self):
        try:
            data = request.get_json()
            time_str = data.get('time')
            layer = data.get('layer')
            enabled = data.get('enabled', True)
            
            if not time_str:
                return {"status": "error", "message": "timeが必要です"}, 400
            
            result = camera_manager.add_schedule(time_str, layer, enabled)
            
            if result['success']:
                return {
                    "status": "success",
                    "data": {
                        "schedule_id": result['schedule_id'],
                        "message": "スケジュールを追加しました"
                    }
                }, 201
            else:
                return {"status": "error", "message": result['error']}, 400
                
        except Exception as e:
            logger.error(f"スケジュール追加エラー: {e}")
            return {"status": "error", "message": str(e)}, 500
    
    def delete(self, schedule_id):
        try:
            result = camera_manager.remove_schedule(schedule_id)
            
            if result['success']:
                return {
                    "status": "success",
                    "message": "スケジュールを削除しました"
                }, 200
            else:
                return {"status": "error", "message": result['error']}, 400
                
        except Exception as e:
            logger.error(f"スケジュール削除エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


class CameraStatusResource(Resource):
    """カメラ状態取得"""
    
    def get(self):
        try:
            status = camera_manager.get_status()
            return {
                "status": "success",
                "data": status
            }, 200
        except Exception as e:
            logger.error(f"カメラ状態取得エラー: {e}")
            return {"status": "error", "message": str(e)}, 500


# APIエンドポイントの登録
api.add_resource(CameraListResource, '/list')
api.add_resource(CameraAddResource, '/add')
api.add_resource(CameraRemoveResource, '/remove/<string:camera_id>')
api.add_resource(CameraCaptureResource, '/capture')
api.add_resource(CameraImageResource, '/image/<string:image_name>')
api.add_resource(CameraHistoryResource, '/history')
api.add_resource(CameraScheduleResource, '/schedule', '/schedule/<string:schedule_id>')
api.add_resource(CameraStatusResource, '/status')
