import requests
import json
import time

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
EXTERNAL_API_URL = "https://phoneintelligence.abstractapi.com/v1/?api_key=dcbd92d91bda456b8564da0db2bfaef2&phone="

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

user_states = {}
offset = 0


def send_message(chat_id, text, parse_mode=None, reply_markup=None):
    url = BASE_URL + "sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    if parse_mode:
        data["parse_mode"] = parse_mode
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    requests.post(url, data=data)


def handle_phone(chat_id, phone):
    if phone.isdigit() and len(phone) == 10:
        phone = "+91" + phone

    send_message(chat_id, "🔎 Checking number...")

    try:
        response = requests.get(EXTERNAL_API_URL + phone, timeout=10)
        data = response.json()

        carrier = data.get("phone_carrier", {}).get("name", "Unknown")
        line_type = data.get("phone_carrier", {}).get("line_type", "Unknown")
        country = data.get("phone_location", {}).get("country_name", "Unknown")
        region = data.get("phone_location", {}).get("region", "Unknown")
        valid = data.get("phone_validation", {}).get("is_valid", False)
        risk = data.get("phone_risk", {}).get("risk_level", "Unknown")
        voip = data.get("phone_validation", {}).get("is_voip", False)

        status = "✅ Valid Number" if valid else "❌ Invalid Number"

        message = (
            f"📱 *Phone Number Info*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📞 Number: `{phone}`\n"
            f"📡 Carrier: {carrier}\n"
            f"📶 Line Type: {line_type}\n"
            f"🌍 Country: {country}\n"
            f"📍 Region: {region}\n"
            f"⚠ Risk Level: {risk}\n"
            f"🌐 VOIP: {'Yes' if voip else 'No'}\n"
            f"\n{status}"
        )

        send_message(chat_id, message, parse_mode="Markdown")

    except Exception as e:
        print("API ERROR:", e)
        send_message(chat_id, "⚠️ Error fetching data. Try again later.")

    user_states[chat_id] = None


def handle_update(update):
    global offset

    if "message" not in update:
        return

    message = update["message"]
    chat_id = message["chat"]["id"]

    if "text" not in message:
        return

    text = message["text"].strip()

    if text == "/start":
        keyboard = {
            "keyboard": [["📱 Phone Lookup"]],
            "resize_keyboard": True
        }
        send_message(chat_id, "👋 Welcome!Send 10 digit mobile number", reply_markup=keyboard)

    elif text == "📱 Phone Lookup":
        user_states[chat_id] = "waiting_phone"
        send_message(chat_id, "📞 Send 10 digit mobile number:")

    elif user_states.get(chat_id) == "waiting_phone":
        if text.replace("+", "").isdigit() and len(text.replace("+", "")) >= 10:
            handle_phone(chat_id, text)
        else:
            send_message(chat_id, "❌ Invalid number. Send 10 digit mobile number.")

    offset = update["update_id"] + 1


def get_updates():
    global offset
    url = BASE_URL + "getUpdates"
    params = {"timeout": 30, "offset": offset}
    response = requests.get(url, params=params)
    return response.json()


print("🤖 Bot is running...")

while True:
    updates = get_updates()
    for update in updates.get("result", []):
        handle_update(update)
    time.sleep(1)
