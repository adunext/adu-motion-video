import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { inventory } from '../scripts/authored_units.mjs';

test('nested authored units retain private helpers and independent closures', () => {
  const source = `(() => { const title='😀源标题'; const offset=3;
    (() => { const s=new Scene(0,10,'white'); s.update=t=>t+offset; s.text=title; S(1,'hit'); })();
    {const s=new Scene(10,20,'black');s.update=t=>t-offset;s.text=title;S(12,'ding');}
  })();`;
  const result = inventory(source);
  assert.equal(result.units.length, 2);
  const scenes = [], sounds = [];
  const context = vm.createContext({ Scene: class { constructor(a,b) {this.a=a;this.b=b;scenes.push(this);} }, S: (...cue)=>sounds.push(cue) });
  for (const unit of result.units) {
    vm.runInContext(unit.block, context);
    const literal = unit.strings.find(s => s.value === '😀源标题');
    assert.equal([...unit.block].slice(literal.start,literal.end).join(''), literal.raw);
  }
  assert.equal(scenes[0].update(2), 5); assert.equal(scenes[1].update(12), 9);
  assert.deepEqual(sounds, [[1,'hit'],[12,'ding']]);
});

test('shared scene factory is preserved without executing unused sibling groups', () => {
  const result = inventory(`(()=>{function scene(a,b){return new Scene(a,b);}
    {const sc=scene(84.3,101.666);sc.update=t=>t;}
    {const sc=scene(101.666,118.2);sc.update=t=>t;}
  })();`);
  assert.equal(result.units.length,2);
  const scenes=[];
  vm.runInNewContext(result.units[1].block,{Scene:class{constructor(a,b){scenes.push([a,b]);}}});
  assert.deepEqual(scenes,[[101.666,118.2]]);
});

test('braces in strings and templates do not split performance code', () => {
  const result=inventory("(()=>{const helper='})(); { not code';(()=>{const s=new Scene(0,2);s.html=`<b>${helper}</b>`;})();})();");
  assert.equal(result.units.length,1);
  assert.ok(result.units[0].block.includes("})(); { not code"));
});

test('frame arithmetic and per-block constants retain their own scene boundaries', () => {
  const r=inventory(`(()=>{(()=>{const A=84.3,Z=101.666,s=new Scene(A,Z);s.update=t=>t;})();
    (()=>{const A=149.4,Z=9794/60,s=new Scene(A,Z);s.update=t=>t;})();})();`);
  assert.deepEqual(r.units.map(x=>x.source),[{start:84.3,end:101.666},{start:149.4,end:9794/60}]);
});
