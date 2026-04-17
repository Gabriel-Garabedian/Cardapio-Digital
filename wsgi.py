"""
Entrypoint para servidor de produção.

Uso:
  Waitress (Windows/Linux):
    waitress-serve --port=$PORT wsgi:app

  Gunicorn (Linux):
    gunicorn --workers 3 --bind 0.0.0.0:$PORT wsgi:app
"""
import traceback
from damassa.app import app, init_db

# Inicializa o banco de dados (cria tabelas se não existirem)
# Ignora erros - se banco não existe, app não vai funcionar
try:
    init_db()
except Exception:
    traceback.print_exc()
    print("ATENÇÃO: init_db falhou. Se o app não funcionar, o banco pode não estar configurado.")
