/* Preview-only placeholders: never used by build/import/export. */
(()=>{'use strict';
const base=new URL('../',location.href);
const media=v=>new URL(/noise/i.test(v)?'noise.svg':/demo-presenter|talk|face/i.test(v)?'presenter.svg':'evidence.svg',base).href;
const image=Object.getOwnPropertyDescriptor(HTMLImageElement.prototype,'src');
Object.defineProperty(HTMLImageElement.prototype,'src',{...image,set(v){image.set.call(this,media(String(v)));}});
const html=Object.getOwnPropertyDescriptor(Element.prototype,'innerHTML');
Object.defineProperty(Element.prototype,'innerHTML',{...html,set(v){html.set.call(this,rewrite(String(v)).replace(/(<img\b[^>]*\bsrc\s*=\s*)(["'])(.*?)\2/gi,(_,a,q,s)=>a+q+media(s)+q));}});
const css=Object.getOwnPropertyDescriptor(CSSStyleDeclaration.prototype,'cssText');
const rewrite=v=>String(v).replace(/url\((["']?)([^)]+?)\1\)/gi,(all,q,s)=>/\.(png|jpg|jpeg|webp|svg)(\?|$)/i.test(s)?'url("'+media(s)+'")':all);
Object.defineProperty(CSSStyleDeclaration.prototype,'cssText',{...css,set(v){css.set.call(this,rewrite(v));}});
const bg=Object.getOwnPropertyDescriptor(CSSStyleDeclaration.prototype,'backgroundImage');
if(bg?.set)Object.defineProperty(CSSStyleDeclaration.prototype,'backgroundImage',{...bg,set(v){bg.set.call(this,rewrite(v));}});
})();
