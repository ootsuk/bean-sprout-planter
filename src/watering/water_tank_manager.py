# 豆苗プランター - 給水タンク管理

"""
豆苗栽培に特化した給水タンク管理システム
ユーザー入力による初期設定、給水量計算、残量管理
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path


class WaterTankManager:
    """給水タンクマネージャー"""
    
    def __init__(self):
        """給水タンクマネージャーの初期化"""
        self.logger = logging.getLogger("water_tank_manager")
        
        # タンク設定
        self.tank_capacity = int(os.getenv('TANK_CAPACITY_ML', 2000))  # ml
        self.low_water_threshold = int(os.getenv('TANK_LOW_WATER_THRESHOLD', 200))  # ml
        self.refill_notification_enabled = os.getenv('TANK_REFILL_NOTIFICATION', 'True').lower() == 'true'
        
        # 現在の状態
        self.current_volume = self.tank_capacity  # ml
        self.water_usage_history = []
        self.refill_history = []
        
        # 設定ファイル
        self.config_file = Path("config/water_tank_config.json")
        self.history_file = Path("config/water_tank_history.json")
        
        # ディレクトリ作成
        self._create_directories()
        
        # 設定と履歴を読み込み
        self._load_config()
        self._load_history()
    
    def _create_directories(self):
        """必要なディレクトリを作成"""
        directories = ["config", "logs"]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def _load_config(self):
        """設定を読み込み"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_volume = config.get('current_volume', self.tank_capacity)
                    self.tank_capacity = config.get('tank_capacity', self.tank_capacity)
                    self.low_water_threshold = config.get('low_water_threshold', self.low_water_threshold)
            else:
                # デフォルト設定で保存
                self._save_config()
        except Exception as e:
            self.logger.error(f"設定読み込みエラー: {str(e)}")
    
    def _save_config(self):
        """設定を保存"""
        try:
            config = {
                'current_volume': self.current_volume,
                'tank_capacity': self.tank_capacity,
                'low_water_threshold': self.low_water_threshold,
                'refill_notification_enabled': self.refill_notification_enabled,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"設定保存エラー: {str(e)}")
    
    def _load_history(self):
        """履歴を読み込み"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                    self.water_usage_history = history_data.get('usage_history', [])
                    self.refill_history = history_data.get('refill_history', [])
        except Exception as e:
            self.logger.error(f"履歴読み込みエラー: {str(e)}")
    
    def _save_history(self):
        """履歴を保存"""
        try:
            history_data = {
                'usage_history': self.water_usage_history[-100:],  # 最新100件のみ保持
                'refill_history': self.refill_history[-50:],      # 最新50件のみ保持
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"履歴保存エラー: {str(e)}")
    
    def set_initial_volume(self, volume: int) -> Dict[str, Any]:
        """初期水量を設定"""
        try:
            # 容量チェック
            if volume < 0:
                return {'success': False, 'message': '水量は0以上である必要があります'}
            
            if volume > self.tank_capacity:
                return {'success': False, 'message': f'水量はタンク容量({self.tank_capacity}ml)以下である必要があります'}
            
            # 水量設定
            previous_volume = self.current_volume
            self.current_volume = volume
            
            # 設定保存
            self._save_config()
            
            self.logger.info(f"初期水量設定: {volume}ml (前回: {previous_volume}ml)")
            
            return {
                'success': True,
                'message': f'初期水量を{volume}mlに設定しました',
                'previous_volume': previous_volume,
                'new_volume': volume,
                'percentage': (volume / self.tank_capacity) * 100
            }
            
        except Exception as e:
            self.logger.error(f"初期水量設定エラー: {str(e)}")
            return {'success': False, 'message': f'設定エラー: {str(e)}'}
    
    def calculate_remaining_volume(self, watering_amount: int) -> Dict[str, Any]:
        """給水後の残量を計算"""
        try:
            # 給水量チェック
            if watering_amount < 0:
                return {'success': False, 'message': '給水量は0以上である必要があります'}
            
            # 残量計算
            previous_volume = self.current_volume
            self.current_volume -= watering_amount
            self.current_volume = max(0, self.current_volume)  # 0以下にならないよう調整
            
            # 使用履歴に記録
            usage_record = {
                'timestamp': datetime.now().isoformat(),
                'watering_amount': watering_amount,
                'previous_volume': previous_volume,
                'remaining_volume': self.current_volume,
                'percentage': (self.current_volume / self.tank_capacity) * 100
            }
            self.water_usage_history.append(usage_record)
            
            # 設定と履歴を保存
            self._save_config()
            self._save_history()
            
            # 低水位警告チェック
            warning_message = None
            if self.current_volume <= self.low_water_threshold:
                warning_message = f"水位が低下しています ({self.current_volume}ml)"
                self.logger.warning(warning_message)
            
            self.logger.info(f"給水実行: {watering_amount}ml, 残量: {self.current_volume}ml")
            
            return {
                'success': True,
                'watering_amount': watering_amount,
                'previous_volume': previous_volume,
                'remaining_volume': self.current_volume,
                'percentage': (self.current_volume / self.tank_capacity) * 100,
                'warning': warning_message
            }
            
        except Exception as e:
            self.logger.error(f"残量計算エラー: {str(e)}")
            return {'success': False, 'message': f'計算エラー: {str(e)}'}
    
    def refill_tank(self, amount: int) -> Dict[str, Any]:
        """タンクに水を補充"""
        try:
            # 補充量チェック
            if amount <= 0:
                return {'success': False, 'message': '補充量は0より大きい必要があります'}
            
            # 補充実行
            previous_volume = self.current_volume
            self.current_volume += amount
            self.current_volume = min(self.current_volume, self.tank_capacity)  # 容量上限チェック
            
            actual_refill_amount = self.current_volume - previous_volume
            
            # 補充履歴に記録
            refill_record = {
                'timestamp': datetime.now().isoformat(),
                'refill_amount': actual_refill_amount,
                'requested_amount': amount,
                'previous_volume': previous_volume,
                'new_volume': self.current_volume,
                'percentage': (self.current_volume / self.tank_capacity) * 100
            }
            self.refill_history.append(refill_record)
            
            # 設定と履歴を保存
            self._save_config()
            self._save_history()
            
            self.logger.info(f"タンク補充: {actual_refill_amount}ml, 残量: {self.current_volume}ml")
            
            return {
                'success': True,
                'message': f'タンクに{actual_refill_amount}ml補充しました',
                'requested_amount': amount,
                'actual_refill_amount': actual_refill_amount,
                'previous_volume': previous_volume,
                'new_volume': self.current_volume,
                'percentage': (self.current_volume / self.tank_capacity) * 100
            }
            
        except Exception as e:
            self.logger.error(f"タンク補充エラー: {str(e)}")
            return {'success': False, 'message': f'補充エラー: {str(e)}'}
    
    def get_tank_status(self) -> Dict[str, Any]:
        """タンク状態を取得"""
        try:
            percentage = (self.current_volume / self.tank_capacity) * 100
            
            # 状態判定
            if percentage <= (self.low_water_threshold / self.tank_capacity) * 100:
                status = 'low'
                status_message = '水位低下'
            elif percentage <= 30:
                status = 'warning'
                status_message = '注意'
            else:
                status = 'normal'
                status_message = '正常'
            
            # 推定日数計算
            estimated_days = self._calculate_estimated_days()
            
            # 最後の補充日
            last_refill = self._get_last_refill_date()
            
            return {
                'current_volume': self.current_volume,
                'tank_capacity': self.tank_capacity,
                'percentage': round(percentage, 1),
                'status': status,
                'status_message': status_message,
                'low_water_threshold': self.low_water_threshold,
                'estimated_days_remaining': estimated_days,
                'last_refill': last_refill,
                'refill_needed': status == 'low',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"タンク状態取得エラー: {str(e)}")
            return {'error': str(e)}
    
    def get_usage_statistics(self, days: int = 7) -> Dict[str, Any]:
        """使用統計を取得"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 指定期間の使用履歴をフィルタリング
            recent_usage = [
                record for record in self.water_usage_history
                if datetime.fromisoformat(record['timestamp']) >= cutoff_date
            ]
            
            if not recent_usage:
                return {
                    'total_usage': 0,
                    'average_daily': 0,
                    'peak_usage': 0,
                    'usage_count': 0,
                    'period_days': days
                }
            
            # 統計計算
            total_usage = sum(record['watering_amount'] for record in recent_usage)
            average_daily = total_usage / days if days > 0 else 0
            peak_usage = max(record['watering_amount'] for record in recent_usage)
            usage_count = len(recent_usage)
            
            # 効率スコア計算（理想的な使用量との比較）
            ideal_daily_usage = 100  # ml/日（豆苗栽培の理想値）
            efficiency_score = min(10, max(0, 10 - abs(average_daily - ideal_daily_usage) / 10))
            
            return {
                'total_usage': total_usage,
                'average_daily': round(average_daily, 1),
                'peak_usage': peak_usage,
                'usage_count': usage_count,
                'period_days': days,
                'efficiency_score': round(efficiency_score, 1),
                'ideal_daily_usage': ideal_daily_usage,
                'usage_trend': self._calculate_usage_trend(recent_usage)
            }
            
        except Exception as e:
            self.logger.error(f"使用統計取得エラー: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_estimated_days(self) -> int:
        """残量から推定日数を計算"""
        try:
            if not self.water_usage_history:
                return 999  # 履歴がない場合は長期とみなす
            
            # 過去7日間の平均使用量を計算
            recent_days = 7
            cutoff_date = datetime.now() - timedelta(days=recent_days)
            
            recent_usage = [
                record for record in self.water_usage_history
                if datetime.fromisoformat(record['timestamp']) >= cutoff_date
            ]
            
            if not recent_usage:
                return 999
            
            total_usage = sum(record['watering_amount'] for record in recent_usage)
            average_daily = total_usage / recent_days
            
            if average_daily <= 0:
                return 999
            
            estimated_days = int(self.current_volume / average_daily)
            return max(0, estimated_days)
            
        except Exception as e:
            self.logger.error(f"推定日数計算エラー: {str(e)}")
            return 0
    
    def _get_last_refill_date(self) -> Optional[str]:
        """最後の補充日を取得"""
        try:
            if not self.refill_history:
                return None
            
            # 最新の補充記録を取得
            latest_refill = max(self.refill_history, key=lambda x: x['timestamp'])
            return latest_refill['timestamp']
            
        except Exception as e:
            self.logger.error(f"最後の補充日取得エラー: {str(e)}")
            return None
    
    def _calculate_usage_trend(self, recent_usage: List[Dict[str, Any]]) -> str:
        """使用量の傾向を計算"""
        try:
            if len(recent_usage) < 2:
                return 'stable'
            
            # 前半と後半の平均使用量を比較
            mid_point = len(recent_usage) // 2
            first_half = recent_usage[:mid_point]
            second_half = recent_usage[mid_point:]
            
            first_half_avg = sum(record['watering_amount'] for record in first_half) / len(first_half)
            second_half_avg = sum(record['watering_amount'] for record in second_half) / len(second_half)
            
            diff_percentage = ((second_half_avg - first_half_avg) / first_half_avg) * 100
            
            if diff_percentage > 10:
                return 'increasing'
            elif diff_percentage < -10:
                return 'decreasing'
            else:
                return 'stable'
                
        except Exception as e:
            self.logger.error(f"使用傾向計算エラー: {str(e)}")
            return 'unknown'
    
    def reset_tank(self) -> Dict[str, Any]:
        """タンクをリセット（満水状態に）"""
        try:
            previous_volume = self.current_volume
            self.current_volume = self.tank_capacity
            
            # リセット記録を履歴に追加
            reset_record = {
                'timestamp': datetime.now().isoformat(),
                'action': 'reset',
                'previous_volume': previous_volume,
                'new_volume': self.tank_capacity,
                'percentage': 100.0
            }
            self.refill_history.append(reset_record)
            
            # 設定と履歴を保存
            self._save_config()
            self._save_history()
            
            self.logger.info(f"タンクリセット: {self.tank_capacity}ml")
            
            return {
                'success': True,
                'message': 'タンクをリセットしました',
                'previous_volume': previous_volume,
                'new_volume': self.tank_capacity,
                'percentage': 100.0
            }
            
        except Exception as e:
            self.logger.error(f"タンクリセットエラー: {str(e)}")
            return {'success': False, 'message': f'リセットエラー: {str(e)}'}
    
    def get_history(self, limit: int = 50) -> Dict[str, Any]:
        """履歴を取得"""
        try:
            return {
                'usage_history': self.water_usage_history[-limit:],
                'refill_history': self.refill_history[-limit:],
                'total_usage_records': len(self.water_usage_history),
                'total_refill_records': len(self.refill_history)
            }
            
        except Exception as e:
            self.logger.error(f"履歴取得エラー: {str(e)}")
            return {'error': str(e)}



