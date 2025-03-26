import sys
import subprocess
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lista de pacotes críticos que precisamos garantir que estão instalados
REQUIRED_PACKAGES = [
    "setuptools>=65.5.0",
    "wheel>=0.38.4",
    "pandas==1.5.3",
    "numpy==1.23.5",
    "xlsxwriter==3.1.2"
]

# Verificar se estamos em um ambiente Vercel
def is_vercel_env():
    return 'VERCEL' in os.environ

# Verificar e instalar pacotes necessários
def ensure_packages():
    logger.info("Verificando pacotes necessários...")
    try:
        # Primeiro instalar setuptools e wheel
        subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools>=65.5.0", "wheel>=0.38.4"])
        logger.info("Setuptools e wheel instalados com sucesso")
        
        for package in REQUIRED_PACKAGES:
            try:
                # Verificar se já está instalado
                package_name = package.split('==')[0]
                if package_name not in ["setuptools", "wheel"]:  # Pular os que já instalamos
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