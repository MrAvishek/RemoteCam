from flask import Flask, render_template, Response, request, redirect, session, url_for
import cv2
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = "super_secret_key_change_this"

USERNAME = os.getenv("USERN")
PASSWORD = os.getenv("PASSWORD")
# print(f"password: {PASSWORD} {type(PASSWORD)}")
# print(f"USERNAME: {USERNAME} {type(USERNAME)}")
# camera = cv2.VideoCapture(0)


# camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# camera.set(cv2.CAP_PROP_FPS, 15)

def initialize_camera():

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("ERROR: Camera not detected!")

        return None

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 15)

    print("Camera initialized successfully")

    return camera


camera = initialize_camera()
if camera is None:

    print("No camera available")

    raise Exception("Camera initialization failed")

def generate_frames():

    while True:

        try:
            success, frame = camera.read()

            if not success:
                break

            _, buffer = cv2.imencode(
                '.jpg',
                frame,
                [cv2.IMWRITE_JPEG_QUALITY, 60]
            )

            frame = buffer.tobytes()

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' +
                frame +
                b'\r\n'
            )

        except GeneratorExit:
            print("Browser disconnected.")
            break

        except Exception as e:
            print("Stream error:", e)
            break


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/')
def home():

    if 'logged_in' in session:
        return redirect(url_for('dashboard'))

    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        if username == USERNAME and password == PASSWORD:

            session['logged_in'] = True

            return redirect(url_for('dashboard'))

        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)


@app.route('/dashboard')
def dashboard():

    if 'logged_in' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html')


@app.route('/video_feed')
def video_feed():

    if 'logged_in' not in session:
        return ('Unauthorized', 401)

    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/logout')
def logout():

    session.clear()

    response = redirect(url_for('login'))

    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response


if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True
    )