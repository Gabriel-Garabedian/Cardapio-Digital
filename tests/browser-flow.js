async (page) => {
  const base = new URL(page.url()).origin;
  await page.context().clearCookies();
  await page.evaluate(() => sessionStorage.clear());
  await page.goto(base + '/menu');
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const check = (condition, message) => { if (!condition) throw new Error(message); };
  const sizes = [360, 390, 768, 1440];
  for (const width of sizes) {
    await page.setViewportSize({ width, height: 900 });
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Overflow em ${width}px`);
    const cards = await page.locator('.cat-section.active .menu-card').evaluateAll(elements => elements.map(element => {
      const rect = element.getBoundingClientRect();
      return { x: rect.x, y: rect.y, width: rect.width, visible: getComputedStyle(element).opacity === '1' };
    }));
    check(cards.every(card => card.visible), `Pratos ocultos em ${width}px`);
    check(width >= 700 ? cards[0].y === cards[1].y : cards[0].y < cards[1].y, `Grade incorreta em ${width}px`);
    check(await page.locator('.cat-section.active .btn-add-cart').first().evaluate(element => element.getBoundingClientRect().height >= 44), 'Botão de adicionar pequeno para toque');
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole('button', { name: 'Gnocchi (Nhoque)', exact: true }).click();
  const picker = page.locator('.sauce-picker[data-item-id="5"]');
  check(await picker.locator('option:disabled').count() > 0, 'Premium sem preço deve ficar indisponível');
  await picker.selectOption('Pomodoro');
  await page.locator('.btn-add-cart[data-id="5"]').click();
  await page.getByRole('button', { name: 'Aumentar quantidade', exact: true }).click();
  check((await page.locator('#cartTotal').textContent()).includes('80,00'), 'Total do carrinho incorreto');
  await page.getByRole('button', { name: 'Finalizar Pedido', exact: true }).click();
  await page.waitForURL('**/login');
  await page.goto(base + '/register');
  const stamp = Date.now();
  const email = `smoke_${stamp}@example.test`;
  await page.locator('[name=full_name]').fill('Teste de funcionamento');
  await page.locator('[name=username]').fill(`smoke_${stamp}`);
  await page.locator('[name=email]').fill(email);
  await page.locator('[name=password]').fill('Smoke-test-12345');
  await page.getByRole('button', { name: 'Criar Conta', exact: true }).click();
  await page.waitForURL('**/login');
  await page.locator('[name=email]').fill(email);
  await page.locator('[name=password]').fill('Smoke-test-12345');
  await page.locator('#btnLogin').click();
  await page.waitForURL('**/menu');
  check(await page.locator('#cartBadge').textContent() === '2', 'Carrinho não restaurado após cadastro e login');
  await page.locator('#cartFab').click();
  await page.getByRole('button', { name: 'Finalizar Pedido', exact: true }).click();
  await page.locator('#ckAddress').fill('Rua de teste');
  await page.locator('#ckNumber').fill('123');
  await page.locator('#ckCity').fill('Recife');
  let whatsapp = '';
  await page.route('https://wa.me/**', async route => {
    whatsapp = route.request().url();
    await route.fulfill({ status: 200, contentType: 'text/html', body: '<p>WhatsApp interceptado pelo teste. Nenhuma mensagem enviada.</p>' });
  });
  await page.getByRole('button', { name: 'Enviar pelo WhatsApp', exact: true }).click();
  await page.waitForURL('https://wa.me/**');
  check(decodeURIComponent(whatsapp).includes('80.00'), 'Link do WhatsApp com total errado');
  await page.goto(base + '/orders');
  check((await page.locator('body').innerText()).includes('Batata Inglesa'), 'Pedido ausente do histórico');
  const orderNumber = await page.locator('.order-id').textContent();
  const cancel = page.getByRole('button', { name: 'Cancelar pedido', exact: true });
  for (const width of [360, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Histórico com overflow em ${width}px`);
    check(await cancel.evaluate(element => element.getBoundingClientRect().height >= 44), 'Cancelamento pequeno para toque');
  }
  await page.screenshot({ path: 'output/playwright/orders-cancel-desktop.png', fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  page.once('dialog', dialog => dialog.dismiss());
  await cancel.click();
  check(await cancel.isVisible(), 'Desistir da confirmação alterou o pedido');
  page.once('dialog', dialog => dialog.accept());
  await cancel.click();
  await page.locator('.order-card.status-cancelado').waitFor();
  check(await cancel.count() === 0, 'Pedido cancelado ainda oferece cancelamento');
  await page.reload();
  check(await page.locator('.order-id').textContent() === orderNumber, 'Identificador do pedido foi alterado');
  check(await page.locator('.order-status-badge').innerText() === 'Cancelado', 'Cancelamento não persistiu');
  await page.screenshot({ path: 'output/playwright/orders-canceled-mobile.png', fullPage: true });
  await page.goto(base + '/profile');
  check(await page.locator('[name=full_name]').inputValue() === 'Teste de funcionamento', 'Perfil inválido');
  await page.goto(base + '/chef');
  check(new URL(page.url()).pathname === '/menu', 'Cliente conseguiu acessar painel do chef');
  check(errors.length === 0, `Erros JavaScript: ${errors.join(', ')}`);
  await page.screenshot({ path: 'output/playwright/menu-mobile.png', fullPage: true });
  console.log(JSON.stringify({ ok: true, base, email, viewports: sizes, javascriptErrors: errors, whatsappIntercepted: true, cancellationVerified: true }));
}
