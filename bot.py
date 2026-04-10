import requests
import time
import os

API_KEY = os.getenv("API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

seen = {}

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_gainers():
    url = f"https://financialmodelingprep.com/api/v3/stock_market/gainers?apikey={API_KEY}"
    try:
        return requests.get(url).json()
    except:
        return []

def detect_setup(change, volume):
    if change > 30 and volume > 2_000_000:
        return "💣 SQUEEZE"
    elif change > 15:
        return "🔥 BREAKOUT"
    else:
        return "⚡ MOMENTUM"

def main():
    send("🚀 Momentum Bot v2 aktif!")

    while True:
        stocks = get_gainers()

        for s in stocks:
            try:
                symbol = s["symbol"]
                price = float(s["price"])
                change = float(s["changesPercentage"].replace("%",""))
                volume = float(s["volume"])

                # Ana filtre
                if not (0.5 < price < 10 and change > 10 and volume > 1_000_000):
                    continue

                # Spam engelle (aynı hisse 30 dk tekrar atılmaz)
                now = time.time()
                if symbol in seen and now - seen[symbol] < 1800:
                    continue

                setup = detect_setup(change, volume)

                msg = f"""
🚀 STOCK SIGNAL

Ticker: {symbol}
Price: {price}
Change: %{change}
Volume: {int(volume)}

Setup: {setup}
"""

                send(msg)
                seen[symbol] = now

                time.sleep(0.5)

            except:
                continue

        time.sleep(120)

main()