import requests
import json
from datetime import datetime
import schedule
import time

TOKEN = "8479448510:AAFxgJOeL0gVheefOdPY1cqWkP3xg88o9LA"  # Twój token bota
CHAT_IDS_FILE = "chat_ids.txt"

# --- Funkcje pomocnicze ---
def get_updates():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        return requests.get(url).json()
    except:
        return None

def save_chat_ids():
    updates = get_updates()
    if not updates or "result" not in updates:
        return
    chat_ids = set()
    try:
        with open(CHAT_IDS_FILE, "r") as f:
            for line in f:
                chat_ids.add(line.strip())
    except FileNotFoundError:
        pass
    for update in updates["result"]:
        if "message" in update:
            chat_id = str(update["message"]["chat"]["id"])
            if chat_id not in chat_ids:
                chat_ids.add(chat_id)
    with open(CHAT_IDS_FILE, "w") as f:
        for cid in chat_ids:
            f.write(cid + "\n")

def send_message(text):
    try:
        with open(CHAT_IDS_FILE, "r") as f:
            for line in f:
                chat_id = line.strip()
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                requests.post(url, data={"chat_id": chat_id, "text": text})
    except FileNotFoundError:
        pass

# --- Funkcje raportów ---
def daily_report():
    save_chat_ids()
    # Tu dodaj logikę pobierania cen top 100 + wzrost w stosunku do BTC od dołka 2022
    report = f"📅 {datetime.now().date()}\nTwój codzienny raport Crypto AI"
    send_message(report)

def weekly_report():
    save_chat_ids()
    # Tu dodaj logikę oceny trendu rynku
    report = f"📅 {datetime.now().date()}\n📊 Tygodniowe podsumowanie rynku"
    send_message(report)

# --- Harmonogram ---
schedule.every().day.at("09:00").do(daily_report)           # codzienny raport
schedule.every().monday.at("09:00").do(weekly_report)       # cotygodniowe podsumowanie

# --- Pętla główna ---
while True:
    schedule.run_pending()
    time.sleep(60)
