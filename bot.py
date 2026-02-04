import requests
import json
import time

# ================== CONFIG ==================
BOT_TOKEN = "8570866416:AAFqqGvK4RAl8U2s51PqEldHDyUwpzTuM8Q"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

EXTERNAL_API_URL = ""  # <-- PUT YOUR PHONE LOOKUP API URL HERE
# Example format expected: EXTERNAL_API_URL + mobile_number

# Store user states
user_states = {}

# ================== TELEGRAM FUNCTIONS ==================

def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    url = API_URL + "sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    if parse_mode:
        payload["parse_mode"] = parse_mode

    requests.post(url, data=payload)


def get_updates(offset=None):
    url = API_URL + "getUpdates"
    params = {
        "timeout": 30
    }
    if offset:
        params["offset"] = offset

    response = requests.get(url, params=params)
    return response.json()


# ================== KEYBOARD ==================

def get_main_keyboard():
    return {
        "keyboard": [
            ["📱 Phone Lookup"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }


# ================== HANDLERS ==================

def handle_start(chat_id):
    text = (
        "👋 Welcome!\n\n"
        "I can help you lookup phone information.\n"
        "Use the button below to get started."
    )
    send_message(chat_id, text, reply_markup=get_main_keyboard())


def handle_phone_lookup(chat_id):
    user_states[chat_id] = "WAITING_FOR_PHONE"
    send_message(chat_id, "📞 Send 10 digit mobile number:")


def handle_phone_number(chat_id, phone):
    if not phone.isdigit() or len(phone) != 10:
        send_message(chat_id, "❌ Invalid number. Please send a valid 10 digit mobile number.")
        return

    send_message(chat_id, "🔎 Looking up number... Please wait.")

    try:
        response = requests.get(EXTERNAL_API_URL + phone, timeout=10)
        data = response.json()

        formatted = "<pre>" + json.dumps(data, indent=2) + "</pre>"
        send_message(chat_id, formatted, parse_mode="HTML")

    except Exception as e:
        send_message(chat_id, "⚠️ Error fetching data from API.")

    user_states[chat_id] = None


# ================== MAIN LOOP ==================

def main():
    print("🤖 Bot is running...")
    offset = None

    while True:
        try:
            updates = get_updates(offset)

            if "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1

                    if "message" not in update:
                        continue

                    message = update["message"]
                    chat_id = message["chat"]["id"]

                    if "text" not in message:
                        continue

                    text = message["text"].strip()

                    # Command: /start
                    if text == "/start":
                        handle_start(chat_id)
                        continue

                    # Button pressed
                    if text == "📱 Phone Lookup":
                        handle_phone_lookup(chat_id)
                        continue

                    # If waiting for phone number
                    if user_states.get(chat_id) == "WAITING_FOR_PHONE":
                        handle_phone_number(chat_id, text)
                        continue

                    # Default reply
                    send_message(chat_id, "Please use the keyboard buttons 🙂", reply_markup=get_main_keyboard())

        except Exception as e:
            print("Error:", e)
            time.sleep(5)

        time.sleep(1)


# ================== RUN ==================

if __name__ == "__main__":
    main()
