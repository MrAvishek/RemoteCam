import requests

BOT_TOKEN = "8515559954:AAFPPvFDVKhJ-7Y4H6BKfwSodx5DRUU37wY"
CHAT_ID = "7163767478"

message = "✅ Telegram bot is working!"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

data = {
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(url, data=data)

print(response.text)