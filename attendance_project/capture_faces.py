# capture_faces_detect.py
import cv2, os, time

NAME = input("Enter person name (no .jpg/.png): ").strip().replace(" ", "_")
if not NAME or "." in NAME:
    print("Invalid name. Use simple letters like 'madhuri'")
    raise SystemExit

OUT = os.path.join("dataset", NAME)
os.makedirs(OUT, exist_ok=True)

NUM = 20   # change to 30 if you want more
print(f"Capturing up to {NUM} face images for: {NAME} (press q to stop)")

# face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# open camera (try indexes)
cap = None
for i in (0,1,2):
    c = cv2.VideoCapture(i)
    if c.isOpened():
        cap = c; cam_idx = i; break
    else:
        c.release()
if cap is None:
    print("No camera found. Close other apps and try again.")
    raise SystemExit

print("Using camera index:", cam_idx)
count = len([f for f in os.listdir(OUT) if f.lower().endswith((".jpg",".jpeg",".png"))])
print("Already in folder:", count, "images")

try:
    while count < NUM:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.2); continue
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(100,100))
        for (x,y,w,h) in faces:
            # expand box a bit
            pad = int(0.15 * min(w,h))
            x1 = max(0, x-pad); y1 = max(0, y-pad)
            x2 = min(frame.shape[1], x+w+pad); y2 = min(frame.shape[0], y+h+pad)
            face = frame[y1:y2, x1:x2]
            face_gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            face_resized = cv2.resize(face_gray, (200,200))
            # save only clear faces
            path = os.path.join(OUT, f"{NAME}_{count:03d}.jpg")
            cv2.imwrite(path, face_resized)
            print("Saved:", path)
            count += 1
            break  # save one face per frame
        # UI
        if faces is None or len(faces) == 0:
            cv2.putText(frame, "No face detected - move closer", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
        else:
            cv2.putText(frame, f"Saved {count}/{NUM}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.imshow("Capture (face-only)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    print("Interrupted")
finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Done. Total images in folder:", len([f for f in os.listdir(OUT) if f.lower().endswith(('.jpg','.jpeg','.png'))]))
