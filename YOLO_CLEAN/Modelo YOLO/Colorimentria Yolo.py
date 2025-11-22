# ================================================
#  ENTRENAMIENTO DE YOLOv8 - Colorimetría Innova
#  Compatible con Ultralytics 8.3.x
# ================================================
from calendar import error
import cv2
from ultralytics import YOLO
import torch
import os
import time


# --- Verificar GPU disponible ---

if torch.cuda.is_available():
    device = 0
    print(f"✅ GPU detectada: {torch.cuda.get_device_name(0)}")
else:
    device = "cpu"
    print("⚠️ No se detectó GPU, se usará CPU (más lento)")

# --- Ruta al dataset ---
DATASET_PATH = r"C:\Users\alber\Desktop\Innova dataset\data.yaml"

# --- Cargar modelo base ---
model = YOLO("yolov8s.pt")

# --- Cargar modelo para reentrenamiento desde x epoch, partir desde last.pt o best.pt ---
model = YOLO(r"C:\Users\alber\PycharmProjects\PythonProject1\Pruebas Innova\Modelo YOLO\runs\detect\innova_colorimetria6\weights\last.pt")

# --- Callback personalizado para progreso ---
class EpochLogger:
    def __init__(self):
        self.start_time = None

    def on_train_start(self, trainer):
        self.start_time = time.time()
        print(f"\n Entrenamiento iniciado con {trainer.epochs} epochs.\n")

    def on_fit_epoch_end(self, trainer):
        tiempo = int(time.time() - self.start_time)
        epoch = trainer.epoch + 1
        total = trainer.epochs
        loss = getattr(trainer, "loss", 0)
        print(f"📈 Epoch {epoch}/{total} completada | Loss: {loss:.4f} | Tiempo total: {tiempo // 60}m {tiempo % 60}s")
        print("Ctrl + C para que termine el programa después de este último Epoch. si se hace 2 veces")

    def on_train_end(self, trainer):
        save_dir = os.path.join(trainer.save_dir, "weights")
        print(f"\n Entrenamiento terminado.\n Pesos guardados en: {save_dir}\n Modelo óptimo: best.pt\n")

    def train_error(self, trainer, error):
        print(f"Error: {error}\n")
        print(f"El entrenamiento de {trainer.epochs} ha finalizado ")




# --- Registrar callbacks manualmente ---
logger = EpochLogger()
model.add_callback("on_train_start", logger.on_train_start)
model.add_callback("on_fit_epoch_end", logger.on_fit_epoch_end)
model.add_callback("on_train_end", logger.on_train_end)

# --- Entrenamiento principal ---
epochs = 100
try:
    model.train(
        data=DATASET_PATH,
        epochs=300,
        imgsz=128,
        batch=4,
        optimizer="AdamW",
        lr0=0.001,
        dropout=0.1,
        cache=True,
        augment=True,
        patience=25,
        device=device,
        workers=0,
        project="runs/detect",
        name="innova_colorimetria",
        verbose=True,
        # Si es true, seguirá entrenando desde el último epoch etrenado guardado
        resume=True,
        save_period = 1 # Guarda por cada epoch
    )
except AssertionError as e:
    model.add_callback("train_error", logger.on_fit_epoch_end)
    print(f"Error{e}")