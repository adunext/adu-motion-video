// Measure actual content with loaded fonts, keeping every word and a readable
// floor. Do not shrink the presenter/Canvas/world to accommodate text.
window.VIBRANT_FIT=(host,id)=>{
const root=host.querySelector('[data-vibrant-node=front] .sc');
const n=[...root.children].filter(e=>e.classList.contains('e'));
const fit=(e,width,min)=>{
 if(!e)return;const style=getComputedStyle(e);if(!e.dataset.vibrantBase)e.dataset.vibrantBase=style.fontSize;
 e.style.fontSize=e.dataset.vibrantBase;e.style.width='max-content';
 let size=parseFloat(e.dataset.vibrantBase);
 if(getComputedStyle(e).display==='inline')e.style.display='inline-block';
 while(e.scrollWidth>width+1&&size>min){size=Math.max(min,size-1);e.style.fontSize=size+'px';}
 if(e.scrollWidth>width+1)throw Error('Text does not fit '+id+' above '+min+'px; shorten or change group');
};
if(id==='answer-to-question'){fit(n[0].firstChild,900,80);fit(n[1].querySelector('.ht'),800,44);}
if(id==='steps-to-uniformity'){
 const lab=n[0].firstChild;fit(lab,900,18);for(const e of n.slice(1,5))fit(e.firstChild,420,28);
 fit(n[5].firstChild,700,48);fit(n[6].firstChild,940,90);fit(n[7].firstChild,880,32);
}
if(id==='echo-focus'){for(const e of n[0].firstChild.children)fit(e,960,110);fit(n[1].firstChild,920,36);}
if(id==='cost-to-verdict'){
 fit(n[0].firstChild,700,18);for(const e of n.slice(1,4)){fit(e.firstChild.children[0],250,18);fit(e.firstChild.children[1],250,26);}
 fit(n[4].firstChild,940,130);fit(n[5].querySelector('.ht'),900,44);const row=n[6].firstChild.firstChild;
 fit(row.firstChild,690,18);
}
const lines=(e,height,min)=>{
 if(!e.dataset.vibrantBase)e.dataset.vibrantBase=getComputedStyle(e).fontSize;
 let size=parseFloat(e.dataset.vibrantBase);e.style.fontSize=size+'px';
 while((e.scrollHeight>height+1||e.scrollWidth>e.clientWidth+1)&&size>min){size=Math.max(min,size-1);e.style.fontSize=size+'px';}
 if(e.scrollHeight>height+1||e.scrollWidth>e.clientWidth+1)throw Error('Paragraph does not fit '+id+' at '+min+'px; reduce copy or choose another scene');
};
if(id==='basic-keyword'){for(const e of n[0].firstChild.children)fit(e,740,72);lines(n[1].firstChild,220,32);}
if(id==='basic-points'){fit(n[0].querySelector('.ht'),900,44);for(const e of n.slice(1,3))lines(e.querySelector('span'),170,30);}
if(id==='basic-summary'){lines(n[0].firstChild,270,48);lines(n[1].firstChild,310,32);}
};
