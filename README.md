# obbrepo
pagina de obb
Train Stations Map - Austria

🚆 Train Stations Map es una aplicación interactiva en Streamlit que permite visualizar la satisfacción de los pasajeros en estaciones de tren de Viena, Austria. Además, los usuarios pueden enviar opiniones, dar feedback rápido con emojis y usar un pizarrón interactivo para tomar notas o dibujar.

Características principales:

* Visualización de estaciones de tren en un mapa interactivo con emojis que reflejan la satisfacción promedio.
* Encuesta para que los usuarios compartan su experiencia en cada estación.
* Nube de palabras generada a partir de los comentarios de los usuarios.
* Feedback rápido con emojis y selección de palabras asociadas a emociones.
* Pizarrón interactivo para dibujar o tomar notas.
* Datos de usuarios almacenados localmente en un archivo CSV (opiniones_austria.csv).

Dependencias:

* Python >= 3.9
* Streamlit
* Streamlit Drawable Canvas
* pandas
* pydeck
* pathlib
* datetime
* re
* collections
* math
* random

Instalación:

1. Clonar el repositorio:
   git clone [https://github.com/tu-usuario/train-stations-map.git](https://github.com/tu-usuario/train-stations-map.git)
   cd train-stations-map

2. Crear un entorno virtual (opcional pero recomendado):
   python -m venv venv

3. Activar el entorno:

   * Windows: venv\Scripts\activate
   * Mac/Linux: source venv/bin/activate

4. Instalar las dependencias:
   pip install -r requirements.txt

   Si no tienes requirements.txt, puedes instalar manualmente:
   pip install streamlit streamlit-drawable-canvas pandas pydeck

Ejecutar la aplicación localmente:
python -m streamlit run 1.py --server.address 0.0.0.0 --server.port 8501

* Abrir en tu navegador de PC: [http://localhost:8501](http://localhost:8501)
* Abrir en tu móvil (misma red Wi-Fi): http://TU_IP_LOCAL:8501
  (Para obtener tu IP local en Windows, usa: ipconfig)

Despliegue en línea (opcional):
Streamlit Community Cloud:

1. Crear un repositorio en GitHub con tu app (1.py) y el CSV vacío opiniones_austria.csv.
2. Crear un archivo requirements.txt con todas las librerías necesarias.
3. Acceder a [https://share.streamlit.io/](https://share.streamlit.io/) y conectar tu repositorio.
4. La app se publicará con una URL global.

Estructura de archivos:
train-stations-map/
├── 1.py                   # Script principal de Streamlit
├── opiniones_austria.csv   # Archivo CSV donde se guardan las opiniones
├── requirements.txt       # Dependencias (opcional)
└── README.txt             # Este archivo

Notas:

* La app guarda los datos de los usuarios en opiniones_austria.csv.
* El pizarrón interactivo no almacena los dibujos de forma persistente (puedes agregar persistencia si lo deseas).
* Asegúrate de que tu firewall permita conexiones si quieres acceder desde otros dispositivos en la misma red.

