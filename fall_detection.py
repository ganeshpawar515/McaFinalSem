# fall_detection.py
import cv2
import mediapipe as mp
import time
import smtplib
import ssl
from email.message import EmailMessage
import os
from speak import say

cap = cv2.VideoCapture(0)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mpDraw = mp.solutions.drawing_utils

fall_start_time = None
alert_sent = False

def send_fall_email(img):
    say("Sending fall alert email.")
    print("\U0001F4E9 Sending alert email...")

    filename = "fall_alert.png"
    cv2.imwrite(filename, img)
    EMAIL_ADDRESS = "smarthomesystem515"          # Replace with your Gmail
    EMAIL_PASSWORD = "qdou tdxo lqpi yykb"            # Use Gmail App Password
    RECEIVER = "ganeshp.py07@gmail.com"   

    msg = EmailMessage()
    msg['Subject'] = 'Fall Detected - Smart Home System'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECEIVER
    msg.set_content('A fall has been detected and has persisted for over 1 minute.')

    with open(filename, 'rb') as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype='image', subtype='png', filename=filename)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Use App Password
        smtp.send_message(msg)

    print("✅ Email sent.")

def run():
    global fall_start_time, alert_sent
    fall_start_time = None
    alert_sent = False

    while True:
        success, img = cap.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)

        fall_detected = False

        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            landmarks = results.pose_landmarks.landmark

            shoulder_y = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y
            ankle_y = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y

            if abs(shoulder_y - ankle_y) < 0.1:
                fall_detected = True

                if fall_start_time is None:
                    fall_start_time = time.time()
                else:
                    elapsed = time.time() - fall_start_time

                    if int(elapsed) % 5 == 0:  # Speak every 5 seconds while fall persists
                        say("Fall detected. Please respond.")

                    if elapsed >= 60 and not alert_sent:
                        send_fall_email(img)
                        alert_sent = True

                cv2.putText(img, "Fall Detected!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            else:
                fall_start_time = None
                alert_sent = False

        cv2.imshow("Fall Detection", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()