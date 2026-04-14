#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# El comando collectstatic necesita BASE_DIR y ROOT_DIR configurados.
# Por defecto settings.py usa las rutas relativas si no hay variables de entorno.
python web/manage.py collectstatic --no-input

# Correr migraciones para la base de datos (SQLite o PostgreSQL)
python web/manage.py migrate
