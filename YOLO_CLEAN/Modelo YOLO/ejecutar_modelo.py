import cv2
from ultralytics import YOLO
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model = YOLO(r"runs\detect\innova_colorimetria3\weights\best.pt")

model.to(device)

cap = cv2.VideoCapture(2)  # 0 = cámara cel defecto

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (640, 480))
    if not ret:
        break

    results = model(frame, conf=0.15, verbose=False)

    annotated = results[0].plot()
    cv2.imshow("Colorimetria en tiempo real", annotated)

    # salir con "q"
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
