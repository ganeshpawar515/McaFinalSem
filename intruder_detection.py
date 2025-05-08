# intruder_detection.py
import cv2
import time
import smtplib
import imghdr
from email.message import EmailMessage

def send_email_alert(image_path):
    print("sending emails nownklns")
    EMAIL_ADDRESS = "smarthomesystem515"          
    EMAIL_PASSWORD = "qdou tdxo lqpi yykb"            
    RECEIVER = "ganeshp.py07@gmail.com"           

    msg = EmailMessage()
    msg['Subject'] = 'Intruder Alert 🚨'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECEIVER
    msg.set_content('Intruder detected. Image is attached.')

    with open(image_path, 'rb') as f:
        img_data = f.read()
        img_type = imghdr.what(f.name)
        msg.add_attachment(img_data, maintype='image', subtype=img_type, filename='intruder.jpg')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        print("📧 Email sent with image alert!")

def run():
    cap = cv2.VideoCapture(0)
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    last_sent_time = 0  

    while cap.isOpened():
        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) < 1000:
                continue
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame1, (x,y), (x+w, y+h), (0,255,0), 2)
            cv2.putText(frame1, "Intruder Detected", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

            # Save image and send email once every 10 seconds
            if time.time() - last_sent_time > 10:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                img_path = f"intruder_{timestamp}.jpg"
                cv2.imwrite(img_path, frame1)
                send_email_alert(img_path)
                last_sent_time = time.time()

        cv2.imshow("Security Feed", frame1)
        frame1 = frame2
        ret, frame2 = cap.read()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
