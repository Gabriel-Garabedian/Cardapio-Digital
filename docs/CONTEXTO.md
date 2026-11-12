# Contexto — Cardápio Digital / Da Massa

Atualizado em 12/11/2026.

- Pedido: revisar funcionamento e hospedar na Vercel. Usuário confirmou que preços finais serão definidos pelo chef.
- Repositório: Gabriel-Garabedian/Cardapio-Digital, branch master; base 0eadd7d. Clone local em C:/Users/Antonio Pedro/Projects/cardapio-digital.
- Vercel: equipe voryn (team_0fDPokRDzboxsb3U1uN3tjgv), projeto damassa-cardapio (prj_dyML6Lm9ASBigKLTYxSTrOoDz17S), Flask/wsgi.py/gru1. Conta atual Hobby; uso comercial requer plano compatível. Usuário foi consultado sobre demonstração versus pedidos reais, sem upgrade contratado.
- Neon Marketplace: damassa-db, plano free_v3, gru1, auth=false; aceite dos termos feito pelo usuário. DATABASE_URL com pool provisionada nos três ambientes; segredos de sessão/chef nos ambientes production/preview.
- Acesso do chef: credenciais somente no arquivo privado Downloads/Acesso Da Massa.txt e arquivos .env ignorados. Não copiar conteúdo para docs/Git. Senha inicial aleatória; trocar em Perfil e senha. Senha fixa do repositório removida.
- Correções: SQL e IDs compatíveis SQLite/Postgres; erros duplicados; datas; fechamento de conexões; inicialização PG serializada; CSRF; limite persistente compartilhado entre logins; JSON em sessão expirada; validação de pedido/quantidades/molhos; fotos e WhatsApp no banco; fotos com validação e transação atômica; escaping de textos e edição com apóstrofos; chamada JS inexistente removida; WhatsApp abre na mesma aba para evitar bloqueio de popup; CSS/JS em public/static no CDN.
- Chef edita preço final do prato por molho em Molhos e preços. Premium sem preço indisponível; simples sem preço específico usa preço do prato. Valores originais do cardápio preservados até chef alterar.
- Verificações: 12 testes SQLite; os mesmos 12 fluxos em PostgreSQL real com schemas descartáveis, mais regressão de upload atômico repetida após ajuste. Checagens de sintaxe JS/diff/UTF-8. Playwright local: fluxo de visitante até cadastro/login/pedido/histórico/perfil/permissões, carrinho restaurado, WhatsApp interceptado (sem envio), larguras 360/390/768/1440 sem overflow e sem pageerror.
- Evidência local ignorada: output/playwright e .playwright-cli. Há SQLite sintético em output/browser.db. Não confundir com dados reais. Testes reais usam schemas test_<uuid> e removem ao concluir.
- Publicação e verificação pública ainda pendentes nesta etapa; atualizar após deploy.
- Limites: não garante zero bugs/100% uptime; não testado envio efetivo no aplicativo WhatsApp, aparelho físico ou carga prolongada. Neon Free pode suspender computação ociosa e retomar no acesso. Não foram migrados dados/fotos de instalações externas, pois não foram fornecidos.
