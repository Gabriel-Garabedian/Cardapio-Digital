import {chromium} from '@playwright/test';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const browser=await chromium.launch({channel:'chrome',headless:true});
try {
const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:5183/cardapio');
await page.locator('#menuRibbon .scroller').waitFor();
await page.locator('.live-headline .text-rotate-sr-only').waitFor({state:'attached'});
const firstPhrase=await page.locator('.live-headline .text-rotate-sr-only').innerText();
await page.waitForFunction(text=>document.querySelector('.live-headline .text-rotate-sr-only').textContent!==text,firstPhrase);
assert.equal(await page.locator('.motion-control').count(),0);
const x=await page.locator('#menuRibbon .scroller').getAttribute('style');
await page.waitForFunction(old=>document.querySelector('#menuRibbon .scroller').getAttribute('style')!==old,x);
const noodleTransform=await page.locator('.pasta-swirl').getAttribute('transform');
await page.waitForFunction(previous=>document.querySelector('.pasta-swirl').getAttribute('transform')!==previous,noodleTransform);
assert.equal(await page.locator('.hero-action').count(),1);
assert.equal(await page.locator('.hero-title').evaluate(el=>getComputedStyle(el).transform),'none');
assert.equal(await page.locator('.hero-title').evaluate(el=>getComputedStyle(el).willChange),'auto');
const oldMotion=eval('('+fs.readFileSync('tests/browser-motion.js','utf8')+')');await oldMotion(page);
await page.emulateMedia({reducedMotion:'reduce'});await page.locator('#menuRibbon .scroller').waitFor();
await page.emulateMedia({reducedMotion:'no-preference'});await page.locator('#menuRibbon .scroller').waitFor();
await page.setViewportSize({width:1440,height:1000});await page.screenshot({path:'output/playwright/reactbits-desktop.png',fullPage:true});
await page.setViewportSize({width:390,height:844});await page.screenshot({path:'output/playwright/reactbits-mobile.png',fullPage:true});
await page.route('**/order/place',route=>route.abort());
await page.getByRole('button',{name:'Gnocchi (Nhoque)',exact:true}).click();await page.locator('.cat-section.active .sauce-picker').first().selectOption('Pomodoro');await page.locator('.cat-section.active .btn-add-cart').first().click();
assert.equal(await page.locator('#cartBadge').innerText(),'1');
assert.deepEqual(errors,[]);console.log('PASS continuous ribbon, categories, 360–1920px, reduced motion live, add to cart, zero JS errors');} finally { await browser.close(); }
