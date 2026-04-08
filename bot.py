import requests
import time
import os
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Telegram hata")

send("⚡ SCANNER BOT AKTİF")

last_heartbeat = datetime.utcnow()

def get_gainers():
    url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=25&scrIds=day_gainers"
    
    try:
        r = requests.get(url, timeout=10)

        if r.status_code == 429:
            print("Rate limit! Bekleniyor...")
            time.sleep(120)
            return []

        if r.status_code != 200:
            print("API hata:", r.status_code)
            return []

        data = r.json()

        if "finance" not in data or not data["finance"]["result"]:
            return []

        results = data["finance"]["result"][0]["quotes"]

        stocks = []

        for s in results:
            try:
                price = s.get("regularMarketPrice", 0)
                change = s.get("regularMarketChangePercent", 0)
                volume = s.get("regularMarketVolume", 0)
                symbol = s.get("symbol")

                if price and change and symbol:
                    if price < 20 and change > 10:
                        stocks.append((symbol, change, volume))

            except:
                continue

        return stocks

    except Exception as e:
        print("API hata:", e)
        return []

sent = set()

while True:
    try:
        now = datetime.utcnow()

        if now - last_heartbeat >= timedelta(minutes=60):
            send("🟢 SCANNER AKTİF (60 dk kontrol)")
            last_heartbeat = now

        stocks = get_gainers()

        if not stocks:
            print("Hisse yok (normal)")

        for sym, change, vol in stocks:

            if sym in sent:
                continue

            msg = f"""🔥 SCANNER
💰 ${sym}
📈 Change: %{round(change,2)}
📊 Volume: {vol}
"""

            send(msg)
            sent.add(sym)

        # 🔥 EN KRİTİK SATIR
        time.sleep(90)

    except Exception as e:
        print("Loop hata:", e)
        time.sleep(30)