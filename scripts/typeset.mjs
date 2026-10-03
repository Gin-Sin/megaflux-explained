// Render math before publication: HTML for sighted readers, MathML for assistive
// technology. No runtime renderer or CDN is needed; no-JS reading is preserved.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import katex from 'katex';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const assets=path.join(root,'site/assets/katex');
fs.mkdirSync(assets,{recursive:true});
const dist=path.join(root,'node_modules/katex/dist');
fs.copyFileSync(path.join(dist,'katex.min.css'),path.join(assets,'katex.min.css'));
fs.cpSync(path.join(dist,'fonts'),path.join(assets,'fonts'),{recursive:true});
fs.copyFileSync(path.join(root,'node_modules/katex/LICENSE'),path.join(assets,'LICENSE'));
const manifest=[];
for(const [source,target] of [['content/article.html','site/index.html'],['content/storyboard.html','site/storyboard.html']]) {
  let html=fs.readFileSync(path.join(root,source),'utf8');
  const expressions=[];
  html=html.replace(/<math-(inline|block)>([\s\S]*?)<\/math-\1>/g,(_,mode,encoded)=>{
    const tex=encoded.replaceAll('&amp;','&').replaceAll('&gt;','>').replaceAll('&lt;','<');
    const display=mode==='block';
    const rendered=katex.renderToString(tex,{displayMode:display,output:'htmlAndMathml',throwOnError:true,strict:'error',trust:false});
    expressions.push({mode,tex});
    return display?`<div class="math-display" tabindex="0">${rendered}</div>`:`<span class="math-inline">${rendered}</span>`;
  });
  if(!html.includes('assets/katex/katex.min.css'))html=html.replace('<link rel="stylesheet" href="style.css">','<link rel="stylesheet" href="assets/katex/katex.min.css"><link rel="stylesheet" href="style.css">');
  // Existing readers should get the new typography and movies immediately.
  html=html.replace(/(href|src|poster)="(style\.css|app\.js|assets\/[^"?]+\.(?:mp4|png))"/g,'$1="$2?v=20261003-fonts2"');
  fs.writeFileSync(path.join(root,target),html);
  manifest.push({page:target,expressions});
  console.log(`Typeset ${expressions.length} expressions in ${target}`);
}
fs.writeFileSync(path.join(root,'site/assets/math-audit.json'),JSON.stringify(manifest,null,2));
