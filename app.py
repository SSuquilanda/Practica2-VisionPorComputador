#Practica 2 - Visión por Computador con ESP32-CAM y Flask
#Aplicación web en Flask que procesa video en tiempo real desde una cámara ESP32-CAM
# Nombres: Felipe Peralta y Samantha Suquilanda


#Sección 1: usamos las herramientas de flask para crear la app web, render para el html y 
# response para enviar video
from flask import Flask, render_template, Response
from io import BytesIO 

import cv2 # necesitamos opencv
import numpy as np 
import requests # cn esto nos conectamos al stream de la cámara
import torch # PyTorch como lo aprendimos en clase, procesamiento
import torch.nn.functional as F 
import time 

# Secccion 2: inicializamos la app de flask
app = Flask(__name__) 

# SEcción 3: configuración de la cámara

_URL = 'http://10.0.0.11' # Dirección IP de tu ESP32-CAM
_PORT = '81'             # Puerto estándar del stream
_ST = '/stream'          # Ruta estándar del stream
SEP = ':'
stream_url = ''.join([_URL, SEP, _PORT, _ST]) # URL completa: 'http://10.0.0.11:81/stream'

# Parte 1-A

# 1. Sustractor de Fondo (MOG2):Este objeto aprende, por asi decirlo, cuál es el fondo estático y lo separa de lo que se mueve
backSub = cv2.createBackgroundSubtractorMOG2()

# 2. Mejoramos el contraste con clahe, que es un ecualizador de histograma adaptativo
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# 3. dado que necesitamos calcular los FPS, inicializamos una variable para guaradar el tiempo previo
tiempo_prev = 0

# Parte 1-B
# Dado que debemos generar ruido Gaussiano y Speckle, creamos funciones para cada uno.
# en nuestro caso estamos creando una matriz de ruido con numero aleatorios y la sumamos a la imagen original
#Primera función: ruido Gaussiano
def mas_ruido_gaussiano(imagen):
    
    # 'mean' y 'std' (desviación estándar), nos ayuda a definir el ruido
    fila, col, ch = imagen.shape
    mean = 0
    std = 25 # podemos cambiar este valor para aumentar o disminuir el ruido
    gauss = np.random.normal(mean, std, (fila, col, ch))
    gauss = gauss.reshape(fila, col, ch)
    ruido = imagen + gauss
    # esta parte nos ayuda a que los valores no se salgan de 0-255
    return np.clip(ruido, 0, 255).astype(np.uint8)

# Segunda función: ruido Speckle
def mas_ruido_speckle(imagen):

    fila, col, ch = imagen.shape
    gauss = np.random.randn(fila, col, ch) * 0.5 # Juega con este multiplicador
    gauss = gauss.reshape(fila, col, ch)
    ruido = imagen + imagen * gauss
    return np.clip(ruido, 0, 255).astype(np.uint8)

# Tercera función: captura y procesamiento de video
def cap_video():
    global tiempo_prev, backSub, clahe # usamos nuestras variables globales

    # con esto nos conectamos al stream de la cámara
    try:
        res = requests.get(stream_url, stream=True)
    except Exception as e:
        print(f"Error conectando a la cámara: {e}")
        # Si falla, generamos una imagen negra con un mensaje de error
        img_error = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(img_error, "Error: Camara no conectada", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        while True:
            (flag, encodedImage) = cv2.imencode(".jpg", img_error)
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                  bytearray(encodedImage) + b'\r\n')
            time.sleep(1)

    # Tarea 1-B: Definimos el kernel para el filtro PyTorch
    # usaremos un kernel de "Sharpen" (Realce de nitidez), este filtro resta los vecinos y suma 5 al centro, realzando bordes
    kernel_sharpen = torch.tensor([[ 0, -1,  0],
                                   [-1,  5, -1],
                                   [ 0, -1,  0]], dtype=torch.float32)

    # con '.unsqueeze(0).unsqueeze(0)' añadimos las dimensiones de batch y channel
    # ya que PyTorch necesita un formato [B, C, H, W]
    kernel_torch = kernel_sharpen.unsqueeze(0).unsqueeze(0)

    # creamos un bucle de procesamiento infinito
    # 'iter_content' lee el video "chunk" por "chunk"
    for chunk in res.iter_content(chunk_size=100000):
        if len(chunk) > 100:
            try:
                # convertimos nuestro chunk a una imagen OpenCV
                img_chunk = BytesIO(chunk)
                cv_img = cv2.imdecode(np.frombuffer(img_chunk.read(), np.uint8), 1)

                # si la imagen está vacía saltamos al siguiente chunk
                if cv_img is None:
                    continue

                # calculamos los FPS
                tiempo_actual = time.time()
                fps = 1 / (tiempo_actual - tiempo_prev)
                tiempo_prev = tiempo_actual

                # Procesos para la parte 1-A y 1-B
                
                # a) eliminamos el fondo con MOG2 
                # creamos una mascara que es una imagen en blanco y negro
                fgMask = backSub.apply(cv_img)
                
                # b) recortamos la imagen usando la máscara
                # 'bitwise_and' usa la máscara para poner en negro todo lo que NO es el frente
                frame_recortado = cv2.bitwise_and(cv_img, cv_img, mask=fgMask)

                # c) por los filtros de luz necesitamos la imagen en escala de grises
                gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

                # d) crea la imagen ecualizada
                equ = cv2.equalizeHist(gray)

                # e) ecualizamos la imagen usando CLAHE
                clahe_img = clahe.apply(gray)
                
                # f) investigamos el Metodo Gamma
            
                # es importante tener en cuenta que:  Gamma < 1 aclara, Gamma > 1 oscurece.
                gamma = 1.5 
                # Creamos una tabla de consulta para eficiencia, se conoce como LUP
                lup = np.empty((1,256), np.uint8)
                for i in range(256):
                    lup[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
                # Aplicamos la tabla a la imagen original (a color)
                gamma_img = cv2.LUT(cv_img, lup)

                # procesamos para la parte 1-C: Reducción de Ruido y Detección de Bordes

                # a) generamos ruido en la imagen
                # IMPORTANTE: debemos descomentar la línea del tipo de ruido que queremos usar

                ruido_frame = mas_ruido_gaussiano(cv_img.copy())
                # ruido_frame = mas_ruido_especular(cv_img.copy())

                # b) aplicar filtros de reducción de ruido

                # Filtro de Mediana 
                mediana_filtro = cv2.medianBlur(ruido_frame, 5)

                # Filtro Gaussiano (bueno para ruido Gaussiano)
                gaussian_filtro = cv2.GaussianBlur(ruido_frame, (5, 5), 0)

                # Filtro de Media (simple blur)
                blur_filtro = cv2.blur(ruido_frame, (5, 5))

                # c) aplicar convolución con PyTorch, sharpen

                
                img_tensor = torch.from_numpy(gray.astype(np.float32)).unsqueeze(0).unsqueeze(0)
                convolved_output = F.conv2d(
                    input = img_tensor,
                    weight = kernel_torch, # Usamos nuestro kernel de Sharpen
                    padding = 1, # 'padding=1' mantiene el tamaño de la imagen
                    bias = None
                )
                img_output_torch = convolved_output.cpu().numpy().squeeze()
                img_output_torch = cv2.convertScaleAbs(img_output_torch) # Convertimos a 8-bit

                # d) detección de bordes
                # Es MEJOR aplicar bordes sobre una imagen CON FILTRO, nuestro caso usamos el filtro Gaussiano
                # para reducir el ruido falso
                gray_filtered_edges = cv2.cvtColor(gaussian_filtro, cv2.COLOR_BGR2GRAY)

                # Algoritmo 1: Canny para detección de bordes
                edges_canny = cv2.Canny(gray_filtered_edges, 100, 200)
                
                # Algoritmo 2: Sobel para detección de bordes con gradiente
                sobel_x = cv2.Sobel(gray_filtered_edges, cv2.CV_64F, 1, 0, ksize=5)
                sobel_y = cv2.Sobel(gray_filtered_edges, cv2.CV_64F, 0, 1, ksize=5)
                edges_sobel = cv2.convertScaleAbs(cv2.magnitude(sobel_x, sobel_y))

                # Secccion 4: Preparación de la salida visual
                # Aquí decidimos qué mostrar en la cuadrícula 2x2
                
                # Dibujamos los FPS en la imagen original
                cv2.putText(cv_img, f"FPS: {int(fps)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # convertimos las imágenes grises a BGR de 3 canales para poder apilarlas
                clahe_img_bgr = cv2.cvtColor(clahe_img, cv2.COLOR_GRAY2BGR)
                edges_canny_bgr = cv2.cvtColor(edges_canny, cv2.COLOR_GRAY2BGR)
                
                # Creamos una cuadrícula de 2x2 para mostrar 4 resultados, podemos cambiar cuáles variables mostrar aquí
            
                # Redimensionamos todo a un tamaño estándar para que coincidan
                H, W = 240, 320
                frame_original = cv2.resize(cv_img, (W, H))
                frame_fondo = cv2.resize(frame_recortado, (W, H))
                frame_clahe = cv2.resize(clahe_img_bgr, (W, H))
                frame_bordes = cv2.resize(edges_canny_bgr, (W, H))

                # Apilamos horizontalmente (HStack)
                top_fila = np.hstack((frame_original, frame_fondo))
                bottom_fila = np.hstack((frame_clahe, frame_bordes))

                # Apilamos verticalmente (VStack) para crear la cuadrícula
                total_image = np.vstack((top_fila, bottom_fila))

                # Sección 5: Codificación y envío del frame al navegador
                # Codificamos la imagen final (nuestra cuadrícula) a formato .jpg
                (flag, encodedImage) = cv2.imencode(".jpg", total_image)
                
                # Si la codificación falla, saltamos
                if not flag:
                    continue

                # Enviamos el frame al navegador
                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                      bytearray(encodedImage) + b'\r\n')

            except Exception as e:
                # Si algo falla en el bucle (ej. un frame corrupto), lo imprimimos y continuamos
                print(f"Error en el bucle de procesamiento: {e}")
                continue

# rutas de flask

@app.route("/")
def index():
    
    return render_template("index.html")

@app.route("/video_stream")
def video_stream():
    
    # 'mimetype' es importante para que el navegador sepa que es un video multipart
    return Response(cap_video(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

# nuestro punto de entrada principal
if __name__ == "__main__":
    # 'debug=False' es mejor para producción. Pon 'True' si algo falla.
    # 'host='0.0.0.0'' nos permite que otros dispositivos en la red vean la app
    app.run(debug=True, host='0.0.0.0', port=5000)