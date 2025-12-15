from ultralytics import YOLO

model = YOLO(r"runs\detect\innova_colorimetria3\weights\best.pt")
model.predict(
    source=r"C:\Users\drbof\Downloads\video1.mp4",
    save=True,          # guarda video con cajas
    project="runs/colorimetria_video"             # fuerza fps de salida (opcional)
)