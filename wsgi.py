try:
    from vercel_entry import app
except ImportError:
    # Fallback para importação direta se vercel_entry não estiver disponível
    from app import app

if __name__ == "__main__":
    app.run() 