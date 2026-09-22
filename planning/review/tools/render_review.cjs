const fs = require('fs');
const path = require('path');
const { chromium } = require('/Users/apple/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const out=path.resolve(__dirname,'../deliverables/requirements-review');
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const page=await browser.newPage({viewport:{width:1400,height:1000}});
 await page.setContent('<html><meta charset="utf-8"><body></body></html>');
 await page.addScriptTag({path:path.join(__dirname,'vendor/mermaid.min.js')});
 await page.evaluate(()=>mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'base',themeVariables:{fontFamily:'Hiragino Sans, sans-serif',fontSize:'16px',primaryColor:'#e6f2ed',primaryTextColor:'#173f3a',lineColor:'#486f67'},flowchart:{htmlLabels:false,curve:'linear'},er:{useMaxWidth:true}}));
 const list=fs.readdirSync(path.join(out,'diagrams')).filter(x=>x.endsWith('.mmd')&&!x.startsWith('ifdam-'));
 let n=0;
 for(const name of list){
  const source=fs.readFileSync(path.join(out,'diagrams',name),'utf8');
  const svg=await page.evaluate(async ({source,id})=>{const raw=(await mermaid.render(id,source)).svg;const box=document.createElement('div');box.innerHTML=raw;return new XMLSerializer().serializeToString(box.querySelector('svg'));},{source,id:'diagram'+(++n)});
  fs.writeFileSync(path.join(out,'diagrams',name.replace('.mmd','.svg')),svg);
 }
 await page.goto('file://'+path.join(out,'index.html'));
 await page.evaluate(()=>document.fonts.ready);
 const broken=await page.locator('img').evaluateAll(imgs=>imgs.filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src));
 if(broken.length)throw Error('Broken images '+broken);
 await page.screenshot({path:path.join(out,'review-cover.png'),fullPage:false});
 await page.locator('#INT-KARATE-03-01').screenshot({path:path.join(out,'review-flow.png')});
 await page.pdf({path:path.join(out,'要件とIFDAM.pdf'),format:'A4',printBackground:true,margin:{top:'15mm',bottom:'15mm',left:'13mm',right:'13mm'},displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:8px;width:100%;text-align:center;color:#777">空手道場出席アプリ 要件確認版 R001 · <span class="pageNumber"></span> / <span class="totalPages"></span></div>'});
 console.log(JSON.stringify({renderedDiagrams:n,brokenImages:broken,pdf:path.join(out,'要件とIFDAM.pdf')}));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
