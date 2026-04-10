import requests
import time
import os

API_KEY = os.getenv("API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

seen = {}

GOOD_NEWS = ["ai", "contract", "fda", "partnership", "award", "earnings"]
BAD_NEWS = ["offering", "dilution", "bankruptcy", "shelf"]

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def analyze_news(text):
    score = 0
    for w in GOOD_NEWS:
        if w in text:
            score += 1
    for w in BAD_NEWS:
        if w in text:
            score -= 2
    return score

def detect_setup(change, volume):
    if change > 30 and volume > 2_000_000:
        return "💣 SQUEEZE"
    elif change > 15:
        return "🔥 BREAKOUT"
    else:
        return "⚡ MOMENTUM"

def main():
    # ✅ TEST MESAJI
    send("🧪 TEST MESAJI - BOT ÇALIŞIYOR")
    send("🚀 PRO BOT AKTİF (v3 TEST)")

    while True:

        # ✅ SAHTE TEST VERİSİ (ZORLA SİNYAL)
        stocks = [{
            "symbol": "TEST",
            "price": "2.5",
            "changesPercentage": "25%",
            "volume": "2000000"
        }]

        for s in stocks:
            try:
                symbol = s["symbol"]
                price = float(s["price"])
                change = float(s["changesPercentage"].replace("%",""))
                volume = float(s["volume"])

                now = time.time()
                if symbol in seen and now - seen[symbol] < 1800:
                    continue

                # Fake float + news (test için)
                float_val = 10_000_000
                news_score = 1

                setup = detect_setup(change, volume)

                msg = f"""
🚀 TEST SIGNAL

Ticker: {symbol}
Price: {price}
Change: %{change}
Volume: {int(volume)}

Float: {int(float_val)}
Setup: {setup}
News Score: {news_score}
"""

                send(msg)
                seen[symbol] = now

            except:
                continue

        time.sleep(60)

main()