# Practica 2 - Parte 2: Operaciones Morfológicas
# Nombres: Felipe Peralta y Samantha Suquilanda

import os
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename # Herramienta para subir archivos de forma segura

# configuración de la aplicación Flask
UPLOAD_FOLDER = 'static/uploads/' # aqui guardaremos las imágenes subidas y procesadas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'bmp'} 

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # proceso cuando el usuario envía una imagen 
    if request.method == 'POST':
        # Revisa si la petición tiene un archivo
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        
        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)
        
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # desarrollo de la Parte 2: Operaciones Morfológicas

        # creamos un kernel de tamaño grande (37x37) para realzar detalles
        # y aplicamos las operaciones morfológicas pedidas
        
        # Llamamos a nuestra función de procesamiento
        output_filenames = process_image(filepath, filename)
        
        # nos ayuda a volver a la página mostrando las imágenes procesadas
        return render_template('medical.html', 
                               original=filename, 
                               tophat=output_filenames['tophat'],
                               blackhat=output_filenames['blackhat'],
                               result=output_filenames['result'])

    # esta parte nos ayuda a mostrar la página inicialmente, solo le da la opcion de subir imagenes
    # un metodo GET
    return render_template('medical.html', 
                           original=None, 
                           tophat=None, 
                           blackhat=None, 
                           result=None)

def process_image(filepath, filename):
    

    # 1. cargar la imagen en escala de grises
    img_original = cv2.imread(filepath)
    gray = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)
    
    # 2. definimos el kernel morfológico grande de 37x37
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (37, 37))
    
    # 3. aqui tenemos 4 opciones de operaciones morfológicas, solo hay que descomentar las que se quieran usar
    # y comentar las que no se quieran usar.:
    # a) Erosión
    # erosion = cv2.erode(gray, kernel, iterations=1)
    
    # b) Dilatación
    # dilatacion = cv2.dilate(gray, kernel, iterations=1)
    
    # c) Top Hat, nos ayuda a Resaltar objetos brillantes en fondos oscuros
    tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
    
    # d) Black Hat, nos ayuda a Resaltar objetos oscuros en fondos brillantes
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)

    # la siguiente es una fórmula clave para mejorar el contraste local
    # e) Imagen Original + (Top Hat - Black Hat)
    
    # Usamos cv2.add y cv2.subtract para evitar desbordes (valores > 255 o < 0)
    result = cv2.add(gray, cv2.subtract(tophat, blackhat))
    
    # 4. guardamos las imágenes procesadas con nombres distintivos en static/uploads/
    output_filenames = {
        'tophat': f"tophat_{filename}",
        'blackhat': f"blackhat_{filename}",
        'result': f"result_{filename}"
    }
    
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], output_filenames['tophat']), tophat)
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], output_filenames['blackhat']), blackhat)
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], output_filenames['result']), result)
    
    return output_filenames

# punto de entrada de la aplicación
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001) # Usamos el puerto 5001 para no chocar con la Parte 1