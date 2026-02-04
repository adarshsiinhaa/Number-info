import requests
import json
import time

# ================== CONFIG ==================
BOT_TOKEN = "8570866416:AAFqqGvK4RAl8U2s51PqEldHDyUwpzTuM8Q"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

EXTERNAL_API_URL = "https://phoneintelligence.abstractapi.com/v1/?api_key=dcbd92d91bda456b8564da0db2bfaef2&phone="

user_states = {}

# ================== FUNCTIONS ==================
    def handle_phone(chat_id, phone):
    # Auto add +91 if only 10 digits
    if phone.isdigit() and len(phone) == 10:
        phone = "+91" + phone

    send_message(chat_id, "🔎 Checking number...")

    try:
        response = requests.get(EXTERNAL_API_URL + phone, timeout=10)
        data = response.json()

        # Extracting useful fields
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
