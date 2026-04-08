import requests
import time
import os
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
FMP_KEY = os.getenv("API_KEY")
POLYGON_KEY = os.getenv("POLYGON_KEY")

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

sent = {}
volume_cache = {}
last_reset_day = datetime.utcnow().date()

def safe_float(val):
    try:
        return float(str(val).replace("%","").replace(",",""))
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
        url = f"https://financialmodelingprep.com/api/v3/stock_market/actives?apikey={FMP_KEY}"
        r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 else []
    except:
        return []

# 🔥 Yahoo
def fetch_yahoo():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=25&scrIds=day_gainers"
        r = requests.get(url, timeout=10)
        data = r.json()
        return data["finance"]["result"][0]["quotes"]
    except:
        return []

# 🔥 Polygon (EN ÖNEMLİ)
def fetch_polygon():
    try:
        url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?apiKey={POLYGON_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        return data.get("tickers", [])
    except:
        return []

last_heartbeat = datetime.utcnow()
started = False
first_cycle = True

while True:
    try:
        now = datetime.utcnow()

        if not started:
            send("🚀 ULTRA SCANNER AKTİF (ULTIMATE)")
            started = True

        if now - last_heartbeat >= timedelta(minutes=60):
            send("🟢 BOT AKTİF")
            last_heartbeat = now

        # reset
        if datetime.utcnow().date() != last_reset_day:
            sent.clear()
            volume_cache.clear()
            last_reset_day = datetime.utcnow().date()

        stocks = []

        # 🔥 1. FMP
        fmp = fetch_fmp()
        print("FMP:", len(fmp))

        # 🔥 2. Yahoo
        yahoo = fetch_yahoo()
        print("Yahoo:", len(yahoo))

        # 🔥 3. Polygon
        polygon = fetch_polygon()
        print("Polygon:", len(polygon))

        # FMP ekle
        for s in fmp:
            stocks.append({
                "symbol": s.get("symbol"),
                "volume": s.get("volume", 0),
                "change": safe_float(s.get("changesPercentage", 0))
            })

        # Yahoo ekle
        for s in yahoo:
            stocks.append({
                "symbol": s.get("symbol"),
                "volume": s.get("regularMarketVolume", 0),
                "change": safe_float(s.get("regularMarketChangePercent", 0))
            })

        # Polygon ekle
        for s in polygon:
            stocks.append({
                "symbol": s.get("ticker"),
                "volume": s.get("day", {}).get("v", 0),
                "change": safe_float(s.get("todaysChangePerc", 0))
            })

        print("Toplam:", len(stocks))

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

                vol_ratio = volume / prev_vol if prev_vol else 1
                volume_cache[symbol] = volume

                now_ts = time.time()

                if symbol in sent and now_ts - sent[symbol] < 1800:
                    continue

                score = ai_score(change, vol_ratio)
                prob = pump_probability(score)

                if score >= 40:
                    send(f"""🚨 AI SIGNAL
💰 ${symbol}
🧠 {score}/100
📊 Pump %{prob}
📊 Vol x{round(vol_ratio,2)}
📈 %{round(change,2)}
""")
                    sent[symbol] = now_ts

            except:
                continue

        first_cycle = False
        time.sleep(120)

    except Exception as e:
        print("HATA:", e)
        time.sleep(30)
        
        import requests
import os

FMP_KEY = os.getenv("API_KEY")
POLYGON_KEY = os.getenv("POLYGON_KEY")

print("FMP KEY:", FMP_KEY)
print("POLYGON KEY:", POLYGON_KEY)

# FMP test
try:
    r = requests.get(f"https://financialmodelingprep.com/api/v3/stock_market/actives?apikey={FMP_KEY}")
    print("FMP status:", r.status_code)
    print("FMP data:", r.text[:200])
except Exception as e:
    print("FMP error:", e)

# Polygon test
try:
    r = requests.get(f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?apiKey={POLYGON_KEY}")
    print("Polygon status:", r.status_code)
    print("Polygon data:", r.text[:200])
except Exception as e:
    print("Polygon error:", e)