#!/usr/bin/env python3
"""Extract reviewed Doubao console groups with private source-native canvases."""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from build_macro_project import bind_authored_block
from extract_authored_pack import attach_adaptation_profile, literal
from source_registry import verify


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def replace_once(text, old, new):
    require(text.count(old) == 1, f"Reviewed runtime port changed: {old[:90]}")
    return text.replace(old, new)


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def source_ports(texts, prelude):
    """Small, asserted ports; source drawing formulas stay byte-for-byte."""
    lib = replace_once(texts["lib.js"], "const $ = id => document.getElementById(id);", "const $ = id => nodes[id];")
    lib = replace_once(lib, "const SFX = []; window.SFX = SFX;", "const SFX = [];")
    lib = replace_once(lib, "window.imgWait = () => Promise.all([..._pending].map(im => im.complete ? 0 : new Promise(r => { im.onload = im.onerror = r; }))).then(() => _pending.clear());", "")
    lib = replace_once(lib, "function setFrame(imgEl, src) { if (imgEl._src !== src) { imgEl._src = src; imgEl.src = src; _pending.add(imgEl); } }",
                       "function setFrame(imgEl, src) { OUTPUT_FRAME(imgEl, src); }")
    lib = replace_once(lib, "const talkSrc = t => {", "const talkSrc = t => { t = window.MACRO_OUTPUT_T ?? t;")
    lib = replace_once(lib, "function faceAt(t) {", "function faceAt(t) { t = window.MACRO_OUTPUT_T ?? t;")
    core = texts["core.js"]
    # Unused source-episode catalogues are not capability defaults.
    core, n = re.subn(r"const NF = \{[^\n]+\};", "const NF = {};", core)
    require(n == 1, "Reviewed NF catalogue changed")
    core, n = re.subn(r"const EPS = \[[\s\S]*?\];", "const EPS = [];", core, count=1)
    require(n == 1, "Reviewed EPS catalogue changed")
    core = replace_once(core, "const voxAt = t => VOX[clamp(Math.floor(t * 60), 0, VOX.length - 1)] || 0;", """const voxAt = () => {
  const vox = window.DOUBAO_OUTPUT_VOX;
  if (!Array.isArray(vox) || !vox.length) throw Error('Run reviewed Doubao episode preparation on the imported voice');
  const frame = Math.floor((window.MACRO_OUTPUT_T || 0) * 60 + 1e-6);
  return vox[clamp(frame, 0, vox.length - 1)];
};""")
    core = replace_once(core, "REC · 阿杜Next", "${window.PACK_PRESENTER_LABEL}")
    core = replace_once(core, ">AduNext</b>", ">${window.PACK_BRAND_HTML}</b>")
    core = replace_once(core, "HUD.tcs.textContent = tc(t);", "HUD.tcs.textContent = OUTPUT_TC(window.MACRO_OUTPUT_T);")
    core = replace_once(core, "const sec = Math.floor(t);", "const sec = Math.floor(window.MACRO_OUTPUT_T);")
    core = replace_once(core, "HUD.tf.style.width = (t / (window.END || CONFIG.end) * 100)",
                        "HUD.tf.style.width = (window.MACRO_OUTPUT_T / (window.END || CONFIG.end) * 100)")
    line = next(line for line in core.splitlines() if "HUD.ticks.innerHTML = CHAP.map" in line)
    core = replace_once(core, line, "    HUD.ticks.innerHTML = window.MACRO_PLAN.scenes.map(s => `<i style=\"position:absolute;left:${(s.output_start_frame / window.MACRO_PLAN.end_frame * 100).toFixed(2)}%;top:-4px;width:2px;height:10px;background:rgba(255,255,255,.18)\"></i>`).join('');")
    prelude = replace_once(prelude, "const PRELOAD = window.PRELOAD = [];", "const PRELOAD = [];")
    prelude = replace_once(prelude, "const AFLAT = preImg('sc/atlas/flat_0.jpg');", "const AFLAT = null; // unselected wall catalogue deliberately not loaded")
    main = texts["main.js"].split("(function () {", 1)[1].split("  window.READY =", 1)[0]
    main = replace_once(main, "window.renderAt = function (t) {", "const drawAt = function (t) {")
    main = replace_once(main, "tkUpdate(t); hudUpdate(t); trans(t);", "tkUpdate(t); hudUpdate(t);")
    main = replace_once(main, "fade.style.opacity = clamp((t - (E - .7)) / .65).toFixed(3);", "fade.style.opacity = '0'; // output host owns deliberate final fade")
    main = replace_once(main, "if (window.OVERLAY) window.OVERLAY(t);", "// Output host owns this episode's captions.")
    return lib, core, prelude, main


def scoped_css(texts):
    css = texts["style.css"] + "\n" + "\n".join(re.findall(r"<style[^>]*>([\s\S]*?)</style>", texts["index.html"]))
    css = re.sub(r"@font-face\s*\{[^}]*\}", "", css)
    rules = ["html,body{margin:0;padding:0;width:1920px;height:1080px;overflow:hidden;background:#000}",
             "#stage{position:relative;width:1920px;height:1080px;overflow:hidden;background:#06070A}",
             "#world,#fx{position:absolute;inset:0;transform-origin:960px 540px}",
             ".sc{position:absolute;inset:0;overflow:hidden;display:none}"]
    for selectors, declarations in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        selected = []
        for selector in selectors.split(","):
            selector = selector.strip()
            if selector in ("html", "html,body"):
                continue
            if selector in ("body", "#stage", ":root"):
                selected.append(".doubao-host")
            else:
                selector = re.sub(r"#([A-Za-z0-9_-]+)", r'[data-doubao-node="\1"]', selector)
                selected.append(".doubao-host " + selector)
        if selected:
            rules.append(",".join(selected) + "{" + declarations + "}")
    return "\n".join(rules)


def wrap_unit(raw, spec, inventory, texts):
    start, end = raw["source"]["start"], raw["source"]["end"]
    initial = spec.get("adapter", {}).get("initialTalkKey")
    preceding = [key for key in inventory["talkKeys"] if key["at"] < start]
    if preceding:
        require(isinstance(initial, str) and initial.strip() == preceding[-1]["source"].strip(),
                f"{spec['id']}: explicitly review the last preceding source tkKey; no invented presenter pose")
    else:
        require(initial is None, f"{spec['id']}: no preceding presenter key exists")
    raw_statement = raw["statement"]
    require(not any(re.search(rf"\b{name}\b", raw_statement) for name in ("AFLAT", "ATLAS", "WALL", "EPS", "clipAt", "beatK")),
            f"{spec['id']}: selected group needs an unreviewed wall/clip/beat adapter")
    lib, core, prelude, main = source_ports(texts, inventory["prelude"])
    statement = raw_statement
    contract = deepcopy(spec["contract"])
    slots = contract.setdefault("slots", [])
    for slot in slots:
        if "/Volumes/" in slot.get("sourceText", "") or "/Users/" in slot.get("sourceText", ""):
            require(slot.get("id") == "path-message", "An additional private path needs explicit adapter review")
            require(statement.count(slot["sourceText"]) == 1, "Reviewed private path occurrence changed")
            statement = statement.replace(slot["sourceText"], "本期素材路径由使用者填写")
            slot["sourceText"] = "本期素材路径由使用者填写"
    # Existing builder relocates images beneath assets/. Keep exact pixels while
    # replacing the source-specific folder prefix in the reviewed statement.
    for slot in slots:
        if slot.get("type") == "image":
            original = slot["sourceAsset"]
            relocated = "assets/" + Path(original).name
            require(original in statement, f"{spec['id']}: image binding absent from source: {original}")
            statement = statement.replace(original, relocated)
            slot["sourceAsset"] = relocated
    header = f"""((OUTPUT_SCENE,OUTPUT_FRAME,OUTPUT_TC,FORWARD_S) => {{
const outer = new OUTPUT_SCENE({start!r},{end!r},'#06070A',{{}});
const host = document.createElement('div');host.className='doubao-host';
host.style.cssText='position:absolute;inset:0;overflow:hidden';outer.el.appendChild(host);
host.innerHTML='<div data-doubao-node="world"></div><div data-doubao-node="fx"></div><div data-doubao-node="tk"></div><div data-doubao-node="front"></div><div data-doubao-node="hud"></div><div data-doubao-node="ov" style="position:absolute;inset:0;pointer-events:none"></div>';
const nodes=Object.fromEntries([...host.querySelectorAll('[data-doubao-node]')].map(e=>[e.dataset.doubaoNode,e]));
const HITS=[]; // selected groups do not use source-track beatK()
"""
    prefix = header + lib + "\n" + core + "\n" + prelude + "\n" + (initial or "") + "\n"
    code_start = len(prefix)
    body = prefix + statement + "\n" + main + "\n" + (HERE / "bridge.js").read_text()
    body += """
outer.opt={...SCENES[0].opt};
let lastSource=outer.s;
outer.update=t=>{lastSource=t;drawAt(t);};
outer.macroTransition=context=>doubaoTransition({wipe,circ,flash,world:nodes.world},FLASH,lastSource,{...context,scene:outer});
SFX.forEach(c=>{const {t,type,g,p,...extra}=c;FORWARD_S(t,type,g,p,extra);});
outer.doubaoDiagnostics={clock:'source-geometry/output-media',sourceScenes:SCENES.length,sourceSfx:SFX.length,initialTalkKey:TKK[0]};
})(Scene,setFrame,tc,S);
"""
    occupied = []
    for slot in slots:
        if slot.get("type") not in ("text", "dynamicText"):
            continue
        old = slot.get("sourceText")
        require(isinstance(old, str) and old, f"{slot['id']}: sourceText is required")
        matches = [m for m in re.finditer(re.escape(old), statement)
                   if not any(m.start() < b and a < m.end() for a, b in occupied)]
        occurrence = slot.pop("occurrence", None)
        if occurrence is not None:
            require(isinstance(occurrence, int) and 0 <= occurrence < len(matches), f"{slot['id']}: invalid occurrence")
            matches = matches[occurrence:occurrence + 1]
        require(matches, f"{slot['id']}: reviewed text missing from selected statement")
        occupied.extend((m.start(), m.end()) for m in matches)
        slot["sourceSpans"] = [{"start": code_start + m.start(), "end": code_start + m.end(),
                                "renderContext": slot.get("renderContext", "html")} for m in matches]
    ids = {s["id"] for s in slots}
    require(not {"presenter", "grainTexture"} & ids, "Adapter owns presenter and grainTexture slots")
    slots += [{"id": "presenter", "type": "talk", "required": True},
              {"id": "grainTexture", "type": "image", "required": True, "sourceAsset": "assets/noise.png"}]
    return body, {**contract, "id": spec["id"], "source": raw["source"],
                  "sourceCodeFile": f"units/{spec['id']}.js", "sourceBlockSha256": sha(body.encode()),
                  "requiresFaceTracking": True,
                  "provenance": {"adapter": "adapters/doubao-console/extract.py", "sourceFile": "scenes.js",
                                 "sourceLines": raw["sourceLines"], "sourceStatementSha256": raw["sourceStatementSha256"],
                                 "helperSha256": sha((texts["lib.js"] + texts["core.js"]).encode()),
                                 "adapterSha256": sha(Path(__file__).read_bytes()), "initialTalkKey": initial,
                                 "ports": ["private DOM/Scene/canvas state", "output-clock narration/face/HUD progress",
                                           "source-clock geometry and chapter", "native transition plane hook",
                                           "new narration RMS glow", "source SFX forwarded once", "explicit owner texture/fonts"]}}


def audio_timeline(text, duration, groups):
    import ast
    values = {}
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {"ENV", "HITS"}:
                    values[target.id] = literal(node.value, duration)
    require(set(values) == {"ENV", "HITS"}, "Reviewed source ENV/HITS cannot be extracted")
    return {"schema": "adu-authored-score/1", "sourceSha256": sha(text.encode()),
            "SEC": [{"id": g["id"], "start": g["source"]["start"], "end": g["source"]["end"],
                     "mode": "synth", "energy": .25, "options": {"kick_on": False, "clapon": False}} for g in groups],
            "ENV": [{"at": at, "db": db} for at, db in values["ENV"]], "HITS": values["HITS"], "DARK": [],
            "sfxEvents": [], "mix": {"profile": "opus-five-v1"},
            "limits": ["Source uses an external music recording; it is not bundled or claimed reproduced.",
                       "Default synth bed is a disclosed replacement. Source ENV/HITS and runtime S() are remapped per selected group."]}


def extract(record: Path, proposal_path: Path, output: Path):
    proposal = json.loads(proposal_path.read_text())
    source = json.loads((record / "source.json").read_text())
    require(not output.exists() and output.parent.is_dir(), "Use a fresh output path with an existing parent")
    require(proposal.get("sourceRevision") == source["revision"], "Proposal source revision differs from frozen record")
    require(re.fullmatch(r"\d+\.\d+\.\d+-candidate", proposal.get("version", "")), "New adapter version must remain candidate")
    require(proposal.get("adaptationProfile"), "New extraction requires adaptationProfile")
    require(verify(record)["verified"], "Frozen source verification failed")
    required = {"scenes.js", "core.js", "lib.js", "main.js", "index.html", "style.css", "config.js", "audio.py"}
    require(required <= set(proposal.get("sourceFiles", {})), "Proposal must pin every runtime source file")
    texts = {}
    for filename, expected in proposal["sourceFiles"].items():
        require(not Path(filename).is_absolute() and ".." not in Path(filename).parts, "Source file escaped record")
        data = (record / "snapshot" / filename).read_bytes()
        require(sha(data) == expected == source["sourceFiles"][filename]["sha256"], f"Reviewed source changed: {filename}")
        texts[filename] = data.decode()
    with tempfile.TemporaryDirectory(prefix="adu-doubao-extract-") as temporary:
        temp = Path(temporary)
        subprocess.run(["node", str(HERE / "inventory.mjs"), str(record / "snapshot/scenes.js"), str(temp / "inventory.json")],
                       check=True, capture_output=True, text=True)
        inventory = json.loads((temp / "inventory.json").read_text())
        stage = temp / "pack"
        (stage / "units").mkdir(parents=True)
        scenes = []
        for spec in proposal["units"]:
            require(re.fullmatch(r"[a-z][a-z0-9-]{0,63}", spec.get("id", "")), "Invalid recipe id")
            require(spec.get("file") == "scenes.js", "Only reviewed scenes.js groups are supported")
            raw = inventory["units"][spec["index"]]
            require(spec.get("expectedStatementSha256") == raw["sourceStatementSha256"], f"{spec['id']}: reviewed statement hash differs")
            body, scene = wrap_unit(raw, spec, inventory, texts)
            scene["sourceRevision"] = source["revision"]
            values = {s["id"]: s["sourceText"] for s in scene["slots"] if s["type"] in ("text", "dynamicText")}
            bind_authored_block(body, {**scene, "slots": [{**s, "mustChange": False} for s in scene["slots"]]}, values, scene["id"])
            (stage / scene["sourceCodeFile"]).write_text(body)
            scenes.append(scene)
        fonts, font_rules = [], []
        for filename, meta in source["mediaFiles"].items():
            match = re.fullmatch(r"fonts/(Geist|GeistMono)-normal-(400|500|600|700|800)\.woff2", filename)
            if not match:
                continue
            base, weight = match.groups(); family = "Geist Mono" if base == "GeistMono" else "Geist"
            fid = ("geist-mono-" if base == "GeistMono" else "geist-") + weight
            fonts.append({"id": fid, "family": family, "sha256": meta["sha256"], "format": "woff2", "extension": ".woff2",
                          "required": True, "sourceFile": filename, "distribution": "explicit-owner-supplied; not bundled"})
            font_rules.append(f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};src:url(fonts/{fid}.woff2) format('woff2')}}")
        require(len(fonts) == 8, "Reviewed Geist/Geist Mono font set differs")
        (stage / "style.css").write_text("\n".join(font_rules) + "\n" + scoped_css(texts))
        for filename in ("lib.js", "config.js"):
            shutil.copy2(ROOT / "packs/classic-performance/1.0.0" / filename, stage / filename)
        (stage / "doubao_fonts.js").write_text("window.DOUBAO_FONT_READY=Promise.all([\"500 20px 'Geist Mono'\",\"600 40px Geist\",\"700 40px Geist\"].map(f=>document.fonts.load(f,'本期 ABC 0123')));\n")
        duration = proposal.get("sourceDuration", source["render"]["probe"]["durationSeconds"])
        write(stage / "audio_timeline.json", audio_timeline(texts["audio.py"], duration, scenes))
        shutil.copy2(HERE / "pack-readme.md", stage / "README.md")
        manifest = {"id": proposal["id"], "version": proposal["version"], "title": proposal["title"],
                    "status": "candidate", "sourceFormat": "authored-unit/1", "sourceRevision": source["revision"],
                    "source": {"engine": "DOM/Canvas/private-source-host", "assetPolicy": "Bind this episode's narration, images and owner-supplied grain texture."},
                    "fps": 60, "width": 1920, "height": 1080, "requireMotionWindows": True,
                    "runtimeFiles": ["doubao_fonts.js"], "generatedRuntimeFiles": ["doubao_episode.js"],
                    "episodePreparation": {"kind": "doubao-voice-rms/1", "implementationSha256": sha((HERE / "prepare_episode.py").read_bytes())},
                    "runtimeHooks": ["macroTransition/1"], "scenes": scenes, "assetDefinitions": {}, "externalFonts": fonts,
                    "environment": {"platform": "macOS", "systemFonts": ["PingFang SC"], "format": "1920x1080/60"},
                    "validation": {"sourceReplay": "pending", "newContent": "pending", "independentUse": "pending"},
                    "files": {p.relative_to(stage).as_posix(): sha(p.read_bytes()) for p in sorted(stage.rglob("*")) if p.is_file()}}
        attach_adaptation_profile(manifest, proposal["adaptationProfile"])
        write(stage / "manifest.json", manifest)
        shutil.copytree(stage, output)
    return {"pack": manifest["id"], "version": manifest["version"], "units": len(scenes), "path": str(output), "status": "candidate"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path); parser.add_argument("proposal", type=Path); parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(extract(args.record.resolve(), args.proposal.resolve(), args.output.resolve()), ensure_ascii=False))
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Doubao extraction failed: {exc}") from exc
