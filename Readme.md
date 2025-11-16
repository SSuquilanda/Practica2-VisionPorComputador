# Práctica 2 - Visión por Computador con ESP32-CAM

**Autores:** Felipe Peralta y Samantha Suquilanda

Este repositorio contiene dos aplicaciones Flask independientes para procesamiento de imágenes en tiempo real y análisis de imágenes médicas utilizando técnicas de Visión por Computador con OpenCV, PyTorch y operaciones morfológicas.

---

##  Descripción General

Este proyecto se divide en **dos partes complementarias**:

### **Parte 1: Video Streaming en Tiempo Real ([app.py](app.py))**
Aplicación Flask que captura video desde una cámara **ESP32-CAM** y aplica múltiples técnicas de procesamiento de imágenes en tiempo real:
-  Sustracción de fondo (Background Subtraction)
-  Mejora de contraste (CLAHE)
-  Detección de bordes (Canny)
-  Filtros de ruido (Gaussiano, Mediana, PyTorch Conv2D)
-  Visualización en cuadrícula 2x2

### **Parte 2: Operaciones Morfológicas Médicas ([Practica_parte2/app_medica.py](Practica_parte2/app_medica.py))**
Aplicación web para procesar imágenes médicas (radiografías, TAC, etc.) utilizando:
-  **Top Hat**: Resaltar estructuras brillantes (huesos, calcificaciones)
-  **Black Hat**: Resaltar estructuras oscuras (tejidos blandos)
-  **Mejora de contraste local**: `Original + (TopHat - BlackHat)`

---

## 📁 Estructura del Proyecto

```
Practica2-VisionPorComputador/
│
├── app.py                          # Parte 1: Aplicación de streaming ESP32-CAM
├── templates/
│   └── index.html                  # Interfaz web Parte 1 (cuadrícula 2x2)
│
├── Practica_parte2/
│   ├── app_medica.py               # Parte 2: Procesamiento de imágenes médicas
│   ├── templates/
│   │   └── medical.html            # Interfaz web Parte 2 (upload + resultados)
│   └── static/
│       └── uploads/                # Carpeta de imágenes subidas/procesadas
│           └── .gitkeep
│
├── static/                         # Recursos estáticos Parte 1
├── pasos_ejecucion_parte1.md       # Guía detallada Parte 1
├── Practica_parte2/pasos_ejecucion_md  # Guía Parte 2
├── Readme.md                       # Este archivo
├── .gitignore                      # Configuración de Git
└── __pycache__/                    # Archivos compilados de Python
```

---

##  Requisitos Previos

### **Hardware (Solo para Parte 1)**
-  **ESP32-CAM** (modelo AI-Thinker o compatible)
-  Programador FTDI o cable USB-Serial
-  Red WiFi de 2.4GHz

### **Software**
-  **Python 3.8+** (recomendado Python 3.9 o superior)
-  **Arduino IDE** (para programar la ESP32-CAM)
-  Navegador web moderno (Chrome, Firefox, Edge)

### **Bibliotecas de Python**
```bash
Flask>=2.3.0
opencv-python>=4.8.0
numpy>=1.24.0
torch>=2.0.0
requests>=2.31.0
werkzeug>=2.3.0
```

---

##  Instalación

### **1. Clonar el Repositorio**
```bash
git clone https://github.com/tu-usuario/Practica2-VisionPorComputador.git
cd Practica2-VisionPorComputador
```

### **2️. Crear Entorno Virtual**
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### **3️. Instalar Dependencias**
```bash
pip install Flask opencv-python numpy torch requests werkzeug
```

### **4️. Crear Carpeta de Uploads (Parte 2)**
```bash
# Ya está creada, pero verifica que exista:
mkdir -p Practica_parte2/static/uploads
```

---

##  Parte 1: Streaming de Video ESP32-CAM

### **Configuración del Hardware**

#### **Paso 1: Programar la ESP32-CAM**

1. Abre **Arduino IDE**
2. Ve a `File` → `Examples` → `ESP32` → `Camera` → `CameraWebServer`
3. Edita el archivo:
   ```cpp
   // Descomentar el modelo de tu cámara
   #define CAMERA_MODEL_AI_THINKER
   
   // Configurar WiFi
   const char* ssid = "TU_RED_WIFI";
   const char* password = "TU_CONTRASEÑA";
   ```
4. Selecciona `Tools` → `Board` → `AI Thinker ESP32-CAM`
5. Conecta la ESP32-CAM y presiona **Upload**
6. Abre el **Serial Monitor** (`Ctrl+Shift+M`) a **115200 baud**
7. Presiona el botón **RST** en la placa
8. **¡IMPORTANTE!** Copia la dirección IP que aparece:
   ```
   Camera Ready! Use 'http://192.168.1.XX' to connect
   ```

#### **Paso 2: Configurar app.py**

Edita [app.py](app.py) línea 16:

````python
# filepath: [app.py](http://_vscodecontentref_/0)
_URL = 'http://192.168.68.106'  #  se debe reemplazar con la IP de tu ESP32-CAM
````

### **Uso de la Aplicación**

1. **Iniciar el Servidor Flask:**
   ```bash
   python app.py
   ```
2. **Acceder a la Interfaz Web:**
   - Abre un navegador y ve a `http://127.0.0.1:5000/`
   - Deberías ver la cuadrícula de video en tiempo real desde la ESP32-CAM.

### **Funcionalidades de Procesamiento de Imágenes**

La aplicación realiza las siguientes operaciones en tiempo real sobre el stream de video:

- **Sustracción de Fondo:** Elimina el fondo estático, resaltando objetos en movimiento.
- **Mejora de Contraste (CLAHE):** Aumenta el contraste adaptativamente en regiones locales.
- **Detección de Bordes (Canny):** Resalta los bordes de los objetos en la imagen.
- **Filtros de Ruido:**
  - **Gaussiano:** Suaviza la imagen reduciendo el ruido.
  - **Mediana:** Filtra el ruido manteniendo los bordes más nítidos.
  - **PyTorch Conv2D:** Aplica un filtro personalizado definido por el usuario.

---

### **Salida Esperada (Cuadrícula 2x2)**
1. Superior Izquierda: Video Original + FPS
2. Superior Derecha Fondo Recortado (MOG2)
3. Inferior Izquierda: Mejora de Contraste CLAHE
4. Inferior Derecha: Detección de Bordes (Canny)


---


## Troubleshooting

### **Problemas Comunes**

- **Error de Conexión a la ESP32-CAM:**
  - Asegúrate de que la ESP32-CAM esté conectada a la misma red WiFi que tu computadora.
  - Verifica que la dirección IP en `app.py` sea la correcta.

- **Problemas de Dependencias en Python:**
  - Asegúrate de haber activado el entorno virtual (si estás usando uno).
  - Revisa que todas las bibliotecas requeridas estén instaladas y actualizadas.

- **Errores en el Navegador:**
  - Prueba a limpiar la caché del navegador o usar un navegador diferente.
  - Asegúrate de que no haya extensiones bloqueando el contenido (como bloqueadores de anuncios).

---

## Parte 2: Procesamiento de Imágenes Médicas

### **Descripción General**

Esta aplicación web permite cargar imágenes médicas (radiografías, angiografías, TAC, etc.) y aplicar operaciones morfológicas avanzadas para mejorar la visualización de estructuras anatómicas.

### **Características Principales**

-  **Upload de Imágenes**: Interfaz web intuitiva para cargar imágenes médicas
- **Top Hat Morphology**: Resalta estructuras brillantes (huesos, calcificaciones, vasos con contraste)
- **Black Hat Morphology**: Resalta estructuras oscuras (tejidos blandos, espacios intersticiales)
- **Mejora de Contraste Local**: Combina ambas operaciones para realzar detalles finos
- **Visualización Comparativa**: Muestra 4 imágenes lado a lado para análisis visual

---

### **Configuración y Ejecución**

#### **Paso 1: Navegar a la Carpeta de la Parte 2**

```bash
cd Practica_parte2
```
---
#### **Paso 2: Verificar Estructura de Carpetas**
```bash
# Windows
if not exist "static\uploads\" mkdir static\uploads
if not exist "templates\" mkdir templates

# Linux/macOS
mkdir -p static/uploads templates
```
---

#### **Paso 3: Activar el Entorno Virtual**

```bash
# Windows
..\venv\Scripts\activate

# Linux/macOS
source ../venv/bin/activate
```
---

#### **Paso 4:  Ejecutar la Aplicación**

```bash
python app_medica.py
```
---

#### **Paso 5:  Acceder a la Interfaz Web**
Abre tu navegador en:

```bash
http://127.0.0.1:5001

```
---

### **Cómo Usar la Aplicación**
1. Obtener Imágenes Médicas de Prueba
Puedes descargar imágenes médicas de fuentes públicas:

Fuentes Recomendadas:

- NIH Chest X-rays
- Radiopaedia
- The Cancer Imaging Archive

#### Ejemplos de búsqueda en Google:

chest x-ray image
angiography medical image
ct scan bones
thorax radiography

#### Formatos soportados:

- .png
- .jpg / .jpeg
- .tif / .tiff
- .bmp

#### Cargar y Procesar una Imagen
1. Haz clic en el botón "Elegir archivo"
2. Selecciona una imagen médica desde tu computadora
3. Presiona "Procesar Imagen"
4. Espera unos segundos (dependiendo del tamaño de la imagen)


---

## 2. Interpretar los resultados
La aplicación mostrará 4 imágenes organizadas en una cuadrícula responsiva:

1.	Imagen Original:	Imagen médica sin procesar.	Referencia inicial para comparación
2.	Top Hat	Resalta píxeles brillantes que están rodeados de píxeles más oscuros.	Útil para detectar: Microcalcificaciones en mamografías, Nódulos pulmonares pequeños, Vasos sanguíneos con contraste
3.	Black Hat:	Resalta píxeles oscuros que están rodeados de píxeles más brillantes.	Útil para detectar:Espacios intersticiales pulmonares, Pequeñas lesiones hipodensas, Vasos sanguíneos sin contraste
4.	Resultado Final (Contraste Mejorado):	Combina la información de Top Hat y Black Hat con la imagen original.	Imagen con contraste local mejorado que facilita la visualización de estructuras anatómicas sutiles

## 3. Parámetros de configuración
#### Tamaño del Kernel Morfológico
El código usa un kernel de 37x37 píxeles (línea 73 de app_medica.py):
```bash
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (37, 37))

```
---

#### ¿Cómo ajustarlo?

- Pequeño (3x3 - 9x9):	Detecta detalles muy finos. Para	Microcalcificaciones, pequeñas lesiones
- Mediano (11x11 - 25x25):	Balance entre detalle y estructura.	Uso general, nódulos pulmonares
- Grande (37x37 - 51x51):	Enfatiza estructuras más amplias como	vasos sanguíneos, contornos anatómicos

---

#### Ejemplo de modificación:
```bash
# filepath: Practica_parte2/app_medica.py
# ...existing code...
# Para detectar detalles más finos, usa un kernel más pequeño:
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))

# Para estructuras más amplias, usa un kernel más grande:
# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (51, 51))
# ...existing code...
```
---

#### Otras Operaciones Morfológicas Disponibles
El código incluye operaciones comentadas que puedes activar (líneas 76-83):
```bash
# filepath: Practica_parte2/app_medica.py
# ...existing code...
# a) Erosión - reduce el tamaño de objetos brillantes
erosion = cv2.erode(gray, kernel, iterations=1)

# b) Dilatación - aumenta el tamaño de objetos brillantes
dilatacion = cv2.dilate(gray, kernel, iterations=1)
# ...existing code...
```
---

### Gestión de Archivos
#### Ubicación de las Imágenes
Todas las imágenes (originales y procesadas) se guardan en:
```bash
Practica_parte2/static/uploads/
```
---
