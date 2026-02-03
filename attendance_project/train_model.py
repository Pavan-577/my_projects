import cv2, os, json, numpy as np

DATASET = "dataset"
MODEL_DIR = "model"
os.makedirs(MODEL_DIR, exist_ok=True)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

faces = []
labels = []
label_map = {}
label_id = 0

print("\nTraining started...\n")

for person in sorted(os.listdir(DATASET)):
    person_path = os.path.join(DATASET, person)
    if not os.path.isdir(person_path):
        continue

    print(person)
    label_map[label_id] = person
    person_face_count = 0

    for img_name in os.listdir(person_path):
        if not img_name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        img_path = os.path.join(person_path, img_name)
        img = cv2.imread(img_path)
        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        detected = face_cascade.detectMultiScale(gray, 1.2, 5)

        # ✅ If face detected → crop face
        if len(detected) > 0:
            x, y, w, h = detected[0]
            face = gray[y:y+h, x:x+w]
        else:
            # ✅ If no face detected → use full image
            face = gray

        face = cv2.resize(face, (200, 200))
        face = cv2.equalizeHist(face)

        faces.append(face)
        labels.append(label_id)
        person_face_count += 1

    print(f"  images used: {person_face_count}")
    label_id += 1

if len(faces) < 2:
    print("❌ Not enough training data. Add clearer images.")
    exit()

faces = np.array(faces)
labels = np.array(labels)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(faces, labels)

recognizer.save("model/face_model.yml")
with open("model/names.json", "w") as f:
    json.dump(label_map, f)

print("\n✅ Training completed successfully")
print("Label map:", label_map)
