Paso 2: Ejecuta el servidor (cuando tengas la cámara).

    Abre tu terminal o CMD.

    Navega a la carpeta de tu proyecto.

    Activa tu entorno virtual (¡importante!): .\venv\Scripts\activate

    Ejecuta el script: python app.py

    Verás que el terminal se queda "escuchando" en http://0.0.0.0:5000/ o http://127.0.0.1:5000/.

Paso 3: Míralo en tu navegador.

    Abre Google Chrome o Firefox.

    Escribe en la barra de direcciones: http://127.0.0.1:5000

    ¡Ahí deberías ver tu cuadrícula de video 2x2 en vivo!

--------

#  Guía de Pruebas "Go-Live" (Cuando tengas la cámara)

Este es el plan de acción para probar el proyecto una vez que tengas la cámara ESP32-CAM.

## Fase 1: Preparar el Hardware (La Cámara)

El objetivo es cargar el software a la cámara y obtener su dirección IP.

1.  **Abrir Arduino IDE:** Inicia el IDE que ya configuraste.
2.  **Cargar Ejemplo:** Ve a `File` > `Examples` > `ESP32` > `Camera` > `CameraWebServer`.
3.  **Configurar el Código:**
    * [cite_start]En la pestaña `CameraWebServer`, descomenta el modelo de tu cámara (ej: `#define CAMERA_MODEL_AI_THINKER`)[cite: 303].
    * [cite_start]En la pestaña `arduino_secrets.h` (o dentro del mismo archivo, busca `ssid`), pon el **nombre (SSID) y la contraseña** de tu red WiFi [cite: 305-307].
4.  [cite_start]**Seleccionar Tarjeta:** Ve a `Tools` > `Board` y selecciona tu tarjeta (ej. "AI Thinker ESP32-CAM")[cite: 186].
5.  **Seleccionar Puerto:** Conecta la cámara a tu PC. Ve a `Tools` > `Port` y selecciona el puerto COM que apareció.
6.  **Subir Código:** Presiona el botón "Upload" (flecha derecha).
    * *Nota: Algunas cámaras ESP32-CAM requieren que presiones el botón "RST" (Reset) en la placa justo cuando el IDE dice "Connecting...".*
7.  **¡OBTENER LA IP!:**
    * [cite_start]Una vez subido el código, abre el **Serial Monitor** (`Tools` > `Serial Monitor`)[cite: 321].
    * Presiona el botón "RST" de la cámara otra vez.
    * Verás un montón de texto. Espera a que se conecte al WiFi. Al final, verás un mensaje como:
        `Camera Ready! Use 'http://192.168.1.10' to connect` [cite: 322]
    * **¡Apunta esa dirección IP!**

## Fase 2: Configurar el Software (Tu PC)

1.  **Abrir `app.py`:** Abre tu proyecto en VS Code.
2.  **Actualizar la IP:** Ve a la línea `_URL = 'http://10.0.0.11'` y reemplaza la IP `10.0.0.11` por la IP real que te dio la cámara en el paso anterior.
3.  **Guardar** el archivo.

## Fase 3: Ejecutar y Probar

1.  **Abrir Terminal:** Abre un terminal (CMD o PowerShell) en la carpeta de tu proyecto.
2.  **Activar Entorno Virtual:**
    ```bash
    .\venv\Scripts\activate
    ```
3.  **Ejecutar Servidor:**
    ```bash
    python app.py
    ```
4.  **Abrir Navegador:** Abre Chrome o Firefox.
5.  **Visitar la Página:** Escribe `http://127.0.0.1:5000` en la barra de direcciones.

Si todo salió bien, deberías estar viendo una cuadrícula de 2x2 con tu video procesado en vivo.

1. ¿Cuál será tu salida en el navegador?
Con tu app.py actual y el index.html de tu profesor, esto es lo que verás:

Abrirás http://127.0.0.1:5000 en tu navegador.

Verás la página con el fondo amarillo (#f1f1bc) y el título "Video Streaming".

Debajo del título, verás un solo bloque de video en vivo.

Este bloque de video estará dividido en una cuadrícula de 2x2 gracias a tu código (np.hstack y np.vstack).

La cuadrícula mostrará:

Arriba-Izquierda: El video Original de la cámara, con el contador de FPS [cite: 500-509].

Arriba-Derecha: El video con el Fondo Recortado (solo se verá lo que se mueve).

Abajo-Izquierda: El video con la Mejora de Contraste CLAHE.

Abajo-Derecha: El video con los Bordes detectados por Canny.

Tu index.html funciona perfectamente porque solo tiene una etiqueta <img>, y tu app.py inteligentemente combina las 4 vistas en una sola imagen (total_image) antes de enviarla.