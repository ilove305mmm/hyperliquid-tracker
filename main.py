
import time
import os
import requests
from hyperliquid.info import Info
from hyperliquid.utils import constants

ADDRESS = "0x5078C2fBeA2b2aD61bc840Bc023E35Fce56BeDb6"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

info = Info(constants.MAINNET_API_URL, skip_ws=True)
last_state_str = ""

def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"[錯誤] 發送 Telegram 訊息失敗：{e}")

def format_position(position):
    coin = position["position"]["coin"]
    size = float(position["position"]["szi"])
    side = "多單" if size > 0 else "空單"
    entry = float(position["position"]["entryPx"])
    return f"{coin} {side} 倉位：數量 {abs(size)}，進場價 {entry}"

def monitor():
    global last_state_str
    try:
        user_state = info.user_state(ADDRESS)
        positions = user_state.get("assetPositions", [])
        current_state = "\n".join([format_position(p) for p in positions]) if positions else "目前已無持倉。"

        if current_state != last_state_str:
            if positions:
                send_message(f"📈 [倉位更新] James Wynn 現在持有：\n{current_state}")
            else:
                send_message("📉 [倉位清空] James Wynn 目前已無持倉。")
            last_state_str = current_state
    except Exception as e:
        send_message(f"[錯誤] 無法取得 SDK 倉位資訊：{e}")

if __name__ == "__main__":
    send_message("✅ 追蹤啟動：開始監控 James Wynn 在 Hyperliquid 的倉位...")
    while True:
        monitor()
        time.sleep(300)
