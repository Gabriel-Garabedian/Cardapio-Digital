# Movimento do cardápio

React Bits (`ScrollVelocity`, `Magnet`, `RotatingText` e `CircularText`) integrado em pequenas ilhas React no cardápio Flask. GSAP controla os detalhes de comida, fotos e interação dos cards. O título principal fica estável após uma entrada de opacidade. Sem mudanças no carrinho, cadastro ou checkout.

Na raiz do repositório:

```powershell
npm ci --prefix frontend
npm --prefix frontend run build
```

O build gera `public/static/js/menu-motion.js`, `menu-motion.css` e `react-bits-LICENSE.txt`, versionados para o deploy Flask funcionar sem Node no servidor. Sempre reconstruir após editar `frontend/`.

Animações ativas por padrão; o padrão é movimento completo, inclusive com prefers-reduced-motion do sistema; o link no rodapé abre a alternativa explícita ?motion=reduce. A faixa tem conteúdo estático antes do JavaScript carregar. A aplicação continua funcionando se o bundle não carregar.

Componentes copiados de `DavidHDev/react-bits`; licença em `react-bits/LICENSE.md`. Versões das dependências fixadas no lockfile.

Com um servidor Flask **local de teste** em `127.0.0.1:5183` e banco sintético:

```powershell
node frontend/check.mjs
node frontend/check-flow.mjs
```

O segundo teste cria cadastro e pedido sintéticos e testa cancelamento. Não executar contra produção. O WhatsApp é interceptado.

Componentes adicionais: RotatingText e CircularText. As cópias de ScrollVelocity/RotatingText/CircularText delegam movimento reduzido ao pai. Animações são automáticas e não há botão para ativar/pausar; a alternativa acessível fica em ?motion=reduce, sem redução automática pela configuração do navegador.

Para verificar início automático com movimento reduzido: `node frontend/check-reduced.mjs`. O teste só faz leituras e aceita MOTION_URL para conferir o endereço publicado.
