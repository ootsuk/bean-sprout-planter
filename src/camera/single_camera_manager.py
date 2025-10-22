# 豆苗プランター - 単一カメラ管理モジュール

"""
単一カメラを使用した撮影管理
- 自動撮影
- 手動撮影
- 設定に基づく解像度・保存先管理
"""

import cv2
import os
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class SingleCameraManager:
    """単一カメラ管理クラス"""
    
    def __init__(self):
        self.camera = None
        self.initialized = False
        self.data_manager = None
        self.image_dir = Path("data/images")
        self.image_dir.mkdir(parents=True, exist_ok=True)
        
    def initialize(self, data_manager):
        """カメラを初期化"""
        try:
            self.data_manager = data_manager
            
            # Raspberry Pi環境チェック
            if self._is_raspberry_pi():
                # Raspberry Pi環境でのみカメラ初期化
                try:
                    self.camera = cv2.VideoCapture(0)
                    if self.camera.isOpened():
                        self.initialized = True
                        logger.info("Raspberry Pi USBカメラ初期化完了")
                    else:
                        logger.warning("USBカメラが開けませんでした（ダミーモード）")
                        self.initialized = False
                except Exception as e:
                    logger.warning(f"USBカメラ初期化失敗（ダミーモード）: {e}")
                    self.initialized = False
            else:
                # 開発環境（macOS/Windows等）ではダミーモード
                logger.info("開発環境検出 - ダミーモードで動作")
                self.initialized = False
                
        except Exception as e:
            logger.error(f"カメラ管理初期化エラー: {e}")
            raise
    
    def _is_raspberry_pi(self) -> bool:
        """Raspberry Pi環境かどうかを判定"""
        try:
            # Raspberry Pi特有のファイルをチェック
            import os
            return os.path.exists('/proc/device-tree/model') and 'Raspberry Pi' in open('/proc/device-tree/model').read()
        except:
            return False
    
    def capture_once(self) -> Dict[str, Any]:
        """単発撮影実行"""
        try:
            logger.info("カメラ撮影を開始します")
            
            # 設定を取得
            camera_config = self.data_manager.get_setting_section('camera')
            resolution_width = camera_config.get('resolution_width', 1280)
            resolution_height = camera_config.get('resolution_height', 720)
            
            # 撮影実行
            result = self._capture_image(resolution_width, resolution_height)
            
            # 履歴保存
            if result['success']:
                self._save_camera_history(result)
            
            logger.info(f"カメラ撮影完了: {result['file_path']}")
            return result
            
        except Exception as e:
            logger.error(f"カメラ撮影エラー: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _capture_image(self, width: int, height: int) -> Dict[str, Any]:
        """実際の画像撮影"""
        timestamp = datetime.now()
        filename = f"capture_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
        file_path = self.image_dir / filename
        
        try:
            if not self.initialized or self.camera is None:
                # ダミーモード
                return self._create_dummy_image(file_path, width, height, timestamp)
            
            # カメラ設定
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # 撮影
            ret, frame = self.camera.read()
            
            if ret:
                # 画像保存
                cv2.imwrite(str(file_path), frame)
                
                return {
                    'success': True,
                    'file_path': str(file_path),
                    'timestamp': timestamp.isoformat(),
                    'resolution': f"{width}x{height}",
                    'file_size': file_path.stat().st_size
                }
            else:
                return {
                    'success': False,
                    'error': 'カメラから画像を取得できませんでした',
                    'timestamp': timestamp.isoformat()
                }
                
        except Exception as e:
            logger.error(f"画像撮影エラー: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': timestamp.isoformat()
            }
    
    def _create_dummy_image(self, file_path: Path, width: int, height: int, timestamp: datetime) -> Dict[str, Any]:
        """ダミー画像作成（開発環境用）"""
        try:
            import numpy as np
            
            # ダミー画像生成
            dummy_image = np.zeros((height, width, 3), dtype=np.uint8)
            
            # テキスト描画
            cv2.putText(dummy_image, f"DUMMY IMAGE", (50, height//2 - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            cv2.putText(dummy_image, timestamp.strftime('%Y-%m-%d %H:%M:%S'), 
                       (50, height//2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # 保存
            cv2.imwrite(str(file_path), dummy_image)
            
            return {
                'success': True,
                'file_path': str(file_path),
                'timestamp': timestamp.isoformat(),
                'resolution': f"{width}x{height}",
                'file_size': file_path.stat().st_size,
                'mode': 'dummy'
            }
            
        except Exception as e:
            logger.error(f"ダミー画像作成エラー: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': timestamp.isoformat()
            }
    
    def _save_camera_history(self, result: Dict[str, Any]):
        """カメラ撮影履歴を保存"""
        try:
            history_data = {
                'timestamp': result['timestamp'],
                'camera_id': 'single_camera',
                'layer': 1,
                'file_path': result['file_path'],
                'success': result['success']
            }
            
            if self.data_manager:
                self.data_manager.save_camera_history(history_data)
                
        except Exception as e:
            logger.error(f"カメラ履歴保存エラー: {e}")
    
    def get_latest_image_path(self) -> Optional[str]:
        """最新の画像パスを取得"""
        try:
            if not self.image_dir.exists():
                return None
            
            # 最新の画像ファイルを検索
            image_files = list(self.image_dir.glob("capture_*.jpg"))
            if not image_files:
                return None
            
            # ファイル名でソート（最新が最後）
            image_files.sort(key=lambda x: x.name)
            latest_file = image_files[-1]
            
            return str(latest_file)
            
        except Exception as e:
            logger.error(f"最新画像取得エラー: {e}")
            return None
    
    def get_image_list(self, limit: int = 10) -> list:
        """画像リストを取得"""
        try:
            if not self.image_dir.exists():
                return []
            
            image_files = list(self.image_dir.glob("capture_*.jpg"))
            image_files.sort(key=lambda x: x.name, reverse=True)
            
            images = []
            for img_file in image_files[:limit]:
                images.append({
                    'filename': img_file.name,
                    'file_path': str(img_file),
                    'created_time': datetime.fromtimestamp(img_file.stat().st_ctime).isoformat(),
                    'file_size': img_file.stat().st_size
                })
            
            return images
            
        except Exception as e:
            logger.error(f"画像リスト取得エラー: {e}")
            return []
    
    def cleanup_old_images(self, days: int = 30):
        """古い画像を削除"""
        try:
            if not self.image_dir.exists():
                return
            
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            deleted_count = 0
            
            for img_file in self.image_dir.glob("capture_*.jpg"):
                if img_file.stat().st_ctime < cutoff_time:
                    img_file.unlink()
                    deleted_count += 1
            
            logger.info(f"{deleted_count}個の古い画像を削除しました")
            
        except Exception as e:
            logger.error(f"画像クリーンアップエラー: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """カメラ状態を取得"""
        return {
            'initialized': self.initialized,
            'camera_available': self.camera is not None and self.camera.isOpened() if self.camera else False,
            'image_directory': str(self.image_dir),
            'total_images': len(list(self.image_dir.glob("capture_*.jpg"))) if self.image_dir.exists() else 0
        }
    
    def __del__(self):
        """デストラクタ"""
        if self.camera:
            self.camera.release()


# グローバルインスタンス
single_camera_manager = SingleCameraManager()

