import cv2
import os
import time
import pandas as pd
import config
from datetime import datetime
import serial
import numpy as np

#occupancy = 0

def is_dark_rectangle(frame, contour):
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)
    mean_val = cv2.mean(frame, mask=mask)
    brightness = sum(mean_val[:3]) / 3
    return brightness < 80 

def detect_id_card(ser):
    print("[INFO] Starting camera feed...")
    start_cam_time = time.time()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    print("[INFO] Camera initialized in", time.time() - start_cam_time, "seconds")

    detected = False
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"id_{timestamp}.jpg"
    save_path = os.path.join("static/images", filename)

    start_time = time.time()
    while time.time() - start_time < 5:
        ret, frame = cap.read()
        if not ret:
            print("[WARNING] Frame not captured")
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blur, 20, 80)

        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.03 * cv2.arcLength(cnt, True), True)
            area = cv2.contourArea(cnt)
            if len(approx) == 4 and cv2.isContourConvex(approx) and area > 1000:
                if is_dark_rectangle(frame, approx):
                    color = (0, 0, 255)
                else:
                    color = (0, 255, 0)

                cv2.drawContours(frame, [approx], 0, color, 3)

                if not detected and is_dark_rectangle(frame, approx):
                    cv2.imwrite(save_path, frame)
                    print("[INFO] Image saved:", filename)
                    detected = True

        cv2.imshow("ID Card Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Camera closed")

    if detected:
        config.occupancy += 1
        config.save_occupancy(config.occupancy)
        log_data(timestamp, filename)
        ser.write(b"S")
        print("[INFO] Sent signal back to Arduino")
    time.sleep(2)

def log_data(timestamp, filename):
    log_file = "Log_Book.xlsx"
    new_entry = {
        "Serial No.": None,
        "Timestamp": timestamp,
        "Image FileName": filename,
        "Entry Status": "Detected",
        "Access Method": "ID Card",
        "Notes": None
    }

    if os.path.exists(log_file):
        df = pd.read_excel(log_file, engine="openpyxl")
        new_entry["Serial No."] = len(df) + 1
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    else:
        new_entry["Serial No."] = 1
        df = pd.DataFrame([new_entry])

    df.to_excel(log_file, index=False)
    print("[INFO] Log updated")

def start_detection_loop():
    global occupancy
    print("[INFO] Starting detection loop...")
    try:
        ser = serial.Serial('COM5', 9600, timeout=1)
        time.sleep(2)
        ser.flushInput()
        print("[INFO] Serial connected")

        while config.detection_running:
            if ser.in_waiting:
                val = ser.readline().decode().strip()
                print("[INFO] Received from Arduino:", val)
                if val == "1":
                    #config.occupancy += 1
                    print("[INFO] Motion detected at", time.time())
                    detect_id_card(ser)
                    print("[INFO] Detection finished at", time.time())
                elif val == "2":
                    config.occupancy = max(0, config.occupancy - 1)
                    config.save_occupancy(config.occupancy)
    except Exception as e:
        print("[ERROR]", e)
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
        print("[INFO] Serial closed")

if __name__ == "_main_":
    start_detection_loop()