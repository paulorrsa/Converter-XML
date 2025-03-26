import os
import sys

# Verificar a versão do Python em uso
python_version = sys.version
print(f"Python version: {python_version}")

# Importar setuptools
try:
    import setuptools
    print(f"Setuptools version: {setuptools.__version__}")
except ImportError:
    print("Setuptools not installed")

# Importar a aplicação principal
from app import app

def handler(request, response):
    return app(request, response) 