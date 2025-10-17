import smbus2
import time
import requests
import json
# LINEチャネルアクセストークン
CHANNEL_ACCESS_TOKEN = '90JZASSXjMMU7nhwd+hW5UL6HJRnBdECJOWjHRAVztEOoLDZWLPx8V/A+ue9yRo6g+hhP4f/k8LktdmFAV9lOSKYAvnfn9J2jCIRjGjp6KzZaG6dm9jKkFWk296N7kq5byJRE0MJPF2Z7ZIDHo0zagdB04t89/1O/w1cDnyilFU='
# I2C設定（ADT7410）
I2C_ADDR = 0x48
bus = smbus2.SMBus(1)
def read_temperature_adt7410():
    raw = bus.read_word_data(I2C_ADDR, 0x00)
    raw = ((raw << 8) & 0xFF00) + (raw >> 8)
    if raw & 0x1000:
        raw -= 1 << 13
    temp_c = raw / 128.0
    return round(temp_c, 2)
def send_line_broadcast(message):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print("送信ステータス:", response.status_code)
    print("レスポンス:", response.text)
def main():
    while True:
        try:
            temp = read_temperature_adt7410()
            print(f"取得した気温: {temp}℃")
            # 条件①：25〜28℃
            if 25.0 <= temp < 28.0:
                message = f"現在 {temp}℃ です。こまめな休憩を心掛けましょう。"
                send_line_broadcast(message)
            # 条件②：28〜31℃
            elif 28.0 <= temp < 31.0:
                message = f"現在 {temp}℃ です。炎天下を避けて、水分補給をしましょう。"
                send_line_broadcast(message)
            elif 31.0 <= temp:
                message = f"現在 {temp}℃ です。涼しい室内に移動して水分補給と休憩をとりましょう。"
                send_line_broadcast(message)
            else:
                print("通知条件外の温度です。送信スキップ。")
        except Exception as e:
            print("エラー:", e)
        time.sleep(1800)  # 1時間に1回チェック
if __name__ == '__main__':
    main()