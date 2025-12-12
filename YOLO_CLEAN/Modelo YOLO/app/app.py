# https://youtube.com/shorts/eQX6W1f6r5Y?si=_Rpr7uVtuplsQN_P
import streamlit as st
import os

# ⚠️ URL del Logo - REEMPLAZA ESTA URL CON EL ENLACE DIRECTO DE TU IMAGEN
LOGO_URL = "https://i.imgur.com/gH6dXd3.jpeg"
LOGO_TAG = f'<img src="{LOGO_URL}" alt="Logo Bluesight" style="height: 30px; margin-right: 10px;"/>'
URL_INICIO = "http://localhost:8501"


# ====================================================================
# FUNCIÓN Y CONFIGURACIÓN INICIAL
# ====================================================================

def load_css(file_name):
    """Carga el CSS desde un archivo externo."""
    try:
        css_path = os.path.join(os.path.dirname(__file__), file_name)
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo CSS en la ruta: {css_path}")


st.set_page_config(
    page_title="BlueSight - Detección Inteligente",
    layout="wide",
    initial_sidebar_state="collapsed"
)

load_css("styles/main.css")

# ====================================================================
# BARRA DE NAVEGACIÓN (SOLUCIÓN FINAL Y LÓGICA DE BOTONES)
# ====================================================================

# 1. Creamos y ocultamos los botones funcionales (Streamlit los necesita para el callback)
#    Creamos los botones en un contenedor invisible (fuera de la vista).

st.markdown('<div style="position: fixed; top: -100px; opacity: 0;">', unsafe_allow_html=True)
if st.button("🔔", key="notify_btn_funcional", help="Ver notificaciones"):
    st.toast("Notificaciones: No hay alertas.", icon="🔔")

if st.button("⚙️", key="settings_btn_funcional", help="Configuración de usuario"):
    st.toast("Configuración abierta (funcionalidad pendiente)", icon="⚙️")
st.markdown('</div>', unsafe_allow_html=True)

# 2. Renderizamos el diseño estético FIJO (Este es el que el usuario ve)
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
                <button onclick="document.querySelector('[key=\"notify_btn_funcional\"]').click()" class="icon-btn-style">🔔</button>
                <button onclick="document.querySelector('[key=\"settings_btn_funcional\"]').click()" class="icon-btn-style">⚙️</button>
            </div>

            <div class="user-info-text">Alberto Bofill</div>
            <div class="profile-icon">AB</div>
        </div>
    </div>
    """, unsafe_allow_html=True
)

# 3. Aplicamos un div vacío para asegurar que el contenido inferior se renderice correctamente
#    después del header fijo.
st.markdown('<div style="height: 0px;"></div>', unsafe_allow_html=True)

# ====================================================================
# CONTENIDO PRINCIPAL (TARJETAS DE BIENVENIDA)
# ====================================================================

# 1. Manejo del estado para el file_uploader (debe ir fuera de cualquier columna)
if 'file_ready' not in st.session_state:
    st.session_state['file_ready'] = False

col_left, col_right = st.columns([1, 2.5], gap="large")

with col_left:
    # --- Tarjeta 1: Subir Archivo ---
    st.markdown('<div class="content-card" style="position: relative;">', unsafe_allow_html=True)
    st.header("Subir Archivo")

    # st.file_uploader funcional (con lógica de estado)
    file = st.file_uploader("Escoge o arrastra un archivo", type=["csv", "mp4", "jpg", "jpeg", "png"])
    if file is not None and not st.session_state['file_ready']:
        st.success(f"Archivo cargado: {file.name}")
        st.session_state['file_ready'] = True
    elif file is None and st.session_state['file_ready']:
        st.session_state['file_ready'] = False

    # Botón Análisis (Simulado)
    st.markdown('<div class="grad-button-1"><a href="#">Analizar Archivo</a></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


    st.text("") # Espacio


    # --- Tarjeta 2: Prueba Tú Mismo ---
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("¿No tienes un video?")
    st.markdown('<div class="grad-button-2"><a href="#">Prueba tú mismo</a></div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size: 14px; margin-top: 10px; color: #6C757D;">Usa tu camara de celular para probarlo en tiempo real.</p>',
        unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


with col_right:
    # --- Mapa de Calor PLACEHOLDER ---
    st.markdown('<div class="content-card" style="min-height: 600px;">', unsafe_allow_html=True)
    st.header("Mapa de Calor - Detección de Arándanos")
    st.markdown('<p style="color: #6C757D;">Visualización de la densidad y distribución de arándanos detectados</p>',
                unsafe_allow_html=True)

    # Contenedor del Mapa con Placeholder Overlay
    st.markdown("""
        <div id="map-container" style="height: 400px; background-color: white; border-radius: 8px; border: 1px solid #CED4DA; display: flex; justify-content: center; align-items: center;">
            <div style="text-align: center; color: #ADB5BD; background-color: white; padding: 20px; border-radius: 10px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3m-18 0v3a2 2 0 0 0 2 2h3"></path></svg>
                <p style="margin-top: 20px; font-size: 16px;">Sube un video o imagen para ver el mapa de calor</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)