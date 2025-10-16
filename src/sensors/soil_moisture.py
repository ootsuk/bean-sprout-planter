"""
SEN0193土壌水分センサー制御モジュール
MCP3002 ADC経由でアナログ値を取得
"""

import time
import logging
from typing import Dict, Any
from .base_sensor import BaseSensor

# Raspberry Pi環境チェック
try:
    from gpiozero import MCP3002
    GPIOZERO_AVAILABLE = True
except ImportError:
    GPIOZERO_AVAILABLE = False


class SEN0193Sensor(BaseSensor):
    """SEN0193土壌水分センサー制御クラス"""
    
    def __init__(self, channel: int = 0, vref: float = 3.3):
        super().__init__("SEN0193", channel)
        self.channel = channel  # ADCチャンネル番号
        self.vref = vref        # 基準電圧
        self.adc = None
        self.initialized = False
        
        # Raspberry Pi以外の環境対応
        if not GPIOZERO_AVAILABLE:
            self.logger.info("gpiozero未インストール（開発環境）")
        
    def initialize(self) -> bool:
        """センサーを初期化"""
        if not GPIOZERO_AVAILABLE:
            self.logger.info("SEN0193センサー: ダミーモード")
            self.initialized = True
            return True
        
        try:
            self.adc = MCP3002(channel=self.channel)
            self.initialized = True
            self.logger.info(f"SEN0193センサー初期化完了（チャンネル{self.channel}）")
            return True
            
        except Exception as e:
            self.logger.error(f"SEN0193初期化エラー: {str(e)}")
            self.increment_error_count()
            return False
    
    def read_data(self) -> Dict[str, Any]:
        """土壌水分データを読み取る"""
        # ダミーモード（Raspberry Pi以外）
        if not GPIOZERO_AVAILABLE or self.adc is None:
            return {
                "raw_value": 180,
                "voltage": 2.1,
                "moisture_percentage": 45.0,
                "status": "Optimal",
                "timestamp": time.time(),
                "mode": "dummy"
            }
        
        if not self.initialized:
            if not self.initialize():
                return {"error": "初期化失敗"}
        
        try:
            # ADC値を読み取り（0.0-1.0）
            adc_value = self.adc.value
            
            # 生の値（0-255）に変換
            raw_value = int(adc_value * 255)
            
            # 電圧に変換
            voltage = adc_value * self.vref
            
            # 水分状態を判定
            status = self._get_moisture_status(raw_value)
            
            # パーセンテージに変換（逆スケール: 255=乾燥, 0=湿潤）
            moisture_percentage = ((255 - raw_value) / 255) * 100
            
            self.reset_error_count()
            return {
                "raw_value": raw_value,
                "voltage": round(voltage, 2),
                "moisture_percentage": round(moisture_percentage, 1),
                "status": status,
                "timestamp": time.time(),
                "mode": "real"
            }
            
        except Exception as e:
            self.logger.error(f"SEN0193読み取りエラー: {str(e)}")
            self.increment_error_count()
            return {"error": str(e)}
    
    def _get_moisture_status(self, raw_value: int) -> str:
        """生の水分値から状態文字列を返す"""
        if raw_value > 200:
            return "Dry"        # 乾燥
        elif raw_value > 150:
            return "Optimal"    # 最適
        else:
            return "VeryWet"    # 過湿
    
    def get_status(self) -> Dict[str, Any]:
        """センサー状態を取得"""
        base_status = super().get_status()
        base_status['initialized'] = self.initialized
        base_status['channel'] = self.channel
        base_status['vref'] = self.vref
        base_status['available'] = GPIOZERO_AVAILABLE
        return base_status
