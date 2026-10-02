import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const flush = () => new Promise(resolve => setImmediate(resolve));
function fixture() {
  const elements = new Map(), windowEvents = {}, documentEvents = {};
  const element = () => ({hidden: false, textContent: '', handlers: {},
    addEventListener(name, fn) { this.handlers[name] = fn; },
    load() { this.currentSrc = this.src; }});
  let current = {schema:'adu-preview-delivery/1',version:'a'.repeat(64),
    media:`video-${'a'.repeat(64)}.mp4`,title:'First delivery'};
  const context = {URL,location:{href:'http://127.0.0.1:8912/preview/index.html'},
    setInterval(fn) { context.poll = fn; },
    document:{hidden:false,getElementById(id) {
      if (!elements.has(id)) elements.set(id, element()); return elements.get(id);
    }, addEventListener(name, fn) { documentEvents[name] = fn; }},
    async fetch(url, options) {
      assert.equal(options.cache, 'no-store');
      assert.equal(String(url), 'http://127.0.0.1:8912/preview/delivery.json');
      return {ok:true,json:async()=>structuredClone(current)};
    }, addEventListener(name, fn) { windowEvents[name] = fn; }};
  context.window = context;
  vm.runInNewContext(fs.readFileSync(new URL('../scripts/preview_player.js',import.meta.url),'utf8'),context);
  return {context, elements, windowEvents, documentEvents, set(record) { current = record; }};
}

test('open tab detects a new delivery without silently replacing playback', async () => {
  const f = fixture(); await flush();
  const oldSrc = f.elements.get('video').currentSrc;
  assert.match(oldSrc, /video-a{64}\.mp4$/);
  f.set({schema:'adu-preview-delivery/1',version:'b'.repeat(64),media:`video-${'b'.repeat(64)}.mp4`,title:'New delivery'});
  f.windowEvents.focus(); await flush();
  assert.equal(f.elements.get('video').currentSrc, oldSrc);
  assert.equal(f.elements.get('notice').hidden, false);
  assert.equal(f.elements.get('status').textContent, '正在显示旧版本');
  f.elements.get('update').handlers.click();
  assert.match(f.elements.get('video').currentSrc, /video-b{64}\.mp4$/);
  assert.equal(f.elements.get('download').href, f.elements.get('video').currentSrc);
  assert.match(f.elements.get('version').textContent, /bbbbbbbbbbbb/);
});

test('malformed version and mismatched actual media cannot claim newest delivery', async () => {
  const f = fixture(); await flush();
  f.elements.get('video').currentSrc = 'http://127.0.0.1:8912/old.mp4';
  f.windowEvents.focus(); await flush();
  assert.equal(f.elements.get('status').textContent, '版本未确认');
  assert.match(f.elements.get('message').textContent, /实际播放地址/);
  f.set({schema:'adu-preview-delivery/1',version:'b'.repeat(64),media:'old.mp4'});
  f.context.poll(); await flush();
  assert.equal(f.elements.get('status').textContent, '版本未确认');
  assert.equal(f.elements.get('update').hidden, true);
});

test('visible tab checks current manifest after returning from background', async () => {
  const f = fixture(); await flush();
  f.context.document.hidden = true;
  f.set(null); f.context.poll(); await flush();
  assert.notEqual(f.elements.get('status').textContent, '版本未确认');
  f.context.document.hidden = false;
  f.documentEvents.visibilitychange(); await flush();
  assert.equal(f.elements.get('status').textContent, '版本未确认');
});
