# 豆苗プランター - 多層化カメラ管理

"""
豆苗栽培の多層化に対応したカメラ管理システム
複数カメラの管理、階層別撮影制御、スケジュール管理
"""

import cv2
import os
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import schedule


class MultiCameraManager:
    """多層化カメラマネージャー"""
    
    def __init__(self):
        """多層化カメラマネージャーの初期化"""
        self.logger = logging.getLogger("multi_camera_manager")
        
        # カメラ管理
        self.cameras = {}
        self.camera_configs = self._load_camera_configs()
        
        # 撮影設定
        self.image_width = int(os.getenv('CAMERA_RESOLUTION_WIDTH', 1280))
        self.image_height = int(os.getenv('CAMERA_RESOLUTION_HEIGHT', 720))
        self.save_dir = "plant_images"
        
        # スケジュール管理
        self.schedules = {}
        self.schedule_thread = None
        self.schedule_running = False
        
        # ディレクトリ作成
        self._create_directories()
        
        # 既存カメラの初期化
        self._initialize_existing_cameras()
    
    def _load_camera_configs(self) -> Dict[str, Any]:
        """カメラ設定を読み込み"""
        config_file = Path("config/camera_configs.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"カメラ設定読み込みエラー: {str(e)}")
        
        return {}
    
    def _save_camera_configs(self):
        """カメラ設定を保存"""
        try:
            config_file = Path("config/camera_configs.json")
            config_file.parent.mkdir(exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.camera_configs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"カメラ設定保存エラー: {str(e)}")
    
    def _create_directories(self):
        """必要なディレクトリを作成"""
        directories = [
            self.save_dir,
            "config",
            "logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def _initialize_existing_cameras(self):
        """既存のカメラ設定を初期化"""
        for camera_id, config in self.camera_configs.items():
            try:
                self.add_camera(
                    camera_id=camera_id,
                    camera_index=config['index'],
                    layer=config['layer'],
                    enabled=config.get('enabled', True)
                )
            except Exception as e:
                self.logger.error(f"カメラ {camera_id} 初期化エラー: {str(e)}")
    
    def add_camera(self, camera_id: str, camera_index: int, layer: int, enabled: bool = True) -> bool:
        """カメラをシステムに追加"""
        try:
            # カメラの存在確認
            if not self._test_camera(camera_index):
                self.logger.warning(f"カメラ {camera_index} が見つかりません")
                return False
            
            # カメラ情報を追加
            self.cameras[camera_id] = {
                'index': camera_index,
                'layer': layer,
                'enabled': enabled,
                'last_capture': None,
                'capture_count': 0,
                'error_count': 0,
                'status': 'active' if enabled else 'disabled'
            }
            
            # 設定ファイルに保存
            self.camera_configs[camera_id] = {
                'index': camera_index,
                'layer': layer,
                'enabled': enabled,
                'added_at': datetime.now().isoformat()
            }
            self._save_camera_configs()
            
            self.logger.info(f"カメラ {camera_id} を追加しました (階層: {layer}, インデックス: {camera_index})")
            return True
            
        except Exception as e:
            self.logger.error(f"カメラ追加エラー: {str(e)}")
            return False
    
    def remove_camera(self, camera_id: str) -> bool:
        """カメラをシステムから削除"""
        try:
            if camera_id in self.cameras:
                del self.cameras[camera_id]
                
            if camera_id in self.camera_configs:
                del self.camera_configs[camera_id]
                self._save_camera_configs()
            
            self.logger.info(f"カメラ {camera_id} を削除しました")
            return True
            
        except Exception as e:
            self.logger.error(f"カメラ削除エラー: {str(e)}")
            return False
    
    def enable_camera(self, camera_id: str) -> bool:
        """カメラを有効化"""
        try:
            if camera_id in self.cameras:
                self.cameras[camera_id]['enabled'] = True
                self.cameras[camera_id]['status'] = 'active'
                
                if camera_id in self.camera_configs:
                    self.camera_configs[camera_id]['enabled'] = True
                    self._save_camera_configs()
                
                self.logger.info(f"カメラ {camera_id} を有効化しました")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"カメラ有効化エラー: {str(e)}")
            return False
    
    def disable_camera(self, camera_id: str) -> bool:
        """カメラを無効化"""
        try:
            if camera_id in self.cameras:
                self.cameras[camera_id]['enabled'] = False
                self.cameras[camera_id]['status'] = 'disabled'
                
                if camera_id in self.camera_configs:
                    self.camera_configs[camera_id]['enabled'] = False
                    self._save_camera_configs()
                
                self.logger.info(f"カメラ {camera_id} を無効化しました")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"カメラ無効化エラー: {str(e)}")
            return False
    
    def capture_layer(self, layer: int) -> List[Dict[str, Any]]:
        """指定階層の撮影を実行"""
        try:
            # 指定階層のカメラを取得
            layer_cameras = {
                cam_id: config for cam_id, config in self.cameras.items()
                if config['layer'] == layer and config['enabled']
            }
            
            if not layer_cameras:
                self.logger.warning(f"階層 {layer} に有効なカメラがありません")
                return []
            
            results = []
            for camera_id, config in layer_cameras.items():
                result = self._capture_single_camera(camera_id, config)
                results.append(result)
            
            self.logger.info(f"階層 {layer} の撮影完了: {len(results)} 台")
            return results
            
        except Exception as e:
            self.logger.error(f"階層撮影エラー: {str(e)}")
            return []
    
    def capture_all_layers(self) -> Dict[int, List[Dict[str, Any]]]:
        """全階層の撮影を実行"""
        try:
            all_results = {}
            
            # 各階層のカメラを取得
            layers = set(config['layer'] for config in self.cameras.values() if config['enabled'])
            
            for layer in layers:
                results = self.capture_layer(layer)
                all_results[layer] = results
            
            self.logger.info(f"全階層撮影完了: {len(layers)} 階層")
            return all_results
            
        except Exception as e:
            self.logger.error(f"全階層撮影エラー: {str(e)}")
            return {}
    
    def _capture_single_camera(self, camera_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """単一カメラの撮影を実行"""
        try:
            camera_index = config['index']
            layer = config['layer']
            
            # カメラを開く
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                raise Exception(f"カメラ {camera_index} を開けませんでした")
            
            # 解像度設定
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.image_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.image_height)
            
            # フレーム取得
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                raise Exception("フレームを読み込めませんでした")
            
            # ファイル名生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_L{layer}_{camera_id}.jpg"
            filepath = os.path.join(self.save_dir, filename)
            
            # 画像保存
            cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            # カメラ情報更新
            self.cameras[camera_id]['last_capture'] = datetime.now().isoformat()
            self.cameras[camera_id]['capture_count'] += 1
            self.cameras[camera_id]['error_count'] = 0
            
            result = {
                'camera_id': camera_id,
                'layer': layer,
                'image_path': filepath,
                'filename': filename,
                'timestamp': datetime.now().isoformat(),
                'success': True,
                'file_size': os.path.getsize(filepath)
            }
            
            self.logger.info(f"カメラ {camera_id} 撮影成功: {filename}")
            return result
            
        except Exception as e:
            # エラーカウント増加
            self.cameras[camera_id]['error_count'] += 1
            
            # エラーが多すぎる場合は無効化
            if self.cameras[camera_id]['error_count'] >= 5:
                self.disable_camera(camera_id)
                self.logger.error(f"カメラ {camera_id} を無効化しました（エラー回数: {self.cameras[camera_id]['error_count']}）")
            
            self.logger.error(f"カメラ {camera_id} 撮影エラー: {str(e)}")
            return {
                'camera_id': camera_id,
                'layer': config['layer'],
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }
    
    def schedule_capture(self, schedule_config: Dict[str, Any]) -> Dict[str, Any]:
        """撮影スケジュールを設定"""
        try:
            schedule_id = f"schedule_{int(time.time())}"
            
            # スケジュール情報を保存
            self.schedules[schedule_id] = {
                'id': schedule_id,
                'layers': schedule_config.get('layers', []),
                'times': schedule_config.get('times', []),
                'enabled': schedule_config.get('enabled', True),
                'created_at': datetime.now().isoformat()
            }
            
            # スケジュールジョブを設定
            if schedule_config.get('enabled', True):
                self._setup_schedule_jobs(schedule_id, schedule_config)
            
            self.logger.info(f"撮影スケジュール設定完了: {schedule_id}")
            return {
                'status': 'success',
                'schedule_id': schedule_id,
                'message': '撮影スケジュールを設定しました'
            }
            
        except Exception as e:
            self.logger.error(f"スケジュール設定エラー: {str(e)}")
            return {
                'status': 'error',
                'message': f'スケジュール設定に失敗しました: {str(e)}'
            }
    
    def _setup_schedule_jobs(self, schedule_id: str, config: Dict[str, Any]):
        """スケジュールジョブを設定"""
        try:
            layers = config.get('layers', [])
            times = config.get('times', [])
            
            for time_str in times:
                # 各時刻にスケジュールを設定
                schedule.every().day.at(time_str).do(
                    self._execute_scheduled_capture,
                    schedule_id=schedule_id,
                    layers=layers
                )
            
            # スケジューラースレッドを開始
            if not self.schedule_running:
                self.start_scheduler()
                
        except Exception as e:
            self.logger.error(f"スケジュールジョブ設定エラー: {str(e)}")
    
    def _execute_scheduled_capture(self, schedule_id: str, layers: List[int]):
        """スケジュール撮影を実行"""
        try:
            self.logger.info(f"スケジュール撮影実行: {schedule_id}")
            
            for layer in layers:
                results = self.capture_layer(layer)
                self.logger.info(f"階層 {layer} スケジュール撮影完了: {len(results)} 台")
                
        except Exception as e:
            self.logger.error(f"スケジュール撮影エラー: {str(e)}")
    
    def start_scheduler(self):
        """スケジューラーを開始"""
        if not self.schedule_running:
            self.schedule_running = True
            self.schedule_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.schedule_thread.start()
            self.logger.info("スケジューラーを開始しました")
    
    def stop_scheduler(self):
        """スケジューラーを停止"""
        self.schedule_running = False
        if self.schedule_thread:
            self.schedule_thread.join(timeout=5)
        self.logger.info("スケジューラーを停止しました")
    
    def _scheduler_loop(self):
        """スケジューラーループ"""
        while self.schedule_running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"スケジューラーループエラー: {str(e)}")
                time.sleep(5)
    
    def get_camera_status(self) -> Dict[str, Any]:
        """全カメラの状態を取得"""
        try:
            active_cameras = sum(1 for config in self.cameras.values() if config['enabled'])
            total_cameras = len(self.cameras)
            
            camera_list = []
            for camera_id, config in self.cameras.items():
                camera_info = {
                    'camera_id': camera_id,
                    'layer': config['layer'],
                    'index': config['index'],
                    'status': config['status'],
                    'last_capture': config['last_capture'],
                    'capture_count': config['capture_count'],
                    'error_count': config['error_count']
                }
                camera_list.append(camera_info)
            
            return {
                'total_cameras': total_cameras,
                'active_cameras': active_cameras,
                'disabled_cameras': total_cameras - active_cameras,
                'cameras': camera_list,
                'schedules': list(self.schedules.keys())
            }
            
        except Exception as e:
            self.logger.error(f"カメラ状態取得エラー: {str(e)}")
            return {'error': str(e)}
    
    def get_layer_cameras(self, layer: int) -> List[Dict[str, Any]]:
        """指定階層のカメラ情報を取得"""
        try:
            layer_cameras = []
            for camera_id, config in self.cameras.items():
                if config['layer'] == layer:
                    layer_cameras.append({
                        'camera_id': camera_id,
                        'index': config['index'],
                        'enabled': config['enabled'],
                        'status': config['status'],
                        'last_capture': config['last_capture']
                    })
            return layer_cameras
            
        except Exception as e:
            self.logger.error(f"階層カメラ取得エラー: {str(e)}")
            return []
    
    def _test_camera(self, camera_index: int) -> bool:
        """カメラの存在確認"""
        try:
            cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                ret, _ = cap.read()
                cap.release()
                return ret
            return False
        except Exception:
            return False
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        try:
            self.stop_scheduler()
            self.logger.info("多層化カメラマネージャーをクリーンアップしました")
        except Exception as e:
            self.logger.error(f"クリーンアップエラー: {str(e)}")

