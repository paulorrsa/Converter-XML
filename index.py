try:
    from app import app
except Exception as e:
    import os
    import sys
    print(f"Erro ao importar app: {e}")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir('.')}")
    
    # Fallback simples para caso de erro
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return "Erro ao inicializar a aplicação principal. Verifique os logs."

# Necessário para o Vercel
app = app 