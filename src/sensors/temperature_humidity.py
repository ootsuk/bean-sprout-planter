"""
AHT25温湿度センサー制御モジュール
I2C通信で温度と湿度を取得
"""

import time
import logging
from typing import Dict, Any
from .base_sensor import BaseSensor

# Raspberry Pi環境チェック
try:
    import smbus2
    SMBUS_AVAILABLE = True
except ImportError:
    SMBUS_AVAILABLE = False


class AHT25Sensor(BaseSensor):
    """AHT25温湿度センサー制御クラス"""
    
    def __init__(self):
        super().__init__("AHT25", 0)
        self.bus = None
        self.address = 0x38  # AHT25のI2Cアドレス
        self.initialized = False
        
        # Raspberry Pi以外の環境対応
        if SMBUS_AVAILABLE:
            try:
                self.bus = smbus2.SMBus(1)
            except Exception as e:
                self.logger.warning(f"I2Cバス初期化失敗（開発環境）: {e}")
        else:
            self.logger.info("smbus2未インストール（開発環境）")
        
    def initialize(self) -> bool:
        """AHT25センサーを初期化"""
        if not SMBUS_AVAILABLE or self.bus is None:
            self.logger.info("AHT25センサー: ダミーモード")
            self.initialized = True
            return True
        
        try:
            # センサーリセット
            self.bus.write_byte(self.address, 0xBA)
            time.sleep(0.1)
            
            # 初期化コマンド
            self.bus.write_byte(self.address, 0xBE)
            self.bus.write_byte(self.address, 0x08)
            self.bus.write_byte(self.address, 0x00)
            time.sleep(0.1)
            
            self.initialized = True
            self.logger.info("AHT25センサー初期化完了")
            return True
            
        except Exception as e:
            self.logger.error(f"AHT25初期化エラー: {str(e)}")
            self.increment_error_count()
            return False
    
    def read_data(self) -> Dict[str, Any]:
        """温湿度データを読み取る"""
        # ダミーモード（Raspberry Pi以外）
        if not SMBUS_AVAILABLE or self.bus is None:
            return {
                "temperature": 25.5,
                "humidity": 60.0,
                "timestamp": time.time(),
                "mode": "dummy"
            }
        
        if not self.initialized:
            if not self.initialize():
                return {"error": "初期化失敗"}
        
        try:
            # 測定開始コマンド
            self.bus.write_byte(self.address, 0xAC)
            self.bus.write_byte(self.address, 0x33)
            self.bus.write_byte(self.address, 0x00)
            
            # 測定完了待機
            time.sleep(0.1)
            
            # データ読み取り
            data = self.bus.read_i2c_block_data(self.address, 0x00, 6)
            
            # データ解析
            humidity_raw = (data[1] << 12) | (data[2] << 4) | (data[3] >> 4)
            temperature_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
            
            # 値に変換
            humidity = (humidity_raw / 0x100000) * 100
            temperature = (temperature_raw / 0x100000) * 200 - 50
            
            # 値の妥当性チェック
            if not (0 <= humidity <= 100) or not (-40 <= temperature <= 85):
                raise ValueError("センサー値が範囲外です")
            
            self.reset_error_count()
            return {
                "temperature": round(temperature, 1),
                "humidity": round(humidity, 1),
                "timestamp": time.time(),
                "mode": "real"
            }
            
        except Exception as e:
            self.logger.error(f"AHT25読み取りエラー: {str(e)}")
            self.increment_error_count()
            return {"error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """センサー状態を取得"""
        base_status = super().get_status()
        base_status['initialized'] = self.initialized
        base_status['address'] = hex(self.address)
        base_status['available'] = SMBUS_AVAILABLE
        return base_status
