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
        url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=100&scrIds=day_gainers"
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()

        return data.get("finance", {}).get("result", [])[0].get("quotes", [])

    except Exception as e:
        print("Yahoo hata:", e)
        return []

def is_good_stock(price, change, volume, symbol):
    # 🔥 1. Fiyat filtresi (low float benzeri alan)
    if not (0.5 < price < 10):
        return False

    # 🔥 2. ERKEN momentum (asıl fark)
    if not (5 < change < 15):
        return False

    # 🔥 3. Hacim filtresi (patlama belirtisi)
    if volume < 800000:
        return False

    # 🔥 4. Büyük hisseleri ele (basit blacklist)
    big_caps = ["AAPL","TSLA","NIO","AMD","NVDA","MSFT","AMZN","META"]
    if symbol in big_caps:
        return False

    return True

def detect_setup(change, volume):
    if change > 10 and volume > 2_000_000:
        return "💣 EARLY SQUEEZE"
    elif change > 7:
        return "🔥 EARLY BREAKOUT"
    else:
        return "⚡ MOMENTUM BUILDING"

def main():
    print("BOT BAŞLADI")
    send("🚀 SHARP BOT AKTİF (EARLY SYSTEM)")

    while True:
        try:
            stocks = get_gainers()

            for s in stocks:
                try:
                    if not isinstance(s, dict):
                        continue

                    symbol = s.get("symbol")
                    price = s.get("regularMarketPrice", 0)
                    change = s.get("regularMarketChangePercent", 0)
                    volume = s.get("regularMarketVolume", 0)

                    if not symbol:
                        continue

                    if symbol in seen:
                        continue

                    # 💣 ANA FİLTRE
                    if not is_good_stock(price, change, volume, symbol):
                        continue

                    setup = detect_setup(change, volume)

                    msg = f"""
🚀 EARLY SIGNAL (SHARP)

Ticker: {symbol}
Price: {price}
Change: %{round(change,2)}
Volume: {volume}

Setup: {setup}
"""

                    send(msg)
                    seen.add(symbol)

                    time.sleep(0.5)

                except Exception as e:
                    print("Hisse hata:", e)
                    continue

            time.sleep(180)

        except Exception as e:
            print("MAIN HATA:", e)
            time.sleep(60)

main()