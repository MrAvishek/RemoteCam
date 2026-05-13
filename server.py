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

    print("Waiting for internet connection...", flush=True)

    while True:

        try:

            socket.create_connection(
                ("1.1.1.1", 53),
                timeout=5
            )

            print("Internet connected!", flush=True)

            return

        except OSError:

            print(
                "No internet... retrying in 5 seconds",
                flush=True
            )

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

        response = requests.post(
            url,
            data=data
        )

        print("Telegram Response:", flush=True)
        print(response.text, flush=True)

    except Exception as e:

        print(
            f"Telegram Error: {e}",
            flush=True
        )

# --------------------------------
# START FLASK SERVER
# --------------------------------

def start_flask_server():

    while True:

        print(
            "Starting Flask camera server...",
            flush=True
        )

        flask_process = subprocess.Popen(
            ["python", "app.py"]
        )

        flask_process.wait()

        print(
            "Flask server stopped!",
            flush=True
        )

        print(
            "Restarting in 30 seconds...",
            flush=True
        )

        time.sleep(30)

# --------------------------------
# MAIN STARTUP
# --------------------------------

wait_for_internet()

# --------------------------------
# START FLASK THREAD
# --------------------------------

flask_thread = threading.Thread(
    target=start_flask_server
)

flask_thread.daemon = True

flask_thread.start()

# Give Flask time to start
time.sleep(10)

# --------------------------------
# START CLOUDFLARE TUNNEL
# --------------------------------

print(
    "Starting Cloudflare tunnel...",
    flush=True
)

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

        print(line.strip(), flush=True)

        match = re.search(
            r"https://[-a-zA-Z0-9]+\.trycloudflare\.com",
            line
        )

        if match:

            public_url = match.group(0)

            print(
                "\nFOUND PUBLIC URL:",
                flush=True
            )

            print(
                public_url,
                flush=True
            )

            send_telegram_message(
                f"🎥 Camera Server Online\n\n"
                f"URL:\n{public_url}"
            )

            break

# --------------------------------
# START MONITOR THREAD
# --------------------------------

monitor_thread = threading.Thread(
    target=monitor_cloudflare
)

monitor_thread.daemon = True

monitor_thread.start()

# --------------------------------
# KEEP SCRIPT ALIVE
# --------------------------------

try:

    while True:
        time.sleep(1)

except KeyboardInterrupt:

    print(
        "\nStopping services...",
        flush=True
    )

    cloudflare_process.terminate()