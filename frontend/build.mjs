import {build} from 'esbuild';
import {fileURLToPath} from 'node:url';
import {copyFile} from 'node:fs/promises';
process.chdir(fileURLToPath(new URL('..',import.meta.url)));
await build({absWorkingDir:process.cwd(),entryPoints:['frontend/menu-motion.jsx'],bundle:true,minify:true,jsx:'automatic',format:'iife',target:['es2020'],outfile:'public/static/js/menu-motion.js',legalComments:'eof',banner:{js:'/*! React Bits components by David Haz. License: /static/js/react-bits-LICENSE.txt */'},define:{'process.env.NODE_ENV':'"production"'}});
await copyFile('frontend/react-bits/LICENSE.md','public/static/js/react-bits-LICENSE.txt');
