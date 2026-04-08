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

    if change > 1:
        score += 10
    if change > 3:
        score += 20
    if change > 5:
        score += 30

    if vol_ratio > 1.5:
        score += 20
    if vol_ratio > 2:
        score += 30
    if vol_ratio > 3:
        score += 40

    return min(score, 100)

def pump_probability(score):
    return min(100, int(score * 1.2))

def fetch_data():
    url = f"https://financialmodelingprep.com/api/v3/stock_market/actives?apikey={API_KEY}"
    
    for _ in range(3):
        try:
            r = requests.get(url, timeout=20)

            if r.status_code == 429:
                print("Rate limit bekleniyor...")
                time.sleep(120)
                continue

            return r.json()

        except Exception as e:
            print("API hata:", e)
            time.sleep(5)

    return []

last_heartbeat = datetime.utcnow()
started = False
first_cycle = True  # 🔥 kritik

while True:
    try:
        now = datetime.utcnow()

        # 🚀 başlangıç
        if not started:
            send("🚀 AI VOLUME SCANNER AKTİF (FIXED)")
            started = True

        # 🟢 heartbeat
        if now - last_heartbeat >= timedelta(minutes=60):
            send("🟢 BOT AKTİF (60 dk)")
            last_heartbeat = now

        # 🗓 reset
        current_day = datetime.utcnow().date()
        if current_day != last_reset_day:
            sent.clear()
            volume_cache.clear()
            print("Yeni gün reset")
            last_reset_day = current_day

        data = fetch_data()

        print("Veri sayısı:", len(data))  # 🔥 debug

        for stock in data:
            try:
                symbol = stock.get("symbol")
                volume = stock.get("volume", 0)
                change = safe_float(stock.get("changesPercentage", 0))

                if not symbol or volume == 0:
                    continue

                prev_vol = volume_cache.get(symbol)

                # 🔥 İLK TURDA SADECE CACHE DOLDUR
                if first_cycle:
                    volume_cache[symbol] = volume
                    continue

                if prev_vol and prev_vol > 0:
                    vol_ratio = volume / prev_vol
                else:
                    vol_ratio = 1

                volume_cache[symbol] = volume

                now_ts = time.time()

                if symbol in sent:
                    if now_ts - sent[symbol] < 1800:
                        continue

                score = ai_score(change, vol_ratio)
                prob = pump_probability(score)

                print(symbol, "chg:", change, "volx:", round(vol_ratio,2), "score:", score)

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

        first_cycle = False  # 🔥 ilk tur bitti

        time.sleep(120)

    except Exception as e:
        print("GENEL HATA:", e)
        time.sleep(30)