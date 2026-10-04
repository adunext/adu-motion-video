/** Actual DOM text geometry at the final font, viewport, DPR and transform.
 * No character-count estimate or cached font fallback can count as a fit pass.
 * Canvas text is explicitly unmeasured and must use its renderer's own bounds.
 */
export async function measureTypography(page, frame, fps) {
  return page.evaluate(({frame,fps})=>{
    const stage=document.querySelector('#stage'),sr=stage.getBoundingClientRect();
    const visible=el=>{let alpha=1;for(let p=el;p;p=p.parentElement){const s=getComputedStyle(p);if(s.display==='none'||s.visibility==='hidden')return false;alpha*=+s.opacity;if(alpha<.98)return false;}return true;};
    const measurements=[],findings=[];
    const scene=window.MACRO_PLAN?.scenes?.find(s=>frame>=(s.output_start_frame??s.startFrame)&&frame<(s.output_end_frame??s.endFrame));
    const shape=r=>({left:r.left-sr.left,top:r.top-sr.top,right:r.right-sr.left,bottom:r.bottom-sr.top,width:r.width,height:r.height});
    for(const el of stage.querySelectorAll('*')){
      if(!visible(el))continue;
      const nodes=[...el.childNodes].filter(n=>n.nodeType===Node.TEXT_NODE&&n.textContent.trim());if(!nodes.length)continue;
      const s=getComputedStyle(el),rs=[];
      for(const node of nodes){const range=document.createRange();range.selectNodeContents(node);rs.push(...range.getClientRects());}
      if(!rs.length)continue;
      const bounds={left:Math.min(...rs.map(r=>r.left)),top:Math.min(...rs.map(r=>r.top)),right:Math.max(...rs.map(r=>r.right)),bottom:Math.max(...rs.map(r=>r.bottom))};
      bounds.width=bounds.right-bounds.left;bounds.height=bounds.bottom-bounds.top;
      const text=nodes.map(n=>n.textContent).join(''),record={frame,time:frame/fps,sceneId:scene?.sceneId,sceneInstanceId:scene?.id,slotIds:Object.entries(scene?.slots??{}).filter(([k,v])=>typeof v==='string'&&v.trim()===text.trim()).map(([k])=>k),text,font:s.font,fontFamily:s.fontFamily,fontSize:s.fontSize,fontReady:document.fonts.check(s.font,text),transform:s.transform,viewport:[innerWidth,innerHeight],dpr:devicePixelRatio,box:shape(bounds),selector:el.dataset.slot||el.className||el.tagName};
      measurements.push(record);
      if(!record.fontReady)findings.push({kind:'font-not-ready',...record});
      if(bounds.right>sr.right+2||bounds.left<sr.left-2||bounds.top<sr.top-2||bounds.bottom>sr.bottom+2)findings.push({kind:'settled-text-outside-stage',...record});
      // Transparent/intentional motion masks are reported with their actual
      // geometry, rather than being silently interpreted as missing words.
      for(let p=el.parentElement;p&&p!==stage;p=p.parentElement){const ps=getComputedStyle(p);if(['hidden','clip'].includes(ps.overflowX)||['hidden','clip'].includes(ps.overflowY)){
        const r=p.getBoundingClientRect();if(bounds.left<r.left-2||bounds.right>r.right+2||bounds.top<r.top-2||bounds.bottom>r.bottom+2){findings.push({kind:'text-intersects-clipping-container',...record,container:shape(r)});break;}
      }}
    }
    const caption=document.querySelector('.native-subtitles');
    if(caption&&visible(caption)){
      const leaves=[...caption.querySelectorAll('.sz,.se')];if(leaves.length){
        const rects=leaves.map(e=>{const r=document.createRange();r.selectNodeContents(e);return r.getBoundingClientRect();}),stroke=Math.max(...leaves.map(e=>parseFloat(getComputedStyle(e).webkitTextStrokeWidth)||0))/2;
        const actual={left:Math.min(...rects.map(r=>r.left))-stroke,top:Math.min(...rects.map(r=>r.top))-stroke,right:Math.max(...rects.map(r=>r.right))+stroke,bottom:Math.max(...rects.map(r=>r.bottom))+stroke};
        const position=CONFIG.subtitlePosition??((CONFIG.height>CONFIG.width)?{bottomRatio:.25,leftRatio:.06,rightRatio:.15}:null);
        if(position&&(actual.bottom>sr.top+sr.height*(1-position.bottomRatio)+.1||actual.left<sr.left+sr.width*position.leftRatio-.1||actual.right>sr.right-sr.width*position.rightRatio+.1))findings.push({kind:'caption-safe-space',frame,box:actual,position});
        const faces=[...stage.querySelectorAll('.cam,.tkc')].filter(visible).map(e=>e.getBoundingClientRect());
        if(faces.some(r=>r.left<actual.right&&r.right>actual.left&&r.top<actual.bottom&&r.bottom>actual.top))findings.push({kind:'caption-presenter-overlap-needs-review',frame,box:actual});
      }
    }
    return {frame,measurements,findings,canvasCount:stage.querySelectorAll('canvas').length,limits:'Actual visible DOM only; glyph fallback, Canvas text, artistic masking and continuous reading still require review.'};
  },{frame,fps});
}
