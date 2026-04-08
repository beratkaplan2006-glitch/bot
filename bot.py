import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_KEY = "demo"  # sonra ücretsiz key al

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

send("⚡ SCANNER AKTİF (FMP)")

sent = set()

while True:
    try:
        url = f"https://financialmodelingprep.com/api/v3/stock_market/gainers?apikey={API_KEY}"
        data = requests.get(url).json()

        for stock in data:
            symbol = stock["symbol"]
            change = stock["changesPercentage"]

            if symbol in sent:
                continue

            if change > 1:
                msg = f"""🔥 SCANNER
💰 ${symbol}
📈 Change: {change}
"""
                send(msg)
                sent.add(symbol)

        time.sleep(60)

    except Exception as e:
        print(e)
        time.sleep(30)