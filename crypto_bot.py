import os
import requests
import feedparser
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

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


def send_message(text):
    url = f"{TELEGRAM_API}/sendMessage"
    requests.post(url, data={"chat_id": "@YOUR_USERNAME", "text": text})


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
        msg += f"{n['level']}\n{n['title']}\n\n"

    return msg[:MAX_MSG_LEN]


def main():
    report = build_report()
    send_message(report)


if __name__ == "__main__":
    main()
