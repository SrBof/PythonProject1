import os
import cv2
import av
import torch
import streamlit as st
from ultralytics import YOLO
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode

# =========================
# CONFIG
# =========================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "runs", "detect", "innova_colorimetria3", "weights", "best.pt")

# Si tu app corre solo local, esto ayuda a evitar problemas con WebRTC
RTC_CONFIG = {
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
}

st.set_page_config(page_title="BlueSight - Prueba en Vivo", layout="wide")

st.title("Prueba tú mismo (Tiempo real)")
st.caption("Permite cámara del navegador, ejecuta YOLO en vivo y muestra el stream anotado.")

conf = st.slider("Confianza (conf)", min_value=0.05, max_value=0.90, value=0.35, step=0.05)

# Cargar modelo una sola vez (cache)
@st.cache_resource
def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = YOLO(MODEL_PATH)
    model.to(device)
    return model, device

model, device = load_model()

class YOLOVideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.conf = 0.35

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")

        # (opcional) resize para rendimiento
        img = cv2.resize(img, (640, 480))

        results = model.predict(img, conf=self.conf, verbose=False)
        annotated = results[0].plot()

        return av.VideoFrame.from_ndarray(annotated, format="bgr24")

processor = YOLOVideoProcessor()
processor.conf = conf

webrtc_streamer(
    key="bluesight-live",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIG,
    video_processor_factory=lambda: processor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)
