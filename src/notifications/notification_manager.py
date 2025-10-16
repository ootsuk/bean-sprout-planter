# 豆苗プランター - 通知機能

"""
通知機能
- LINE Notify API
- メール通知
- システム通知
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """通知タイプ"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class NotificationMessage:
    """通知メッセージ"""
    title: str
    message: str
    type: NotificationType
    timestamp: str
    data: Optional[Dict] = None


class NotificationManager:
    """通知管理クラス"""
    
    def __init__(self):
        self.config = {
            "line_notify": {
                "enabled": False,
                "token": "",
                "api_url": "https://notify-api.line.me/api/notify"
            },
            "email": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "",
                "to_emails": []
            },
            "system": {
                "enabled": True,
                "log_level": "INFO"
            }
        }
        
        # 通知履歴
        self.notification_history: List[NotificationMessage] = []
        self.max_history = 100
        
        # 通知テンプレート
        self.templates = {
            "watering": {
                "title": "💧 給水実行",
                "message": "豆苗に給水を実行しました。\n給水量: {amount}ml\n残量: {remaining}ml"
            },
            "harvest_ready": {
                "title": "🌱 収穫時期",
                "message": "豆苗の収穫時期です！\n信頼度: {confidence}%\n推奨事項: {recommendation}"
            },
            "low_water": {
                "title": "⚠️ 水位警告",
                "message": "給水タンクの水位が低くなっています。\n残量: {remaining}ml\n補充をお願いします。"
            },
            "sensor_error": {
                "title": "❌ センサーエラー",
                "message": "センサーでエラーが発生しました。\nセンサー: {sensor_name}\nエラー: {error}"
            },
            "system_start": {
                "title": "🚀 システム起動",
                "message": "豆苗プランターが起動しました。\n時刻: {timestamp}"
            },
            "system_stop": {
                "title": "⏹️ システム停止",
                "message": "豆苗プランターが停止しました。\n時刻: {timestamp}"
            }
        }
    
    def configure_line_notify(self, token: str):
        """LINE Notifyの設定"""
        self.config["line_notify"]["token"] = token
        self.config["line_notify"]["enabled"] = bool(token)
        logger.info("LINE Notify設定を更新しました")
    
    def configure_email(self, smtp_server: str, smtp_port: int, username: str, 
                       password: str, from_email: str, to_emails: List[str]):
        """メール通知の設定"""
        self.config["email"].update({
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "username": username,
            "password": password,
            "from_email": from_email,
            "to_emails": to_emails,
            "enabled": bool(smtp_server and username and password)
        })
        logger.info("メール通知設定を更新しました")
    
    def send_line_notify(self, message: str, image_path: Optional[str] = None) -> bool:
        """LINE Notifyで通知を送信"""
        if not self.config["line_notify"]["enabled"]:
            logger.warning("LINE Notifyが無効です")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.config['line_notify']['token']}"
            }
            
            data = {"message": message}
            
            # 画像がある場合は添付
            files = None
            if image_path:
                files = {"imageFile": open(image_path, "rb")}
            
            response = requests.post(
                self.config["line_notify"]["api_url"],
                headers=headers,
                data=data,
                files=files
            )
            
            if response.status_code == 200:
                logger.info("LINE Notify送信成功")
                return True
            else:
                logger.error(f"LINE Notify送信失敗: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"LINE Notify送信エラー: {e}")
            return False
        finally:
            if files and "imageFile" in files:
                files["imageFile"].close()
    
    def send_email(self, subject: str, message: str, to_emails: Optional[List[str]] = None) -> bool:
        """メール通知を送信"""
        if not self.config["email"]["enabled"]:
            logger.warning("メール通知が無効です")
            return False
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # 送信先の設定
            recipients = to_emails or self.config["email"]["to_emails"]
            if not recipients:
                logger.warning("メール送信先が設定されていません")
                return False
            
            # メール作成
            msg = MIMEMultipart()
            msg["From"] = self.config["email"]["from_email"]
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject
            
            msg.attach(MIMEText(message, "plain", "utf-8"))
            
            # SMTPサーバーに接続して送信
            server = smtplib.SMTP(self.config["email"]["smtp_server"], self.config["email"]["smtp_port"])
            server.starttls()
            server.login(self.config["email"]["username"], self.config["email"]["password"])
            
            text = msg.as_string()
            server.sendmail(self.config["email"]["from_email"], recipients, text)
            server.quit()
            
            logger.info("メール送信成功")
            return True
            
        except Exception as e:
            logger.error(f"メール送信エラー: {e}")
            return False
    
    def send_system_notification(self, message: str, level: str = "INFO"):
        """システム通知を送信"""
        if not self.config["system"]["enabled"]:
            return
        
        # ログに記録
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.log(log_level, f"システム通知: {message}")
    
    def send_notification(self, notification_type: str, data: Dict = None, 
                         channels: List[str] = None) -> bool:
        """通知を送信"""
        if notification_type not in self.templates:
            logger.error(f"未知の通知タイプ: {notification_type}")
            return False
        
        template = self.templates[notification_type]
        data = data or {}
        
        # メッセージを生成
        title = template["title"]
        message = template["message"].format(**data)
        
        # 通知メッセージを作成
        notification = NotificationMessage(
            title=title,
            message=message,
            type=NotificationType.INFO,
            timestamp=datetime.now().isoformat(),
            data=data
        )
        
        # 履歴に追加
        self.notification_history.append(notification)
        if len(self.notification_history) > self.max_history:
            self.notification_history.pop(0)
        
        # 送信チャンネルを決定
        if channels is None:
            channels = []
            if self.config["line_notify"]["enabled"]:
                channels.append("line")
            if self.config["email"]["enabled"]:
                channels.append("email")
            channels.append("system")
        
        success = True
        
        # 各チャンネルに送信
        for channel in channels:
            if channel == "line":
                if not self.send_line_notify(f"{title}\n{message}"):
                    success = False
            elif channel == "email":
                if not self.send_email(title, message):
                    success = False
            elif channel == "system":
                self.send_system_notification(f"{title}: {message}")
        
        return success
    
    def notify_watering(self, amount: int, remaining: int):
        """給水通知"""
        return self.send_notification("watering", {
            "amount": amount,
            "remaining": remaining
        })
    
    def notify_harvest_ready(self, confidence: float, recommendation: str):
        """収穫時期通知"""
        return self.send_notification("harvest_ready", {
            "confidence": confidence,
            "recommendation": recommendation
        })
    
    def notify_low_water(self, remaining: int):
        """水位警告通知"""
        return self.send_notification("low_water", {
            "remaining": remaining
        })
    
    def notify_sensor_error(self, sensor_name: str, error: str):
        """センサーエラー通知"""
        return self.send_notification("sensor_error", {
            "sensor_name": sensor_name,
            "error": error
        })
    
    def notify_system_start(self):
        """システム起動通知"""
        return self.send_notification("system_start", {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def notify_system_stop(self):
        """システム停止通知"""
        return self.send_notification("system_stop", {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def get_notification_history(self, limit: int = 50) -> List[NotificationMessage]:
        """通知履歴を取得"""
        return self.notification_history[-limit:]
    
    def get_config(self) -> Dict:
        """通知設定を取得"""
        # パスワードは返さない
        config = self.config.copy()
        if "password" in config["email"]:
            config["email"]["password"] = "***"
        return config


# グローバルインスタンス
notification_manager = NotificationManager()
