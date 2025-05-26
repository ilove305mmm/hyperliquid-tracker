
import time
import os
import requests
from hyperliquid.info import Info
from hyperliquid.utils import constants

ADDRESS = "0x5078C2fBeA2b2aD61bc840Bc023E35Fce56BeDb6"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

info = Info(constants.MAINNET_API_URL, skip_ws=True)
last_position_string = ""

def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"[錯誤] 發送 Telegram 訊息失敗：{e}")

def format_all_positions(positions):
    lines = []
    for p in positions:
        sz = float(p["position"]["szi"])
        if abs(sz) > 0:
            coin = p["position"]["coin"]
            entry = float(p["position"]["entryPx"])
            side = "多單" if sz > 0 else "空單"
            lines.append(f"{coin} {side} 倉位：數量 {abs(sz)}，進場價 {entry}")
    return "\n".join(lines) if lines else "目前已無持倉。"

def monitor():
    global last_position_string
    try:
        user_state = info.user_state(ADDRESS)
        positions = user_state.get("assetPositions", [])
        formatted = format_all_positions(positions)

        if formatted != last_position_string:
            if "無持倉" in formatted:
                send_message("📉 [倉位清空] James Wynn 目前已無持倉。")
            else:
                send_message(f"📈 [倉位更新] James Wynn 現在持有：\n{formatted}")
            last_position_string = formatted
    except Exception as e:
        send_message(f"[錯誤] 無法取得 SDK 倉位資訊：{e}")

if __name__ == "__main__":
    send_message("✅ 追蹤啟動：開始監控 James Wynn 在 Hyperliquid 的倉位...")
    while True:
        monitor()
        time.sleep(300)
