from pathlib import Path
import os
import sys
import dj_database_url

# Detectar entorno
IS_FROZEN = getattr(sys, 'frozen', False)
IS_PRODUCTION = os.environ.get('RENDER') or os.environ.get('PYTHONANYWHERE_DOMAIN')

if IS_FROZEN:
    # Como .exe, BUNDLE_DIR es donde están los archivos empaquetados (templates, etc)
    # y ROOT_DIR es donde reside el .exe en sí (donde queremos la base de datos).
    ROOT_DIR = Path(os.environ.get('NICO_KIWI_ROOT', os.path.dirname(os.path.abspath(sys.executable))))
    BASE_DIR = Path(os.environ.get('NICO_KIWI_BUNDLE', getattr(sys, '_MEIPASS', str(ROOT_DIR)))) / 'web'
else:
    # Ruta base del proyecto en desarrollo (c:\ki\web)
    BASE_DIR = Path(__file__).resolve().parent.parent
    ROOT_DIR = BASE_DIR.parent

# Asegurar que ambos directorios estén en el path
for p in [str(ROOT_DIR), str(BASE_DIR)]:
    if p not in sys.path: sys.path.insert(0, p)

os.environ.setdefault('NICO_KIWI_ROOT', str(ROOT_DIR))
os.environ.setdefault('NICO_KIWI_BUNDLE', str(BASE_DIR.parent))

# Seguridad
SECRET_KEY = os.environ.get('SECRET_KEY', 'nico-kiwi-tracker-clave-secreta-cambiar-en-produccion-2024')
DEBUG = not IS_PRODUCTION if not IS_FROZEN else True

ALLOWED_HOSTS = ['*'] # En producción real, esto debería ser más restrictivo

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'tracker',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Servir estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'nicokiwi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'nicokiwi.wsgi.application'

# Base de Datos
# Prioridad: 1. DATABASE_URL (Producción) 2. SQLite local
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ROOT_DIR / 'django_sessions.db',
        }
    }

SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_FILE_PATH = os.path.join(ROOT_DIR, 'sessions')
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = False

STATIC_URL = '/static/'
STATIC_ROOT = ROOT_DIR / 'staticfiles'

# Configuración Whitenoise para compresión y caché de estáticos
if not DEBUG or IS_PRODUCTION:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
