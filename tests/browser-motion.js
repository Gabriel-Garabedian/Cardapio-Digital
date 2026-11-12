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
  for (const width of [360, 390, 768, 1440, 1920]) {
    await page.setViewportSize({ width, height: 844 });
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Overflow em ${width}px`);
    check(await page.locator('.category-nav').evaluate(element => getComputedStyle(element, '::after').backgroundImage === 'none'), 'Faixa de degradê antiga ainda presente');
    if (width >= 1100) {
      const sidebar = await page.locator('.category-nav').boundingBox();
      const catalog = await page.locator('.menu-body').boundingBox();
      check(sidebar.x + sidebar.width < catalog.x, 'Categorias não estão na lateral do desktop');
      check(catalog.width >= 900, 'Catálogo estreito no desktop');
      check(await page.locator('.hero-title').evaluate(element => parseFloat(getComputedStyle(element).fontSize) >= 88), 'Cabeçalho com escala de celular no desktop');
    }
    check(await page.locator('.cat-section.active .btn-add-cart').first().isVisible(), 'Pratos inacessíveis');
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: 'output/playwright/menu-rework-mobile.png' });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.screenshot({ path: 'output/playwright/menu-rework-desktop.png' });
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.screenshot({ path: 'output/playwright/menu-desktop-wide.png' });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.getByRole('button', { name: 'Lasanhas', exact: true }).click();
  check(await page.locator('.cat-section.active').evaluate(element => getComputedStyle(element).animationName === 'none'), 'Movimento reduzido não respeitado');
  check(await page.locator('.hero-content').evaluate(element => getComputedStyle(element).animationName === 'none'), 'Entrada do cabeçalho ignora movimento reduzido');
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  check(errors.length === 0, errors.join(', '));
}
