import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

seen = set()

headers = {
    "User-Agent": "Mozilla/5.0"
}

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_gainers():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=50&scrIds=day_gainers"
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()

        quotes = data.get("finance", {}).get("result", [])[0].get("quotes", [])
        return quotes

    except Exception as e:
        print("Yahoo hata:", e)
        return []

def main():
    print("BOT BAŞLADI")
    send("🚀 FREE BOT AKTİF (YAHOO FIX)")

    while True:
        try:
            stocks = get_gainers()

            for s in stocks:
                try:
                    symbol = s.get("symbol")
                    price = s.get("regularMarketPrice", 0)
                    change = s.get("regularMarketChangePercent", 0)
                    volume = s.get("regularMarketVolume", 0)

                    if not symbol:
                        continue

                    if not (0.5 < price < 10):
                        continue

                    if change < 5:
                        continue

                    if volume < 500000:
                        continue

                    if symbol in seen:
                        continue

                    msg = f"""
🚀 EARLY SIGNAL

Ticker: {symbol}
Price: {price}
Change: %{round(change,2)}
Volume: {volume}
"""

                    send(msg)
                    seen.add(symbol)

                except:
                    continue

            time.sleep(180)

        except Exception as e:
            print("MAIN HATA:", e)
            time.sleep(60)

main()