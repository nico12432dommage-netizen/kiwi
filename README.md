# 🍃 Nico-Kiwi Tracker

Nico-Kiwi Tracker es una aplicación moderna de gestión y seguimiento diseñada para ser multiplataforma, permitiendo su uso tanto en computadoras de escritorio como en dispositivos móviles a través de la red local.

## ✨ Características

- **Acceso Multiplataforma**: Accede desde tu PC o desde tu celular (conectados a la misma red WiFi).
- **Interfaz Moderna**: Diseño limpio, responsivo y fácil de usar.
- **Base de Datos Local**: Almacenamiento seguro basado en SQLite.
- **Reportes**: Visualización de datos y generación de reportes (Soporta Excel mediante pandas).

## 🚀 Cómo empezar

### Requisitos previos

- Python 3.10+
- Pip (gestor de paquetes de Python)

### Instalación

1. Clona este repositorio o descarga los archivos.
2. Crea un entorno virtual:
   ```bash
   python -m venv .venv
   ```
3. Activa el entorno virtual:
   - **Windows**: `.venv\Scripts\activate`
   - **Linux/Mac**: `source .venv/bin/activate`
4. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### Ejecución

Para iniciar la aplicación, simplemente ejecuta:

```bash
python run.py
```

La aplicación se abrirá automáticamente en tu navegador predeterminado. También mostrará en la consola la dirección IP para acceder desde otros dispositivos en la red.

## 🛠️ Tecnologías utilizadas

- **Backend**: Django (Python)
- **Procesamiento de Datos**: Pandas / Openpyxl
- **Frontend**: HTML5, CSS3, JavaScript
- **Empaquetado**: PyInstaller (para generar ejecutables .exe)

## 📄 Notas

Este proyecto está configurado para ejecutarse localmente. Asegúrate de que los puertos necesarios (por defecto 8080) estén abiertos en tu firewall si deseas acceder desde otros dispositivos.

## 🌐 Despliegue en Internet (Producción)

El proyecto está preparado para ser desplegado en servicios como **Render** o **PythonAnywhere**.

### Pasos Generales:
1. Sube el código a un repositorio de GitHub.
2. Crea una cuenta en el servicio de hosting elegido.
3. Conecta tu repositorio de GitHub.

### Configuración en Render:
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn --chdir web nicokiwi.wsgi:application`
- **Variables de Entorno**:
  - `SECRET_KEY`: Una clave larga y segura.
  - `DATABASE_URL`: La URL de tu base de datos PostgreSQL (opcional, usa SQLite por defecto).

### Configuración en PythonAnywhere:
- Sigue la guía oficial para proyectos Django.
- Asegúrate de configurar el `WSGI file` para apuntar a `nicokiwi.wsgi`.
