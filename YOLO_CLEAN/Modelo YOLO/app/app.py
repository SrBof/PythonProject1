import os
import tempfile
import glob
import importlib.util
import subprocess
from shutil import which
import base64
import streamlit as st

# =========================
# CONFIG
# =========================
LOGO_URL = "https://i.imgur.com/gH6dXd3.jpeg"
LOGO_TAG = f'<img src="{LOGO_URL}" alt="Logo Bluesight" style="height: 30px; margin-right: 10px;"/>'
URL_INICIO = "http://localhost:8501"

# =========================
# HELPERS
# =========================

import base64

def st_video_fit_card(path: str, uid: int, max_height_px: int = 420):
    ext = os.path.splitext(path)[1].lower().replace(".", "")
    if ext not in ["mp4", "webm", "ogg"]:
        ext = "mp4"

    with open(path, "rb") as f:
        data = f.read()

    b64 = base64.b64encode(data).decode("utf-8")

    st.markdown(
        f"""
        <div id="video-wrap-{uid}" style="width: 100%; max-height: {max_height_px}px; overflow: hidden; border-radius: 10px;">
          <video controls style="width: 100%; height: auto; max-height: {max_height_px}px; display: block;">
            <source src="data:video/{ext};base64,{b64}" type="video/{ext}">
          </video>
        </div>
        """,
        unsafe_allow_html=True
    )


def load_css(file_name: str):
    try:
        css_path = os.path.join(os.path.dirname(__file__), file_name)
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo CSS en la ruta: {css_path}")


def save_uploaded_file(uploaded_file) -> str:
    """Guarda el archivo subido en una carpeta temporal y retorna la ruta absoluta."""
    tmp_dir = tempfile.mkdtemp()
    out_path = os.path.join(tmp_dir, uploaded_file.name)
    with open(out_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return out_path


def import_script(script_path: str):
    """Importa dinámicamente un .py desde una ruta."""
    spec = importlib.util.spec_from_file_location("offline_mod", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod

def st_video_from_file(path: str):
    size = os.path.getsize(path)
    st.caption(f"Video: {os.path.basename(path)} | {size/1024:.1f} KB")
    if size < 2000:
        st.error("El archivo de video es demasiado pequeño (posible archivo corrupto).")
        return

    # key variable para evitar caché raro
    with open(path, "rb") as f:
        data = f.read()

    st.video(data, format="video/mp4", start_time=0)


def find_latest_output(folder: str):
    """
    Busca el output más reciente generado por YOLO.
    Soporta video (mp4/avi/mov/mkv) e imágenes (jpg/png).
    Retorna (ruta, tipo) donde tipo es 'video' o 'image'.
    """
    patterns = ["*.mp4", "*.avi", "*.mov", "*.mkv", "*.jpg", "*.jpeg", "*.png"]
    files = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(folder, p)))

    if not files:
        return None, None

    files.sort(key=os.path.getmtime, reverse=True)
    latest = files[0]
    ext = os.path.splitext(latest)[1].lower()

    if ext in [".mp4", ".avi", ".mov", ".mkv"]:
        return latest, "video"
    return latest, "image"


def ensure_mp4_h264(input_video_path: str) -> str:
    """
    Convierte a MP4 H.264 + AAC con faststart (máxima compatibilidad web).
    Retorna ruta del mp4 final.
    """
    ffmpeg = which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg no está en PATH. Instálalo: winget install Gyan.FFmpeg")

    base, _ = os.path.splitext(input_video_path)
    out_path = base + "_h264.mp4"

    cmd = [
        ffmpeg, "-y",
        "-i", input_video_path,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "aac",
        "-b:a", "128k",
        out_path
    ]
    subprocess.run(cmd, check=True)
    return out_path


def st_video_from_file(path: str):
    """Renderiza video como bytes (más compatible que pasar solo la ruta)."""
    with open(path, "rb") as f:
        st.video(f.read())


# =========================
# PAGE
# =========================
st.set_page_config(
    page_title="BlueSight - Detección Inteligente",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# SESSION STATE
# =========================
if "result_path" not in st.session_state:
    st.session_state["result_path"] = None
if "result_type" not in st.session_state:
    st.session_state["result_type"] = None
if "save_dir" not in st.session_state:
    st.session_state["save_dir"] = None
if "result_id" not in st.session_state:
    st.session_state["result_id"] = 0

load_css("styles/main.css")

# =========================
# HEADER (HTML)
# =========================
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

st.markdown('<div style="height: 0px;"></div>', unsafe_allow_html=True)

# =========================
# MAIN LAYOUT
# =========================
col_left, col_right = st.columns([1, 2.5], gap="large")

with col_left:
    st.header("Subir Archivo")

    file = st.file_uploader(
        "Escoge o arrastra un archivo",
        type=["mp4", "avi", "mov", "mkv", "jpg", "jpeg", "png"],
        key="main_uploader"
    )

    if file is not None:
        # Si cambió el archivo, resetea el resultado
        if st.session_state.get("last_uploaded_name") != file.name:
            st.session_state["last_uploaded_name"] = file.name
            st.session_state["result_path"] = None
            st.session_state["result_type"] = None
            st.session_state["save_dir"] = None
            st.session_state["result_id"] += 1  # fuerza “nueva identidad” visual

    analyze_clicked = st.button(
        "Analizar Archivo",
        use_container_width=True,
        type="primary"
    )

    st.text("")
    st.subheader("¿No tienes un video?")
    if st.button("Prueba tú mismo", use_container_width=True):
        st.switch_page("pages/1_Prueba_en_vivo.py")
    st.markdown(
        '<p style="font-size: 14px; margin-top: 10px; color: #6C757D;">Usa tu cámara de celular para probarlo en tiempo real.</p>',
        unsafe_allow_html=True
    )

with col_right:
    st.header("Mapa de Calor - Detección de Arándanos")
    st.markdown(
        '<p style="color: #6C757D;">Visualización de la densidad y distribución de arándanos detectados</p>',
        unsafe_allow_html=True
    )

    if st.session_state["result_path"] and os.path.exists(st.session_state["result_path"]):
        if st.session_state["result_type"] == "video":
            st_video_fit_card(
                st.session_state["result_path"],
                uid=st.session_state["result_id"],
                max_height_px=420
            )
        else:
            st.image(st.session_state["result_path"], use_column_width=True)
        if st.session_state.get("save_dir"):
            st.caption(f"Salida: {st.session_state['save_dir']}")
    else:
        st.markdown("""
            <div id="map-container" style="height: 400px; background-color: white; border-radius: 8px; border: 1px solid #CED4DA; display: flex; justify-content: center; align-items: center;">
                <div style="text-align: center; color: #ADB5BD; background-color: white; padding: 20px; border-radius: 10px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3m-18 0v3a2 2 0 0 0 2 2h3"></path>
                    </svg>
                    <p style="margin-top: 20px; font-size: 16px;">Sube un video o imagen para ver el resultado</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

# =========================
# RUN YOLO ON CLICK
# =========================
if analyze_clicked:
    if file is None:
        st.warning("Primero sube un archivo (video o imagen).")
    else:
        source_path = save_uploaded_file(file)

        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "script.py"))
        offline = import_script(script_path)

        with st.spinner("Analizando con YOLO..."):
            save_dir = offline.run_offline(source_path)

        st.session_state["save_dir"] = save_dir

        out_path, out_type = find_latest_output(save_dir)

        if out_path:
            if out_type == "video":
                ext = os.path.splitext(out_path)[1].lower()
                if ext != ".mp4":
                    try:
                        out_path = ensure_mp4_h264(out_path)
                    except Exception as e:
                        st.warning(f"No pude convertir a MP4: {e}")

            st.session_state["result_path"] = out_path
            st.session_state["result_type"] = out_type
            st.success("Análisis completado. Mostrando resultado.")
            st.session_state["result_path"] = out_path
            st.session_state["result_type"] = out_type
            st.session_state["result_id"] += 1  # fuerza refresh del video
            st.rerun()

            st.rerun()
        else:
            st.session_state["result_path"] = None
            st.session_state["result_type"] = None
            st.info("El análisis terminó, pero no se encontró salida visual.")
