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

def get_gainers():
    url = f"https://financialmodelingprep.com/api/v3/stock_market/gainers?apikey={API_KEY}"
    try:
        return requests.get(url).json()
    except:
        return []

def get_float(symbol):
    try:
        url = f"https://financialmodelingprep.com/api/v4/shares_float?symbol={symbol}&apikey={API_KEY}"
        data = requests.get(url).json()
        return float(data[0]["floatShares"])
    except:
        return None

def get_news(symbol):
    try:
        url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={symbol}&limit=5&apikey={API_KEY}"
        data = requests.get(url).json()
        text = " ".join([n["title"].lower() for n in data])
        return text
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
    send("🚀 PRO BOT AKTİF (CANLI)")

    while True:
        stocks = get_gainers()  # ✅ GERÇEK VERİ

        for s in stocks:
            try:
                symbol = s["symbol"]
                price = float(s["price"])
                change = float(s["changesPercentage"].replace("%",""))
                volume = float(s["volume"])

                # ANA FİLTRE
                if not (0.5 < price < 10 and change > 10 and volume > 1_000_000):
                    continue

                # SPAM ENGEL (30 dk)
                now = time.time()
                if symbol in seen and now - seen[symbol] < 1800:
                    continue

                # FLOAT FİLTRE
                float_val = get_float(symbol)
                if float_val is None or float_val > 20_000_000:
                    continue

                # NEWS FİLTRE
                news_text = get_news(symbol)
                news_score = analyze_news(news_text)

                if news_score < 0:
                    continue

                # SETUP
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
                seen[symbol] = now

                time.sleep(0.5)

            except:
                continue

        time.sleep(120)

main()