import PyInstaller.__main__
import os
import shutil

# Configuración
APP_NAME = "NicoKiwiTracker"
ENTRY_POINT = "run.py"

# Limpiar carpetas previas
for folder in ['build', 'dist']:
    if os.path.exists(folder):
        shutil.rmtree(folder)

# Parámetros de PyInstaller
params = [
    ENTRY_POINT,
    '--name=%s' % APP_NAME,
    '--onefile',                       # Un solo archivo .exe
    '--windowed',                      # Ocultar terminal (opcional, cambiar si se quiere ver consola)
    '--add-data=web;web',             # Incluir carpeta web (templates, static)
    '--hidden-import=django.contrib.sessions.backends.file',
    '--hidden-import=passlib.handlers.pbkdf2',
    '--hidden-import=openpyxl.cell._writer',
    '--clean',
]

print(f"--- Iniciando compilación de {APP_NAME} ---")
PyInstaller.__main__.run(params)

print(f"\n--- Compilación terminada ---")
print(f"El ejecutable está en: dist/{APP_NAME}.exe")
print("Recordá copiar nico_kiwi.db y django_sessions.db junto al .exe para no perder datos.")
