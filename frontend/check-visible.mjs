import {chromium} from '@playwright/test';
import assert from 'node:assert/strict';
const browser=await chromium.launch({channel:'chrome',headless:true});
const page=await browser.newPage({viewport:{width:1280,height:800},recordVideo:{dir:'output/playwright/motion-v3',size:{width:1280,height:800}}});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:5183/cardapio');
await page.locator('.live-headline .text-rotate-sr-only').waitFor({state:'attached'});
const phrases=[];for(let i=0;i<3;i++){const text=await page.locator('.live-headline .text-rotate-sr-only').innerText();phrases.push(text);await page.waitForFunction(t=>document.querySelector('.live-headline .text-rotate-sr-only').textContent!==t,text)}
await page.screenshot({path:'output/playwright/motion-v3-desktop.png'});
assert.equal(await page.locator('.motion-control').count(),0);
await page.setViewportSize({width:390,height:844});await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'output/playwright/motion-v3-mobile.png'});
assert.deepEqual(errors,[]);console.log(JSON.stringify({phrases,automaticMotionWithoutControls:'PASS',errors}));const video=page.video();await page.close();await video.saveAs('output/playwright/motion-v3.webm');await browser.close();
