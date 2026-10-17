const fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
const out=path.resolve(__dirname,'..'); const mermaidPath=process.argv[2]; if(!mermaidPath)throw Error('Pass the local Mermaid 11.12.0 bundle path as first argument');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 await page.setContent('<html><meta charset="utf-8"><body></body></html>');
 await page.addScriptTag({path:mermaidPath});
 await page.evaluate(()=>mermaid.initialize({startOnLoad:false,securityLevel:'loose',theme:'base',themeVariables:{fontFamily:'Hiragino Sans, sans-serif',fontSize:'17px',lineColor:'#4e6765'},flowchart:{htmlLabels:true,curve:'linear',nodeSpacing:35,rankSpacing:65,padding:25}}));
 const names=fs.readdirSync(path.join(out,'diagrams')).filter(n=>n.endsWith('.mmd'));let i=0;const sizes=[];
 for(const name of names){
  const source=fs.readFileSync(path.join(out,'diagrams',name),'utf8');
  const result=await page.evaluate(async({source,id})=>{
   const result=await mermaid.render(id,source);const div=document.createElement('div');div.innerHTML=result.svg;document.body.append(div);
   const svg=div.querySelector('svg');
   for(const g of svg.querySelectorAll('g.node.function')){
    const old=g.querySelector('.basic.label-container');if(!old)throw Error('Function shape missing '+g.id);
    const b=old.getBBox(),el=document.createElementNS('http://www.w3.org/2000/svg','ellipse');
    for(const a of old.attributes)if(!['x','y','width','height','rx','ry'].includes(a.name))el.setAttribute(a.name,a.value);
    el.setAttribute('cx',b.x+b.width/2);el.setAttribute('cy',b.y+b.height/2);el.setAttribute('rx',b.width/2);el.setAttribute('ry',b.height/2);el.setAttribute('style','fill:#e0f2ec;stroke:#147864;stroke-width:2px');old.replaceWith(el); const label=g.querySelector('g.label'); const lb=label.getBBox(); label.setAttribute('transform',`translate(${-lb.width*.465},${-lb.height*.465}) scale(.93)`);
   }
   svg.style.maxWidth='none';svg.setAttribute('width',svg.viewBox.baseVal.width);svg.setAttribute('height',svg.viewBox.baseVal.height);
   const res={svg:new XMLSerializer().serializeToString(svg),width:svg.viewBox.baseVal.width,height:svg.viewBox.baseVal.height,nodes:[...svg.querySelectorAll('g.node')].map(g=>g.id)};div.remove();return res;
  },{source,id:'r002'+(++i)});
  fs.writeFileSync(path.join(out,'diagrams',name.replace('.mmd','.svg')),result.svg);sizes.push({file:name,width:result.width,height:result.height,nodes:result.nodes});
 }
 fs.writeFileSync(path.join(out,'rendered-sizes.json'),JSON.stringify(sizes,null,2));
 await page.goto('file://'+path.join(out,'index.html'));await page.evaluate(()=>document.fonts.ready);
 const broken=await page.locator('img').evaluateAll(xs=>xs.filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src));if(broken.length)throw Error(broken);
 await page.pdf({path:path.join(out,'IFDAM-R002.pdf'),preferCSSPageSize:true,printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:8px;text-align:center;width:100%;color:#557">IFDAM R002 ・確認用草案・ <span class="pageNumber"></span> / <span class="totalPages"></span></div>'});
 await page.addStyleTag({content:'nav{visibility:hidden}'}); await page.locator('#sheet-03B').screenshot({path:path.join(out,'preview-attendance.png')});
 await browser.close();console.log(JSON.stringify({rendered:names.length,broken,sizes:sizes.map(({file,width,height})=>({file,width,height}))}));
})().catch(e=>{console.error(e);process.exit(1)});
