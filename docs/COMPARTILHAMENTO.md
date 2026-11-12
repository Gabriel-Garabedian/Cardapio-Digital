# Prévia ao compartilhar

Capa gerada com a ferramenta integrada image_gen, sem imagem de referência. Arte ilustrativa, não uma fotografia dos pratos reais. Arquivo: `public/static/images/da-massa-compartilhar-v1.png` (1732 × 908, PNG).

Metadados em `damassa/templates/base.html`. Título: Da Massa — Massas artesanais. Destino canônico: https://damassa-cardapio.vercel.app/menu. Não requer login ou execução de JavaScript.

Para testar, cole o link em uma nova mensagem e aguarde a prévia. O aplicativo decide o formato final e pode manter dados antigos em cache; mensagens já enviadas não necessariamente mudam.

## Prompt usado

Create a polished social link preview cover for an existing Brazilian artisanal pasta restaurant called Da Massa. Use case: ads-marketing. Final asset is a landscape Open Graph banner, exact intended canvas 1200 by 630 pixels, aspect 1.905:1. Strong composition readable in a small WhatsApp link card. Existing brand: very dark espresso brown (#21180e), warm antique gold (#c9a84c), cream (#faf7f0), elegant italic high-contrast serif typography. Left 60 percent: large beautiful gold serif wordmark with EXACT TEXT 'Da Massa', underneath cream text 'Massas artesanais', and smaller text 'Escolha seu prato. Peça pelo WhatsApp.' Right 40 percent: tasteful flat editorial illustration of a swirl of handmade fettuccine on a cream ceramic plate, with two basil leaves and a fork, subtle paper grain, restrained warm lighting. Graphic artwork rather than a photo, so no suggestion that it shows actual restaurant dishes. Premium intimate Italian kitchen feel, generous margins, calm hierarchy, high contrast, no generic website screenshot, no frames, no fake interface, no badges, no ratings, no prices, no extra words, no contact numbers, no WhatsApp logo. All essential text and plate fully within generous safe margins so center cropping preserves meaning.

A geração entregou 1732×908; os metadados declaram as dimensões reais, preservando a proporção solicitada.

## Ícone e prévia leve — atualização 12/11

Usuário informou que a imagem não apareceu no link e pediu ícone com a identidade Da Massa. O favicon anterior estava vazio (`data:,`). A capa PNG de 2.633.966 bytes era acessível por HTTP, mas não houve comprovação de que o WhatsApp a exibisse; o tamanho foi tratado como possível fator, não causa confirmada.

- Novo monograma DM dourado sobre café, criado pela ferramenta integrada image_gen. Exportações de tamanho/formato por Pillow, sem redesenhar o conteúdo.
- Link novo para compartilhar: https://damassa-cardapio.vercel.app/cardapio, servido sem redirecionamento para evitar depender da prévia antiga. `/menu`, links de navegação e demais fluxos preservados.
- Open Graph/Twitter usam `public/static/images/da-massa-icone-v2.jpg`, 600×600, 18.680 bytes.
- Ícones PNG de 32/180/512 em `public/static/icons`, ICO de 16/32/48/64 em `public/favicon.ico` e `public/static/icons/da-massa-v2.ico`.
- A capa anterior continua acessível para links antigos, mas não é a imagem principal dos metadados.
- O aplicativo pode manter cache ou ter a opção de desativar prévias habilitada. Não enviar mensagens para terceiros nem mudar a privacidade do usuário para testar.

### Prompt do ícone

Create one square brand app icon and favicon for Da Massa, an artisanal pasta restaurant in Brazil. It must work as a tiny browser-tab icon and as a clean social-link thumbnail. Logo-brand use case. Square 1:1 canvas, flat vector-like graphic, solid dark espresso brown background #1A1209, warm antique gold #C9A84C foreground. The ONLY text is the monogram 'DM', with D and M together as one beautifully balanced, confident, bold italic serif mark, inspired by classic Italian restaurant typography. Very large letterforms, occupying about 70% of the canvas, generous 15% safe padding. Elegant, minimal, legible and calm. Do not overlap letters so much that they stop reading as D and M. Thick enough strokes to remain readable at 16 pixels. Crisp edges and entirely uniform fills. Absolutely no texture, photo, gradients, shadow, glow, thin flourishes, small text, pasta illustration, utensils, plates, leaves, border, rounded-square outline, watermark or mockup. Full-bleed square with unrounded corners; the browser/platform can crop it as needed.
