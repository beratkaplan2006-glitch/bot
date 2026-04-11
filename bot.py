import requests
import time
import os

API_KEY = os.getenv("API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

seen = set()

GOOD_NEWS = ["ai", "contract", "fda", "partnership", "award", "earnings"]
BAD_NEWS = ["offering", "dilution", "bankruptcy", "shelf"]

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Telegram hata:", e)

def get_gainers():
    try:
        url = f"https://financialmodelingprep.com/api/v3/stock_market/gainers?apikey={API_KEY}"
        res = requests.get(url, timeout=10)
        return res.json()
    except Exception as e:
        print("Gainers hata:", e)
        return []

def get_float(symbol):
    try:
        url = f"https://financialmodelingprep.com/api/v4/shares_float?symbol={symbol}&apikey={API_KEY}"
        res = requests.get(url, timeout=10).json()
        return float(res[0]["floatShares"])
    except:
        return None

def get_news(symbol):
    try:
        url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={symbol}&limit=5&apikey={API_KEY}"
        res = requests.get(url, timeout=10).json()
        return " ".join([n["title"].lower() for n in res])
    except:
        return ""

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
    print("BOT BAŞLADI")  # log için
    send("🚀 PRO BOT AKTİF (STABLE)")

    while True:
        try:
            stocks = get_gainers()

            for s in stocks:
                try:
                    symbol = s.get("symbol")
                    price = float(s.get("price", 0))
                    change = float(str(s.get("changesPercentage", "0")).replace("%", ""))
                    volume = float(s.get("volume", 0))

                    if not symbol:
                        continue

                    # ANA FİLTRE
                    if not (0.5 < price < 10 and change > 10 and volume > 1_000_000):
                        continue

                    # SPAM ENGEL
                    if symbol in seen:
                        continue

                    # FLOAT
                    float_val = get_float(symbol)
                    if float_val is None or float_val > 20_000_000:
                        continue

                    # NEWS
                    news_text = get_news(symbol)
                    news_score = analyze_news(news_text)

                    if news_score < 0:
                        continue

                    setup = detect_setup(change, volume)

                    msg = f"""
🚀 PRO SIGNAL

Ticker: {symbol}
Price: {price}
Change: %{change}
Volume: {int(volume)}

Float: {int(float_val)}
Setup: {setup}
News Score: {news_score}
"""

                    send(msg)
                    seen.add(symbol)

                    time.sleep(0.5)

                except Exception as e:
                    print("Hisse hata:", e)
                    continue

            time.sleep(120)

        except Exception as e:
            print("MAIN LOOP HATA:", e)
            time.sleep(30)

main()