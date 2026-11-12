async (page) => {
  const check = (condition, message) => { if (!condition) throw new Error(message); };
  const base = new URL(page.url()).origin;
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await page.goto(base + '/cardapio');
  await page.getByRole('button', { name: 'Gnocchi (Nhoque)', exact: true }).click();
  const animation = await page.locator('.cat-section.active').evaluate(element => ({
    name: getComputedStyle(element).animationName,
    running: element.getAnimations().length > 0
  }));
  check(animation.name === 'menu-enter' && animation.running, 'Animação da categoria não iniciou');
  await page.locator('.cat-section.active').evaluate(element => Promise.all(element.getAnimations().map(animation => animation.finished)));
  for (const width of [360, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 844 });
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Overflow em ${width}px`);
    check(await page.locator('.category-nav').evaluate(element => getComputedStyle(element, '::after').backgroundImage.includes('linear-gradient')), 'Degradê ausente');
    check(await page.locator('.cat-section.active .btn-add-cart').first().isVisible(), 'Pratos inacessíveis');
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: 'output/playwright/menu-gradient-mobile.png' });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.screenshot({ path: 'output/playwright/menu-gradient-desktop.png' });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.getByRole('button', { name: 'Lasanhas', exact: true }).click();
  check(await page.locator('.cat-section.active').evaluate(element => getComputedStyle(element).animationName === 'none'), 'Movimento reduzido não respeitado');
  check(await page.locator('.hero-content').evaluate(element => getComputedStyle(element).animationName === 'none'), 'Entrada do cabeçalho ignora movimento reduzido');
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  check(errors.length === 0, errors.join(', '));
}
