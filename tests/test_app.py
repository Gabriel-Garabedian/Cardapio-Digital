import importlib
import io
import os
import sqlite3
import tempfile
import unittest
from contextlib import contextmanager
from unittest.mock import patch

os.environ.setdefault('SECRET_KEY', 'test-secret-not-for-production')
os.environ.setdefault('CHEF_PASSWORD', 'test-chef-password')
web = importlib.import_module('damassa.app')


class AppTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

        @contextmanager
        def connect():
            db = sqlite3.connect(os.path.join(self.directory.name, 'test.db'))
            db.row_factory = sqlite3.Row
            db.execute('PRAGMA foreign_keys=ON')
            try:
                yield db
            finally:
                db.close()

        self.db_patch = patch.object(web, 'get_db', connect)
        self.db_patch.start()
        self.addCleanup(self.db_patch.stop)
        web.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        web.init_db()
        self.client = web.app.test_client()

    def customer(self):
        self.client.post('/register', data={'username': 'cliente', 'email': 'cliente@example.test', 'password': 'password123'})
        self.client.post('/login', data={'email': 'cliente@example.test', 'password': 'password123'})

    def chef(self):
        self.client.post('/login', data={'email': 'chef@damassa.com', 'password': os.environ['CHEF_PASSWORD']})

    def order(self, cart=None):
        return self.client.post('/order/place', json={'cart': cart if cart is not None else [{'id': 1, 'qty': 2}], 'address': 'Rua Teste', 'number': '10', 'city': 'Recife'})

    def test_public_menu_and_seed_are_idempotent(self):
        web.init_db()
        self.assertEqual(self.client.get('/menu').status_code, 200)
        data = self.client.get('/api/menu').get_json()
        self.assertEqual(len(data['items']), 14)
        self.assertEqual(len(data['categories']), 4)
        self.assertTrue(all(i['id'] is not None for i in data['items']))

    def test_duplicate_registration_and_profile_do_not_crash(self):
        self.customer()
        response = self.client.post('/register', data={'username': 'cliente', 'email': 'cliente@example.test', 'password': 'password123'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('cadastrado', response.text)
        response = self.client.post('/profile', data={'username': 'chef_josue'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('existe', response.text)

    def test_checkout_uses_server_price_and_renders_history(self):
        self.customer()
        response = self.order([{'id': 1, 'qty': 2, 'price': 0.01}])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['total'], 90)
        self.assertIn('wa.me/', response.json['wa_url'])
        self.assertEqual(self.client.get('/orders').status_code, 200)
        self.assertEqual(self.client.get('/chef').status_code, 302)

    def test_bad_cart_is_rejected_without_partial_order(self):
        self.customer()
        for cart in ([{'id': 1, 'qty': 'oops'}], [{'id': 99999, 'qty': 1}, {'id': 1, 'qty': 1}], [{'id': 1, 'qty': -1}], [{'id': 1, 'qty': 1.5}], ['invalid'], 'invalid'):
            with self.subTest(cart=cart):
                self.assertEqual(self.order(cart).status_code, 400)
        with web.get_db() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) c FROM orders').fetchone()['c'], 0)

    def test_expired_session_checkout_returns_json(self):
        response = self.order()
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json['ok'])

    def test_settings_persist_and_chef_can_change_password(self):
        self.chef()
        self.assertEqual(self.client.get('/profile').status_code, 200)
        self.client.post('/chef/whatsapp', data={'whatsapp': '5511999999999'})
        with web.get_db() as db:
            self.assertEqual(db.execute("SELECT value FROM settings WHERE key='chef_whatsapp'").fetchone()['value'], '5511999999999')
        self.assertEqual(web.get_chef_whatsapp(), '5511999999999')
        self.assertIn('https://wa.me/5511999999999', self.client.get('/menu').text)

    def test_upload_is_persistent_and_validated(self):
        from PIL import Image
        self.chef()
        photo = io.BytesIO()
        Image.new('RGB', (2, 2), 'red').save(photo, format='PNG')
        photo.seek(0)
        self.client.post('/chef/item/add', data={'category': 'lasanha', 'name': "Chef's <prato>", 'price': '12.50', 'image': (photo, 'foto.png')})
        with web.get_db() as db:
            row = db.execute('SELECT image FROM items ORDER BY id DESC').fetchone()
        response = self.client.get('/uploads/' + row['image'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'image/png')
        self.assertEqual(self.client.get('/chef').status_code, 200)
        self.client.post('/chef/item/add', data={'category': 'lasanha', 'name': 'Invalido', 'price': '10', 'image': (io.BytesIO(b'<script>bad</script>'), 'fake.png')})
        with web.get_db() as db:
            self.assertIsNone(db.execute("SELECT id FROM items WHERE name='Invalido'").fetchone())
        self.client.post('/chef/item/add', data={'category': 'missing', 'name': 'Categoria invalida', 'price': '10', 'image': (io.BytesIO(response.data), 'foto.png')})
        with web.get_db() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) c FROM uploads').fetchone()['c'], 1)

    def test_category_with_sauces_can_be_removed_when_empty(self):
        self.chef()
        with web.get_db() as db:
            db.execute('DELETE FROM items WHERE category_id=2')
            db.commit()
        response = self.client.post('/chef/category/delete/2', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with web.get_db() as db:
            self.assertIsNone(db.execute('SELECT id FROM categories WHERE id=2').fetchone())

    def test_invalid_price_and_status_are_rejected(self):
        self.chef()
        for value in ['-1', 'NaN', 'Infinity']:
            self.client.post('/chef/item/add', data={'category': 'lasanha', 'name': 'Invalid price', 'price': value})
        with web.get_db() as db:
            self.assertIsNone(db.execute("SELECT id FROM items WHERE name='Invalid price'").fetchone())

    def test_csrf_protects_mutations(self):
        web.app.config['WTF_CSRF_ENABLED'] = True
        self.assertEqual(self.client.post('/register', data={}).status_code, 400)

    def test_chef_controls_final_sauce_price(self):
        self.customer()
        with web.get_db() as db:
            sauce = db.execute("SELECT * FROM sauces WHERE price_type='premium' ORDER BY id").fetchone()
        cart = [{'id': 5, 'qty': 2, 'sauce': sauce['name']}]
        self.assertEqual(self.order(cart).status_code, 400)
        self.client.get('/logout')
        self.chef()
        response = self.client.post(f"/chef/sauce/{sauce['id']}/price", data={'price': '47.50'})
        self.assertEqual(response.status_code, 302)
        self.client.get('/logout')
        self.client.post('/login', data={'email': 'cliente@example.test', 'password': 'password123'})
        response = self.order(cart)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['total'], 95)

    def test_rate_limit_expires_and_is_shared_between_login_routes(self):
        for _ in range(5):
            self.client.post('/login', data={'email': 'wrong@example.test', 'password': 'wrong'})
        response = self.client.post('/api/checkout-login', json={'email': 'wrong@example.test', 'password': 'wrong'})
        self.assertEqual(response.status_code, 429)
        with patch.object(web.time, 'time', return_value=web.time.time() + 61):
            response = self.client.post('/api/checkout-login', json={'email': 'wrong@example.test', 'password': 'wrong'})
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
