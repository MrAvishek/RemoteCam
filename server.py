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
# WAIT FOR INTERNET
# --------------------------------

def wait_for_internet():

    print(
        "Waiting for internet connection...",
        flush=True
    )

    while True:

        try:

            socket.create_connection(
                ("1.1.1.1", 53),
                timeout=5
            )

            print(
                "Internet connected!",
                flush=True
            )

            return

        except OSError:

            print(
                "No internet... retrying in 5 sec",
                flush=True
            )

            time.sleep(5)

# --------------------------------
# TELEGRAM
# --------------------------------

def send_telegram_message(message):

    try:

        url = (
            f"https://api.telegram.org/"
            f"bot{BOT_TOKEN}/sendMessage"
        )

        data = {
            "chat_id": CHAT_ID,
            "text": message
        }

        response = requests.post(
            url,
            data=data,
            timeout=10
        )

        print(
            response.text,
            flush=True
        )

    except Exception as e:

        print(
            f"Telegram Error: {e}",
            flush=True
        )

# --------------------------------
# FLASK WATCHDOG
# --------------------------------

def start_flask_server():

    while True:

        print(
            "Starting camera server...",
            flush=True
        )

        process = subprocess.Popen(
            ["python", "app.py"]
        )

        process.wait()

        print(
            "Camera server stopped",
            flush=True
        )

        print(
            "Restarting in 30 sec",
            flush=True
        )

        time.sleep(30)

# --------------------------------
# CLOUDFLARE WATCHDOG
# --------------------------------

def start_cloudflare():

    while True:

        print(
            "Starting Cloudflare tunnel...",
            flush=True
        )

        process = subprocess.Popen(
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

        url_sent = False

        for line in process.stdout:

            print(
                line.strip(),
                flush=True
            )

            match = re.search(
                r"https://[-a-zA-Z0-9]+\.trycloudflare\.com",
                line
            )

            if match and not url_sent:

                public_url = match.group(0)

                print(
                    f"FOUND URL:\n{public_url}",
                    flush=True
                )

                send_telegram_message(
                    f"🎥 Camera Online\n\n"
                    f"{public_url}"
                )

                url_sent = True

        print(
            "Tunnel disconnected",
            flush=True
        )

        print(
            "Creating new tunnel in 10 sec",
            flush=True
        )

        time.sleep(10)

# --------------------------------
# MAIN STARTUP
# --------------------------------

wait_for_internet()

# --------------------------------
# START FLASK
# --------------------------------

flask_thread = threading.Thread(
    target=start_flask_server
)

flask_thread.daemon = True

flask_thread.start()

# allow Flask startup

time.sleep(10)

# --------------------------------
# START CLOUDFLARE
# --------------------------------

cloudflare_thread = threading.Thread(
    target=start_cloudflare
)

cloudflare_thread.daemon = True

cloudflare_thread.start()

# --------------------------------
# KEEP PROCESS ALIVE
# --------------------------------

try:

    while True:

        time.sleep(1)

except KeyboardInterrupt:

    print(
        "\nStopping...",
        flush=True
    )