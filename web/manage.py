#!/usr/bin/env python
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent  # c:\ki\
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / 'web'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nicokiwi.settings')
os.environ.setdefault('NICO_KIWI_ROOT', str(ROOT_DIR))


def main():
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Ejecuta: pip install django"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
