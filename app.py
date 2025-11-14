#Practica 2 - Visión por Computador con ESP32-CAM y Flask
#Aplicación web en Flask que procesa video en tiempo real desde una cámara ESP32-CAM
# Nombres: Felipe Peralta y Samantha Suquilanda

from flask import Flask, render_template, Response
from io import BytesIO 
import cv2
import numpy as np 
import requests 
import torch 
import torch.nn.functional as F 
import time 

app = Flask(__name__) 

# SEcción 3: configuración de la cámara

_URL = 'http://192.168.68.106' # IP de tu ESP32-CAM
_PORT = '81'             # Puerto estándar del stream
_ST = '/stream'          # Ruta estándar del stream
SEP = ':'
stream_url = ''.join([_URL, SEP, _PORT, _ST]) 

# Parte 1-A
backSub = cv2.createBackgroundSubtractorMOG2()
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
tiempo_prev = 0

# Parte 1-B
def mas_ruido_gaussiano(imagen):
    fila, col, ch = imagen.shape
    mean = 0
    std = 25 
    gauss = np.random.normal(mean, std, (fila, col, ch))
    gauss = gauss.reshape(fila, col, ch)
    ruido = imagen + gauss
    return np.clip(ruido, 0, 255).astype(np.uint8)

def mas_ruido_speckle(imagen):
    fila, col, ch = imagen.shape
    gauss = np.random.randn(fila, col, ch) * 0.5 
    gauss = gauss.reshape(fila, col, ch)
    ruido = imagen + imagen * gauss
    return np.clip(ruido, 0, 255).astype(np.uint8)

# aqui capturamos el video
def cap_video():
    global tiempo_prev, backSub, clahe 

    # metodo para capturar video desde la cámara ESP32-CAM
    # usamos cv2.VideoCapture.
    # una función está diseñada para manejar streams MJPEG
    print(f"Intentando conectar a: {stream_url}")
    cap = cv2.VideoCapture(stream_url) 
    
    # Verificamos si la conexión fue exitosa
    if not cap.isOpened():
        print(f"Error: No se pudo abrir el stream de video en {stream_url}")
        # Genera el mismo frame de error
        img_error = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(img_error, "Error: Camara no conectada", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        while True:
            (flag, encodedImage) = cv2.imencode(".jpg", img_error)
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                  bytearray(encodedImage) + b'\r\n')
            time.sleep(1)

    print("¡Conexión exitosa al stream! Empezando procesamiento...")

    # Tarea 1-B: Definimos el kernel para el filtro PyTorch
    kernel_sharpen = torch.tensor([[ 0, -1,  0],
                                   [-1,  5, -1],
                                   [ 0, -1,  0]], dtype=torch.float32)
    kernel_torch = kernel_sharpen.unsqueeze(0).unsqueeze(0)

    # un bucle infinito para procesar cada frame
    while True:
        try:
            # leer el frame de la cámara
            # 'cap.read()' lee el stream y decodifica un frame
            ret, cv_img = cap.read()
            
            # Si 'ret' es False, significa que el frame está corrupto o se perdió la conexión
            if not ret or cv_img is None:
                print("Error: Frame perdido o corrupto. Reintentando...")
                continue # Salta esta iteración y prueba con el siguiente frame

            # cálculo de FPS
            tiempo_actual = time.time()
            fps = 1 / (tiempo_actual - tiempo_prev)
            tiempo_prev = tiempo_actual

            # procesos para la parte 1-A
            fgMask = backSub.apply(cv_img)
            frame_recortado = cv2.bitwise_and(cv_img, cv_img, mask=fgMask)
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            equ = cv2.equalizeHist(gray)
            clahe_img = clahe.apply(gray)
            
            gamma = 1.5 
            lup = np.empty((1,256), np.uint8)
            for i in range(256):
                lup[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
            gamma_img = cv2.LUT(cv_img, lup)

            # procesos para la parte 1-B
            ruido_frame = mas_ruido_gaussiano(cv_img.copy())
            mediana_filtro = cv2.medianBlur(ruido_frame, 5)
            gaussian_filtro = cv2.GaussianBlur(ruido_frame, (5, 5), 0)
            blur_filtro = cv2.blur(ruido_frame, (5, 5))

            img_tensor = torch.from_numpy(gray.astype(np.float32)).unsqueeze(0).unsqueeze(0)
            convolved_output = F.conv2d(
                input = img_tensor,
                weight = kernel_torch, 
                padding = 1, 
                bias = None
            )
            img_output_torch = convolved_output.cpu().numpy().squeeze()
            img_output_torch = cv2.convertScaleAbs(img_output_torch)

            gray_filtered_edges = cv2.cvtColor(gaussian_filtro, cv2.COLOR_BGR2GRAY)
            edges_canny = cv2.Canny(gray_filtered_edges, 100, 200)
            sobel_x = cv2.Sobel(gray_filtered_edges, cv2.CV_64F, 1, 0, ksize=5)
            sobel_y = cv2.Sobel(gray_filtered_edges, cv2.CV_64F, 0, 1, ksize=5)
            edges_sobel = cv2.convertScaleAbs(cv2.magnitude(sobel_x, sobel_y))

            # preparación de la salida visual
            cv2.putText(cv_img, f"FPS: {int(fps)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            clahe_img_bgr = cv2.cvtColor(clahe_img, cv2.COLOR_GRAY2BGR)
            edges_canny_bgr = cv2.cvtColor(edges_canny, cv2.COLOR_GRAY2BGR)
            
            H, W = 240, 320
            frame_original = cv2.resize(cv_img, (W, H))
            frame_fondo = cv2.resize(frame_recortado, (W, H))
            frame_clahe = cv2.resize(clahe_img_bgr, (W, H))
            frame_bordes = cv2.resize(edges_canny_bgr, (W, H))

            top_fila = np.hstack((frame_original, frame_fondo))
            bottom_fila = np.hstack((frame_clahe, frame_bordes))
            total_image = np.vstack((top_fila, bottom_fila))

            # codificación y streaming
            (flag, encodedImage) = cv2.imencode(".jpg", total_image)
            if not flag:
                continue
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                  bytearray(encodedImage) + b'\r\n')

        except Exception as e:
            print(f"Error en el bucle de procesamiento: {e}")
            # Si hay un error, saltamos al siguiente frame
            continue
    
    # liberar recursos al finalizar
    print("Cerrando el stream...")
    cap.release()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_stream")
def video_stream():
    return Response(cap_video(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

# ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)