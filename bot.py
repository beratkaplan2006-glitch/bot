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

sent = {}
volume_cache = {}
last_reset_day = datetime.utcnow().date()

def safe_float(val):
    try:
        return float(str(val).replace("%", "").replace(",", ""))
    except:
        return 0.0

def ai_score(change, vol_ratio):
    score = 0
    if change > 1: score += 10
    if change > 3: score += 20
    if change > 5: score += 30

    if vol_ratio > 1.5: score += 20
    if vol_ratio > 2: score += 30
    if vol_ratio > 3: score += 40

    return min(score, 100)

def pump_probability(score):
    return min(100, int(score * 1.2))

# 🔥 FMP
def fetch_fmp():
    try:
        url = f"https://financialmodelingprep.com/api/v3/stock_market/actives?apikey={API_KEY}"
        r = requests.get(url, timeout=15)

        if r.status_code == 429:
            print("FMP rate limit")
            return []

        data = r.json()
        return data if isinstance(data, list) else []
    except:
        return []

# 🔥 Yahoo (fallback)
def fetch_yahoo():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=25&scrIds=day_gainers"
        r = requests.get(url, timeout=15)
        data = r.json()

        quotes = data["finance"]["result"][0]["quotes"]

        # ⚠️ boş veya saçma veri kontrolü
        if not quotes or len(quotes) < 3:
            print("Yahoo veri yetersiz")
            return []

        return quotes
    except:
        print("Yahoo hata/ban")
        return []

last_heartbeat = datetime.utcnow()
started = False
first_cycle = True

while True:
    try:
        now = datetime.utcnow()

        if not started:
            send("🚀 AI VOLUME SCANNER AKTİF (SMART)")
            started = True

        if now - last_heartbeat >= timedelta(minutes=60):
            send("🟢 BOT AKTİF (60 dk)")
            last_heartbeat = now

        # 🗓 reset
        current_day = datetime.utcnow().date()
        if current_day != last_reset_day:
            sent.clear()
            volume_cache.clear()
            last_reset_day = current_day

        stocks = []

        # 🔥 FMP çek
        fmp_data = fetch_fmp()
        print("FMP veri:", len(fmp_data))

        # 🔥 yeterliyse sadece FMP
        if len(fmp_data) >= 5:
            for s in fmp_data:
                stocks.append({
                    "symbol": s.get("symbol"),
                    "volume": s.get("volume", 0),
                    "change": safe_float(s.get("changesPercentage", 0))
                })

        else:
            print("FMP yetersiz → Yahoo deneniyor")
            yahoo_data = fetch_yahoo()

            if yahoo_data:
                for s in yahoo_data:
                    stocks.append({
                        "symbol": s.get("symbol"),
                        "volume": s.get("regularMarketVolume", 0),
                        "change": safe_float(s.get("regularMarketChangePercent", 0))
                    })
            else:
                print("Yahoo da başarısız → skip")

        print("Toplam veri:", len(stocks))

        for stock in stocks:
            try:
                symbol = stock["symbol"]
                volume = stock["volume"]
                change = stock["change"]

                if not symbol or volume == 0:
                    continue

                prev_vol = volume_cache.get(symbol)

                if first_cycle:
                    volume_cache[symbol] = volume
                    continue

                vol_ratio = volume / prev_vol if prev_vol and prev_vol > 0 else 1
                volume_cache[symbol] = volume

                now_ts = time.time()

                if symbol in sent and now_ts - sent[symbol] < 1800:
                    continue

                score = ai_score(change, vol_ratio)
                prob = pump_probability(score)

                print(symbol, change, "volx:", round(vol_ratio,2), "score:", score)

                if score >= 40:
                    msg = f"""🚨 AI SIGNAL
💰 ${symbol}
🧠 Skor: {score}/100
📊 Pump: %{prob}
📊 Volume x{round(vol_ratio,2)}
📈 Change: %{round(change,2)}
"""
                    send(msg)
                    sent[symbol] = now_ts

            except:
                continue

        first_cycle = False
        time.sleep(120)

    except Exception as e:
        print("GENEL HATA:", e)
        time.sleep(30)