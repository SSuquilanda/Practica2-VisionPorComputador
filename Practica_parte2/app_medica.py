# Practica 2 - Parte 2: Operaciones Morfológicas
# Nombres: Felipe Peralta y Samantha Suquilanda

import os
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename # Herramienta para subir archivos de forma segura

# --- Configuración de Flask ---
UPLOAD_FOLDER = 'static/uploads/' # Carpeta para guardar las imágenes subidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'bmp'} # Extensiones permitidas

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """ Revisa si la extensión del archivo es válida """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # --- Lógica para cuando el usuario SUBE una imagen ---
    if request.method == 'POST':
        # Revisa si la petición tiene un archivo
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        # Si el usuario no selecciona archivo, el navegador envía un 'file' vacío
        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)
        
        # Si todo está bien, guardamos el archivo
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # --- (AQUÍ OCURRE LA MAGIA DE LA PARTE 2) ---
        # Procesamos la imagen que acabamos de guardar
        # La guía pide 3 tamaños de kernel, pero para mostrarlo,
        # usaremos el de 37x37 que sugiere
        
        # Llamamos a nuestra función de procesamiento
        output_filenames = process_image(filepath, filename)
        
        # Regresamos a la página, pero ahora con los nombres de las imágenes procesadas
        return render_template('medical.html', 
                               original=filename, 
                               tophat=output_filenames['tophat'],
                               blackhat=output_filenames['blackhat'],
                               result=output_filenames['result'])

    # --- Lógica para cuando el usuario SOLO VISITA la página ---
    # (Método GET)
    return render_template('medical.html', 
                           original=None, 
                           tophat=None, 
                           blackhat=None, 
                           result=None)

def process_image(filepath, filename):
    """
    Aplica las operaciones morfológicas pedidas en la Parte 2
    """
    # 1. Cargar la imagen en escala de grises
    img_original = cv2.imread(filepath)
    gray = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)
    
    # 2. Definir el kernel (elemento estructurante)
    # La guía sugiere un tamaño grande como 37x37 para realzar detalles
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (37, 37))
    
    # 3. Aplicar las operaciones (a, b, c, d)
    # (Puedes guardar y mostrar erosión y dilatación si quieres)
    # erosion = cv2.erode(gray, kernel, iterations=1)
    # dilatacion = cv2.dilate(gray, kernel, iterations=1)
    
    # c) Top Hat (Resalta objetos brillantes en fondos oscuros)
    tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
    
    # d) Black Hat (Resalta objetos oscuros en fondos brillantes)
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    
    # e) Imagen Original + (Top Hat - Black Hat)
    # Esta es la fórmula clave para mejorar el contraste local
    # Usamos cv2.add y cv2.subtract para evitar desbordes (valores > 255 o < 0)
    result = cv2.add(gray, cv2.subtract(tophat, blackhat))
    
    # 4. Guardar las imágenes de resultado en la carpeta 'static'
    output_filenames = {
        'tophat': f"tophat_{filename}",
        'blackhat': f"blackhat_{filename}",
        'result': f"result_{filename}"
    }
    
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], output_filenames['tophat']), tophat)
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], output_filenames['blackhat']), blackhat)
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], output_filenames['result']), result)
    
    return output_filenames

# --- Punto de entrada principal ---
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001) # Usamos el puerto 5001 para no chocar con la Parte 1