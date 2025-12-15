import os
import cv2
import av
import torch
import streamlit as st
from ultralytics import YOLO
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode


# =========================
# CONFIG HEADER (igual que app.py)
# =========================
LOGO_URL = "https://i.imgur.com/gH6dXd3.jpeg"
LOGO_TAG = f'<img src="{LOGO_URL}" alt="Logo Bluesight" style="height: 30px; margin-right: 10px;"/>'
URL_INICIO = "http://localhost:8501"


# =========================
# PATHS (root del proyecto + modelo)
# pages/ -> app/ -> Modelo YOLO
# =========================
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Ajusta aquí si tu corrida de modelo es otra (ej: 75epochs)
MODEL_PATH = os.path.join(
    ROOT_DIR, "runs", "detect", "innova_colorimetria3", "weights", "best.pt"
)

RTC_CONFIG = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}


# =========================
# HELPERS (CSS + header)
# =========================
def load_css(file_name: str):
    # En pages/, __file__ apunta a .../app/pages/
    # main.css suele estar en .../app/styles/main.css
    css_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", file_name))
    try:
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"No se encontró CSS en: {css_path}")

def render_header():
    st.markdown(
        f"""
        <div class="custom-header">
            <div class="logo-container">
                <a href="{URL_INICIO}" style="text-decoration: none; color: inherit;">
                    {LOGO_TAG}
                    <span style="font-weight: bold; color: #4B0082; font-size: 20px;">BlueSight</span>
                </a>
            </div>
            <div class="header-menu-container">
                <div class="fixed-functional-buttons">
                    <button class="icon-btn-style" title="Notificaciones">🔔</button>
                    <button class="icon-btn-style" title="Configuración">⚙️</button>
                </div>
                <div class="user-info-text">Alberto Bofill</div>
                <div class="profile-icon">AB</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    # “separador” para que no se monte el contenido con el header fijo
    st.markdown('<div style="height: 0px;"></div>', unsafe_allow_html=True)


# =========================
# PAGE
# =========================
st.set_page_config(page_title="BlueSight - Prueba en vivo", layout="wide", initial_sidebar_state="collapsed")
load_css("styles/main.css")
render_header()


# =========================
# MODELO (cacheado)
# =========================
@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"No se encontró el modelo en: {MODEL_PATH}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("[LIVE] device:", device)
    print("[LIVE] model_path:", MODEL_PATH)

    m = YOLO(MODEL_PATH)
    m.to(device)
    return m

model = load_model()


# =========================
# UI PRINCIPAL (mismo layout: 1 / 2.5)
# =========================
col_left, col_right = st.columns([1, 2.5], gap="large")

with col_left:
    st.header("Prueba tú mismo")
    st.markdown(
        '<p style="color: #6C757D;">Activa tu cámara y mira las detecciones en tiempo real.</p>',
        unsafe_allow_html=True
    )

    conf = st.slider("Confianza (conf)", 0.05, 0.90, 0.35, 0.05)
    st.caption("Tip: si va lento, baja resolución o sube conf.")

    with st.expander("Debug (rutas)", expanded=False):
        st.write("ROOT_DIR:", ROOT_DIR)
        st.write("MODEL_PATH:", MODEL_PATH)
        st.write("MODEL_EXISTS:", os.path.exists(MODEL_PATH))

with col_right:
    st.header("Vista en vivo (detección)")
    st.markdown(
        '<p style="color: #6C757D;">La cámara corre en el navegador y el modelo anota los frames en la app.</p>',
        unsafe_allow_html=True
    )

    # Contenedor para que se vea “dentro de una caja” similar a tus cards
    st.markdown('<div class="content-card" style="min-height: 520px;">', unsafe_allow_html=True)

    class YOLOVideoProcessor(VideoProcessorBase):
        def __init__(self):
            self.conf = 0.35

        def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
            img = frame.to_ndarray(format="bgr24")

            # Ajusta tamaño: más chico = más rápido
            img = cv2.resize(img, (640, 480))

            results = model.predict(img, conf=self.conf, verbose=False)
            annotated = results[0].plot(labels=False, conf=False)

            return av.VideoFrame.from_ndarray(annotated, format="bgr24")

    def processor_factory():
        p = YOLOVideoProcessor()
        p.conf = conf
        return p

    webrtc_streamer(
        key="bluesight-live",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIG,
        video_processor_factory=processor_factory,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
