/* Fit real text against reviewed regions. Never hide or truncate copy. */
window.STICKER_FIT=(host,id)=>{
 const n=[...host.querySelector('[data-sticker-node=world] .sc').children].filter(e=>e.classList.contains('e'));
 const fit=(e,width,min)=>{
  if(!e)return;e.style.width='max-content';if(getComputedStyle(e).display==='inline')e.style.display='inline-block';const initial=e.dataset.typeBase||parseFloat(getComputedStyle(e).fontSize);e.dataset.typeBase=initial;
  let size=+initial;e.style.fontSize=size+'px';
  while(e.scrollWidth>width+1&&size>min){size=Math.max(min,size-1);e.style.fontSize=size+'px';}
  if(e.scrollWidth>width+1)throw Error('Text does not fit '+id+' at readable minimum '+min+'px; shorten input or choose another group');
 };
 if(id==='keyword-to-conclusion'){fit(n[0]?.querySelector('.w'),432,32);const lines=n[1]?.firstElementChild?.children;if(lines){fit(lines[0],1100,28);fit(lines[1],1100,72);}}
 if(id==='prepared-to-reuse'){
  for(const row of [n[1],n[6]]){const body=row?.firstElementChild;if(body){const base=body.style.width;body.style.width='max-content';for(const child of body.children)fit(child,310,22);if(body.scrollWidth>1020)throw Error('Tool row exceeds 1020px; shorten labels');body.style.width=base;}}
  fit(n[0]?.querySelector('.ht'),840,44);fit(n[4]?.firstElementChild,420,22);fit(n[7]?.firstElementChild,760,44);
 }
 if(id==='feedback-to-update'){
  fit(n[0]?.firstElementChild,1000,44);for(const e of n.slice(1,4))fit(e.firstElementChild,340,32);
  const children=n[4]?.firstElementChild?.children;if(children){fit(children[0],400,18);fit(children[1],400,28);fit(children[2],220,20);}
 }
};
