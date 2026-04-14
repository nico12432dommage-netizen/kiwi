import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent  # c:\ki\
sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nicokiwi.settings')
os.environ.setdefault('NICO_KIWI_ROOT', str(ROOT_DIR))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
