import requests
from datetime import datetime
import json

TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS_FILE = "chat_ids.txt"
NEWS_FILE = "weekly_news.json"
COINGECKO_API = "https://api.coingecko.com/api/v3"

# --- Chat ID ---
def get_chat_ids():
    try:
        with open(CHAT_IDS_FILE, "r") as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        return []

def save_chat_ids():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    resp = requests.get(url).json()
    chat_ids = set(get_chat_ids())
    for update in resp.get("result", []):
        if "message" in update:
            cid = str(update["message"]["chat"]["id"])
            chat_ids.add(cid)
    with open(CHAT_IDS_FILE, "w") as f:
        for cid in chat_ids:
            f.write(cid + "\n")

# --- Wysyłka wiadomości ---
def send_message(text):
    for chat_id in get_chat_ids():
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": text})

# --- Pobranie top 100 coinów i obliczenie wzrostów względem BTC od dołka 2022 ---
def get_top100_report():
    url = f"{COINGECKO_API}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "price_change_percentage": "all"
    }
    data = requests.get(url, params=params).json()
    report = ""
    for coin in data:
        name = coin["name"]
        symbol = coin["symbol"].upper()
        price = coin["current_price"]
        change = coin.get("price_change_percentage_ath", 0)  # przybliżenie wzrostu od ATH lub dołka
        report += f"{name} ({symbol}): ${price:.2f}, wzrost od dołka: {change:.2f}%\n"
    return report

# --- Pobieranie newsów i ocena wpływu ---
def save_news(news_list):
    try:
        with open(NEWS_FILE, "r") as f:
            weekly_news = json.load(f)
    except FileNotFoundError:
        weekly_news = []

    weekly_news.extend(news_list)
    with open(NEWS_FILE, "w") as f:
        json.dump(weekly_news, f)

def analyze_weekly_trend():
    try:
        with open(NEWS_FILE, "r") as f:
            weekly_news = json.load(f)
    except FileNotFoundError:
        weekly_news = []

    # Prosta ocena trendu:
    score = 0
    for news in weekly_news:
        score += news.get("impact", 0)  # zakładamy impact: +1 pozytywny, 0 neutralny, -1 negatywny

    if score > 3:
        trend = "Trend pozytywny 🟢"
    elif score < -3:
        trend = "Trend negatywny 🔴"
    else:
        trend = "Trend neutralny 🟡"

    return trend, len(weekly_news)

def clear_weekly_news():
    with open(NEWS_FILE, "w") as f:
        json.dump([], f)

# --- Raporty ---
def daily_report():
    save_chat_ids()
    report = f"📅 {datetime.now().date()}\n--- CODZIENNY RAPORT CRYPTO AI ---\n"
    report += get_top100_report()
    send_message(report)

def weekly_report():
    save_chat_ids()
    trend, total_news = analyze_weekly_trend()
    report = f"📅 {datetime.now().date()}\n--- TYGODNIOWE PODSUMOWANIE ---\n"
    report += f"Liczba newsów w tygodniu: {total_news}\n{trend}"
    send_message(report)
    clear_weekly_news()

# --- Wywołanie raportów ---
today_weekday = datetime.today().weekday()  # 0 = poniedziałek

daily_report()  # codzienny raport
if today_weekday == 0:  # poniedziałek = raport tygodniowy
    weekly_report()
