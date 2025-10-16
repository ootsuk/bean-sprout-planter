"""
センサー基底クラス
全てのセンサーの共通機能を提供
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseSensor(ABC):
    """センサーの基底クラス"""
    
    def __init__(self, name: str, pin: int = 0):
        self.name = name                    # センサー名を設定
        self.pin = pin                      # GPIOピン番号を設定
        self.error_count = 0                # エラーカウントを初期化
        self.max_errors = 3                 # 最大エラー数を設定
        self.is_enabled = True              # センサー有効フラグを設定
        self.logger = logging.getLogger(f"sensor.{name}")  # ロガーを取得
        
    @abstractmethod
    def read_data(self) -> Dict[str, Any]:
        """センサーデータを読み取る（サブクラスで実装必須）"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """センサーを初期化する（サブクラスで実装必須）"""
        pass
    
    def is_healthy(self) -> bool:
        """センサーの健全性をチェック"""
        return self.error_count < self.max_errors and self.is_enabled
    
    def reset_error_count(self):
        """エラーカウントをリセット"""
        self.error_count = 0
        self.logger.info(f"{self.name} のエラーカウントをリセットしました")
    
    def increment_error_count(self):
        """エラーカウントを増加"""
        self.error_count += 1
        self.logger.warning(f"{self.name} エラーカウント: {self.error_count}/{self.max_errors}")
        
        if self.error_count >= self.max_errors:
            self.logger.error(f"{self.name} センサーが故障状態になりました")
            self.is_enabled = False
    
    def enable(self):
        """センサーを有効化"""
        self.is_enabled = True
        self.reset_error_count()
        self.logger.info(f"{self.name} を有効化しました")
    
    def disable(self):
        """センサーを無効化"""
        self.is_enabled = False
        self.logger.info(f"{self.name} を無効化しました")
    
    def get_status(self) -> Dict[str, Any]:
        """センサーの状態を取得"""
        return {
            'name': self.name,
            'enabled': self.is_enabled,
            'healthy': self.is_healthy(),
            'error_count': self.error_count,
            'pin': self.pin
        }
