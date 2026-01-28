import requests
import json
from datetime import datetime

TOKEN = "8479448510:AAFxgJOeL0gVheefOdPY1cqWkP3xg88o9LA"
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
    # Tutaj dodaj logikę pobierania cen top 100 i wzrostów względem BTC
    report = f"📅 {datetime.now().date()}\nTwój codzienny raport Crypto AI"
    send_message(report)

def weekly_report():
    save_chat_ids()
    # Tutaj dodaj logikę oceny trendu rynku
    report = f"📅 {datetime.now().date()}\n📊 Tygodniowe podsumowanie rynku"
    send_message(report)

# --- Logika wywołania dla GitHub Actions ---
today_weekday = datetime.today().weekday()  # 0 = poniedziałek
daily_report()
if today_weekday == 0:  # Poniedziałek = raport tygodniowy
    weekly_report()
