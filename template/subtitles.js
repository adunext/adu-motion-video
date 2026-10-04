/* Shared output-clock captions. Preserve text and half-open cue intervals. */
if (typeof SUBS !== 'undefined' && CONFIG.subtitles !== false) (() => {
  const portrait = (CONFIG.height || 1080) > (CONFIG.width || 1920);
  const presets = {
    standard: {top:872, gap:8, zhSize:44, enSize:26, compact:false},
    'large-en': {top:940, gap:6, zhSize:44, enSize:30, compact:true},
  };
  const name = CONFIG.subtitlePreset || 'standard';
  if (!presets[name]) throw Error(`Unknown subtitlePreset: ${name}`);
  const style = {...presets[name], ...(portrait ? {zhSize:46,enSize:30} : {}), ...CONFIG.subtitleStyle};
  const position = CONFIG.subtitlePosition ?? (portrait ? {bottomRatio:.18,leftRatio:.06,rightRatio:.15} : null);
  const width = CONFIG.width || 1920, height = CONFIG.height || 1080;
  const box = document.createElement('div'); box.className='native-subtitles';
  box.dataset.captionClock='final-output';
  box.style.cssText=`position:absolute;display:flex;flex-direction:column;align-items:center;gap:${style.gap}px;pointer-events:none;box-sizing:border-box`;
  // Inline priority deliberately beats frozen legacy portrait stylesheets.
  const set = (k,v) => box.style.setProperty(k,v,'important');
  if (position) {
    for (const key of ['bottomRatio','leftRatio','rightRatio']) if (!Number.isFinite(position[key]) || position[key]<0 || position[key]>=1) throw Error('Invalid subtitlePosition.'+key);
    if (position.leftRatio+position.rightRatio>=.9) throw Error('Insufficient caption width');
    set('top','auto'); set('bottom',`${height*position.bottomRatio}px`);
    set('left',`${width*position.leftRatio}px`); set('right',`${width*position.rightRatio}px`);
  } else { set('top',`${style.top}px`);set('bottom','auto');set('left','0');set('right','0'); }
  set('width','auto');set('max-width','none');
  const ov=document.getElementById('ov');if(!ov)throw Error('Missing caption mount #ov');ov.appendChild(box);
  const create=(text,lang,formatting) => {
    const el=document.createElement('div');el.className=lang==='zh'?'sz':'se';el.lang=lang;
    el.style.cssText=`display:block;box-sizing:border-box;max-width:100%;padding:4px 12px;text-align:center;overflow-wrap:anywhere;color:#fff;background:transparent;paint-order:stroke fill;text-shadow:none`;
    el.style.setProperty('font-size',`${lang==='zh'?style.zhSize:style.enSize}px`,'important');
    el.style.setProperty('line-height','1.28','important');el.style.setProperty('white-space','pre-wrap','important');
    el.style.fontFamily="-apple-system,'PingFang SC',sans-serif";el.style.fontWeight=lang==='zh'?'600':'500';
    el.style.webkitTextStroke=lang==='zh'?'4px rgba(10,10,10,.9)':'2.6px rgba(10,10,10,.85)';
    // Exact literal <, &, line breaks and combining characters; never innerHTML.
    if(formatting==='srt-basic'){
      // Only explicit SRT b/i/u tags; attributes and unknown tags stay literal.
      const stack=[el];for(const token of text.split(/(<\/?[biu]>)/gi)){
        const tag=token.match(/^<(\/?)([biu])>$/i);
        if(!tag){stack.at(-1).append(document.createTextNode(token));continue;}
        const name=tag[2].toLowerCase();
        if(!tag[1]){const child=document.createElement(name);stack.at(-1).append(child);stack.push(child);}
        else if(stack.length>1&&stack.at(-1).tagName.toLowerCase()===name)stack.pop();
        else stack.at(-1).append(document.createTextNode(token));
      }
    }else el.textContent=text;
    box.appendChild(el);return el;
  };
  let key='';
  window.OVERLAY = t => {
    const active=SUBS.filter(g=>t>=g.t0&&t<g.t1);
    if(!active.length){box.style.opacity='0';return;}
    const current=JSON.stringify(active.map(g=>[g.id,g.t0,g.t1,g.zh,g.en,g.formatting]));
    if(current!==key){key=current;box.replaceChildren();for(const g of active){if(g.zh)create(g.zh,'zh',g.formatting);if(g.en)create(g.en,'en',g.formatting);}}
    const first=active[0];const enter=Math.max(0,Math.min(1,(t-first.t0)/.12));
    box.style.opacity='1';
    // Enter upwards: even the translated box remains above the configured bottom.
    const canvasCenter=width/2;
    const dx=position||CONFIG.subtitleXByStart?.[String(first.t0)]===undefined ? 0 : CONFIG.subtitleXByStart[String(first.t0)]-canvasCenter;
    box.style.transform=`translate(${dx}px,${-10*(1-enter)}px)`;
    box.dataset.cueIds=JSON.stringify(active.map(g=>g.id??g.t0));
    const rect=box.getBoundingClientRect();
    box.dataset.fit=rect.top>=0&&rect.bottom<=height&&rect.left>=0&&rect.right<=width?'fits':'overflow';
  };
})();
