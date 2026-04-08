import requests
import time
import os
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("API_KEY")

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Telegram hata")

sent = set()
last_heartbeat = datetime.utcnow()
started = False

while True:
    try:
        now = datetime.utcnow()

        # 🔥 başlangıç mesajı (garanti)
        if not started:
            send("⚡ SCANNER AKTİF (FMP)")
            started = True

        # 🟢 60 dk heartbeat
        if now - last_heartbeat >= timedelta(minutes=60):
            send("🟢 SCANNER AKTİF (60 dk kontrol)")
            last_heartbeat = now

        # 🔥 API çağrısı
        url = f"https://financialmodelingprep.com/api/v3/stock_market/gainers?apikey={API_KEY}"
        
        r = requests.get(url, timeout=20)
        data = r.json()

        for stock in data:
            try:
                symbol = stock.get("symbol")
                change = stock.get("changesPercentage", 0)

                if not symbol or symbol in sent:
                    continue

                if change > 1:
                    msg = f"""🔥 SCANNER (FMP)
💰 ${symbol}
📈 Change: {change}
"""
                    send(msg)
                    sent.add(symbol)

            except:
                continue

        time.sleep(60)

    except Exception as e:
        print("HATA:", e)
        time.sleep(30)