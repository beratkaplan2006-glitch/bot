import requests
import time
import re

# ===== AYARLAR =====
TELEGRAM_TOKEN = "BURAYA_BOT_TOKEN"
CHAT_ID = "BURAYA_CHAT_ID"

# Takip edilecek hesaplar
ACCOUNTS = [
    "Benzinga",
    "unusual_whales",
    "DeItaone",
    "financialjuice"
]

# Anahtar kelimeler
KEYWORDS = [
    "partnership", "deal", "agreement", "acquisition",
    "merger", "AI", "crypto", "FDA", "approval",
    "contract", "expansion", "earnings"
]

# Daha önce atılan tweetleri tut
seen_tweets = set()

# ===== TELEGRAM GÖNDER =====
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

# ===== TICKER BUL =====
def extract_ticker(text):
    matches = re.findall(r'\$[A-Z]{2,5}', text)
    return matches

# ===== TWEET ÇEK =====
def get_tweets(username):
    url = f"https://cdn.syndication.twimg.com/widgets/timelines/profile?screen_name={username}"
    try:
        r = requests.get(url)
        data = r.json()
        return data.get("body", "")
    except:
        return ""

# ===== ANA LOOP =====
while True:
    for account in ACCOUNTS:
        content = get_tweets(account)

        if not content:
            continue

        tweets = content.split("timeline-Tweet-text")

        for tweet in tweets:
            if tweet in seen_tweets:
                continue

            seen_tweets.add(tweet)

            # Keyword kontrol
            if any(k.lower() in tweet.lower() for k in KEYWORDS):

                tickers = extract_ticker(tweet)

                msg = f"🚨 HABER YAKALANDI\n\nHesap: @{account}\n"

                if tickers:
                    msg += f"Hisse: {' '.join(tickers)}\n"

                msg += f"\nTweet:\n{tweet[:300]}"

                send_telegram(msg)
                print(msg)

    time.sleep(30)