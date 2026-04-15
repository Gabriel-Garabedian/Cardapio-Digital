"""
Entrypoint para servidor de produção.

Uso:
  Waitress (Windows/Linux):
    waitress-serve --port=$PORT wsgi:app

  Gunicorn (Linux):
    gunicorn --workers 3 --bind 0.0.0.0:$PORT wsgi:app
"""
from damassa.app import app

# Tenta inicializar o banco, mas não falha se der erro
try:
    from damassa.app import init_db
    init_db()
except Exception as e:
    print(f"WARNING: init_db falhou: {e}")
    # O banco já existe, então é OK
