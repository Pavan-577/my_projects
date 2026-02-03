import cv2, json, csv, os
from datetime import datetime

# Load model
rec = cv2.face.LBPHFaceRecognizer_create()
rec.read("model/face_model.yml")

with open("model/names.json") as f:
    names = json.load(f)
names = {int(k): v for k, v in names.items()}

# Face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Attendance file
if not os.path.exists("attendance.csv"):
    with open("attendance.csv", "w", newline="") as f:
        csv.writer(f).writerow(["Name", "Time", "Date"])

cap = cv2.VideoCapture(0)

CONFIDENCE_THRESHOLD = 70   # 🔑 VERY IMPORTANT

print("Live attendance started (Press q to quit)")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (200, 200))
        face = cv2.equalizeHist(face)

        label, confidence = rec.predict(face)

        if confidence < CONFIDENCE_THRESHOLD:
            name = names[label]
            now = datetime.now()
            time_now = now.strftime("%H:%M:%S")
            date_now = now.strftime("%Y-%m-%d")

            with open("attendance.csv", "a", newline="") as f:
                csv.writer(f).writerow([name, time_now, date_now])

            text = f"{name} IN: {time_now}"
            color = (0, 255, 0)
        else:
            text = "Unknown"
            color = (0, 0, 255)

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, text, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    cv2.imshow("Attendance", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
