# Ajuste básico do Da Massa — 12/11/2026

Pedido: reduzir a aparência genérica e o excesso de emojis, preservando o cardápio existente.

- Paleta existente: café #1A1209, marrom #3D2B1F, dourado #C9A84C, creme #FAF6F0, branco #FFF9F3. Dourado em fundos escuros/detalhes; texto monetário marrom sobre claro, com contraste legível.
- Tipografia: Playfair Display na marca e títulos; DM Sans na leitura e nos controles. Menos caixa alta e espaçamento artificial entre letras.
- Hero mais compacto, sem emojis flutuantes, partículas ou brilho. Identificação direta do chef.
- Cards sem espaços vazios quando não há foto. Fotos reais continuam disponíveis quando cadastradas. Nome e preço no corpo, grade de duas colunas no desktop e uma no celular.
- Carrinho, checkout, login, perfil e painel usam texto e SVG simples. Controles principais com área de toque de pelo menos 44px, foco visível e respeito a movimento reduzido.
- Sem novas bibliotecas, sem novos produtos/preços, sem substituir fotos reais pela capa ilustrativa. A prévia de compartilhamento existente permanece.

Frontend Design e UI/UX Pro Max aplicadas; agente de design fez revisão somente leitura e outro agente cuidou dos templates/JS. CSS e integração sob responsabilidade do agente principal. Plugin Vercel utilizado para conferir publicação. Evidências visuais em output/playwright, ignoradas pelo Git.

## Ajuste pedido em seguida

Usuário pediu uma animação como havia antes e um degradê entre cabeçalho marrom e área clara do cardápio. Entrada discreta de500ms no hero e320ms na categoria, deslocamento8px, sem ocultação permanente. Transição marrom/creme44px abaixo da navegação com espaço reservado para não cobrir os títulos. Hover com sombra leve. Preferência de movimento reduzido respeitada por CSS e pela rolagem horizontal. Verificação em tests/browser-motion.js.
