# 🍝 Da Massa — Cardápio Digital

Sistema completo de cardápio digital com backend Flask + SQLite para restaurantes de massa.

## Funcionalidades

### Cliente
- Cadastro e login próprio
- Visualização do cardápio com fotos e descrições
- Montagem de pedidos com molhos personalizados
- Histórico de pedidos
- Perfil editável: nome, telefone, endereço, cidade
- Troca de senha

### Chef
- Painel de controle com estatísticas
- CRUD completo: pratos e categorias
- Ativar/desativar itens do cardápio
- Gerenciar pedidos: status (novo, em preparo, enviado, entregue)
- Upload de fotos dos pratos
- Integração com WhatsApp para recebimento de pedidos
- Alterações refletem imediatamente para os clientes
- API pública `/api/menu`

## Instalação

### Desenvolvimento Local

```bash
pip install -r requirements.txt
cp .env.example .env
# Edite .env e defina SECRET_KEY:
# SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
python app.py
```

Acesse: http://localhost:5000

### Produção

```bash
pip install -r requirements.txt
cp .env.example .env
# Edite .env com sua SECRET_KEY e demais configurações
waitress-serve --port=$PORT wsgi:app
```

## Credenciais padrão

| Perfil | E-mail | Senha |
|--------|--------|-------|
| Chef (fixo) | chef@damassa.com | admin123 |
| Cliente | cadastre-se na tela de registro | — |

> **Importante:** Troque a senha do chef após o primeiro login!

## Estrutura

```
├── wsgi.py                 # Entrypoint para produção
├── damassa/
│   ├── app.py              # Backend Flask + SQLite
│   ├── requirements.txt
│   ├── .env.example        # Template de configurações
│   ├── templates/
│   │   ├── base.html       # Layout base + navbar
│   │   ├── login.html      # Tela de login
│   │   ├── register.html   # Cadastro de cliente
│   │   ├── menu.html       # Cardápio do cliente
│   │   ├── my_orders.html  # Pedidos do cliente
│   │   ├── profile.html    # Perfil do cliente
│   │   └── chef.html       # Painel do chef
│   └── static/
│       ├── css/style.css   # Estilos
│       ├── js/script.js    # Interatividade
│       └── uploads/        # Fotos dos pratos
└── .gitignore
```

## Deploy

### Render (gratuito)

1. Crie um **Web Service** conectando este repositório
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `waitress-serve --port=$PORT wsgi:app`
4. Adicione as variáveis de ambiente no painel:
   - `SECRET_KEY` — gere com `python -c "import secrets; print(secrets.token_hex(32))"`
   - `CHEF_WHATSAPP` — número com DDI
   - `PROD=1`

### Hospedagem caseira (VPS/Windows)

```bash
setx SECRET_KEY "sua-chave-secreta-aqui"
setx PROD 1
waitress-serve --port=5000 wsgi:app
```

## Segurança

- `SECRET_KEY` nunca deve ser commitada (use variável de ambiente ou `.env`)
- `.env` e `*.db` estão no `.gitignore`
- Rate limiting contra brute force no login (5 tentativas/minuto)
- Cookies de sessão com HttpOnly e SameSite=Lax
- Upload de imagens limitado a 8MB (apenas PNG/JPG/GIF/WEBP)
