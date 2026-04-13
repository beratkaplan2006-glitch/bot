import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

seen = {}

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

# 💣 RUNNER SKOR
def calculate_score(price, change, volume):
    score = 0

    # fiyat (ucuz = iyi)
    if price < 5:
        score += 2
    elif price < 8:
        score += 1

    # erken hareket
    if 3 < change < 8:
        score += 2
    elif 8 <= change < 12:
        score += 3

    # hacim
    if volume > 5_000_000:
        score += 3
    elif volume > 2_000_000:
        score += 2
    elif volume > 1_000_000:
        score += 1

    return score

def main():
    print("RUNNER BOT BAŞLADI")
    send("💣 RUNNER BOT AKTİF")

    while True:
        try:
            stocks = get_gainers()
            now = time.time()

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

                    # tekrar sinyal (30 dk)
                    if symbol in seen and now - seen[symbol] < 1800:
                        continue

                    # 💣 ANA FİLTRE
                    if not (0.3 < price < 8):
                        continue

                    if not (3 < change < 12):
                        continue

                    if volume < 800000:
                        continue

                    # büyük hisseleri ele
                    big_caps = ["AAPL","TSLA","NIO","AMD","NVDA","MSFT","AMZN","META","NOK"]
                    if symbol in big_caps:
                        continue

                    # 💣 SKOR
                    score = calculate_score(price, change, volume)

                    # düşük skoru ele
                    if score < 4:
                        continue

                    # setup
                    if score >= 7:
                        setup = "💣 HIGH PROB RUNNER"
                    elif score >= 5:
                        setup = "🔥 POTENTIAL RUNNER"
                    else:
                        setup = "⚡ EARLY MOVE"

                    msg = f"""
💣 RUNNER ALERT

Ticker: {symbol}
Price: {price}
Change: %{round(change,2)}
Volume: {volume}

Score: {score}/10
Setup: {setup}
"""

                    send(msg)
                    seen[symbol] = now

                    time.sleep(0.5)

                except Exception as e:
                    print("Hisse hata:", e)
                    continue

            time.sleep(180)

        except Exception as e:
            print("MAIN HATA:", e)
            time.sleep(60)

main()