import subprocess
import threading
import requests
import re
import time
import socket
import os
from dotenv import load_dotenv

load_dotenv()

# --------------------------------
# TELEGRAM CONFIG
# --------------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# --------------------------------
# Wait Till Internet gets connected
# --------------------------------
def wait_for_internet():

    print("Waiting for internet connection...")

    while True:

        try:

            socket.create_connection(("1.1.1.1", 53), timeout=5)

            print("Internet connected!")

            return

        except OSError:

            print("No internet... retrying in 5 seconds")

            time.sleep(5)

# --------------------------------
# SEND TELEGRAM MESSAGE
# --------------------------------

def send_telegram_message(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:

        response = requests.post(url, data=data)

        print("Telegram Response:")
        print(response.text)

    except Exception as e:

        print("Telegram Error:", e)


# --------------------------------
# START FLASK SERVER
# --------------------------------
wait_for_internet()
print("Starting Flask camera server...")

flask_process = subprocess.Popen(
    ["python", "app.py"]
)

time.sleep(5)

# --------------------------------
# START CLOUDFLARE TUNNEL
# --------------------------------

print("Starting Cloudflare tunnel...")

cloudflare_process = subprocess.Popen(
    [
        "cloudflared",
        "tunnel",
        "--url",
        "http://localhost:5000"
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# --------------------------------
# READ CLOUDFLARE OUTPUT
# --------------------------------

def monitor_cloudflare():

    for line in cloudflare_process.stdout:

        print(line.strip())

        match = re.search(
            r"https://[-a-zA-Z0-9]+\.trycloudflare\.com",
            line
        )

        if match:

            public_url = match.group(0)

            print("\nFOUND PUBLIC URL:")
            print(public_url)

            send_telegram_message(
                f"🎥 Camera Server Online\n\n"
                f"URL:\n{public_url}\n\n"
                # f"Username: admin\n"
                # f"Password: 1234"
            )

            break


# --------------------------------
# START MONITOR THREAD
# --------------------------------

thread = threading.Thread(target=monitor_cloudflare)
thread.daemon = True
thread.start()

# --------------------------------
# KEEP PROCESS RUNNING
# --------------------------------

try:

    flask_process.wait()
    cloudflare_process.wait()

except KeyboardInterrupt:

    print("\nStopping services...")

    flask_process.terminate()
    cloudflare_process.terminate()