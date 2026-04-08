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
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print("Telegram hata:", e)

# 🔁 tekrar kontrol
sent = {}

# 🗓 günlük reset
last_reset_day = datetime.utcnow().date()

# 🔄 kaynak değiştirici (rate limit azaltır)
use_fmp = True

# 🔥 güçlü fetch
def fetch_json(url, retries=3, delay=5):
    for i in range(retries):
        try:
            r = requests.get(url, timeout=20)

            # 🚨 RATE LIMIT
            if r.status_code == 429:
                print("RATE LIMIT! 2 dk bekleniyor...")
                time.sleep(120)
                continue

            if r.status_code != 200:
                print("Status hata:", r.status_code)
                time.sleep(delay)
                continue

            return r.json()

        except Exception as e:
            print("Fetch hata:", e)
            time.sleep(delay)

    return None

def fetch_fmp():
    url = f"https://financialmodelingprep.com/api/v3/stock_market/gainers?apikey={API_KEY}"
    return fetch_json(url)

def fetch_yahoo():
    url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=20&scrIds=day_gainers"
    data = fetch_json(url)

    try:
        return data["finance"]["result"][0]["quotes"]
    except:
        return []

last_heartbeat = datetime.utcnow()
started = False

while True:
    try:
        now = datetime.utcnow()

        # 🚀 başlangıç mesajı
        if not started:
            send("🚀 ULTRA SCANNER AKTİF (STABLE v2)")
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

        # 🔄 sırayla kaynak kullan (rate limit çözümü)
        if use_fmp:
            print("FMP kullanılıyor")
            data = fetch_fmp()
            use_fmp = False

            if isinstance(data, list):
                for s in data:
                    try:
                        symbol = s.get("symbol")
                        change = float(s.get("changesPercentage", 0))
                        if symbol:
                            stocks.append((symbol, change))
                    except:
                        continue

        else:
            print("Yahoo kullanılıyor")
            data = fetch_yahoo()
            use_fmp = True

            for s in data:
                try:
                    symbol = s.get("symbol")
                    change = s.get("regularMarketChangePercent", 0)
                    if symbol:
                        stocks.append((symbol, change))
                except:
                    continue

        # 🔥 sinyal sistemi
        for symbol, change in stocks:

            if not symbol:
                continue

            now_ts = time.time()

            # ⏱ 30 dk tekrar kuralı
            if symbol in sent:
                if now_ts - sent[symbol] < 1800:
                    continue

            if change and change > 1:
                msg = f"""🔥 ULTRA SCANNER
💰 ${symbol}
📈 Change: %{round(change,2)}
"""
                send(msg)
                sent[symbol] = now_ts

        # 🔥 RATE LIMIT FIX (EN ÖNEMLİ)
        time.sleep(120)

    except Exception as e:
        print("GENEL HATA:", e)
        time.sleep(30)