from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify, flash, send_from_directory, send_file)
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.security import generate_password_hash, check_password_hash
import os, functools, uuid, urllib.parse, unicodedata, re, secrets, time, sqlite3, math, io
from contextlib import contextmanager
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv

# ─────────────────────────────────────────
#  CONFIGURAÇÕES
#  ─────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

USE_PG = bool(os.environ.get("DATABASE_URL"))
if os.environ.get('VERCEL') and not USE_PG:
    raise RuntimeError('DATABASE_URL obrigatória na Vercel para preservar os dados')
if USE_PG:
    import psycopg2
    INTEGRITY_ERRORS = (sqlite3.IntegrityError, psycopg2.IntegrityError)
else:
    INTEGRITY_ERRORS = (sqlite3.IntegrityError,)

def _get_upload_folder():
    return os.environ.get("UPLOAD_FOLDER", os.path.join(os.path.dirname(__file__), "static", "uploads"))

app = Flask(__name__, static_folder='../public/static', static_url_path='/static')

# ─── Segurança de sessão ───
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    if os.environ.get('VERCEL') or os.environ.get('PROD'):
        raise RuntimeError('SECRET_KEY obrigatória em produção')
    import warnings
    warnings.warn(
        "SECRET_KEY não configurada! Gerando uma chave temporária. "
        "Em produção, defina a variável SECRET_KEY ou crie um arquivo .env. "
        "Ex: SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')"
    )
    app.secret_key = secrets.token_hex(32)
app.config.update({
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Lax',
    'PERMANENT_SESSION_LIFETIME': 3600 * 12,
    'MAX_CONTENT_LENGTH': 4 * 1024 * 1024,
})
if os.environ.get("PROD") or os.environ.get("DYNO") or os.environ.get('VERCEL'):
    app.config['SESSION_COOKIE_SECURE'] = True
CSRFProtect(app)

@app.errorhandler(CSRFError)
def csrf_error(error):
    if request.is_json:
        return jsonify(ok=False, msg='Sessão expirada. Atualize a página.'), 400
    return 'Sessão expirada. Atualize a página e tente novamente.', 400

@app.template_filter('order_date')
def order_date(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime('%d/%m/%Y %H:%M') if value else 'N/A'

UPLOAD_FOLDER = _get_upload_folder()
ALLOWED_EXT   = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# ─── WhatsApp do chef ───
CHEF_WHATSAPP_DEFAULT = os.environ.get("CHEF_WHATSAPP", "5581989073030")

def get_chef_whatsapp():
    with get_db() as db:
        row = db.execute("SELECT value FROM settings WHERE key='chef_whatsapp'").fetchone()
    return row['value'] if row else CHEF_WHATSAPP_DEFAULT

def set_chef_whatsapp(value):
    with get_db() as db:
        db.execute("INSERT INTO settings (key,value) VALUES ('chef_whatsapp',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (value,))
        db.commit()

# ─────────────────────────────────────────
#  RATE LIMITING PERSISTENTE
# ─────────────────────────────────────────
def _check_rate_limit(key: str, max_requests: int, window_seconds: int) -> bool:
    now = time.time()
    with get_db() as db:
        row = db.execute('''INSERT INTO rate_limits (rate_key, request_count, expires_at)
            VALUES (?, 1, ?) ON CONFLICT(rate_key) DO UPDATE SET
            request_count=CASE WHEN rate_limits.expires_at<=? THEN 1 ELSE rate_limits.request_count+1 END,
            expires_at=CASE WHEN rate_limits.expires_at<=? THEN excluded.expires_at ELSE rate_limits.expires_at END
            RETURNING request_count''', (key, now + window_seconds, now, now)).fetchone()
        db.execute('DELETE FROM rate_limits WHERE expires_at<?', (now - 3600,))
        db.commit()
    return row['request_count'] <= max_requests

# ─────────────────────────────────────────
#  CAMADA DE BANCO (SQLite ou PostgreSQL)
# ─────────────────────────────────────────

class _PgCursor:
    """Wrapper que imita sqlite3.Connection para queries com PostgreSQL"""
    def __init__(self, conn):
        from psycopg2.extras import RealDictCursor
        self._conn = conn
        self._cur = conn.cursor(cursor_factory=RealDictCursor)
        self.lastrowid = None

    def execute(self, sql, params=None):
        sql = sql.replace('?', '%s')
        self._cur.execute(sql, params or ())
        # Captura lastrowid para INSERT com RETURNING
        if sql.strip().upper().startswith('INSERT') and 'RETURNING ID' in sql.upper():
            row = self._cur.fetchone()
            if row:
                self.lastrowid = row['id']
        return self

    def fetchone(self):
        r = self._cur.fetchone()
        return dict(r) if r else None

    def fetchall(self):
        return [dict(r) for r in self._cur.fetchall()]

    def commit(self):
        self._conn.commit()

    def close(self):
        self._cur.close()
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


@contextmanager
def get_db():
    if USE_PG:
        with _PgCursor(psycopg2.connect(os.environ["DATABASE_URL"], connect_timeout=10)) as db:
            yield db
    else:
        DB_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(__file__), "damassa.db"))
        conn = sqlite3.connect(DB_PATH, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute('PRAGMA foreign_keys=ON')
        try:
            with conn:
                yield conn
        finally:
            conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def save_image(db, field='image'):
    f = request.files.get(field)
    if f and f.filename:
        if not allowed_file(f.filename):
            raise ValueError('Formato de imagem inválido')
        content = f.read()
        with Image.open(io.BytesIO(content)) as image:
            image.verify()
            mime = Image.MIME.get(image.format)
        if mime not in {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}:
            raise ValueError('Formato de imagem inválido')
        ext  = f.filename.rsplit('.', 1)[1].lower()
        name = f"{uuid.uuid4().hex}.{ext}"
        db.execute('INSERT INTO uploads (filename,content,mime) VALUES (?,?,?)', (name, content, mime))
        return name
    return None

def delete_image(db, filename):
    if filename:
        db.execute('DELETE FROM uploads WHERE filename=?', (filename,))

def slugify(text):
    text = unicodedata.normalize('NFKD', text.lower()).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip()
    return re.sub(r'[-\s]+', '-', text) or 'cat'

# ─────────────────────────────────────────
#  INIT DB
# ─────────────────────────────────────────
def _create_tables():
    """Cria todas as tabelas do banco. Usa conexão própria."""
    with get_db() as db:
        db.execute('CREATE TABLE IF NOT EXISTS rate_limits (rate_key TEXT PRIMARY KEY, request_count INTEGER NOT NULL, expires_at DOUBLE PRECISION NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        binary_type = 'BYTEA' if USE_PG else 'BLOB'
        db.execute(f'CREATE TABLE IF NOT EXISTS uploads (filename TEXT PRIMARY KEY, content {binary_type} NOT NULL, mime TEXT NOT NULL)')
        # users
        db.execute(f"""CREATE TABLE IF NOT EXISTS users (
            id {'SERIAL' if USE_PG else 'INTEGER'} PRIMARY KEY, username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'cliente', full_name TEXT DEFAULT '',
            phone TEXT DEFAULT '', address TEXT DEFAULT '', number TEXT DEFAULT '',
            city TEXT DEFAULT '', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        db.execute(f"""CREATE TABLE IF NOT EXISTS categories (
            id {'SERIAL' if USE_PG else 'INTEGER'} PRIMARY KEY, slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL, size TEXT DEFAULT '500g', sort INTEGER DEFAULT 0)""")
        db.execute(f"""CREATE TABLE IF NOT EXISTS items (
            id {'SERIAL' if USE_PG else 'INTEGER'} PRIMARY KEY, category_id INTEGER NOT NULL,
            name TEXT NOT NULL, description TEXT DEFAULT '',
            price REAL NOT NULL, active INTEGER DEFAULT 1,
            sort INTEGER DEFAULT 0, image TEXT DEFAULT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id))""")
        db.execute(f"""CREATE TABLE IF NOT EXISTS sauces (
            id {'SERIAL' if USE_PG else 'INTEGER'} PRIMARY KEY, category_id INTEGER NOT NULL,
            name TEXT NOT NULL, price_type TEXT DEFAULT 'simples', final_price REAL DEFAULT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id))""")
        if USE_PG:
            db.execute('ALTER TABLE sauces ADD COLUMN IF NOT EXISTS final_price REAL DEFAULT NULL')
        elif 'final_price' not in {row['name'] for row in db.execute('PRAGMA table_info(sauces)').fetchall()}:
            db.execute('ALTER TABLE sauces ADD COLUMN final_price REAL DEFAULT NULL')
        db.execute(f"""CREATE TABLE IF NOT EXISTS orders (
            id {'SERIAL' if USE_PG else 'INTEGER'} PRIMARY KEY, user_id INTEGER NOT NULL, total REAL NOT NULL,
            address TEXT DEFAULT '', number TEXT DEFAULT '', city TEXT DEFAULT '',
            note TEXT DEFAULT '', status TEXT DEFAULT 'novo',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id))""")
        db.execute(f"""CREATE TABLE IF NOT EXISTS order_items (
            id {'SERIAL' if USE_PG else 'INTEGER'} PRIMARY KEY, order_id INTEGER NOT NULL, item_id INTEGER NOT NULL,
            item_name TEXT NOT NULL, quantity INTEGER NOT NULL DEFAULT 1,
            unit_price REAL NOT NULL, sauce TEXT DEFAULT '',
            FOREIGN KEY (order_id) REFERENCES orders(id))""")
        db.commit()

def _seed_data():
    """Insere dados iniciais (chef, categorias, pratos). Usa conexão PRÓPRIA."""
    with get_db() as db:
        # Seed chef
        if os.environ.get('CHEF_PASSWORD') and not db.execute("SELECT id FROM users WHERE email='chef@damassa.com'").fetchone():
            db.execute("INSERT INTO users (username,email,password,role,full_name) VALUES (?,?,?,'chef','Josue Matheus')",
                       ('chef_josue','chef@damassa.com', generate_password_hash(os.environ['CHEF_PASSWORD'])))
            db.commit()

        # Seed categories
        for slug, name, size, sort in [
            ('lasanha','Lasanhas','500g',1),
            ('gnocchi','Gnocchi (Nhoque)','500g',2),
            ('fettuccine','Fettuccine','500g',3),
            ('ravioli','Ravioli','500g',4)]:
            if not db.execute("SELECT id FROM categories WHERE slug=?",(slug,)).fetchone():
                db.execute("INSERT INTO categories (slug,name,size,sort) VALUES (?,?,?,?)",(slug,name,size,sort))
        db.commit()

        def cid(slug):
            r = db.execute("SELECT id FROM categories WHERE slug=?",(slug,)).fetchone()
            return r['id'] if r else None

        # Seed items only if none exist
        if db.execute("SELECT COUNT(*) as c FROM items").fetchone()['c'] == 0:
            items = [
                ('lasanha','Alla Bolognesi (Bolonhesa)','Massa artesanal, ragù de carne moída, molho bechamel, queijo muçarela e finalizada com queijo parmesão.',45),
                ('lasanha','Frango','Massa artesanal, frango desfiado, molho bechamel, queijo muçarela e finalizada com queijo parmesão.',45),
                ('lasanha','Presunto e Queijo','Massa artesanal, presunto, queijo muçarela e finalizada com molho bechamel e queijo parmesão.',45),
                ('lasanha','Ragù de Ossobuco (Chambaril)','Massa artesanal, ragù de ossobuco desfiado, queijo muçarela, molho bechamel e finalizada com queijo parmesão.',55),
                ('gnocchi','Batata Inglesa','Nhoque artesanal feito com batata inglesa. Escolha seu molho favorito.',40),
                ('gnocchi','Batata Doce','Nhoque artesanal feito com batata doce. Escolha seu molho favorito.',40),
                ('gnocchi','Banana da Terra','Nhoque artesanal feito com banana da terra. Escolha seu molho favorito.',40),
                ('fettuccine','Fettuccine Artesanal','Massa fresca no formato fettuccine. Escolha seu molho favorito abaixo.',40),
                ('ravioli','Frango com Catupiry','Ravioli recheado com frango temperado e cream cheese catupiry.',45),
                ('ravioli','Três Queijos','Ravioli com blend de queijos selecionados, cremoso e irresistível.',45),
                ('ravioli','Ricota com Espinafre','Ravioli recheado com ricota fresca e espinafre salteado.',45),
                ('ravioli','Ricota com Limão Siciliano','Ravioli de ricota com toque cítrico do limão siciliano.',45),
                ('ravioli','Ragù de Ossobuco','Ravioli com ragù de ossobuco desfiado, intenso e aromático.',45),
                ('ravioli','Camarão com Cream Cheese','Ravioli recheado com camarão e cream cheese, leve e sofisticado.',55),
            ]
            for i, (s, n, d, p) in enumerate(items):
                c = cid(s)
                if c:
                    db.execute("INSERT INTO items (category_id,name,description,price,sort) VALUES (?,?,?,?,?)",(c,n,d,p,i))
            db.commit()

        # Seed sauces only if none exist
        if db.execute("SELECT COUNT(*) as c FROM sauces").fetchone()['c'] == 0:
            for cat_slug in ['gnocchi','fettuccine']:
                c = cid(cat_slug)
                if c:
                    for n in ['Pomodoro','Bechamel']:
                        db.execute("INSERT INTO sauces (category_id,name,price_type) VALUES (?,?,'simples')",(c,n))
                    for n in ['Bolonhesa','Quatro Queijos','Costela na Cerveja','Ragù de Ossobuco','Filé Mignon com Gorgonzola','Camarão com Espinafre']:
                        db.execute("INSERT INTO sauces (category_id,name,price_type) VALUES (?,?,'premium')",(c,n))
            db.commit()

def init_db():
    if USE_PG:
        with get_db() as db:
            db.execute('SELECT pg_advisory_xact_lock(74201931)')
            _create_tables()
            _seed_data()
    else:
        _create_tables()
        _seed_data()

# ─────────────────────────────────────────
#  DECORATORS
# ─────────────────────────────────────────
def login_required(f):
    @functools.wraps(f)
    def w(*a,**kw):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify(ok=False, msg='Faça login para continuar.'), 401
            flash('Faça login para continuar.','info')
            return redirect(url_for('login'))
        return f(*a,**kw)
    return w

def chef_required(f):
    @functools.wraps(f)
    def w(*a,**kw):
        if session.get('role') != 'chef':
            flash('Acesso restrito ao chef.','danger')
            return redirect(url_for('menu'))
        return f(*a,**kw)
    return w

# ─────────────────────────────────────────
#  AUTH ROUTES
# ─────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('menu'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        pw    = request.form.get('password','')

        # Rate limiting: 5 tentativas por minuto por IP
        ip = request.remote_addr or 'unknown'
        rate_key = f'login:{ip}'
        if not _check_rate_limit(rate_key, max_requests=5, window_seconds=60):
            flash('Muitas tentativas. Aguarde um minuto.','danger')
            return redirect(url_for('login'))

        if not email or not pw:
            flash('Preencha e-mail e senha.','danger')
            return redirect(url_for('login'))

        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
        if user and check_password_hash(user['password'], pw):
            session.clear()
            session.update({'user_id':user['id'],'role':user['role'],
                            'username':user['username'],'full_name':user['full_name'] or user['username']})
            return redirect(url_for('chef_dashboard') if user['role']=='chef' else url_for('menu'))
        flash('E-mail ou senha incorretos.','danger')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form.get('username','').strip()
        e = request.form.get('email','').strip().lower()
        p = request.form.get('password','')
        f = request.form.get('full_name','').strip()
        if not all([u,e,p]):
            flash('Preencha todos os campos.','danger')
            return render_template('register.html')
        if len(p) < 6:
            flash('Senha: mínimo 6 caracteres.','danger')
            return render_template('register.html')
        try:
            with get_db() as db:
                db.execute("INSERT INTO users (username,email,password,role,full_name) VALUES (?,?,?,'cliente',?)",
                           (u,e,generate_password_hash(p),f))
                db.commit()
            flash('Conta criada! Faça login.','success')
            return redirect(url_for('login'))
        except INTEGRITY_ERRORS:
            flash('E-mail ou usuário já cadastrado.','danger')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─────────────────────────────────────────
#  CUSTOMER ROUTES
# ─────────────────────────────────────────
@app.route('/painel')
@login_required
def painel():
    if session['role'] == 'chef':
        return redirect(url_for('chef_dashboard'))
    with get_db() as db:
        cats   = db.execute("SELECT * FROM categories ORDER BY sort").fetchall()
        iraw   = db.execute("SELECT i.*,c.slug cat_slug FROM items i JOIN categories c ON i.category_id=c.id WHERE i.active=1 ORDER BY i.sort").fetchall()
        sraw   = db.execute("SELECT * FROM sauces ORDER BY id").fetchall()
        user   = db.execute("SELECT * FROM users WHERE id=?",(session['user_id'],)).fetchone()
    items  = {c['slug']:[r for r in iraw if r['cat_slug']==c['slug']] for c in cats}
    sauces = {c['slug']:[r for r in sraw if r['category_id']==c['id']] for c in cats}
    return render_template('menu.html', categories=cats, items=items, sauces=sauces, user=user)
@app.route('/menu')
def menu():
    with get_db() as db:
        cats   = db.execute("SELECT * FROM categories ORDER BY sort").fetchall()
        iraw   = db.execute("SELECT i.*,c.slug cat_slug FROM items i JOIN categories c ON i.category_id=c.id WHERE i.active=1 ORDER BY i.sort").fetchall()
        sraw   = db.execute("SELECT * FROM sauces ORDER BY id").fetchall()
        user   = db.execute("SELECT * FROM users WHERE id=?",(session.get('user_id'),)).fetchone() if session.get('user_id') else None
    items  = {c['slug']:[r for r in iraw if r['cat_slug']==c['slug']] for c in cats}
    sauces = {c['slug']:[r for r in sraw if r['category_id']==c['id']] for c in cats}
    return render_template('menu.html', categories=cats, items=items, sauces=sauces, user=user)

@app.route('/order/place', methods=['POST'])
@login_required
def place_order():
    # Rate limiting: 10 pedidos por minuto por usuário
    user_rate = f'order:{session.get("user_id","unknown")}'
    if not _check_rate_limit(user_rate, max_requests=10, window_seconds=60):
        return jsonify({'ok':False,'msg':'Muitos pedidos. Aguarde.'}), 429

    data    = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(ok=False, msg='Pedido inválido'), 400
    cart    = data.get('cart', [])
    if not isinstance(cart, list) or len(cart) > 100:
        return jsonify(ok=False, msg='Carrinho inválido'), 400
    if any(not isinstance(data.get(key, ''), str) for key in ('address', 'number', 'city', 'note')):
        return jsonify(ok=False, msg='Endereço inválido'), 400
    address = data.get('address','').strip()
    number  = data.get('number','').strip()
    city    = data.get('city','').strip()
    note    = data.get('note','').strip()

    if not cart:
        return jsonify({'ok':False,'msg':'Carrinho vazio'}), 400
    if not address or not number or not city:
        return jsonify({'ok':False,'msg':'Endereço, número e cidade são obrigatórios'}), 400

    with get_db() as db:
        user  = db.execute("SELECT * FROM users WHERE id=?",(session['user_id'],)).fetchone()
        total = 0.0
        lines = []
        for entry in cart:
            if (not isinstance(entry, dict) or type(entry.get('id')) is not int
                    or type(entry.get('qty', 1)) is not int or not 1 <= entry.get('qty', 1) <= 99
                    or not isinstance(entry.get('sauce', ''), str)):
                return jsonify(ok=False, msg='Item ou quantidade inválidos'), 400
            item = db.execute("SELECT * FROM items WHERE id=? AND active=1",(entry['id'],)).fetchone()
            if not item:
                return jsonify(ok=False, msg='Um prato não está mais disponível. Atualize o cardápio.'), 400
            qty  = entry.get('qty', 1)
            sauce = entry.get('sauce','')
            options = db.execute('SELECT * FROM sauces WHERE category_id=?', (item['category_id'],)).fetchall()
            chosen = next((row for row in options if row['name'] == sauce), None)
            if options and not chosen:
                return jsonify(ok=False, msg='Molho inválido'), 400
            if sauce and not chosen:
                return jsonify(ok=False, msg='Molho inválido'), 400
            if chosen and chosen['price_type'] == 'premium' and chosen['final_price'] is None:
                return jsonify(ok=False, msg='O chef ainda não definiu o preço deste molho'), 400
            price = chosen['final_price'] if chosen and chosen['final_price'] is not None else item['price']
            total += round(price * qty, 2)
            lines.append({'id':item['id'],'name':item['name'],'qty':qty,'price':price,'sauce':sauce})

        total = round(total, 2)

        if not lines:
            return jsonify({'ok':False,'msg':'Nenhum item válido'}), 400

        cur      = db.execute("INSERT INTO orders (user_id,total,address,number,city,note) VALUES (?,?,?,?,?,?)" + (' RETURNING id' if USE_PG else ''),
                              (session['user_id'],total,address,number,city,note))
        order_id = cur.lastrowid
        for l in lines:
            db.execute("INSERT INTO order_items (order_id,item_id,item_name,quantity,unit_price,sauce) VALUES (?,?,?,?,?,?)",
                       (order_id,l['id'],l['name'],l['qty'],l['price'],l['sauce']))
        db.commit()

    client = user['full_name'] or user['username']
    phone  = user['phone'] or 'não informado'
    itens_txt = '\n'.join(
        f"  • {l['qty']}x {l['name']}" + (f" c/ {l['sauce']}" if l['sauce'] else '') +
        f"  ➜  R$ {l['price']*l['qty']:.2f}" for l in lines
    )
    msg = (
        f"🍝 *NOVO PEDIDO — Da Massa* 🍝\n\n"
        f"👤 *Cliente:* {client}\n"
        f"📞 *Telefone:* {phone}\n\n"
        f"🛒 *Itens do pedido:*\n{itens_txt}\n\n"
        f"💰 *Total:* R$ {total:.2f}\n\n"
        f"📍 *Entrega:*\n"
        f"   {address}, nº {number} — {city}"
        + (f"\n\n📝 *Obs:* {note}" if note else '')
        + f"\n\n_Pedido #{order_id}_"
    )
    wa_url = f"https://wa.me/{get_chef_whatsapp()}?text={urllib.parse.quote(msg)}"
    return jsonify({'ok':True,'order_id':order_id,'total':total,'wa_url':wa_url})

@app.route('/orders')
@login_required
def my_orders():
    with get_db() as db:
        orders = db.execute("SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC",(session['user_id'],)).fetchall()
        ois    = db.execute("SELECT oi.* FROM order_items oi JOIN orders o ON oi.order_id=o.id WHERE o.user_id=?",(session['user_id'],)).fetchall()
    grouped = {o['id']:{'order':o,'items':[i for i in ois if i['order_id']==o['id']]} for o in orders}
    return render_template('my_orders.html', grouped=grouped)

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        fn = request.form.get('full_name','').strip()
        un = request.form.get('username','').strip()
        ph = request.form.get('phone','').strip()
        ad = request.form.get('address','').strip()
        nm = request.form.get('number','').strip()
        ct = request.form.get('city','').strip()
        np = request.form.get('new_password','')
        if not un:
            flash('Informe o nome de usuário.', 'danger')
            return redirect(url_for('profile'))
        try:
            with get_db() as db:
                if np:
                    if len(np) < 6:
                        flash('Senha: mínimo 6 caracteres.','danger')
                        return redirect(url_for('profile'))
                    db.execute("UPDATE users SET full_name=?,username=?,phone=?,address=?,number=?,city=?,password=? WHERE id=?",
                               (fn,un,ph,ad,nm,ct,generate_password_hash(np),session['user_id']))
                else:
                    db.execute("UPDATE users SET full_name=?,username=?,phone=?,address=?,number=?,city=? WHERE id=?",
                               (fn,un,ph,ad,nm,ct,session['user_id']))
                db.commit()
            session['username'] = un; session['full_name'] = fn
            flash('Perfil atualizado!','success')
        except INTEGRITY_ERRORS:
            flash('Usuário já existe.','danger')
        return redirect(url_for('profile'))
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE id=?",(session['user_id'],)).fetchone()
    return render_template('profile.html', user=user)

# ─────────────────────────────────────────
#  CHEF ROUTES
# ─────────────────────────────────────────
@app.route('/chef')
@login_required
@chef_required
def chef_dashboard():
    with get_db() as db:
        cats        = db.execute("SELECT * FROM categories ORDER BY sort").fetchall()
        sauces      = db.execute('SELECT s.*,c.name category_name FROM sauces s JOIN categories c ON c.id=s.category_id ORDER BY c.sort,s.id').fetchall()
        iraw        = db.execute("SELECT i.*,c.slug cat_slug FROM items i JOIN categories c ON i.category_id=c.id ORDER BY c.sort,i.sort").fetchall()
        total_items = db.execute("SELECT COUNT(*) c FROM items WHERE active=1").fetchone()['c']
        total_users = db.execute("SELECT COUNT(*) c FROM users WHERE role='cliente'").fetchone()['c']
        new_orders  = db.execute("SELECT COUNT(*) c FROM orders WHERE status='novo'").fetchone()['c']
        recent_ords = db.execute("SELECT o.*,u.full_name,u.username,u.phone FROM orders o JOIN users u ON o.user_id=u.id ORDER BY o.created_at DESC LIMIT 15").fetchall()
        all_oi      = db.execute("SELECT * FROM order_items WHERE order_id IN (SELECT id FROM orders ORDER BY created_at DESC LIMIT 15)").fetchall()
    items = {c['slug']:[r for r in iraw if r['cat_slug']==c['slug']] for c in cats}
    og    = {o['id']:{'order':o,'items':[i for i in all_oi if i['order_id']==o['id']]} for o in recent_ords}
    return render_template('chef.html', categories=cats, items=items,
                           sauces=sauces,
                           total_items=total_items, total_users=total_users,
                           new_orders=new_orders, orders_grouped=og,
                           chef_whatsapp=get_chef_whatsapp())

@app.route('/chef/sauce/<int:sid>/price', methods=['POST'])
@login_required
@chef_required
def chef_sauce_price(sid):
    value = request.form.get('price', '').strip()
    try:
        price = float(value) if value else None
        if price is not None and (not math.isfinite(price) or not 0 < price <= 100000 or round(price, 2) != price):
            raise ValueError('Preço inválido')
    except ValueError:
        flash('Informe um preço positivo, com até duas casas decimais.', 'danger')
        return redirect(url_for('chef_dashboard'))
    with get_db() as db:
        db.execute('UPDATE sauces SET final_price=? WHERE id=?', (price, sid))
        db.commit()
    flash('Preço do molho atualizado.', 'success')
    return redirect(url_for('chef_dashboard'))

@app.route('/chef/whatsapp', methods=['POST'])
@login_required
@chef_required
def chef_update_whatsapp():
    n = request.form.get('whatsapp','').strip().replace(' ','').replace('-','').replace('+','')
    if n and all(c.isdigit() for c in n):
        set_chef_whatsapp(n)
        flash(f'WhatsApp atualizado para {n}','success')
    else:
        flash('Número inválido. Use apenas dígitos com DDI.','danger')
    return redirect(url_for('chef_dashboard'))

@app.route('/chef/order/<int:oid>/status', methods=['POST'])
@login_required
@chef_required
def chef_order_status(oid):
    s = request.form.get('status','novo')
    if s not in {'novo', 'em_preparo', 'enviado', 'entregue'}:
        return 'Status inválido', 400
    with get_db() as db:
        db.execute("UPDATE orders SET status=? WHERE id=?",(s,oid))
        db.commit()
    return redirect(url_for('chef_dashboard'))

@app.route('/chef/item/add', methods=['POST'])
@login_required
@chef_required
def chef_add_item():
    cat_slug = request.form.get('category','')
    name     = request.form.get('name','').strip()
    desc     = request.form.get('description','').strip()
    try:
        price = float(request.form.get('price','0'))
        if not name or not math.isfinite(price) or not 0 < price <= 100000:
            raise ValueError('Informe nome e preço válido')
        with get_db() as db:
            cat = db.execute("SELECT id FROM categories WHERE slug=?",(cat_slug,)).fetchone()
            if not cat:
                raise ValueError('Categoria inválida')
            image = save_image(db)
            ms  = db.execute("SELECT MAX(sort) m FROM items WHERE category_id=?",(cat['id'],)).fetchone()['m'] or 0
            db.execute("INSERT INTO items (category_id,name,description,price,sort,image) VALUES (?,?,?,?,?,?)",
                       (cat['id'],name,desc,price,ms+1,image))
            db.commit()
        flash(f'Prato "{name}" adicionado!','success')
    except Exception as ex:
        app.logger.exception('Falha ao salvar prato')
        flash('Não foi possível salvar. Confira os dados e a imagem.','danger')
    return redirect(url_for('chef_dashboard'))

@app.route('/chef/item/edit/<int:iid>', methods=['POST'])
@login_required
@chef_required
def chef_edit_item(iid):
    cat_slug = request.form.get('category','')
    name     = request.form.get('name','').strip()
    desc     = request.form.get('description','').strip()
    active   = 1 if request.form.get('active')=='1' else 0
    try:
        price = float(request.form.get('price','0'))
        if not name or not math.isfinite(price) or not 0 < price <= 100000:
            raise ValueError('Informe nome e preço válido')
        with get_db() as db:
            cat     = db.execute("SELECT id FROM categories WHERE slug=?",(cat_slug,)).fetchone()
            old_img = db.execute("SELECT image FROM items WHERE id=?",(iid,)).fetchone()['image']
            if not cat:
                raise ValueError('Categoria inválida')
            new_img = save_image(db)
            if new_img:
                delete_image(db, old_img)
                db.execute("UPDATE items SET category_id=?,name=?,description=?,price=?,active=?,image=? WHERE id=?",
                           (cat['id'],name,desc,price,active,new_img,iid))
            else:
                db.execute("UPDATE items SET category_id=?,name=?,description=?,price=?,active=? WHERE id=?",
                           (cat['id'],name,desc,price,active,iid))
            db.commit()
        flash(f'"{name}" atualizado!','success')
    except Exception as ex:
        app.logger.exception('Falha ao salvar prato')
        flash('Não foi possível salvar. Confira os dados e a imagem.','danger')
    return redirect(url_for('chef_dashboard'))

@app.route('/chef/item/delete/<int:iid>', methods=['POST'])
@login_required
@chef_required
def chef_delete_item(iid):
    with get_db() as db:
        item = db.execute("SELECT name,image FROM items WHERE id=?",(iid,)).fetchone()
        if item:
            delete_image(db, item['image'])
            db.execute("DELETE FROM items WHERE id=?",(iid,))
            db.commit()
            flash(f'"{item["name"]}" removido.','success')
    return redirect(url_for('chef_dashboard'))

@app.route('/chef/item/toggle/<int:iid>', methods=['POST'])
@login_required
@chef_required
def chef_toggle_item(iid):
    with get_db() as db:
        item = db.execute("SELECT active,name FROM items WHERE id=?",(iid,)).fetchone()
        if item:
            new = 0 if item['active'] else 1
            db.execute("UPDATE items SET active=? WHERE id=?",(new,iid))
            db.commit()
            flash(f'"{item["name"]}" {"ativado" if new else "desativado"}.','success')
    return redirect(url_for('chef_dashboard'))

# ─── CATEGORY CRUD ───
@app.route('/chef/category/add', methods=['POST'])
@login_required
@chef_required
def chef_add_category():
    name = request.form.get('name','').strip()
    size = request.form.get('size','500g').strip()
    if not name:
        flash('Nome da categoria obrigatorio.','danger')
        return redirect(url_for('chef_dashboard'))
    slug = slugify(name)
    try:
        with get_db() as db:
            max_sort = db.execute("SELECT COALESCE(MAX(sort),0) m FROM categories").fetchone()['m']
            db.execute("INSERT INTO categories (slug,name,size,sort) VALUES (?,?,?,?)",
                       (slug, name, size, max_sort + 1))
            db.commit()
        flash(f'Categoria "{name}" adicionada!','success')
    except INTEGRITY_ERRORS:
        flash('Categoria ja existe.','danger')
    return redirect(url_for('chef_dashboard'))

@app.route('/chef/category/edit/<int:cid>', methods=['POST'])
@login_required
@chef_required
def chef_edit_category(cid):
    name = request.form.get('name','').strip()
    size = request.form.get('size','500g').strip()
    if not name:
        flash('Nome da categoria obrigatorio.','danger')
        return redirect(url_for('chef_dashboard'))
    slug = slugify(name)
    try:
        with get_db() as db:
            db.execute("UPDATE categories SET slug=?,name=?,size=? WHERE id=?",(slug,name,size,cid))
            db.commit()
        flash(f'Categoria "{name}" atualizada!','success')
    except INTEGRITY_ERRORS:
        flash('Slug da categoria ja existe.','danger')
    return redirect(url_for('chef_dashboard'))

@app.route('/chef/category/delete/<int:cid>', methods=['POST'])
@login_required
@chef_required
def chef_delete_category(cid):
    with get_db() as db:
        cat = db.execute("SELECT name FROM categories WHERE id=?",(cid,)).fetchone()
        if not cat:
            flash('Categoria nao encontrada.','danger')
            return redirect(url_for('chef_dashboard'))
        items_count = db.execute("SELECT COUNT(*) c FROM items WHERE category_id=?",(cid,)).fetchone()['c']
        if items_count > 0:
            flash(f'Nao foi possivel remover "{cat["name"]}": existem {items_count} prato(s) nesta categoria.','danger')
            return redirect(url_for('chef_dashboard'))
        db.execute("DELETE FROM sauces WHERE category_id=?",(cid,))
        db.execute("DELETE FROM categories WHERE id=?",(cid,))
        db.commit()
        flash(f'Categoria "{cat["name"]}" removida.','success')
    return redirect(url_for('chef_dashboard'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    with get_db() as db:
        image = db.execute('SELECT content,mime FROM uploads WHERE filename=?', (filename,)).fetchone()
    if image:
        response = send_file(io.BytesIO(bytes(image['content'])), mimetype=image['mime'], max_age=86400)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/checkout-login', methods=['POST'])
def api_checkout_login():
    """Login rápido via AJAX no checkout."""
    if session.get('user_id'):
        return jsonify({'ok':True,'logged':True})
    if not _check_rate_limit(f'login:{request.remote_addr or "unknown"}', 5, 60):
        return jsonify(ok=False, msg='Muitas tentativas. Aguarde um minuto.'), 429
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('email'), str) or not isinstance(data.get('password'), str):
        return jsonify(ok=False, msg='Preencha e-mail e senha.'), 400
    email = data['email'].strip().lower()
    pw = data['password']
    if not email or not pw:
        return jsonify({'ok':False,'msg':'Preencha e-mail e senha.'}), 400
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
    if user and check_password_hash(user['password'], pw):
        session.update({'user_id':user['id'],'role':user['role'],
                        'username':user['username'],'full_name':user['full_name'] or user['username']})
        return jsonify({'ok':True,'logged':True,'role':user['role']})
    return jsonify({'ok':False,'msg':'E-mail ou senha incorretos.'}), 401

@app.route('/api/menu')
def api_menu():
    with get_db() as db:
        cats   = db.execute("SELECT * FROM categories ORDER BY sort").fetchall()
        items  = db.execute("SELECT i.*,c.slug FROM items i JOIN categories c ON i.category_id=c.id WHERE i.active=1 ORDER BY i.sort").fetchall()
        sauces = db.execute("SELECT * FROM sauces").fetchall()
    return jsonify({'categories':[dict(c) for c in cats],'items':[dict(i) for i in items],'sauces':[dict(s) for s in sauces]})

if __name__ == '__main__':
    init_db()
    # ⚠️ debug=True APENAS para desenvolvimento local
    # Em produção, use: waitress-serve --port=$PORT damassa.wsgi:app
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=debug_mode, port=port, host='0.0.0.0')
