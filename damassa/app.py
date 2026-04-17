from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify, flash, send_from_directory)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os, functools, uuid, urllib.parse, unicodedata, re, secrets, time
from dotenv import load_dotenv

# ─────────────────────────────────────────
#  CONFIGURAÇÕES
#  ─────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

USE_PG = bool(os.environ.get("DATABASE_URL"))

def _get_upload_folder():
    return os.environ.get("UPLOAD_FOLDER", os.path.join(os.path.dirname(__file__), "static", "uploads"))

app = Flask(__name__)

# ─── Segurança de sessão ───
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
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
    'MAX_CONTENT_LENGTH': 8 * 1024 * 1024,
})
if os.environ.get("PROD") or os.environ.get("DYNO"):
    app.config['SESSION_COOKIE_SECURE'] = True

UPLOAD_FOLDER = _get_upload_folder()
ALLOWED_EXT   = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# ─── WhatsApp do chef ───
CHEF_WHATSAPP_DEFAULT = os.environ.get("CHEF_WHATSAPP", "5581989073030")
_chef_whatsapp = CHEF_WHATSAPP_DEFAULT

def get_chef_whatsapp():
    return _chef_whatsapp

def set_chef_whatsapp(value):
    global _chef_whatsapp
    _chef_whatsapp = value

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─────────────────────────────────────────
#  RATE LIMITING SIMPLE (memória)
# ─────────────────────────────────────────
_rate_limits: dict[str, list[float]] = {}

def _check_rate_limit(key: str, max_requests: int, window_seconds: int) -> bool:
    now = time.time()
    _rate_limits.setdefault(key, [])
    _rate_limits[key] = [t for t in _rate_limits[key] if now - t < window_seconds]
    if len(_rate_limits[key]) >= max_requests:
        return False
    _rate_limits[key].append(now)
    return True

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
        # Para INSERT, adiciona RETURNING id se não tiver
        if sql.strip().upper().startswith('INSERT') and 'RETURNING' not in sql.upper():
            sql = sql.rstrip(';') + ' RETURNING id'
        self._cur.execute(sql, params or ())
        # Captura lastrowid para INSERT com RETURNING
        if sql.strip().upper().startswith('INSERT') and 'RETURNING' in sql.upper():
            row = self._cur.fetchone()
            if row:
                self.lastrowid = row['id']
        return self

    def executescript(self, sql):
        # PostgreSQL não permite executar múltiplos statements com execute()
        # Separamos e executamos um a um com autocommit
        self._conn.autocommit = True
        had_error = False
        try:
            for stmt in sql.split(';'):
                stmt = stmt.strip()
                if stmt:
                    try:
                        self._cur.execute(stmt.replace('?', '%s'))
                    except Exception as e:
                        # IGNORAR erros esperados
                        had_error = True
        finally:
            self._conn.autocommit = False
            if had_error:
                self._conn.rollback()
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


def get_db():
    if USE_PG:
        import psycopg2
        return _PgCursor(psycopg2.connect(os.environ["DATABASE_URL"]))
    else:
        import sqlite3
        DB_PATH = os.path.join(os.path.dirname(__file__), "damassa.db")
        conn = sqlite3.connect(DB_PATH, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def save_image(field='image'):
    f = request.files.get(field)
    if f and f.filename and allowed_file(f.filename):
        ext  = f.filename.rsplit('.', 1)[1].lower()
        name = f"{uuid.uuid4().hex}.{ext}"
        f.save(os.path.join(UPLOAD_FOLDER, name))
        return name
    return None

def delete_image(filename):
    if filename:
        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(path):
            os.remove(path)

def slugify(text):
    text = unicodedata.normalize('NFKD', text.lower()).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip()
    return re.sub(r'[-\s]+', '-', text) or 'cat'

# ─────────────────────────────────────────
#  INIT DB
# ─────────────────────────────────────────
def init_db():
    # Usa conexão separada para criar tabelas (evita transação abortada)
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id         SERIAL PRIMARY KEY,
            username   TEXT    UNIQUE NOT NULL,
            email      TEXT    UNIQUE NOT NULL,
            password   TEXT    NOT NULL,
            role       TEXT    NOT NULL DEFAULT 'cliente',
            full_name  TEXT    DEFAULT '',
            phone      TEXT    DEFAULT '',
            address    TEXT    DEFAULT '',
            number     TEXT    DEFAULT '',
            city       TEXT    DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS categories (
            id   SERIAL PRIMARY KEY,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            size TEXT DEFAULT '500g',
            sort INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS items (
            id          SERIAL PRIMARY KEY,
            category_id INTEGER NOT NULL,
            name        TEXT    NOT NULL,
            description TEXT    DEFAULT '',
            price       REAL    NOT NULL,
            active      INTEGER DEFAULT 1,
            sort        INTEGER DEFAULT 0,
            image       TEXT    DEFAULT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );
        CREATE TABLE IF NOT EXISTS sauces (
            id          SERIAL PRIMARY KEY,
            category_id INTEGER NOT NULL,
            name        TEXT    NOT NULL,
            price_type  TEXT    DEFAULT 'simples',
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );
        CREATE TABLE IF NOT EXISTS orders (
            id         SERIAL PRIMARY KEY,
            user_id    INTEGER NOT NULL,
            total      REAL    NOT NULL,
            address    TEXT    DEFAULT '',
            number     TEXT    DEFAULT '',
            city       TEXT    DEFAULT '',
            note       TEXT    DEFAULT '',
            status     TEXT    DEFAULT 'novo',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id         SERIAL PRIMARY KEY,
            order_id   INTEGER NOT NULL,
            item_id    INTEGER NOT NULL,
            item_name  TEXT    NOT NULL,
            quantity   INTEGER NOT NULL DEFAULT 1,
            unit_price REAL    NOT NULL,
            sauce      TEXT    DEFAULT '',
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
        """)

    # Usa conexão SEPARADA para inserir dados (evita transação abortada)
    with get_db() as db:
        # migration: add image column if missing
        try:
            db.execute("ALTER TABLE items ADD COLUMN image TEXT DEFAULT NULL")
            db.commit()
        except Exception:
            pass

        # Seed chef (locked)
        if not db.execute("SELECT id FROM users WHERE email='chef@damassa.com'").fetchone():
            db.execute("INSERT INTO users (username,email,password,role,full_name) VALUES (?,?,?,'chef','Josue Matheus')",
                       ('chef_josue','chef@damassa.com', generate_password_hash('oDEtfwa7ocHmP5lr4Mr-Hw')))
        # Migrate existing chef name
        chef = db.execute("SELECT id FROM users WHERE role='chef'").fetchone()
        if chef:
            db.execute("UPDATE users SET full_name='Josue Matheus',username='chef_josue' WHERE role='chef'")

        # Seed categories
        for slug,name,size,sort in [
            ('lasanha','Lasanhas','500g',1),
            ('gnocchi','Gnocchi (Nhoque)','500g',2),
            ('fettuccine','Fettuccine','500g',3),
            ('ravioli','Ravioli','500g',4)]:
            if not db.execute("SELECT id FROM categories WHERE slug=?",(slug,)).fetchone():
                db.execute("INSERT INTO categories (slug,name,size,sort) VALUES (?,?,?,?)",(slug,name,size,sort))

        def cid(slug):
            return db.execute("SELECT id FROM categories WHERE slug=?",(slug,)).fetchone()['id']

        if db.execute("SELECT COUNT(*) as c FROM items").fetchone()['c'] == 0:
            for i,(s,n,d,p) in enumerate([
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
            ]):
                db.execute("INSERT INTO items (category_id,name,description,price,sort) VALUES (?,?,?,?,?)",(cid(s),n,d,p,i))

        if db.execute("SELECT COUNT(*) as c FROM sauces").fetchone()['c'] == 0:
            for s in ['gnocchi','fettuccine']:
                c = cid(s)
                for n in ['Pomodoro','Bechamel']:
                    db.execute("INSERT INTO sauces (category_id,name,price_type) VALUES (?,?,?)",(c,n,'simples'))
                for n in ['Bolonhesa','Quatro Queijos','Costela na Cerveja','Ragù de Ossobuco','Filé Mignon com Gorgonzola','Camarão com Espinafre']:
                    db.execute("INSERT INTO sauces (category_id,name,price_type) VALUES (?,?,?)",(c,n,'premium'))

        db.commit()

# ─────────────────────────────────────────
#  DECORATORS
# ─────────────────────────────────────────
def login_required(f):
    @functools.wraps(f)
    def w(*a,**kw):
        if 'user_id' not in session:
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
    if 'user_id' in session:
        return redirect(url_for('menu') if session['role']=='cliente' else url_for('chef_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        pw    = request.form.get('password','').strip()

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
        p = request.form.get('password','').strip()
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
        except sqlite3.IntegrityError:
            flash('E-mail ou usuário já cadastrado.','danger')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─────────────────────────────────────────
#  CUSTOMER ROUTES
# ─────────────────────────────────────────
@app.route('/menu')
@login_required
def menu():
    with get_db() as db:
        cats   = db.execute("SELECT * FROM categories ORDER BY sort").fetchall()
        iraw   = db.execute("SELECT i.*,c.slug cat_slug FROM items i JOIN categories c ON i.category_id=c.id WHERE i.active=1 ORDER BY i.sort").fetchall()
        sraw   = db.execute("SELECT * FROM sauces ORDER BY id").fetchall()
        user   = db.execute("SELECT * FROM users WHERE id=?",(session['user_id'],)).fetchone()
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

    data    = request.get_json(force=True)
    cart    = data.get('cart', [])
    address = data.get('address','').strip()
    number  = data.get('number','').strip()
    city    = data.get('city','').strip()
    note    = data.get('note','').strip()

    if not cart:
        return jsonify({'ok':False,'msg':'Carrinho vazio'}), 400
    if not address or not number:
        return jsonify({'ok':False,'msg':'Endereço e número são obrigatórios'}), 400

    with get_db() as db:
        user  = db.execute("SELECT * FROM users WHERE id=?",(session['user_id'],)).fetchone()
        total = 0.0
        lines = []
        for entry in cart:
            item = db.execute("SELECT * FROM items WHERE id=? AND active=1",(entry['id'],)).fetchone()
            if not item: continue
            qty  = max(1, int(entry.get('qty',1)))
            sauce = entry.get('sauce','')
            total += item['price'] * qty
            lines.append({'id':item['id'],'name':item['name'],'qty':qty,'price':item['price'],'sauce':sauce})

        if not lines:
            return jsonify({'ok':False,'msg':'Nenhum item válido'}), 400

        cur      = db.execute("INSERT INTO orders (user_id,total,address,number,city,note) VALUES (?,?,?,?,?,?)",
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
    if session['role'] == 'chef':
        return redirect(url_for('chef_dashboard'))
    if request.method == 'POST':
        fn = request.form.get('full_name','').strip()
        un = request.form.get('username','').strip()
        ph = request.form.get('phone','').strip()
        ad = request.form.get('address','').strip()
        nm = request.form.get('number','').strip()
        ct = request.form.get('city','').strip()
        np = request.form.get('new_password','').strip()
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
        except sqlite3.IntegrityError:
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
        iraw        = db.execute("SELECT i.*,c.slug cat_slug FROM items i JOIN categories c ON i.category_id=c.id ORDER BY c.sort,i.sort").fetchall()
        total_items = db.execute("SELECT COUNT(*) c FROM items WHERE active=1").fetchone()['c']
        total_users = db.execute("SELECT COUNT(*) c FROM users WHERE role='cliente'").fetchone()['c']
        new_orders  = db.execute("SELECT COUNT(*) c FROM orders WHERE status='novo'").fetchone()['c']
        recent_ords = db.execute("SELECT o.*,u.full_name,u.username,u.phone FROM orders o JOIN users u ON o.user_id=u.id ORDER BY o.created_at DESC LIMIT 15").fetchall()
        all_oi      = db.execute("SELECT * FROM order_items WHERE order_id IN (SELECT id FROM orders ORDER BY created_at DESC LIMIT 15)").fetchall()
    items = {c['slug']:[r for r in iraw if r['cat_slug']==c['slug']] for c in cats}
    og    = {o['id']:{'order':o,'items':[i for i in all_oi if i['order_id']==o['id']]} for o in recent_ords}
    return render_template('chef.html', categories=cats, items=items,
                           total_items=total_items, total_users=total_users,
                           new_orders=new_orders, orders_grouped=og,
                           chef_whatsapp=get_chef_whatsapp())

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
        image = save_image('image')
        with get_db() as db:
            cat = db.execute("SELECT id FROM categories WHERE slug=?",(cat_slug,)).fetchone()
            ms  = db.execute("SELECT MAX(sort) m FROM items WHERE category_id=?",(cat['id'],)).fetchone()['m'] or 0
            db.execute("INSERT INTO items (category_id,name,description,price,sort,image) VALUES (?,?,?,?,?,?)",
                       (cat['id'],name,desc,price,ms+1,image))
            db.commit()
        flash(f'Prato "{name}" adicionado!','success')
    except Exception as ex:
        flash(f'Erro: {ex}','danger')
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
        with get_db() as db:
            cat     = db.execute("SELECT id FROM categories WHERE slug=?",(cat_slug,)).fetchone()
            old_img = db.execute("SELECT image FROM items WHERE id=?",(iid,)).fetchone()['image']
            new_img = save_image('image')
            if new_img:
                delete_image(old_img)
                db.execute("UPDATE items SET category_id=?,name=?,description=?,price=?,active=?,image=? WHERE id=?",
                           (cat['id'],name,desc,price,active,new_img,iid))
            else:
                db.execute("UPDATE items SET category_id=?,name=?,description=?,price=?,active=? WHERE id=?",
                           (cat['id'],name,desc,price,active,iid))
            db.commit()
        flash(f'"{name}" atualizado!','success')
    except Exception as ex:
        flash(f'Erro: {ex}','danger')
    return redirect(url_for('chef_dashboard'))

@app.route('/chef/item/delete/<int:iid>', methods=['POST'])
@login_required
@chef_required
def chef_delete_item(iid):
    with get_db() as db:
        item = db.execute("SELECT name,image FROM items WHERE id=?",(iid,)).fetchone()
        if item:
            delete_image(item['image'])
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
    except sqlite3.IntegrityError:
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
    except sqlite3.IntegrityError:
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
        db.execute("DELETE FROM categories WHERE id=?",(cid,))
        db.commit()
        flash(f'Categoria "{cat["name"]}" removida.','success')
    return redirect(url_for('chef_dashboard'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

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
