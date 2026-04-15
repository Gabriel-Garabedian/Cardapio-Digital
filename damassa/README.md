# 🍝 Da Massa — Cardápio Digital

Sistema completo de cardápio digital com backend Flask + SQLite.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

Acesse: http://localhost:5000

## Credenciais padrão

| Perfil | E-mail | Senha |
|--------|--------|-------|
| Chef (fixo) | chef@damassa.com | admin123 |
| Cliente | cadastre-se na tela de registro | — |

## Funcionalidades

### Cliente
- Cadastro e login próprio
- Visualização do cardápio em tempo real
- Edição de perfil: nome, usuário, telefone, endereço, cidade
- Troca de senha

### Chef
- Login protegido (conta fixa, não editável)
- Painel com estatísticas
- Adicionar, editar, remover e ativar/desativar pratos
- Alterações refletem imediatamente para os clientes
- Endpoint `/api/menu` para integração externa

## Estrutura

```
damassa/
├── app.py              # Backend Flask + SQLite
├── damassa.db          # Banco de dados (gerado automaticamente)
├── requirements.txt
├── templates/
│   ├── base.html       # Layout base + navbar
│   ├── login.html      # Tela de login
│   ├── register.html   # Cadastro de cliente
│   ├── menu.html       # Cardápio do cliente
│   ├── profile.html    # Perfil do cliente
│   └── chef.html       # Painel do chef
└── static/
    ├── css/style.css   # Estilos completos
    └── js/script.js    # Animações e interações
```
