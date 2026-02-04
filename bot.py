import requests
import json
import time

# ================== CONFIG ==================
BOT_TOKEN = "8570866416:AAFqqGvK4RAl8U2s51PqEldHDyUwpzTuM8Q"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

EXTERNAL_API_URL = "https://phoneintelligence.abstractapi.com/v1/?api_key=dcbd92d91bda456b8564da0db2bfaef2&phone="

user_states = {}

# ================== FUNCTIONS ==================

def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    url = API_URL + "sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    if parse_mode:
        payload["parse_mode"] = parse_mode

    requests.post(url, data=payload)


def get_updates(offset=None):
    url = API_URL + "getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    return requests.get(url, params=params).json()


def get_keyboard():
    return {
        "keyboard": [["📱 Phone Lookup"]],
        "resize_keyboard": True
    }


def handle_phone_lookup(chat_id):
    user_states[chat_id] = "WAITING"
    send_message(chat_id, "📞 Send Indian mobile number\nExample: 9876543210 or +919876543210")


def handle_phone(chat_id, phone):
    # Auto add +91 if only 10 digits
    if phone.isdigit() and len(phone) == 10:
        phone = "+91" + phone

    send_message(chat_id, "🔎 Checking number...")

    try:
        response = requests.get(EXTERNAL_API_URL + phone, timeout=10)
        data = response.json()
        formatted = "<pre>" + json.dumps(data, indent=2) + "</pre>"
        send_message(chat_id, formatted, parse_mode="HTML")
    except:
        send_message(chat_id, "⚠️ API Error. Try again later.")

    user_states[chat_id] = None


# ================== MAIN LOOP ==================

print("🤖 Bot is running...")

offset = None
while True:
    try:
        updates = get_updates(offset)

        if "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1

                if "message" not in update or "text" not in update["message"]:
                    continue

                msg = update["message"]
                chat_id = msg["chat"]["id"]
                text = msg["text"].strip()

                if text == "/start":
                    send_message(chat_id, "👋 Welcome! Use button below.", reply_markup=get_keyboard())

                elif text == "📱 Phone Lookup":
                    handle_phone_lookup(chat_id)

                elif user_states.get(chat_id) == "WAITING":
                    handle_phone(chat_id, text)

                else:
                    send_message(chat_id, "Use the keyboard 🙂", reply_markup=get_keyboard())

    except Exception as e:
        print("Error:", e)
        time.sleep(5)

    time.sleep(1)
