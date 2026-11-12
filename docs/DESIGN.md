# Ajuste básico do Da Massa — 12/11/2026

Pedido: reduzir a aparência genérica e o excesso de emojis, preservando o cardápio existente.

- Paleta existente: café #1A1209, marrom #3D2B1F, dourado #C9A84C, creme #FAF6F0, branco #FFF9F3. Dourado em fundos escuros/detalhes; texto monetário marrom sobre claro, com contraste legível.
- Tipografia: Playfair Display na marca e títulos; DM Sans na leitura e nos controles. Menos caixa alta e espaçamento artificial entre letras.
- Cabeçalho tipográfico amplo, sem emojis flutuantes, partículas ou brilho. Identificação direta do chef.
- Cards sem espaços vazios quando não há foto. Fotos reais continuam disponíveis quando cadastradas. Nome e preço no corpo, grade de duas colunas no desktop e uma no celular.
- Carrinho, checkout, login, perfil e painel usam texto e SVG simples. Controles principais com área de toque de pelo menos 44px, foco visível e respeito a movimento reduzido.
- Sem novas bibliotecas, sem novos produtos/preços, sem substituir fotos reais pela capa ilustrativa. A prévia de compartilhamento existente permanece.

Frontend Design e UI/UX Pro Max aplicadas; agente de design fez revisão somente leitura e outro agente cuidou dos templates/JS. CSS e integração sob responsabilidade do agente principal. Plugin Vercel utilizado para conferir publicação. Evidências visuais em output/playwright, ignoradas pelo Git.

## Revisão para desktop

Usuário rejeitou o degradê e a composição com aparência restrita ao celular. Frontend Design e Design Taste aplicadas; agente de design revisou screenshots de 1440, 1920 e 390px sem apontar bloqueadores.

- Transição plana entre café e creme, sem faixa borrada. Cabeçalho dividido em duas colunas no desktop: título grande à esquerda e explicação/ação à direita.
- Conteúdo alinhado em uma largura útil de 1280px. Acima de 1099px, categorias na lateral e catálogo de duas colunas. No tablet, categorias horizontais; abaixo de 700px, uma coluna e cabeçalho empilhado.
- Cards com nomes, preços e controles maiores; botões compactos no desktop e largos no celular. Sombra do carrinho somente quando aberto, eliminando a faixa escura na borda da página.
- Entrada discreta de 500ms no título e 320ms na categoria, deslocamento de 8px. Movimento reduzido continua respeitado no CSS e na rolagem horizontal.

Design Taste: direção split-stage, seed 464483306, preservando paleta e fontes da marca. Sem fotografias inventadas para os produtos. Inspector no navegador em 1440/768/390 encerrou com zero FAIL e três WARN avaliados: creme é a paleta existente; título grande é intencional no cabeçalho público do restaurante; espaço de 54px no card mais curto mantém ações alinhadas ao pé da mesma linha. Relatório e screenshots em output/taste/inspect (ignorados).

Verificações: tests/browser-motion.js em 360/390/768/1440/1920, sem overflow, categorias laterais no desktop e reduced-motion; tests/browser-flow.js com carrinho, cadastro/login, pedido e histórico em banco local sintético, WhatsApp interceptado sem envio. Não substituem teste em aparelho físico.
