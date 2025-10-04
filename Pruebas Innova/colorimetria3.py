import cv2
import numpy as np
import math

pixeles_x_cm = 40.0 # 40 px = 1cm esto para

azul_bajo = np.array([105, 80, 40], dtype=np.uint8)
azul_alto = np.array([125, 255, 255], dtype=np.uint8)

area_min_arandano = 12 # area minima del circulo pa ser considerado arandano
circ_min_arandano = 0.75 # circularidad pa ser considerado arandano
tamano_kernel = 5

camara = cv2.VideoCapture("https//:192.100.124") #0 es camara de pc
if not camara.isOpened():
    raise RuntimeError("No se abrio la cámara gil.")

kernel = np.ones((tamano_kernel, tamano_kernel), np.uint8) #kernel cuadrado para limpiar imagen


def diametros_px(contorno): #funcion retorna diametro y ejes alto y largo para definir el contorno de la imagen
    area = cv2.contourArea(contorno)
    if area <= 0:
        return None, None, {}
    d_eq_px = 2.0 * math.sqrt(area / math.pi)

    d_morf_px = None
    major = minor = None
    if len(contorno) >= 5:
        (cx, cy), (MA, ma), ang = cv2.fitEllipse(contorno) #se ajusta la elipse al contorno
        major, minor = (max(MA, ma), min(MA, ma))
        d_morf_px = minor
    else:
        # Fallback: círculo envolvente
        (x, y), r = cv2.minEnclosingCircle(contorno)
        d_morf_px = 2.0 * r

    return d_morf_px, d_eq_px, {"major": major, "minor": minor}


#bucle video en tiempo real
while True:
    ok, frame = camara.read() #lector de frames
    if not ok:
        break

    #conversor frames BGR a HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, azul_bajo, azul_alto)

    # Limpieza
    mask = cv2.medianBlur(mask, 5) #saca ruido
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1) # saca puntos
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1) # rellena huecos

    # Contornos
    contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #encuentra los contornos
    arandanos = []
    for c in contornos:
        area = cv2.contourArea(c)
        if area < area_min_arandano:
            continue
        per = cv2.arcLength(c, True)
        if per <= 0: #por si la circularidad es 0
            continue
        circ = 4 * math.pi * area / (per * per)  #float 0-1 con 1 circulo perfecto
        if circ < circ_min_arandano:#linea 11 = 0.55
            continue
        arandanos.append(c) #si circularidad es mayor al minimo, se agrega un arandano

    # Camara con solo azul detectado
    camara_azul = cv2.bitwise_and(frame, frame, mask=mask)

    # Diámetros y conteo
    vis = frame.copy()
    total = 0
    for c in arandanos:
        x, y, w, h = cv2.boundingRect(c) #rectangulo para caja
        cv2.rectangle(vis, (x, y), (x + w, y + h), (255, 0, 0), 2) #dibujo de caja en contorno

        d_morf_px, d_eq_px, ex = diametros_px(c) #se calcula la morfologia
        if d_morf_px is None:
            continue
        total += 1 #se agrega arandano

        # Conversión a cm
        d_morf_cm = d_morf_px / pixeles_x_cm
        d_eq_cm = d_eq_px / pixeles_x_cm if d_eq_px is not None else None

        # Texto
        txt = f"{d_morf_cm:.2f} cm"
        if d_eq_cm is not None:
            txt += f"{d_eq_cm:.2f} cm"
        cv2.putText(vis, txt, (x, max(0, y - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 255), 1, cv2.LINE_AA)

        # Dibuja elipse si se pudo ajustar
        if ex.get("major") is not None:
            ellipse = cv2.fitEllipse(c)
            cv2.ellipse(vis, ellipse, (0, 255, 0), 2)
        else:
            # Si no hay elipse, dibuja el círculo envolvente
            (cx, cy), r = cv2.minEnclosingCircle(c)
            cv2.circle(vis, (int(cx), int(cy)), int(r), (0, 255, 0), 2)

    # Conteo total en pantalla
    cv2.putText(vis, f"arandanos: {total}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                (0, 0, 0), 2, cv2.LINE_AA)

    cv2.imshow("visualizacion arananos", vis)
    cv2.imshow("Solo azul detectado", camara_azul)

    # sale del programa con q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camara.release()
cv2.destroyAllWindows()