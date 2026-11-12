"""Entrada de producao para Vercel e servidores WSGI."""
from damassa.app import app, init_db

init_db()
