"""Console bridge checks: deterministic media clock, scoped state, and new VOX."""
from array import array
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from adapt_project import AdaptError


def module(filename, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "adapters/doubao-console" / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


PREPARE = module("prepare_episode.py", "doubao_episode_prepare")


class DoubaoEpisodeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="adu-doubao-unit-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)

    def voice(self):
        with wave.open(str(self.project / "voice.wav"), "wb") as audio:
            audio.setnchannels(1); audio.setsampwidth(2); audio.setframerate(6000)
            audio.writeframes(array("h", [0] * 2000 + [4000] * 2000 + [16000] * 2000).tobytes())

    def test_new_voice_envelope_uses_output_frames_and_no_source_vox(self):
        self.voice()
        report = PREPARE.prepare(self.project)
        js = (self.project / "doubao_episode.js").read_text()
        values = json.loads(js.split("=", 1)[1].strip().rstrip(";"))
        self.assertEqual(len(values), 60)
        self.assertEqual(values[:20], [0] * 20)
        self.assertEqual(values[20:40], [.25] * 20)
        self.assertEqual(values[40:], [1] * 20)
        self.assertEqual(report["clock"], "output")
        self.assertEqual(report["voiceSha256"], hashlib.sha256((self.project / "voice.wav").read_bytes()).hexdigest())
        self.assertFalse((self.project / "vox.js").exists())
        self.assertEqual(PREPARE.prepare(self.project), report)

    def test_prepare_hook_rejects_hash_and_unknown_kind_before_running(self):
        from build_macro_project import prepare_episode_runtime
        self.voice()
        for contract in ({"kind": "doubao-voice-rms/1", "implementationSha256": "0" * 64},
                         {"kind": "arbitrary-python/1", "implementationSha256": "0" * 64}):
            with self.assertRaises(AdaptError):
                prepare_episode_runtime({"episodePreparation": contract,
                                         "generatedRuntimeFiles": ["doubao_episode.js"]}, self.project)
            self.assertFalse((self.project / "doubao_episode.js").exists())

    def test_transition_hook_keeps_native_plane_and_reverses_without_stale_fx(self):
        bridge = (ROOT / "adapters/doubao-console/bridge.js").read_text()
        script = """
const assert=require('node:assert/strict');
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));const lerp=(a,b,x)=>a+(b-a)*x;
const EZ={in:x=>x*x*x,out:x=>1-(1-x)**3,inout:x=>x<.5?4*x*x*x:1-(-2*x+2)**3/2};
""" + bridge + """
const planes=Object.fromEntries(['wipe','circ','flash','world'].map(k=>[k,{style:{}}]));
const current={opt:{}}, next={opt:{trans:'wipe',td:.5,tc:'#abc'}};
const context={frame:600,fps:60,scene:current,item:{output_start_frame:0},nextScene:next,nextItem:{output_start_frame:600}};
doubaoTransition(planes,[],50.5,context);assert.equal(planes.wipe.style.transform,'translateX(0%)');
assert.equal(planes.wipe.style.background,'#abc');
context.frame=300;doubaoTransition(planes,[],49,context);
assert.equal(planes.wipe.style.transform,'translateX(100%)');assert.equal(planes.flash.style.opacity,'0.000');
doubaoTransition(planes,[[49,.6,.3]],49,{...context,nextScene:null});assert.equal(planes.flash.style.opacity,'0.600');
doubaoTransition(planes,[],48,{...context,nextScene:null});assert.equal(planes.flash.style.opacity,'0.000');
"""
        subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True)

    def test_private_style_scoping_keeps_outer_stage_pixel_origin(self):
        extractor = module("extract.py", "doubao_style_adapter")
        css = extractor.scoped_css({"style.css": "html,body{width:1920px;height:1080px}#world{position:absolute}.e{position:absolute}",
                                    "index.html": "<style>#tk,#hud{position:absolute;inset:0}</style>"})
        self.assertIn("html,body{margin:0;padding:0;width:1920px;height:1080px", css)
        self.assertIn('.doubao-host [data-doubao-node="tk"]', css)
        self.assertIn('.doubao-host [data-doubao-node="hud"]', css)


class DoubaoCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Pin the corrected candidate; never let filesystem order select the
        # withdrawn 0.1.0 diagnostic pack or an unreviewed future version.
        cls.directory = ROOT / "packs/doubao-console-performance/0.1.1-candidate"
        cls.pack = json.loads((cls.directory / "manifest.json").read_text())

    def test_source_media_private_paths_and_global_handlers_are_not_bundled(self):
        self.assertEqual(self.pack["status"], "candidate")
        self.assertEqual(self.pack["version"], "0.1.1-candidate")
        self.assertIn("html,body{margin:0;padding:0;width:1920px;height:1080px",
                      (self.directory / "style.css").read_text())
        self.assertEqual(self.pack["runtimeHooks"], ["macroTransition/1"])
        self.assertFalse(any(p.suffix.lower() in {".wav", ".mp3", ".mp4", ".jpg", ".png", ".woff2"}
                             for p in self.directory.rglob("*")))
        for scene in self.pack["scenes"]:
            body = (self.directory / scene["sourceCodeFile"]).read_text()
            for old in ("window.SFX =", "window.imgWait =", "window.renderAt =", "window.PRELOAD =", "/Volumes/", "/Users/"):
                self.assertNotIn(old, body)
            self.assertIn("const $ = id => nodes[id]", body)
            self.assertIn("outer.macroTransition", body)
            self.assertIn("sc.bg(bgx, t)", body)
            self.assertIn("sc.fg(fgx, t)", body)
            self.assertIn("tkUpdate(t); hudUpdate(t);", body)
            self.assertEqual(hashlib.sha256(body.encode()).hexdigest(), scene["sourceBlockSha256"])

    def test_repeat_instances_reverse_seek_and_sfx_do_not_share_state(self):
        fixture = r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const gradient={addColorStop(){}};
const canvas=new Proxy({createLinearGradient:()=>gradient,createRadialGradient:()=>gradient,measureText:t=>({width:String(t).length*20})},{get:(o,k)=>k in o?o[k]:()=>{}});
let sequence=0;
class Element {
 constructor(tag='div'){this.uid=++sequence;this.tagName=tag;this.style={};this.dataset={};this.children=[];this.cache={};this.classList={contains:()=>false};this.complete=true;this.naturalWidth=1920;this.offsetWidth=300;this.offsetHeight=300;}
 appendChild(e){this.children.push(e);return e;}
 set innerHTML(value){this.html=value;if(value.includes('data-doubao-node'))this.nodes=[...value.matchAll(/data-doubao-node="([^"]+)"/g)].map(m=>{const e=new Element;e.dataset.doubaoNode=m[1];return e;});}
 get innerHTML(){return this.html||'';}
 get firstChild(){return this.children[0]||(this.children[0]=new Element);}
 querySelector(q){if(!this.cache[q]){this.cache[q]=new Element;this.cache[q].parentNode=this;}return this.cache[q];}
 querySelectorAll(q){return q==='[data-doubao-node]'?this.nodes:[];}
 getContext(){return canvas;}
}
const hosts=[],frames=[],sounds=[];
class HostScene{constructor(s,e,bg,opt){this.s=s;this.e=e;this.opt=opt;this.el=new Element;hosts.push(this);}cam(){return null;}}
const context={document:{createElement:t=>new Element(t)},location:{search:''},URLSearchParams,
  Image:Element,console,Scene:HostScene,CONFIG:{fps:60,end:20,demo:false,race:{keys:[0,20,21],labels:['start','end']}},TALKF:['new-episode'],
  TALKMAP:Array.from({length:1800},(_,i)=>[0,i+1]),FACE:{},
  setFrame:(image,src)=>frames.push({image,src}),tc:t=>'output-'+t,S:(...args)=>sounds.push(args),
  window:{MACRO_OUTPUT_T:.25,DOUBAO_OUTPUT_VOX:Array(1800).fill(.2),PACK_BRAND_HTML:'NewBrand',PACK_PRESENTER_LABEL:'New Presenter',
    END:20,MACRO_PLAN:{end_frame:1200,scenes:[{output_start_frame:0}]}}};
vm.createContext(context);
const body=fs.readFileSync(process.argv[1],'utf8');
vm.runInContext(body,context);const one=hosts[0],oneSfx=sounds.length;assert(oneSfx>0);
vm.runInContext(body,context);const two=hosts[1];
assert.equal(hosts.length,2);assert.equal(sounds.length,oneSfx*2);assert.notEqual(one.el,two.el);
assert.notEqual(one.doubaoDiagnostics.initialTalkKey,two.doubaoDiagnostics.initialTalkKey);
one.update(one.s+.3);const first=frames.at(-1);assert(first.src.endsWith('f_00016.jpg'));const pose=JSON.stringify(first.image.parentNode.style);
context.window.MACRO_OUTPUT_T=.5;two.update(two.s+.3);const second=frames.at(-1);assert(second.src.endsWith('f_00031.jpg'));assert.notEqual(first.image,second.image);
context.window.MACRO_OUTPUT_T=.25;one.update(one.s+.8);one.update(one.s+.3);assert.equal(frames.at(-1).src,first.src);assert.equal(JSON.stringify(first.image.parentNode.style),pose);
assert.equal(sounds.length,oneSfx*2);assert.equal(context.window.SFX,undefined);assert.equal(context.window.renderAt,undefined);
"""
        for scene in self.pack["scenes"]:
            result = subprocess.run(["node", "-e", fixture, str(self.directory / scene["sourceCodeFile"])],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
