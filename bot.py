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

# 🔁 tekrar kontrol (zaman bazlı)
sent = {}

# 🗓 günlük reset
last_reset_day = datetime.utcnow().date()

def fetch_fmp():
    url = f"https://financialmodelingprep.com/api/v3/stock_market/gainers?apikey={API_KEY}"
    
    for i in range(3):
        try:
            r = requests.get(url, timeout=20)
            return r.json()
        except:
            print("FMP retry...")
            time.sleep(5)
    return []

def fetch_yahoo():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=20&scrIds=day_gainers"
        r = requests.get(url, timeout=15)
        data = r.json()
        return data["finance"]["result"][0]["quotes"]
    except:
        print("Yahoo fallback hata")
        return []

last_heartbeat = datetime.utcnow()
started = False

while True:
    try:
        now = datetime.utcnow()

        # 🔥 başlangıç
        if not started:
            send("🚀 ULTRA SCANNER AKTİF")
            started = True

        # 🟢 heartbeat
        if now - last_heartbeat >= timedelta(minutes=60):
            send("🟢 BOT AKTİF (60 dk)")
            last_heartbeat = now

        # 🗓 günlük reset
        current_day = datetime.utcnow().date()
        if current_day != last_reset_day:
            sent.clear()
            print("Yeni gün reset")
            last_reset_day = current_day

        stocks = []

        # 🔥 1. FMP
        fmp_data = fetch_fmp()

        if isinstance(fmp_data, list) and len(fmp_data) > 0:
            for s in fmp_data:
                try:
                    symbol = s.get("symbol")
                    change = float(s.get("changesPercentage", 0))

                    if symbol:
                        stocks.append((symbol, change))
                except:
                    continue

        # 🔄 fallback Yahoo
        if not stocks:
            yahoo_data = fetch_yahoo()
            for s in yahoo_data:
                try:
                    symbol = s.get("symbol")
                    change = s.get("regularMarketChangePercent", 0)

                    if symbol:
                        stocks.append((symbol, change))
                except:
                    continue

        # 🔥 filtre + tekrar sistemi
        for symbol, change in stocks:

            if not symbol:
                continue

            now_ts = time.time()

            # ⏱ 30 dk kuralı
            if symbol in sent:
                if now_ts - sent[symbol] < 1800:
                    continue

            if change > 1:
                msg = f"""🔥 ULTRA SCANNER
💰 ${symbol}
📈 Change: %{round(change,2)}
"""
                send(msg)
                sent[symbol] = now_ts

        time.sleep(60)

    except Exception as e:
        print("GENEL HATA:", e)
        time.sleep(30)