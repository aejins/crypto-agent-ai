import os
import json
import requests
import feedparser
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

CHAT_IDS_FILE = "chat_ids.txt"
RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://cryptonews.com/news/feed/",
    "https://bitcoinmagazine.com/.rss/full/",
]

KEYWORDS_HIGH = [
    "sec", "etf", "blackrock", "fed", "hack", "exploit",
    "ban", "lawsuit", "approval", "bankruptcy"
]

KEYWORDS_MEDIUM = [
    "binance", "coinbase", "ethereum", "solana",
    "upgrade", "mainnet", "layer", "l2"
]

MAX_MSG_LEN = 3900

# --- Chat ID --- 
def get_chat_ids():
    try:
        with open(CHAT_IDS_FILE, "r") as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        return []

def save_chat_ids_from_telegram():
    url = f"{TELEGRAM_API}/getUpdates"
    resp = requests.get(url).json()
    chat_ids = set(get_chat_ids())
    for update in resp.get("result", []):
        if "message" in update:
            cid = str(update["message"]["chat"]["id"])
            chat_ids.add(cid)
    if chat_ids:
        with open(CHAT_IDS_FILE, "w") as f:
            for cid in chat_ids:
                f.write(cid + "\n")

# --- Wysyłka wiadomości ---
def send_message(text):
    chat_ids = get_chat_ids()
    if not chat_ids:
        save_chat_ids_from_telegram()
        chat_ids = get_chat_ids()
    if not chat_ids:
        print("❌ Brak chat_id, napisz coś do bota na Telegramie")
        return
    for chat_id in chat_ids:
        url = f"{TELEGRAM_API}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": text})

# --- Klasyfikacja i pobranie newsów ---
def classify_news(title):
    t = title.lower()
    if any(k in t for k in KEYWORDS_HIGH):
        return "🚨 HIGH"
    if any(k in t for k in KEYWORDS_MEDIUM):
        return "📌 MEDIUM"
    return "ℹ️ LOW"

def fetch_news():
    items = []
    for feed in RSS_FEEDS:
        parsed = feedparser.parse(feed)
        for e in parsed.entries[:5]:
            items.append({
                "title": e.title,
                "link": e.link,
                "level": classify_news(e.title)
            })
    return items

def build_report():
    news = fetch_news()
    if not news:
        return "⚠️ Brak newsów dziś"
    news.sort(key=lambda x: ["🚨 HIGH", "📌 MEDIUM", "ℹ️ LOW"].index(x["level"]))
    msg = f"📅 {datetime.now().date()}\n🧠 *CRYPTO NEWS DIGEST*\n\n"
    for n in news:
        msg += f"{n['level']}\n{n['title']}\n{n['link']}\n\n"
    return msg[:MAX_MSG_LEN]

# --- Główna funkcja ---
def main():
    save_chat_ids_from_telegram()  # pobiera nowe chat_id z Telegrama
    report = build_report()
    send_message(report)

if __name__ == "__main__":
    main()
