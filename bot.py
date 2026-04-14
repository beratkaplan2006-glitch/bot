import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

headers = {
    "User-Agent": "Mozilla/5.0"
}

# 🧠 hafıza sistemi
seen_stocks = {}  # {symbol: last_score}

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
    except:
        return []

def calculate_score(price, change, volume):
    score = 0

    if price < 5:
        score += 2
    elif price < 8:
        score += 1

    if 5 < change < 10:
        score += 2
    elif change >= 10:
        score += 3

    if volume > 5_000_000:
        score += 3
    elif volume > 2_000_000:
        score += 2
    else:
        score += 1

    return score

def get_setup(score):
    if score >= 8:
        return "💣 STRONG RUNNER"
    elif score >= 6:
        return "🔥 POTENTIAL RUNNER"
    else:
        return "⚡ WEAK"

def main():
    print("BOT BAŞLADI")
    send("🚀 SPAM FIX BOT AKTİF")

    while True:
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

                score = calculate_score(price, change, volume)

                # 🎯 düşükleri at
                if score < 6:
                    continue

                last_score = seen_stocks.get(symbol)

                # 🧠 1. ilk defa geliyorsa
                if symbol not in seen_stocks:
                    seen_stocks[symbol] = score

                    msg = f"""
🚀 RUNNER ALERT

Ticker: {symbol}
Price: {price}
Change: %{round(change,2)}
Volume: {volume}

Score: {score}/10
Setup: {get_setup(score)}
"""
                    send(msg)

                # 🔥 2. güçlenmişse tekrar at
                elif score > last_score:
                    seen_stocks[symbol] = score

                    msg = f"""
📈 POWER UP

Ticker: {symbol}
Price: {price}
Change: %{round(change,2)}
Volume: {volume}

Score: {score}/10 (ARTTI)
Setup: {get_setup(score)}
"""
                    send(msg)

                # ❌ aynıysa hiçbir şey yapma

                time.sleep(0.3)

            except Exception as e:
                print("Hisse hata:", e)

        time.sleep(180)

main()