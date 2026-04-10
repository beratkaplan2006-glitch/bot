import requests
import time

API_KEY = "FMP_API_KEY"
TELEGRAM_TOKEN = "TELEGRAM_BOT_TOKEN"
CHAT_ID = "CHAT_ID"

sent = set()

GOOD_KEYWORDS = ["ai", "contract", "fda", "partnership", "award", "earnings"]
BAD_KEYWORDS = ["offering", "dilution", "bankruptcy", "shelf"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

def get_gainers():
    url = f"https://financialmodelingprep.com/api/v3/stock_market/gainers?apikey={API_KEY}"
    return requests.get(url).json()

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
        texts = " ".join([n["title"].lower() for n in data])
        return texts
    except:
        return ""

def news_score(text):
    score = 0
    for word in GOOD_KEYWORDS:
        if word in text:
            score += 1
    for word in BAD_KEYWORDS:
        if word in text:
            score -= 2
    return score

def detect_setup(change, volume):
    if change > 20 and volume > 2_000_000:
        return "🔥 BREAKOUT"
    elif change > 10:
        return "⚡ MOMENTUM"
    else:
        return "👀 WATCH"

def main():
    while True:
        stocks = get_gainers()

        for s in stocks:
            try:
                symbol = s["symbol"]
                price = float(s["price"])
                change = float(s["changesPercentage"].replace("%",""))
                volume = float(s["volume"])

                if symbol in sent:
                    continue

                # Ana filtre
                if not (0.5 < price < 10 and change > 10 and volume > 1_000_000):
                    continue

                # Float
                float_val = get_float(symbol)
                if float_val is None or float_val > 20_000_000:
                    continue

                # News
                news_text = get_news(symbol)
                score = news_score(news_text)

                if score < 0:
                    continue

                setup = detect_setup(change, volume)

                msg = f"""
🚀 STOCK ALERT

Ticker: {symbol}
Price: {price}
Change: %{change}
Volume: {volume}

Float: {int(float_val)}
Setup: {setup}
News Score: {score}
"""

                send_telegram(msg)
                sent.add(symbol)

                time.sleep(1)

            except:
                continue

        time.sleep(180)

main()