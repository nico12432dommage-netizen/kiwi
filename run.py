#!/usr/bin/env python3
"""
Nico-Kiwi Tracker — Lanzador
Inicia el servidor web y abre el navegador automaticamente.
"""
import os
import sys
import threading
import webbrowser
import time
import socket
import logging

# Configurar salida para modo ventana (sin consola)
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    # En caso de error crítico sin consola, intentamos guardar un log
    try:
        sys.stderr = open(os.path.join(os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)), "error_log.txt"), "a")
    except Exception:
        sys.stderr = open(os.devnull, 'w')

# Detectar si estamos corriendo dentro de un ejecutable de PyInstaller
IS_FROZEN = getattr(sys, 'frozen', False)
if IS_FROZEN:
    # Si es un EXE, las bases de datos están junto al .exe (sys.executable)
    # Pero el código y estáticos están en la carpeta temporal (sys._MEIPASS)
    ROOT_DIR = os.path.dirname(os.path.abspath(sys.executable))
    BUNDLE_DIR = getattr(sys, '_MEIPASS', ROOT_DIR)
else:
    # Si estamos en desarrollo, todo está en la misma carpeta del script
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = ROOT_DIR

os.chdir(ROOT_DIR)

# Añadir al path para encontrar database.py y el proyecto Django
sys.path.insert(0, ROOT_DIR) if ROOT_DIR not in sys.path else None
sys.path.insert(0, os.path.join(BUNDLE_DIR, 'web'))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nicokiwi.settings')
os.environ['NICO_KIWI_ROOT'] = ROOT_DIR
os.environ['NICO_KIWI_BUNDLE'] = BUNDLE_DIR

PORT = 8080


def get_local_ip():
    """Obtiene la IP local de la PC en la red WiFi."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def abrir_navegador():
    """Espera que el servidor este listo y abre el navegador."""
    time.sleep(2)
    url = f"http://localhost:{PORT}"
    linea = "=" * 52
    print(f"\n{linea}")
    print(f"  🍃  Nico-Kiwi Tracker esta corriendo!")
    print(linea)
    print(f"  💻  En esta PC    : http://localhost:{PORT}")
    print(f"  📱  En el celular : http://{get_local_ip()}:{PORT}")
    print(f"  (El celular debe estar en la misma red WiFi)")
    print(f"{linea}\n")
    webbrowser.open(url)


if __name__ == '__main__':
    try:
        # Inicializar Django
        import django
        django.setup()

        # Iniciar migraciones si hace falta
        from django.core.management import call_command
        call_command('migrate', '--run-syncdb', verbosity=0)

        # Abrir navegador en hilo separado
        t = threading.Thread(target=abrir_navegador)
        t.daemon = True
        t.start()

        # Iniciar servidor Django
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{PORT}', '--noreload'])
    except Exception as e:
        # Si algo falla, lo escribimos en el log antes de cerrar
        with open("error_fatal.txt", "a") as f:
            import traceback
            f.write(f"\n[{time.ctime()}] Error fatal:\n")
            f.write(traceback.format_exc())
        sys.exit(1)
