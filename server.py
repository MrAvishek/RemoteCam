import subprocess
import threading
import requests
import re
import time
import socket
import os
import logging

from dotenv import load_dotenv

load_dotenv()

# --------------------------------
# CONFIG
# --------------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

last_url = None
latest_link = "No active tunnel"
# --------------------------------
# LOGGING
# --------------------------------

logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# --------------------------------
# INTERNET
# --------------------------------

def wait_for_internet():

    print("Waiting for internet...", flush=True)

    while True:

        try:

            socket.create_connection(
                ("1.1.1.1", 53),
                timeout=5
            )

            print(
                "Internet connected",
                flush=True
            )

            logging.info(
                "Internet connected"
            )

            return

        except OSError:

            print(
                "No internet. Retry in 5 sec",
                flush=True
            )

            logging.warning(
                "Internet unavailable"
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

        requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": message
            },
            timeout=10
        )

        logging.info(
            "Telegram message sent"
        )

    except Exception as e:

        logging.error(
            f"Telegram error: {e}"
        )

# --------------------------------
# WAIT FOR FLASK
# --------------------------------

def wait_for_flask():

    print(
        "Waiting for Flask server...",
        flush=True
    )

    while True:

        try:

            requests.get(
                "http://localhost:5000",
                timeout=3
            )

            print(
                "Flask ready",
                flush=True
            )

            logging.info(
                "Flask ready"
            )

            return

        except:

            time.sleep(2)

# --------------------------------
# FLASK WATCHDOG
# --------------------------------

def start_flask_server():

    while True:

        print(
            "Starting camera server...",
            flush=True
        )

        logging.info(
            "Starting app.py"
        )

        process = subprocess.Popen(
            ["python", "app.py"]
        )

        process.wait()

        print(
            "Flask stopped",
            flush=True
        )

        logging.warning(
            "app.py exited"
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

    global last_url
    global latest_link

    while True:

        wait_for_internet()

        subprocess.run(
            [
                "taskkill",
                "/F",
                "/IM",
                "cloudflared.exe"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print(
            "Starting tunnel...",
            flush=True
        )

        logging.info(
            "Starting Cloudflare"
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

        for line in process.stdout:

            print(
                line.strip(),
                flush=True
            )

            match = re.search(
                r"https://[-a-zA-Z0-9]+\.trycloudflare\.com",
                line
            )

            if match:

                public_url = match.group(0)

                if public_url != last_url:

                    last_url = public_url

                    latest_link = public_url

                    logging.info(
                        f"Tunnel URL: {public_url}"
                    )

                    send_telegram_message(
                        f"🎥 Camera Online\n\n"
                        f"{public_url}"
                    )

        logging.warning(
            "Tunnel exited"
        )

        print(
            "Tunnel disconnected",
            flush=True
        )

        print(
            "Recreating in 10 sec",
            flush=True
        )

        time.sleep(10)

# --------------------------------
# STARTUP
# --------------------------------

wait_for_internet()

flask_thread = threading.Thread(
    target=start_flask_server,
    daemon=True
)

flask_thread.start()

wait_for_flask()

cloudflare_thread = threading.Thread(
    target=start_cloudflare,
    daemon=True
)

cloudflare_thread.start()

# --------------------------------
# KEEP ALIVE
# --------------------------------

try:

    while True:

        time.sleep(1)

except KeyboardInterrupt:

    logging.info(
        "Stopping server"
    )

    print(
        "Stopping...",
        flush=True
    )