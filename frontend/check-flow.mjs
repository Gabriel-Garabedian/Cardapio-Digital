import {chromium} from '@playwright/test';
import fs from 'node:fs';
const browser=await chromium.launch({channel:'chrome',headless:true});
try{const page=await browser.newPage();await page.goto('http://127.0.0.1:5183/cardapio');await page.locator('#menuRibbon .scroller').waitFor();await eval('('+fs.readFileSync('tests/browser-flow.js','utf8')+')')(page)}finally{await browser.close()}
