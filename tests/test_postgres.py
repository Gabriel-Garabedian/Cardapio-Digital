"""Mesmos fluxos em schema PostgreSQL descartável, sem tocar nos dados do site."""
import os
import unittest
import uuid
from contextlib import contextmanager
from unittest.mock import patch

import test_app
web = test_app.web


@unittest.skipUnless(os.environ.get('RUN_POSTGRES_TESTS') == '1', 'PostgreSQL real opcional')
class PostgresTests(test_app.AppTests):
    def setUp(self):
        import psycopg2
        from psycopg2 import sql
        from dotenv import dotenv_values
        url = dotenv_values('.env.local')['DATABASE_URL_UNPOOLED']
        schema = 'test_' + uuid.uuid4().hex
        with psycopg2.connect(url) as admin:
            with admin.cursor() as cur:
                cur.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(schema)))

        def cleanup():
            with psycopg2.connect(url) as admin:
                with admin.cursor() as cur:
                    cur.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(schema)))

        self.addCleanup(cleanup)

        @contextmanager
        def connect():
            conn = psycopg2.connect(url)
            with conn.cursor() as cur:
                cur.execute(sql.SQL('SET search_path TO {}').format(sql.Identifier(schema)))
            with web._PgCursor(conn) as db:
                yield db

        for name, value in [('USE_PG', True), ('INTEGRITY_ERRORS', (psycopg2.IntegrityError,)), ('get_db', connect)]:
            patcher = patch.object(web, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        web.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        web.init_db()
        self.client = web.app.test_client()
