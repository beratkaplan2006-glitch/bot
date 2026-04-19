import requests
import time
import re
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

ACCOUNTS = [
    "Benzinga",
    "unusual_whales",
    "DeItaone",
    "financialjuice"
]

KEYWORDS = [
    "partnership", "deal", "agreement", "acquisition",
    "merger", "AI", "crypto", "FDA", "approval",
    "contract", "expansion", "earnings"
]

seen_tweets = set()

# ===== TELEGRAM =====
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ===== TICKER =====
def extract_ticker(text):
    return re.findall(r'\$[A-Z]{2,5}', text)

# ===== FİYAT + HACİM =====
def check_stock(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker[1:]}"
        r = requests.get(url).json()

        result = r["chart"]["result"][0]
        meta = result["meta"]

        price = meta["regularMarketPrice"]
        prev = meta["chartPreviousClose"]
        volume = meta["regularMarketVolume"]

        change_pct = ((price - prev) / prev) * 100

        return price, change_pct, volume
    except:
        return None, None, None

# ===== TWEET =====
def get_tweets(username):
    url = f"https://cdn.syndication.twimg.com/widgets/timelines/profile?screen_name={username}"
    try:
        return requests.get(url).json().get("body", "")
    except:
        return ""

# ===== ANA LOOP =====
while True:
    for account in ACCOUNTS:
        content = get_tweets(account)
        tweets = content.split("timeline-Tweet-text")

        for tweet in tweets:
            if tweet in seen_tweets:
                continue

            seen_tweets.add(tweet)

            if not any(k.lower() in tweet.lower() for k in KEYWORDS):
                continue

            tickers = extract_ticker(tweet)
            if not tickers:
                continue

            for ticker in tickers:
                price, change, volume = check_stock(ticker)

                if price is None:
                    continue

                # 🔥 FİLTRELER
                if change < 3:   # %3 altı alma
                    continue

                if volume < 1_000_000:  # düşük hacim alma
                    continue

                msg = f"""
🚀 FİLTRELİ SİNYAL

Hesap: @{account}
Hisse: {ticker}

Fiyat: {price}
Değişim: %{round(change,2)}
Hacim: {volume}

Tweet:
{tweet[:200]}
"""
                send_telegram(msg)
                print(msg)

    time.sleep(30)