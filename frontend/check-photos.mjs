import {chromium} from '@playwright/test';
import assert from 'node:assert/strict';
const browser=await chromium.launch({channel:'chrome',headless:true});
try{
const page=await browser.newPage();await page.goto('http://127.0.0.1:5183/login');await page.locator('[name=email]').fill('chef@damassa.com');await page.locator('[name=password]').fill('local-motion-check');await page.locator('button[type=submit]').click();await page.waitForURL('**/chef');
await page.locator('.chef-item-card').first().getByRole('button',{name:'Adicionar foto',exact:true}).click();assert.ok(await page.locator('#editFile').isVisible());await page.locator('#editFile').setInputFiles('output/test-dish.png');await page.locator('#editPreview').waitFor({state:'visible'});await page.locator('#editForm button[type=submit]').click();await page.waitForURL('**/chef');
assert.ok(await page.locator('.chef-item-card').first().getByRole('button',{name:'Trocar foto',exact:true}).isVisible());
const client=await browser.newContext();const publicPage=await client.newPage();await publicPage.goto('http://127.0.0.1:5183/cardapio');const photo=publicPage.locator('.card-photo img').first();await photo.waitFor();await publicPage.waitForFunction(()=>document.querySelector('.card-photo img')?.naturalWidth>0);const before=await photo.getAttribute('style');await publicPage.waitForFunction(style=>document.querySelector('.card-photo img').getAttribute('style')!==style,before);await publicPage.screenshot({path:'output/playwright/photo-public.png',fullPage:true});console.log('PASS chef upload UI, preview, save, anonymous photo load and animated zoom');await client.close();
}finally{await browser.close()}
