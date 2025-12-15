import os
import time
import cv2
import torch
from ultralytics import YOLO
import subprocess
from shutil import which

# =========================
# RUTAS (relativas al proyecto)
# =========================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR, "runs", "detect", "75epochs", "weights", "best.pt"
)

PROJECT_DIR = os.path.join(BASE_DIR, "runs", "colorimetria_video")

# =========================
# PARÁMETROS
# =========================
CONF_THRESHOLD = 0.25


def _make_mp4_writer(output_path: str, fps: float, w: int, h: int) -> cv2.VideoWriter:
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    if not writer.isOpened():
        raise RuntimeError(
            "No pude inicializar VideoWriter con 'mp4v'. "
            "Solución: instalar opencv-python (no headless) o usar ffmpeg."
        )
    return writer


def _ffmpeg_h264_faststart(in_path: str, out_path: str) -> None:
    ffmpeg = which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg no está en PATH. Instálalo (Windows): winget install Gyan.FFmpeg")

    cmd = [
        ffmpeg, "-y",
        "-i", in_path,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-an",  # sin audio (más simple y compatible)
        out_path
    ]
    subprocess.run(cmd, check=True)


def run_offline(source_path: str) -> str:
    """
    Procesa imagen/video y deja salida en PROJECT_DIR.
    Devuelve PROJECT_DIR.
    """
    print("\n==============================")
    print("🚀 run_offline() INICIO")
    print("source_path:", source_path)
    print("MODEL_PATH:", MODEL_PATH)
    print("MODEL EXISTS:", os.path.exists(MODEL_PATH))
    print("==============================\n")

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"No se encontró el modelo en: {MODEL_PATH}")

    os.makedirs(PROJECT_DIR, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🧠 Device: {device}")

    model = YOLO(MODEL_PATH)
    model.to(device)

    ext = os.path.splitext(source_path)[1].lower()

    # -------------------------
    # IMAGEN
    # -------------------------
    if ext in [".jpg", ".jpeg", ".png"]:
        img = cv2.imread(source_path)
        if img is None:
            raise RuntimeError(f"No pude leer la imagen: {source_path}")

        r = model.predict(img, conf=CONF_THRESHOLD, verbose=False)[0]
        annotated = r.plot(labels=False, conf=False)

        out_img = os.path.join(PROJECT_DIR, f"output_{int(time.time())}.png")
        ok = cv2.imwrite(out_img, annotated)
        if not ok:
            raise RuntimeError("cv2.imwrite falló al guardar la imagen anotada.")

        print("✅ Imagen guardada:", out_img)
        print("🏁 run_offline() FIN\n")
        return PROJECT_DIR

    # -------------------------
    # VIDEO
    # -------------------------
    cap = cv2.VideoCapture(source_path)
    if not cap.isOpened():
        raise RuntimeError(f"No pude abrir el video: {source_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 1:
        fps = 25.0

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if cap.get(cv2.CAP_PROP_FRAME_COUNT) else -1

    print(f"🎥 Video info: {w}x{h} @ {fps:.2f}fps | frames={total_frames}")

    ts = int(time.time())

    # 1) MP4 temporal (mp4v)
    tmp_mp4 = os.path.join(PROJECT_DIR, f"tmp_{ts}.mp4")
    writer = _make_mp4_writer(tmp_mp4, fps, w, h)

    # 2) MP4 final (H264 + faststart)
    out_mp4 = os.path.join(PROJECT_DIR, f"output_{ts}.mp4")

    frame_idx = 0
    t0 = time.time()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame_idx += 1

            # DEBUG por fotograma (cada N frames para no saturar)
            if frame_idx == 1 or frame_idx % 10 == 0:
                elapsed = time.time() - t0
                fps_proc = frame_idx / elapsed if elapsed > 0 else 0.0
                if total_frames > 0:
                    print(f"frame {frame_idx}/{total_frames} | proc_fps={fps_proc:.1f}")
                else:
                    print(f"frame {frame_idx} | proc_fps={fps_proc:.1f}")

            r = model.predict(frame, conf=CONF_THRESHOLD, verbose=False)[0]
            annotated = r.plot(labels=False, conf=False)
            writer.write(annotated)

    finally:
        cap.release()
        writer.release()

    if not os.path.exists(tmp_mp4) or os.path.getsize(tmp_mp4) < 2000:
        raise RuntimeError("El MP4 temporal no se generó correctamente (vacío o inválido).")

    print("✅ MP4 temporal generado:", tmp_mp4, "| size:", os.path.getsize(tmp_mp4))

    # Re-encode/remux para compatibilidad web
    try:
        _ffmpeg_h264_faststart(tmp_mp4, out_mp4)
        print("✅ MP4 final (H264+faststart):", out_mp4, "| size:", os.path.getsize(out_mp4))
        # elimina el temporal para no acumular basura
        try:
            os.remove(tmp_mp4)
        except Exception:
            pass
    except Exception as e:
        print("⚠️ No pude convertir a H264 con ffmpeg:", e)
        print("⚠️ Dejo el temporal como salida (puede no reproducir en navegador):", tmp_mp4)
        out_mp4 = tmp_mp4  # fallback

    print("🏁 run_offline() FIN\n")
    return PROJECT_DIR
