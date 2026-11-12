# Da Massa — Cardápio Digital

Flask, HTML/CSS/JavaScript e PostgreSQL em produção. SQLite apenas no desenvolvimento.

## Uso

- Cardápio público em `/menu`; cadastro/login ao finalizar o pedido.
- Pedidos e perfil do cliente; painel do chef em `/chef`.
- Pratos, fotos, categorias, preços finais dos molhos, WhatsApp e status de pedidos são editáveis pelo chef.
- Molhos premium sem preço definido ficam indisponíveis. O valor configurado é o preço final do prato, não um adicional.
- O pedido é salvo e o cliente é levado ao WhatsApp com a mensagem pronta. O cliente precisa enviá-la no WhatsApp.
- Fotos e configurações ficam no banco; fotos de até 4 MB (incluindo os campos do formulário).

## Desenvolvimento (a partir da raiz)

```powershell
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
$env:SECRET_KEY = 'defina-uma-chave-local'
$env:CHEF_PASSWORD = 'defina-sua-senha-inicial'
.venv/Scripts/python -m flask --app wsgi run
```

O chef inicial usa `chef@damassa.com`. A senha é lida de `CHEF_PASSWORD` somente ao criar a conta; depois pode ser trocada em **Perfil e senha**. Não existe senha administrativa padrão no código.

## Vercel

Projeto `damassa-cardapio`, equipe `voryn`, framework Flask, entrada `wsgi.py`, região `gru1`.

- `DATABASE_URL`: PostgreSQL com pool de conexões (Neon conectado pelo Marketplace).
- `SECRET_KEY`: chave estável e secreta para sessões/CSRF.
- `CHEF_PASSWORD`: senha inicial secreta; não altera uma conta já existente.
- `PROD=1`: cookies seguros HTTPS.
- `CHEF_WHATSAPP`: opcional; a alteração feita pelo painel tem precedência.
- Arquivos estáticos em `public/static`, servidos pelo CDN.

SQLite e uploads no disco da função não são usados em produção. Não copie bancos locais ou segredos para o Git. A criação de tabelas/seed é serializada no PostgreSQL para evitar duplicação durante cold starts. Não há garantia de disponibilidade absoluta; os limites dos planos e os serviços externos continuam aplicáveis.

## Verificação

```powershell
.venv/Scripts/python -m unittest discover -s tests -p test_app.py -v
# Integração real em schemas descartáveis; requer .env.local do projeto:
$env:RUN_POSTGRES_TESTS = '1'
.venv/Scripts/python -m unittest discover -s tests -p test_postgres.py -v
```

`tests/browser-flow.js` pode ser executado por Playwright CLI (`run-code --filename tests/browser-flow.js`) após abrir `/menu`. Ele cria cliente/pedido sintéticos e intercepta o WhatsApp; em produção, remova apenas esses registros identificados após o teste.
