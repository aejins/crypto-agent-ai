import os
import requests
import json
from datetime import datetime

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ Brak BOT_TOKEN w zmiennych środowiskowych")

CHAT_IDS_FILE = "chat_ids.txt"
NEWS_FILE = "weekly_news.json"
OFFSET_FILE = "offset.txt"

COINGECKO_API = "https://api.coingecko.com/api/v3"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

MAX_MSG_LEN = 3900
TIMEOUT = 10

# ================= CHAT IDS =================
def get_chat_ids():
    try:
        with open(CHAT_IDS_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def save_chat_ids():
    offset = 0
    try:
        with open(OFFSET_FILE, "r") as f:
            offset = int(f.read().strip())
    except:
        pass

    resp = requests.get(
        f"{TELEGRAM_API}/getUpdates",
        params={"offset": offset},
        timeout=TIMEOUT
    ).json()

    chat_ids = set(get_chat_ids())
    last_update_id = offset

    for update in resp.get("result", []):
        last_update_id = update["update_id"] + 1
        if "message" in update:
            chat_ids.add(str(update["message"]["chat"]["id"]))

    with open(CHAT_IDS_FILE, "w") as f:
        f.write("\n".join(chat_ids))

    with open(OFFSET_FILE, "w") as f:
        f.write(str(last_update_id))

# ================= TELEGRAM =================
def send_message(text):
    chat_ids = get_chat_ids()
    if not chat_ids:
        return

    chunks = [text[i:i+MAX_MSG_LEN] for i in range(0, len(text), MAX_MSG_LEN)]

    for chat_id in chat_ids:
        for chunk in chunks:
            requests.post(
                f"{TELEGRAM_API}/sendMessage",
                data={
                    "chat_id": chat_id,
                    "text": chunk,
                    "parse_mode": "Markdown"
                },
                timeout=TIMEOUT
            )

# ================= COINGECKO =================
def get_top100_altbtc():
    try:
        resp = requests.get(
            f"{COINGECKO_API}/coins/markets",
            params={
                "vs_currency": "btc",
                "order": "market_cap_desc",
                "per_page": 100,
                "page": 1
            },
            timeout=TIMEOUT
        )
        data = resp.json()
    except Exception:
        return None

    if not isinstance(data, list):
        return None

    coins = []
    for c in data:
        coins.append({
            "name": c["name"],
            "symbol": c["symbol"].upper(),
            "price_btc": c["current_price"]
        })

    return coins

# ================= REPORTS =================
def build_daily_report():
    coins = get_top100_altbtc()
    if not coins:
        return "⚠️ Błąd pobierania danych z CoinGecko"

    coins_sorted = sorted(coins, key=lambda x: x["price_btc"], reverse=True)

    top10 = coins_sorted[:10]
    bottom10 = coins_sorted[-10:]

    report = f"📅 *{datetime.now().date()}*\n"
    report += "*📊 DAILY ALT/BTC REPORT*\n\n"

    report += "🔥 *TOP 10 ALT vs BTC*\n"
    for c in top10:
        report += f"{c['symbol']} — `{c['price_btc']:.8f} BTC`\n"

    report += "\n🩸 *BOTTOM 10 ALT vs BTC*\n"
    for c in bottom10:
        report += f"{c['symbol']} — `{c['price_btc']:.8f} BTC`\n"

    return report

def analyze_weekly_trend():
    try:
        with open(NEWS_FILE, "r") as f:
            news = json.load(f)
    except:
        news = []

    score = sum(n.get("impact", 0) for n in news)

    if score > 3:
        trend = "🟢 Trend pozytywny"
    elif score < -3:
        trend = "🔴 Trend negatywny"
    else:
        trend = "🟡 Trend neutralny"

    return trend, len(news)

def clear_weekly_news():
    with open(NEWS_FILE, "w") as f:
        json.dump([], f)

# ================= MAIN =================
def daily_report():
    save_chat_ids()
    report = build_daily_report()
    send_message(report)

def weekly_report():
    save_chat_ids()
    trend, total = analyze_weekly_trend()

    report = f"📅 *{datetime.now().date()}*\n"
    report += "*📈 WEEKLY SUMMARY*\n\n"
    report += f"News count: {total}\n"
    report += f"{trend}"

    send_message(report)
    clear_weekly_news()

# ================= RUN =================
if __name__ == "__main__":
    today = datetime.today().weekday()  # 0 = Monday

    daily_report()
    if today == 0:
        weekly_report()
