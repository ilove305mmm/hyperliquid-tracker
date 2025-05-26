
import requests
import time
import os

ADDRESS = "0x5078C2fBeA2b2aD61bc840Bc023E35Fce56BeDb6"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

last_position_state = None

def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"[錯誤] 無法發送 Telegram 訊息：{e}")

def fetch_position():
    url = "https://api.hyperliquid.xyz/info"
    payload = {
        "type": "hyperliquid_getUserState",
        "user": ADDRESS
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        if r.status_code != 200:
            send_message(f"[錯誤] API 回應碼：{r.status_code}")
            return None

        if not r.text.strip():
            send_message("[錯誤] API 回傳空白，可能是被擋或 Hyperliquid 無回應")
            return None

        data = r.json()
        return data.get("assetPositions", [])
    except Exception as e:
        send_message(f"[錯誤] 無法取得倉位資訊：{e}")
        return None

def format_position(position):
    coin = position["position"]["coin"]
    size = float(position["position"]["szi"])
    side = "多單" if size > 0 else "空單"
    entry = float(position["position"]["entryPx"])
    return f"{coin} {side} 倉位：數量 {abs(size)}，進場價 {entry}"

def monitor():
    global last_position_state
    positions = fetch_position()
    if positions is None:
        return

    new_state = [format_position(p) for p in positions]
    if new_state != last_position_state:
        if new_state:
            for p in new_state:
                send_message(f"📈 [倉位更新] James Wynn 現在持有：\n{p}")
        else:
            send_message("📉 [倉位清空] James Wynn 目前已無持倉。")
        last_position_state = new_state

if __name__ == "__main__":
    send_message("✅ 追蹤啟動：開始監控 James Wynn 在 Hyperliquid 的倉位...")
    while True:
        monitor()
        time.sleep(300)
