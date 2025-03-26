import sys
import subprocess
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lista de pacotes críticos que precisamos garantir que estão instalados
REQUIRED_PACKAGES = [
    "setuptools>=59.0.0",
    "wheel>=0.37.0",
    "distlib>=0.3.4",
    "pandas==1.3.5",
    "numpy==1.21.6",
    "xlsxwriter==3.0.3"
]

# Verificar se estamos em um ambiente Vercel
def is_vercel_env():
    return 'VERCEL' in os.environ

# Verificar e instalar pacotes necessários
def ensure_packages():
    logger.info("Verificando pacotes necessários...")
    try:
        # Primeiro instalar setuptools, wheel e distlib
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools>=59.0.0", "wheel>=0.37.0", "distlib>=0.3.4"])
        logger.info("Setuptools, wheel e distlib instalados com sucesso")
        
        for package in REQUIRED_PACKAGES:
            try:
                # Verificar se já está instalado
                package_name = package.split('==')[0].split('>=')[0]
                if package_name not in ["setuptools", "wheel", "distlib"]:  # Pular os que já instalamos
                    try:
                        __import__(package_name.lower())
                        logger.info(f"Pacote {package_name} já está instalado")
                    except ImportError:
                        logger.info(f"Instalando {package}...")
                        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                        logger.info(f"Pacote {package} instalado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao instalar {package}: {str(e)}")
                # Continuar para o próximo pacote
    except Exception as e:
        logger.error(f"Erro ao instalar pacotes básicos: {str(e)}")
        # Continuar mesmo se houver erro, pois temos fallbacks

# Em ambiente Vercel, garantir que os pacotes estejam instalados
if is_vercel_env():
    ensure_packages()

try:
    # Agora importar a aplicação
    from app import app
except Exception as e:
    logger.error(f"Erro ao importar app: {str(e)}")
    # Criar uma aplicação mínima para evitar falha total
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error_page():
        return "Erro na inicialização da aplicação. Verifique os logs."

if __name__ == '__main__':
    app.run() 