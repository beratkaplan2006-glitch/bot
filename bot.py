import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

send("⚡ SCANNER BOT AKTİF")

def get_gainers():
    url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=25&scrIds=day_gainers"
    r = requests.get(url).json()

    results = r["finance"]["result"][0]["quotes"]

    stocks = []

    for s in results:
        try:
            price = s.get("regularMarketPrice", 0)
            change = s.get("regularMarketChangePercent", 0)
            volume = s.get("regularMarketVolume", 0)
            symbol = s.get("symbol")

            if price < 20 and change > 10:
                stocks.append((symbol, change, volume))

        except:
            continue

    return stocks

sent = set()

while True:
    try:
        stocks = get_gainers()

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

        time.sleep(30)

    except Exception as e:
        print(e)
        time.sleep(10)