"""
フロートスイッチ制御モジュール
水タンクの水位を検知
"""

import time
import logging
from typing import Dict, Any
from .base_sensor import BaseSensor

# Raspberry Pi環境チェック
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False


class FloatSwitch(BaseSensor):
    """フロートスイッチ制御クラス"""
    
    def __init__(self, pin: int = 18):
        super().__init__("FloatSwitch", pin)
        self.initialized = False
        
        if not GPIO_AVAILABLE:
            self.logger.info("RPi.GPIO未インストール（開発環境）")
        
    def initialize(self) -> bool:
        """フロートスイッチを初期化"""
        if not GPIO_AVAILABLE:
            self.logger.info("フロートスイッチ: ダミーモード")
            self.initialized = True
            return True
        
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            self.initialized = True
            self.logger.info(f"フロートスイッチ初期化完了（GPIO{self.pin}）")
            return True
            
        except Exception as e:
            self.logger.error(f"フロートスイッチ初期化エラー: {str(e)}")
            self.increment_error_count()
            return False
    
    def read_data(self) -> Dict[str, Any]:
        """水位データを読み取る"""
        # ダミーモード（Raspberry Pi以外）
        if not GPIO_AVAILABLE:
            return {
                "water_present": True,
                "level": "normal",
                "raw_value": 1,
                "timestamp": time.time(),
                "mode": "dummy"
            }
        
        if not self.initialized:
            if not self.initialize():
                return {"error": "初期化失敗"}
        
        try:
            # GPIOピンの状態を読み取り
            # LOW = 水あり、HIGH = 水なし
            gpio_state = GPIO.input(self.pin)
            water_present = (gpio_state == GPIO.LOW)
            
            # 水位レベル判定
            if water_present:
                level = "normal"
            else:
                level = "low"
            
            self.reset_error_count()
            return {
                "water_present": water_present,
                "level": level,
                "raw_value": gpio_state,
                "timestamp": time.time(),
                "mode": "real"
            }
            
        except Exception as e:
            self.logger.error(f"フロートスイッチ読み取りエラー: {str(e)}")
            self.increment_error_count()
            return {"error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """センサー状態を取得"""
        base_status = super().get_status()
        base_status['initialized'] = self.initialized
        base_status['available'] = GPIO_AVAILABLE
        return base_status
    
    def cleanup(self):
        """GPIOクリーンアップ"""
        if GPIO_AVAILABLE and self.initialized:
            try:
                GPIO.cleanup(self.pin)
                self.logger.info("GPIO クリーンアップ完了")
            except Exception as e:
                self.logger.warning(f"GPIO クリーンアップエラー: {e}")
