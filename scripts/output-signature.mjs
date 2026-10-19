/** Fixed top-right output-clock / official circle signature, shared by previews and exports. */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

export const signatureAssets = Object.freeze({
  lighter: ['motiongit-circle-lighter.webm', '1a4dc17a2ea86f4cf6b2745b3ee91d89dbae061e812cf78691d2680362776e0d'],
  path: ['motiongit-circle-path.webm', '9e9212233683817eef1ed474a192fbf797700f499839f7c7a3e2b96e1fe5ba8e'],
});

export function signatureWindows(duration) {
  if (!Number.isFinite(duration) || duration <= 0) throw Error('Signature requires a positive output duration');
  if (duration < 14) {
    const end = duration - Math.min(.1, duration * .05);
    const span = Math.min(5.5, end - duration * .5);
    return [{start:end-span,end,fade:Math.min(.4,span/3)}];
  }
  const span = Math.min(5.5, Math.max(duration * .7, duration - .4));
  const start = duration >= 14 ? 8 : Math.max(0, duration - span - Math.min(.5, duration * .1));
  const windows = [];
  for (let at = start; at < duration; at += 30) {
    if (duration >= 14 && at + span > duration + 1e-6) break;
    const end = Math.min(at + span, duration - Math.min(.1, duration * .05));
    if (end > at) windows.push({ start: at, end, fade: Math.min(.4, (end - at) / 3) });
  }
  return windows;
}

/** Existing small header labels alternate with the official mark, on the output clock.
 * The opening label uses the otherwise empty lead-in; subsequent labels recur
 * every 30 seconds, halfway between mark windows. Never infer scene titles. */
export function signatureLabelWindows(duration) {
  const marks = signatureWindows(duration);
  const windows = [];
  const add = (start, end) => {
    if (end > start) windows.push({start, end, fade: Math.min(.4, (end-start)/3)});
  };
  add(0, Math.min(5.5, Math.max(0, marks[0].start - Math.min(.5,duration*.05))));
  for (let start = marks[0].start + 15; start < duration; start += 30) {
    const end = Math.min(start + 5.5, duration - .1);
    // Avoid a truncated flash at the end of a film.
    if (end - start >= Math.min(3, duration * .25)) add(start, end);
  }
  return windows;
}

const decodedAssetCache = new Map();
function decodeAssets(directory, size, selectedTone) {
  for (const [name, expected] of Object.values(signatureAssets)) {
    if (crypto.createHash('sha256').update(fs.readFileSync(path.join(directory, name))).digest('hex') !== expected) throw Error('Official signature asset changed: ' + name);
  }
  const key = JSON.stringify([path.resolve(directory), size, selectedTone, signatureAssets]);
  if (decodedAssetCache.has(key)) return decodedAssetCache.get(key);
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'motiongit-signature-'));
  const result = {};
  try {
    for (const [tone, [name, expected]] of Object.entries(signatureAssets)) {
      if (tone !== selectedTone) continue;
      const source = path.join(directory, name);
      if (crypto.createHash('sha256').update(fs.readFileSync(source)).digest('hex') !== expected) {
        throw Error('Official signature asset changed: ' + name);
      }
      const target = path.join(temporary, tone);
      fs.mkdirSync(target);
      execFileSync('ffmpeg', ['-v', 'error', '-nostdin', '-threads', '1', '-c:v', 'libvpx-vp9', '-i', source,
        '-an', '-vf', `fps=24,scale=${size}:${size}`, '-frames:v', '144', '-threads:v', '1', path.join(target, '%03d.png')],
      { stdio: ['ignore', 'ignore', 'pipe'], timeout: 60000 });
      result[tone] = fs.readdirSync(target).filter(n => n.endsWith('.png')).sort()
        .map(n => 'data:image/png;base64,' + fs.readFileSync(path.join(target, n)).toString('base64'));
      if (result[tone].length < 132) throw Error('Incomplete signature animation: ' + name);
    }
    if (decodedAssetCache.size >= 4) decodedAssetCache.delete(decodedAssetCache.keys().next().value);
    decodedAssetCache.set(key, result);
    return result;
  } finally {
    fs.rmSync(temporary, { recursive: true, force: true });
  }
}

/** Resolve design metadata once. Never inspect background pixels, including dynamic scenes. */
export function resolveBranding({ branding, theme, templateId } = {}) {
  const value = typeof branding === 'string' ? { variant: branding } : branding;
  if (value != null && (typeof value !== 'object' || Array.isArray(value))) throw Error('Invalid fixed branding configuration');
  if (value?.policy != null && value.policy !== 'fixed') throw Error('Only fixed branding is supported');
  if (value?.variant != null && !['light', 'dark', 'lighter', 'path'].includes(value.variant)) throw Error('Invalid fixed Logo variant');
  let variant = value?.variant;
  let source = variant ? 'explicit' : 'compatible-default';
  const declared = typeof theme === 'object' && theme ? theme.signatureVariant : undefined;
  if (!variant && declared != null) {
    if (!['light', 'dark', 'lighter', 'path'].includes(declared)) throw Error('Invalid template Logo variant');
    variant = declared; source = 'template-theme';
  }
  const id = typeof theme === 'string' ? theme : theme?.id;
  const known = {'dark-tech':'light','dark-console':'light','warm-paper':'dark','bright-poster':'dark','vivid':'light','vivid-poster':'dark',
    'template01-editorial-review':'dark','template02-paper-review':'dark','template04-console':'light',
    'template05-sticker-dark':'light','template05-sticker-light':'dark','template05-sticker-orange':'light'};
  if (!variant && known[id ?? templateId]) { variant = known[id ?? templateId]; source = 'template-theme'; }
  variant = ['dark','path'].includes(variant) ? 'dark' : 'light';
  return Object.freeze({ policy:'fixed', variant, tone:variant === 'dark' ? 'path' : 'lighter',
    positionPreset:'top-right', contrastSupport:'clock-outline-logo-backing', source });
}

/** Public per-production content contract. No template/brand/default copy fallback. */
export function resolveContentHeader(inputs = {}, explicitHeader) {
  const header=explicitHeader ?? inputs.header ?? inputs.timeline?.header ?? inputs.brief?.header;
  const headerField=explicitHeader!=null||inputs.header!=null?'header.shortTitle':inputs.timeline?.header!=null?'timeline.header.shortTitle':'brief.header.shortTitle';
  if(header != null){
    if(typeof header!=='object'||Array.isArray(header)||Object.keys(header).some(k=>!['shortTitle','source'].includes(k))||typeof header.shortTitle!=='string'||!header.shortTitle.trim()||header.shortTitle.length>2000)throw Error('Invalid managed content header');
    const source=header.source ?? {kind:'user-explicit',field:headerField};
    if(!source||Object.keys(source).sort().join()!=='field,kind'||!['user-explicit','assistant-summary','bound-excerpt'].includes(source.kind)||typeof source.field!=='string'||!source.field||source.field.length>256)throw Error('Invalid managed header source');
    return {text:header.shortTitle,source,status:'bound'};
  }
  if(typeof inputs.shortTitle==='string'&&inputs.shortTitle.trim())return {text:inputs.shortTitle,source:{kind:'user-explicit',field:'shortTitle'},status:'bound'};
  const candidates=[];
  const push=(text,field)=>{if(typeof text==='string'&&text.trim())candidates.push({text,field});};
  const walk=(node,field,depth=0)=>{
    if(depth>8||!node||typeof node!=='object')return;
    if(Array.isArray(node)){node.slice(0,32).forEach((v,i)=>typeof v==='string'?push(v,field+'['+i+']'):walk(v,field+'['+i+']',depth+1));return;}
    // Caption halves form one sentence. Never turn "not" / a number / its unit
    // into a separately extracted headline by selecting just the first half.
    if(typeof node.a==='string'&&typeof node.b==='string')push(node.a+node.b,field+'.{a,b}');
    if(typeof node.lead==='string'&&typeof node.payoff==='string')push([node.lead,node.payoff].join(' '),field+'.{lead,payoff}');
    for(const key of ['spokenText','text','originalText','title','headline','sentence','zh','en'])push(node[key],field+'.'+key);
    if(typeof node.line1==='string')push([node.line1,node.line2].filter(v=>typeof v==='string').join(' '),field+'.{line1,line2}');
    for(const [key,value]of Object.entries(node)){
      if(['brand','hud','media','assets','src','source','header','a','b'].includes(key))continue;
      if(value&&typeof value==='object')walk(value,field+'.'+key,depth+1);
      else if(/^(?:text|txt)[_-]?\d+$/.test(key))push(value,field+'.'+key);
    }
  };
  for(const key of ['spokenText','text','originalText','title','headline','sentence'])push(inputs[key],key);
  if(inputs.title&&typeof inputs.title==='object')walk(inputs.title,'title');
  for(const key of ['content','captions','copy','brief','segments','timeline'])walk(inputs[key],key);
  for(const candidate of candidates){
    const value=candidate.text.trim();
    const sentence=value.match(/^[\s\S]*?[。！？!?](?:\s|$)|^[\s\S]*?\.(?:\s|$)/)?.[0].trim()||value;
    if(sentence.length<=2000)return {text:sentence,source:{kind:'bound-excerpt',field:candidate.field},status:'bound'};
  }
  return {text:'',source:null,status:'needs-current-copy'};
}

export async function createSignature(page, options) {
  const { width, height, duration, fps = 60, selector = 'canvas', mode = 'canvas' } = options;
  if (![width, height, fps].every(n => Number.isFinite(n) && n > 0)) throw Error('Invalid signature output geometry');
  const windows = signatureWindows(duration), labelWindows = signatureLabelWindows(duration);
  const directory = options.assets ?? fileURLToPath(new URL('../template/brand/', import.meta.url));
  const design = await page.evaluate(() => {
    const timeline=window.MOTION_INPUTS?.timeline;
    const subtitles=typeof SUBS!=='undefined'&&Array.isArray(SUBS)?SUBS:Array.isArray(window.SUBS)?window.SUBS:[];
    return {branding:timeline?.resolvedBranding,inputs:timeline??{captions:subtitles},subtitleOrigin:timeline?null:'runtime.SUBS',
      theme:window.MK?.T?{id:window.MK.T.id,signatureVariant:window.MK.T.signatureVariant}:undefined};
  });
  const branding = resolveBranding({ branding: options.branding ?? design.branding, theme: options.theme ?? design.theme, templateId: options.templateId });
  let resolvedHeader=resolveContentHeader(options.inputs ?? design.inputs,options.header);
  if(resolvedHeader.status!=='bound'&&options.inputs){
    resolvedHeader=resolveContentHeader(design.inputs);
    if(resolvedHeader.source&&design.subtitleOrigin)resolvedHeader.source.field=resolvedHeader.source.field.replace(/^captions/,design.subtitleOrigin);
  }else if(resolvedHeader.source&&!options.inputs&&design.subtitleOrigin){resolvedHeader.source.field=resolvedHeader.source.field.replace(/^captions/,design.subtitleOrigin);}
  const contentHeader={...resolvedHeader,required:options.requireContentHeader===true};
  const title=contentHeader.text;
  const frames = decodeAssets(directory, Math.max(96, Math.ceil(Math.min(width, height) * .06)), branding.tone);
  await page.evaluate(async data => {
    if (window.__motiongitSignature) throw Error('Duplicate automatic signature layer');
    const { width: W, height: H, selector, mode, windows, labelWindows, fps, frames, sourceHud, branding, title } = data;
    const target = document.querySelector(selector);
    if (!target) throw Error('Signature capture surface is missing: ' + selector);
    const scene = mode === 'canvas' ? target.getContext('2d') : null;
    if (mode === 'canvas' && !scene) throw Error('Signature requires the actual 2D output canvas');
    const scale = Math.min(W, H) / 1080;
    const portrait = H > W, fontSize = (portrait ? 32 : 22) * scale;
    const diameter = 56 * scale, right = (portrait ? 96 : 64) * scale, top = (portrait ? 88 : 52) * scale;
    const slot = { x: W - right - 160 * scale, y: top - 10 * scale, w: 196 * scale, h: 76 * scale };
    const headerHeight=Math.ceil(H*.18);
    const layer = document.createElement('canvas');
    layer.width = W; layer.height = headerHeight;
    layer.dataset.motiongitSignature = 'output-clock-circle/1';
    const ctx = layer.getContext('2d');
    if (sourceHud && window.MOTIONGIT_SOURCE_HUD_ADAPTED !== sourceHud) throw Error('Declared source HUD adaptation was not consumed');
    if (scene) {
      // Composite a separate overlay for screenshots; never alter or restore source pixels.
      layer.style.cssText = 'position:fixed;z-index:2147483646;pointer-events:none';
      document.body.append(layer);
    } else {
      if (getComputedStyle(target).position === 'static') target.style.position = 'relative';
      layer.style.cssText = `position:absolute;left:0;top:0;width:100%;height:${headerHeight/H*100}%;z-index:2147483646;pointer-events:none`;
      target.append(layer);
    }
    const composite = scene ? document.createElement('canvas') : null;
    if (composite) { composite.width=W; composite.height=H; }
    function captureCanvas() {
      if (!scene) throw Error('Direct canvas capture requires a canvas surface');
      const c = composite.getContext('2d'); c.clearRect(0,0,W,H);
      c.drawImage(target,0,0,W,H); c.drawImage(layer,0,0); return composite;
    }
    const images = {};
    for (const [tone, sources] of Object.entries(frames)) {
      images[tone] = await Promise.all(sources.map(src => new Promise((resolve, reject) => {
        const image = new Image(); image.onload = () => resolve(image); image.onerror = () => reject(Error('Signature frame failed')); image.src = src;
      })));
    }
    let outputTime = 0, periodicLabelRole = false, sourceLabelDrawn = false, sourceLabelText = '';
    const envelopeAt = (events, time) => {
      const event = events.find(w => time >= w.start && time < w.end);
      return event ? Math.max(0, Math.min(1, (time-event.start)/event.fade, (event.end-time)/event.fade)) : 0;
    };
    // Suppress only source HUD clocks in the reserved output corner. Scene clocks elsewhere remain unchanged.
    for (const surface of scene ? [target] : target.querySelectorAll('canvas')) {
      if (surface === layer) continue;
      const context = surface.getContext('2d');
      if (!context) continue;
      const original = context.fillText;
      context.fillText = function (text, x, y, ...args) {
        const s = String(text).trim();
        const transform = this.getTransform();
        const gx = transform.a * x + transform.c * y + transform.e;
        const gy = transform.b * x + transform.d * y + transform.f;
        const clock = /^\d{2}:\d{2}:\d{2}(?:[.:]\d+)?$/.test(s) || /^(?:SCALE\s+1:1\s+)?T\+\d/.test(s);
        if (clock && gx > W * .65 && gy < H * .13) return;
        if (!periodicLabelRole) return original.call(this, text, x, y, ...args);
        sourceLabelDrawn = true; sourceLabelText = s;
        const alpha = this.globalAlpha;
        try { this.globalAlpha = 0; return original.call(this, text, x, y, ...args); }
        finally { this.globalAlpha = alpha; }
      };
    }
    const style = document.createElement('style');
    style.textContent = '[data-motiongit-source-clock],#vivid-clock,#vivid-mark{visibility:hidden!important}'; document.head.append(style);
    function hideSourceClocks() {
      if (scene) return;
      const bounds = target.getBoundingClientRect();
      for (const node of target.querySelectorAll('[class*="clock"],[class*="timecode"],#clock,#timecode,#tc,.tc,.time')) {
        const box = node.getBoundingClientRect(), text = node.textContent.trim();
        if (box.left > bounds.left + bounds.width * .65 && box.top < bounds.top + bounds.height * .13 &&
          /^\d{2}:\d{2}(?::\d{2}){0,2}(?:[.:]\d+)?$/.test(text)) node.dataset.motiongitSourceClock = 'true';
      }
    }
    // The source Canvas remains untouched, including clip, transform and transparency.
    function label(draw) {
      const previous = periodicLabelRole;
      try { periodicLabelRole = true; return draw(); } finally { periodicLabelRole = previous; }
    }
    function before(time = outputTime) { outputTime = Math.floor(time * fps + 1e-6) / fps; sourceLabelDrawn=false; sourceLabelText=''; }
    function draw(time) {
      // Quantize to the final output frame; source choreography time is deliberately not used.
      const t = Math.floor(time * fps + 1e-6) / fps;
      outputTime = t;
      const labelOpacity = envelopeAt(labelWindows, t);
      const sourceLabels=[...target.querySelectorAll('[data-motiongit-periodic-label]')];
      // Reuse declared user text in the separately managed safe rail; hud:false
      // can still hide its other components. No new left chapter/HUD is enabled.
      const headerTitle=title;
      for(const node of sourceLabels) node.style.visibility='hidden';
      const event = windows.find(w => t >= w.start && t < w.end);
      const envelope = event ? Math.max(0, Math.min(1, (t - event.start) / event.fade, (event.end - t) / event.fade)) : 0;
      if (scene) {
        const box=target.getBoundingClientRect();
        Object.assign(layer.style,{left:box.left+'px',top:box.top+'px',width:box.width+'px',height:(box.height*headerHeight/H)+'px'});
      }
      const tone = branding.tone, light = tone === 'path';
      ctx.clearRect(0, 0, W, H);
      const centerX = W - right - diameter / 2;
      const labelRight=slot.x-24*scale;
      const targetBox=target.getBoundingClientRect(), outputScale=W/targetBox.width;
      const sourceHeaders=[];
      for(const node of target.querySelectorAll('#vivid-chapter,[data-motiongit-hud="left"],#hud .mk-hud-t')){
        if(node.hasAttribute('data-motiongit-periodic-label')||node.querySelector('[data-motiongit-periodic-label],[data-motiongit-source-clock]'))continue;
        const style=getComputedStyle(node),box=node.getBoundingClientRect();
        if(style.visibility==='hidden'||style.display==='none'||Number(style.opacity)<.002||!box.width||!box.height)continue;
        sourceHeaders.push({x:(box.left-targetBox.left)*outputScale,right:(box.right-targetBox.left)*outputScale,
          y:(box.top-targetBox.top)*outputScale,bottom:(box.bottom-targetBox.top)*outputScale});
      }
      // The reviewed native source has a semantic countdown here. Preserve it,
      // including its source clock; move the whole output group beneath it.
      if(sourceHud==='story-deadline')sourceHeaders.push({x:W*.65,right:W-244*scale,y:52*scale,bottom:104*scale});
      ctx.font=`${fontSize}px ui-monospace, SFMono-Regular, Consolas, monospace`;
      const estimatedTitleWidth=headerTitle?Math.min(520*scale,ctx.measureText(headerTitle).width):0;
      const groupLeft=headerTitle?Math.max((portrait?96:64)*scale,labelRight-estimatedTitleWidth):centerX-diameter/2;
      let groupTop=top;
      for(const box of sourceHeaders)if(box.right+12*scale>groupLeft&&box.x-12*scale<W-right&&box.bottom+12*scale>groupTop&&box.y-12*scale<groupTop+diameter){
        groupTop=Math.max(groupTop,box.bottom+12*scale);
      }
      const centerY=groupTop+diameter/2;
      ctx.save(); ctx.globalAlpha = 1 - envelope;
      ctx.font = `${fontSize}px ui-monospace, SFMono-Regular, Consolas, monospace`;
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.lineWidth = 3 * scale; ctx.strokeStyle = light ? 'rgba(255,255,255,.7)' : 'rgba(0,0,0,.7)';
      ctx.fillStyle = light ? '#20242a' : '#dbe2ea';
      const seconds = Math.floor(t), clock = `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
      ctx.strokeText(clock, centerX, centerY); ctx.fillText(clock, centerX, centerY);
      ctx.restore();
      let headerBox=null, displayTitle=headerTitle;
      if (headerTitle && labelOpacity > 0) {
        ctx.save(); ctx.globalAlpha=labelOpacity;
        ctx.font=`${fontSize}px ui-monospace, SFMono-Regular, Consolas, monospace`;
        ctx.textAlign='right'; ctx.textBaseline='middle';
        ctx.lineWidth=3*scale; ctx.strokeStyle=light?'rgba(255,255,255,.7)':'rgba(0,0,0,.7)';
        ctx.fillStyle=light?'#20242a':'#dbe2ea';
        const labelLeft=(portrait?96:64)*scale;
        const labelCenterY=centerY,maxWidth=Math.min(520*scale,labelRight-labelLeft);
        const measured=ctx.measureText(headerTitle).width;
        const readableSize=Math.max(fontSize*.8,fontSize*Math.min(1,maxWidth/Math.max(1,measured)));
        ctx.font=`${readableSize}px ui-monospace, SFMono-Regular, Consolas, monospace`;
        if(ctx.measureText(displayTitle).width>maxWidth){
          const units=typeof Intl.Segmenter==='function'?[...new Intl.Segmenter(undefined,{granularity:'grapheme'}).segment(headerTitle)].map(u=>u.segment):Array.from(headerTitle);
          while(units.length&&ctx.measureText(units.join('')+'…').width>maxWidth)units.pop();
          displayTitle=units.join('')+'…';
        }
        const actualWidth=ctx.measureText(displayTitle).width;
        headerBox={x:labelRight-actualWidth,right:labelRight,y:labelCenterY-readableSize/2,bottom:labelCenterY+readableSize/2,fontSize:readableSize,safeLeft:labelLeft};
        ctx.strokeText(displayTitle,labelRight,labelCenterY);ctx.fillText(displayTitle,labelRight,labelCenterY);ctx.restore();
      }
      if (event && envelope > 0) {
        const assetTime = (t - event.start) * 5.5 / (event.end - event.start);
        const frame = Math.min(images[tone].length - 1, Math.floor(assetTime * 24));
        ctx.save(); ctx.globalAlpha = .20 * envelope;
        ctx.fillStyle = light ? '#ffffff' : '#10151d';
        ctx.beginPath(); ctx.arc(centerX,centerY,diameter*.51,0,Math.PI*2); ctx.fill();
        ctx.globalAlpha = .52 * envelope;
        ctx.drawImage(images[tone][frame], centerX - diameter / 2, groupTop, diameter, diameter); ctx.restore();
      }
      layer.style.visibility = 'visible';
      window.MOTIONGIT_SIGNATURE_STATE = { time: t, clock, envelope, clockOpacity: 1 - envelope,
        ornamentOpacity: .52 * envelope, groupTop, sourceHeaders, groupBox:{x:groupLeft,right:W-right,y:groupTop,bottom:groupTop+diameter}, labelOpacity, headerTitle, displayTitle, headerBox, headerTitleSource:'current-content-header', corner: 'top-right', tone, diameter, centerX, centerY, clockFontSize: fontSize, rightInset: right, topInset: top, event: event ?? null };
    }
    window.__motiongitSignature = { before, draw, label, slot, scene: !!scene, hideSourceClocks, captureCanvas };
  }, { width, height, duration, fps, selector, mode, windows, labelWindows, frames, sourceHud: options.sourceHud ?? null, branding, title });
  return {
    before: time => page.evaluate(time => window.__motiongitSignature.before(time), time),
    draw: time => page.evaluate(time => { window.__motiongitSignature.hideSourceClocks(); window.__motiongitSignature.draw(time); }, time),
    async frame(time) {
      await page.evaluate(async time => {
        const signature = window.__motiongitSignature;
        signature.before(time);
        await window.renderAt(time);
        if (window.imgWait) await window.imgWait();
        signature.hideSourceClocks(); signature.draw(time);
      }, time);
    },
    receipt: { schema: 'motiongit.output-signature/4-alternating', branding, pixelReads:0, samplingScreenshots:0, width, height, fps, windows, labelWindows, contentHeader, labelPolicy:'current-user-copy-managed-header', corner: 'top-right', shape: 'circle',
      portraitInsetsAt1080: { right: 96, top: 88 }, landscapeInsetsAt1080: { right: 64, top: 52 },
      assets: Object.fromEntries(Object.entries(signatureAssets).map(([tone, [file, sha256]]) => [tone, { file, sha256 }])) },
  };
}
