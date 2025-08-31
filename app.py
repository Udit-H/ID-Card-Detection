from flask import Flask, render_template, send_file, redirect, url_for
import threading
import os
import pandas as pd
import config
from main import start_detection_loop

app = Flask(__name__)
detection_thread = None

@app.route('/')
def index():
    if os.path.exists("Log_Book.xlsx"):
        df = pd.read_excel("Log_Book.xlsx", engine='openpyxl')
        table = df.to_html(classes='table table-striped', index=False)
    else:
        table = "<p>No log data available.</p>"

    image_dir = "static/images"
    os.makedirs(image_dir, exist_ok=True)
    image_files = sorted(
        [f for f in os.listdir(image_dir) if f.endswith(".jpg")],
        key=lambda x: os.path.getmtime(os.path.join(image_dir, x)),
        reverse=True
    )

    return render_template("index.html", table=table, images=image_files, detection_running=config.detection_running, occupancy=config.occupancy)

@app.route('/start')
def start_detection():
    global detection_thread
    if not config.detection_running:
        config.detection_running = True
        print("[FLASK] Detection started.")
        detection_thread = threading.Thread(target=start_detection_loop)
        detection_thread.start()
    return redirect(url_for('index'))

@app.route('/stop')
def stop_detection():
    config.detection_running = False
    print("[FLASK] Detection stopped.")
    return redirect(url_for('index'))

@app.route('/download-log')
def download_log():
    if os.path.exists("Log_Book.xlsx"):
        return send_file("Log_Book.xlsx", as_attachment=True)
    return "<p>Log file not found.</p>"

if __name__ == '__main__':
    app.run(debug=True)