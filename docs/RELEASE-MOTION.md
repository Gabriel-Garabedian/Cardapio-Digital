# Animações e fotos dos pratos

Destino: projeto existente `damassa-cardapio`, domínio `damassa-cardapio.vercel.app`, repositório `Gabriel-Garabedian/Cardapio-Digital`. Produção acompanha a branch `master`; a preparação está em `codex/menu-reactbits-motion`. Este documento não indica publicação realizada.

## Conteúdo

- React Bits e GSAP no cardápio, com início automático, sem controle manual, e preferência de movimento reduzido. Título principal estável após entrada suave.
- Botões Adicionar foto/Trocar foto no painel do chef, seleção de arquivo acessível, prévia e zoom lento nas fotos públicas.
- Fotos e dados continuam no armazenamento existente. Nenhuma migração ou alteração de variáveis de ambiente necessária.
- Nenhuma foto real foi cadastrada nesta entrega; o chef precisa enviar as imagens dos pratos.

## Build

Na raiz:

```powershell
npm ci --prefix frontend
npm --prefix frontend run build
```

Os artefatos `public/static/js/menu-motion.js`, `menu-motion.css` e `react-bits-LICENSE.txt` são versionados. O deploy Flask utiliza esses arquivos diretamente, sem executar Node. Não enviar `.env`, bancos locais, `output/` ou `node_modules/`.

## Verificação e publicação

17 testes Python passaram, incluindo armazenamento da foto, troca da imagem e acesso anônimo. Chrome local verificou animações automáticas, 360–1920 px, cadastro, carrinho, pedido e cancelamento; WhatsApp interceptado e banco sintético. O envio de foto pelo painel e exibição anônima também foram testados. Desempenho em celular físico não foi medido.

Antes da integração, conferir que `origin/master` não avançou; se avançar, integrar e verificar o diff resultante. Publicar o commit revisado pela integração Git existente. Não criar novo projeto nem substituir configurações de banco.

Após deploy READY, conferir `/cardapio`, os três artefatos acima, `/login` e prévia de compartilhamento. Não cadastrar pedidos ou imagens de teste em produção. Rollback pela Vercel para o deployment anterior; esta entrega não migra dados.
