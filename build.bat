@echo off
chcp 65001 >nul
echo ================================================
echo   Nico-Kiwi Tracker - Compilador Profesional
echo ================================================
echo.

if not exist .venv (
    echo [ERROR] No se encontró la carpeta .venv.
    echo Asegúrate de inicializar el entorno virtual antes.
    pause
    exit /b 1
)

echo [1/2] Verificando dependencias...
.venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo [2/2] Compilando ejecutable...
.venv\Scripts\python.exe build_exe_script.py

if errorlevel 1 goto error

echo.
echo ================================================
echo   ✔️ PROCESO COMPLETADO
echo   El ejecutable está en: dist\NicoKiwiTracker.exe
echo ================================================
echo.
pause
exit /b 0

:error
echo.
echo ❌ ERROR: Algo salió mal durante la compilación.
pause
exit /b 1

:error
echo.
echo ERROR: Algo salio mal. Revisa los mensajes de arriba.
pause
exit /b 1
