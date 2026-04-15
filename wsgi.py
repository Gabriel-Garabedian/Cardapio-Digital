"""
Entrypoint para servidor de produção.

Uso:
  Waitress (Windows/Linux):
    waitress-serve --port=$PORT wsgi:app

  Gunicorn (Linux):
    gunicorn --workers 3 --bind 0.0.0.0:$PORT wsgi:app
"""
from damassa.app import app, init_db

# Inicializa o banco de dados se não existir
init_db()
