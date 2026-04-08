import requests
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Telegram hata")

send("⚡ SCANNER BOT AKTİF (PRO)")

last_heartbeat = datetime.utcnow()

# 🔥 NASDAQ LİSTE
def load_nasdaq():
    url = "https://raw.githubusercontent.com/datasets/nasdaq-listings/master/data/nasdaq-listed-symbols.csv"
    
    try:
        r = requests.get(url, timeout=10)
        lines = r.text.split("\n")[1:]

        tickers = set()

        for line in lines:
            parts = line.split(",")
            if len(parts) > 0:
                ticker = parts[0].strip()
                if ticker:
                    tickers.add(ticker)

        print("NASDAQ yüklendi:", len(tickers))
        return tickers

    except Exception as e:
        print("NASDAQ yüklenemedi:", e)
        return set()

VALID_TICKERS = load_nasdaq()

# 🔥 SCRAPER
def get_gainers():
    url = "https://www.investing.com/equities/top-stock-gainers"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        rows = soup.select("table tbody tr")

        stocks = []

        for row in rows[:20]:
            try:
                cols = row.find_all("td")

                name = cols[1].text.strip()
                change_text = cols[4].text.strip().replace("%", "").replace(",", "")

                # ticker çek
                if "(" in name and ")" in name:
                    symbol = name.split("(")[-1].replace(")", "").strip()
                else:
                    continue

                change = float(change_text)

                # 🔥 NASDAQ doğrulama
                if symbol in VALID_TICKERS and change > 2:
                    stocks.append((symbol, change))

            except:
                continue

        return stocks

    except Exception as e:
        print("SCRAPE HATA:", e)
        return []

sent = set()

while True:
    try:
        now = datetime.utcnow()

        # 🟢 HEARTBEAT
        if now - last_heartbeat >= timedelta(minutes=60):
            send("🟢 SCANNER AKTİF (60 dk kontrol)")
            last_heartbeat = now

        stocks = get_gainers()

        if not stocks:
            print("Uygun hisse yok (normal)")

        for sym, change in stocks:

            if sym in sent:
                continue

            msg = f"""🔥 SCANNER (PRO)
💰 ${sym}
📈 Change: %{round(change,2)}
"""

            send(msg)
            sent.add(sym)

        time.sleep(60)

    except Exception as e:
        print("LOOP HATA:", e)
        time.sleep(30)