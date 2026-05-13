from flask import Flask, Response
import cv2
import subprocess
import threading
import requests
import re

# -------------------------------
# TELEGRAM SETTINGS
# -------------------------------

BOT_TOKEN = "8515559954:AAFPPvFDVKhJ-7Y4H6BKfwSodx5DRUU37wY"
CHAT_ID = "7163767478"

# -------------------------------
# FLASK APP
# -------------------------------

app = Flask(__name__)

camera = cv2.VideoCapture(0)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 15)


def generate_frames():
    while True:
        success, frame = camera.read()

        if not success:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               frame + b'\r\n')


@app.route('/')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


# -------------------------------
# TELEGRAM MESSAGE FUNCTION
# -------------------------------

def send_telegram_message(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=data)

    print(response.text)


# -------------------------------
# CLOUDFLARE TUNNEL
# -------------------------------

def start_cloudflare():

    process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://localhost:5000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in process.stdout:

        print(line.strip())

        match = re.search(
            r"https://[-a-zA-Z0-9]+\.trycloudflare\.com",
            line
        )

        if match:

            public_url = match.group(0)

            print("FOUND URL:", public_url)

            send_telegram_message(
                f"🎥 Camera Live\n\n{public_url}"
            )

            break


# -------------------------------
# MAIN
# -------------------------------

if __name__ == '__main__':

    tunnel_thread = threading.Thread(target=start_cloudflare)
    tunnel_thread.daemon = True
    tunnel_thread.start()

    app.run(host='0.0.0.0', port=5000, threaded=True)