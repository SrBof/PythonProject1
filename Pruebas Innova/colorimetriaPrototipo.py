import cv2
import numpy as np
import time
import csv
import os
import matplotlib.pyplot as plt

# -------- Config general --------
FUENTE_CAMARA = 0  # 0 = cámara del PC
ESCALA_VENTANA = 1  # para mostrar más chico sin matar la CPU

# Filtros morfológicos (limpieza de máscara)
TAMANO_KERNEL = 5
AREA_MINIMA = 120  # área mínima del contorno para considerar "arándano"
CIRC_MINIMA = 0.65  # qué tan circular debe ser (1 = círculo perfecto)

# Rango inicial HSV (OpenCV: H:0-179, S/V:0-255)
H_MIN_INI, H_MAX_INI = 105, 125
S_MIN_INI, V_MIN_INI = 80, 40

# Parámetros Lab (OpenCV Lab: L/a/b en 0..255; 128 ~ centro de a/b)
# Azul real = b tirando a bajo, L bajo = más oscuro. Se ajusta en terreno.
L_MAX_INI = 140  # L <= L_MAX
B_MAX_INI = 135  # b <= B_MAX

# Pesos para el "puntaje de azul maduro"
# Pesos sujetos a arándano ideal*
PESO_SAT, PESO_OSCURO, PESO_AZUL = 0.5, 0.25, 0.25

# Salidas (carpeta y archivos)
CARPETA_SALIDA = "salidas_arandanos_1"
RUTA_CSV = os.path.join(CARPETA_SALIDA, "registro_arandanos.csv")
RUTA_HEATMAP = os.path.join(CARPETA_SALIDA, "heatmap_arandanos.png")
os.makedirs(CARPETA_SALIDA, exist_ok=True)

# Índices de dónde vamos (hilera/planta) para ir guardando
fila_actual = 1
planta_actual = 1

# Acá acumulamos lo medido por (fila, planta)
# registro[(fila, planta)] = {"n": cantidad_arandanos, "rate_azul": suma_puntajes}
registro = {}


# -------- Utilidades varias --------
def dibujar_texto(img, texto, origen, color=(255, 255, 255), escala=0.6, grosor=1, con_fondo=True):
    # Texto con fondo negro para que no se pierda con el fondo
    if con_fondo:
        (w, h), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, escala, grosor)
        cv2.rectangle(img, (origen[0] - 4, origen[1] - h - 6), (origen[0] + w + 4, origen[1] + 4), (0, 0, 0), -1)
    cv2.putText(img, texto, origen, cv2.FONT_HERSHEY_SIMPLEX, escala, color, grosor, cv2.LINE_AA)


VENTANA_CALIBRE = "Calibracion"
_cache_param = None  # guardamos último valor bueno para no caernos si cierran la ventana


def asegurar_barras():
    """Si la ventana de sliders no existe, la armamos de nuevo. Nada fancy."""

    def nada(x):
        pass

    try:
        visible = cv2.getWindowProperty(VENTANA_CALIBRE, cv2.WND_PROP_VISIBLE)
    except cv2.error:
        visible = -1
    if visible == -1:
        cv2.namedWindow(VENTANA_CALIBRE, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(VENTANA_CALIBRE, 420, 400)
        cv2.createTrackbar("H_MIN", VENTANA_CALIBRE, H_MIN_INI, 179, nada)
        cv2.createTrackbar("H_MAX", VENTANA_CALIBRE, H_MAX_INI, 179, nada)
        cv2.createTrackbar("S_MIN", VENTANA_CALIBRE, S_MIN_INI, 255, nada)
        cv2.createTrackbar("V_MIN", VENTANA_CALIBRE, V_MIN_INI, 255, nada)
        cv2.createTrackbar("L_MAX", VENTANA_CALIBRE, L_MAX_INI, 255, nada)
        cv2.createTrackbar("b_MAX", VENTANA_CALIBRE, B_MAX_INI, 255, nada)


def leer_barras():
    """Leemos sliders y si la ventana no existe, la recreamos. Si falla, devolvemos algo razonable."""
    global _cache_param
    asegurar_barras()
    try:
        H_MIN = cv2.getTrackbarPos("H_MIN", VENTANA_CALIBRE)
        H_MAX = cv2.getTrackbarPos("H_MAX", VENTANA_CALIBRE)
        S_MIN = cv2.getTrackbarPos("S_MIN", VENTANA_CALIBRE)
        V_MIN = cv2.getTrackbarPos("V_MIN", VENTANA_CALIBRE)
        L_MAX = cv2.getTrackbarPos("L_MAX", VENTANA_CALIBRE)
        B_MAX = cv2.getTrackbarPos("b_MAX", VENTANA_CALIBRE)
        _cache_param = (H_MIN, H_MAX, S_MIN, V_MIN, L_MAX, B_MAX)
        return _cache_param
    except cv2.error:
        return _cache_param if _cache_param is not None else (
        H_MIN_INI, H_MAX_INI, S_MIN_INI, V_MIN_INI, L_MAX_INI, B_MAX_INI)


def combinar_mascaras(m1, m2):
    return cv2.bitwise_and(m1, m2)


def normalizar_01(x, xmin, xmax):
    return np.clip((x - xmin) / (xmax - xmin + 1e-6), 0.0, 1.0)


def calcular_puntaje(prom_hsv, prom_lab):
    # prom_hsv: (H,S,V) ; prom_lab: (L,a,b)
    S = prom_hsv[1];
    V = prom_hsv[2];
    b = prom_lab[2];
    L = prom_lab[0]
    sat_norm = normalizar_01(S, 0, 255)  # más saturado = más "azul puro"
    oscuro_norm = normalizar_01(255 - V, 0, 255)  # V bajo = más oscuro
    azul_norm = normalizar_01(128 - b, 0, 128)  # b bajo = más azul
    puntaje = PESO_SAT * sat_norm + PESO_OSCURO * oscuro_norm + PESO_AZUL * azul_norm
    return float(puntaje)


def actualizar_registro(fila, planta, puntajes_arandanos):
    if len(puntajes_arandanos) == 0:
        return
    clave = (fila, planta)
    if clave not in registro:
        registro[clave] = {"n": 0, "rate_azul": 0.0}
    registro[clave]["n"] += len(puntajes_arandanos)
    registro[clave]["rate_azul"] += float(np.sum(puntajes_arandanos))


def guardar_csv(ruta=RUTA_CSV):
    ordenado = sorted(registro.items(), key=lambda x: (x[0][0], x[0][1]))
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["fila", "planta", "n_arandanos", "rate_azul"])
        for (fila, planta), vals in ordenado:
            n = vals["n"]
            prom = vals["rate_azul"] / max(n, 1)
            w.writerow([fila, planta, n, round(prom, 4)])
    print(f"[OK] CSV guardado en: {ruta}")


def guardar_mapa_calor(ruta=RUTA_HEATMAP):
    if not registro:
        print("[ALERTA] No hay datos para heatmap.")
        return
    filas = [k[0] for k in registro.keys()]
    plantas = [k[1] for k in registro.keys()]
    Fmax, Pmax = max(filas), max(plantas)
    matriz = np.full((Fmax, Pmax), np.nan, dtype=float)
    for (fila, planta), vals in registro.items():
        n = vals["n"]
        prom = vals["rate_azul"] / max(n, 1)
        matriz[fila - 1, planta - 1] = prom
    plt.figure(figsize=(max(6, Pmax / 2), max(4, Fmax / 2)))
    plt.imshow(matriz, interpolation="nearest", aspect="auto")
    plt.colorbar(label="Score madurez (0..1)")
    plt.xlabel("Planta")
    plt.ylabel("Hilera")
    plt.title("Mapa de madurez por hilera/planta")
    plt.tight_layout()
    plt.savefig(ruta, dpi=200)
    plt.close()
    print(f"[OK] Heatmap guardado en: {ruta}")


# -------- (Opcional) ArUco para indexar hileras/plantas automático --------
ID_ARUCO_A_FILA_PLANTA = {
    # Ejemplos:
    # 10: (1, 1),
    # 11: (1, 2),
}
try:
    aruco = cv2.aruco
    DICC_ARUCO = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    PARAM_ARUCO = aruco.DetectorParameters()
except Exception:
    aruco = None
    print("[INFO] cv2.aruco no disponible (instala opencv-contrib-python si quieres ArUco).")


# -------- Loop principal --------
def main():
    global fila_actual, planta_actual

    cap = cv2.VideoCapture(FUENTE_CAMARA)
    if not cap.isOpened():
        raise RuntimeError("No se pudo abrir la cámara")

    asegurar_barras()
    kernel = np.ones((TAMANO_KERNEL, TAMANO_KERNEL), np.uint8)

    t_ultimo = time.time()
    fps_aprox = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            print("[WARN] Frame no leído.")
            break

        # Mostramos más chico para no reventar la cpu
        h, w = frame.shape[:2]
        vista = cv2.resize(frame, (int(w * ESCALA_VENTANA), int(h * ESCALA_VENTANA)))

        # Leemos parámetros actuales de los sliders
        H_MIN, H_MAX, S_MIN, V_MIN, L_MAX, B_MAX = leer_barras()

        # Espacios de color
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

        # Máscara por HSV (color)
        hsv_inf = np.array([H_MIN, S_MIN, V_MIN], dtype=np.uint8)
        hsv_sup = np.array([H_MAX, 255, 255], dtype=np.uint8)
        mascara_hsv = cv2.inRange(hsv, hsv_inf, hsv_sup)

        # Máscara por Lab (oscuridad + "azulez")
        L, a, b = cv2.split(lab)
        masc_L = cv2.threshold(L, L_MAX, 255, cv2.THRESH_BINARY_INV)[1]  # 1 si L <= L_MAX
        masc_b = cv2.threshold(b, B_MAX, 255, cv2.THRESH_BINARY_INV)[1]  # 1 si b <= B_MAX
        mascara_lab = cv2.bitwise_and(masc_L, masc_b)

        # Intersección: que sea azul y además oscuro (más robusto que solo HSV)
        mascara = combinar_mascaras(mascara_hsv, mascara_lab)

        # Limpieza piola para sacar puntitos sueltos y rellenar agujeros
        mascara = cv2.medianBlur(mascara, 5)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel, iterations=1)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel, iterations=1)

        # Buscamos contornos (posibles arándanos)
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        arandanos_detectados = []
        puntajes_arandanos = []

        for c in contornos:
            area = cv2.contourArea(c)
            if area < AREA_MINIMA:
                continue
            per = cv2.arcLength(c, True)
            if per <= 0:
                continue
            circ = 4 * np.pi * area / (per * per)
            if circ < CIRC_MINIMA:
                continue

            # Promedios de color dentro del contorno
            masc_c = np.zeros(mascara.shape, dtype=np.uint8)
            cv2.drawContours(masc_c, [c], -1, 255, thickness=cv2.FILLED)

            prom_hsv = cv2.mean(hsv, mask=masc_c)  # (H,S,V,alpha)
            prom_lab = cv2.mean(lab, mask=masc_c)  # (L,a,b,alpha)
            puntaje = calcular_puntaje(prom_hsv, prom_lab)

            arandanos_detectados.append((c, area, circ, puntaje))
            puntajes_arandanos.append(puntaje)

        # Si usas ArUco para indexar: actualizamos fila/planta según el ID visto
        if aruco is not None and len(ID_ARUCO_A_FILA_PLANTA) > 0:
            esquinas, ids, _ = aruco.detectMarkers(frame, DICC_ARUCO, parameters=PARAM_ARUCO)
            if ids is not None:
                for _id, esquina in zip(ids.flatten(), esquinas):
                    if int(_id) in ID_ARUCO_A_FILA_PLANTA:
                        fila_actual, planta_actual = ID_ARUCO_A_FILA_PLANTA[int(_id)]
                    aruco.drawDetectedMarkers(vista, [cv2.resize(esquina, (esquina.shape[1], esquina.shape[0]))],
                                              ids=None)

        # Guardamos lo visto para esta (fila, planta)
        actualizar_registro(fila_actual, planta_actual, puntajes_arandanos)

        # ----- Ventanas de salida -----
        # a) Máscara en B/N
        mascara_v = cv2.resize(mascara, (vista.shape[1], vista.shape[0]))
        cv2.imshow("Mascara (HSV ∩ Lab)", mascara_v)

        # b) Solo lo detectado (en color)
        solo = cv2.bitwise_and(frame, frame, mask=mascara)
        solo_v = cv2.resize(solo, (vista.shape[1], vista.shape[0]))
        cv2.imshow("Deteccion", solo_v)

        # c) Cámara con overlays (cajas y puntajes)
        overlay = vista.copy()
        # Escala coordenadas de contornos a la vista reescalada
        esc_x = vista.shape[1] / frame.shape[1]
        esc_y = vista.shape[0] / frame.shape[0]
        for c, area, circ, puntaje in arandanos_detectados:
            x, y, w2, h2 = cv2.boundingRect(c)
            x = int(x * esc_x);
            y = int(y * esc_y);
            w2 = int(w2 * esc_x);
            h2 = int(h2 * esc_y)
            cv2.rectangle(overlay, (x, y), (x + w2, y + h2), (255, 0, 0), 2)
            dibujar_texto(overlay, f"{puntaje:.2f}", (x, y - 6), (0, 255, 255), 0.5)

        # HUD (un par de datitos útiles)
        ahora = time.time()
        if ahora - t_ultimo >= 0.5:
            fps_aprox = 1.0 / max(1e-6, (ahora - t_ultimo))
            t_ultimo = ahora
        dibujar_texto(overlay, f"Hilera: {fila_actual}  Planta: {planta_actual}", (10, 24))
        dibujar_texto(overlay, f"Arandanos: {len(arandanos_detectados)}", (10, 48))
        dibujar_texto(overlay, f"FPS~: {fps_aprox:.1f}", (10, 72))
        dibujar_texto(overlay, f"H[{H_MIN},{H_MAX}] S>={S_MIN} V>={V_MIN}  L<={L_MAX} b<={B_MAX}",
                      (10, overlay.shape[0] - 12))

        # Atajos de teclado visibles (por si se te olvidan)
        dibujar_texto(overlay, "Teclas: A/D=planta -/+ | W=fila+ | Z=fila- | S=CSV | H=heatmap | Q=salir",
                      (10, overlay.shape[0] - 36), (200, 255, 200))
        cv2.imshow("Camara", overlay)

        # Controles
        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord('q') or tecla == 27:
            break
        elif tecla == ord('a'):
            planta_actual = max(1, planta_actual - 1)
        elif tecla == ord('d'):
            planta_actual += 1
        elif tecla == ord('w'):
            fila_actual += 1
            planta_actual = 1
        elif tecla == ord('z'):
            fila_actual = max(1, fila_actual - 1)
            planta_actual = 1
        elif tecla == ord('s'):
            guardar_csv(RUTA_CSV)
        elif tecla == ord('h'):
            guardar_csv(RUTA_CSV)
            guardar_mapa_calor(RUTA_HEATMAP)

    cap.release()
    cv2.destroyAllWindows()
    # Guardado general
    guardar_csv(RUTA_CSV)
    guardar_mapa_calor(RUTA_HEATMAP)


if __name__ == "__main__":
    main()
