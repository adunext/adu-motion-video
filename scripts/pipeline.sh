#!/bin/bash
# adu-motion-video: explicit local workflow; setup is the only install command.
# doctor                      check tools without installing anything
# setup                       install the skill's Node/Python packages (Chrome/FFmpeg separate)
# new <dir>                   new 36s template demo project; no creator footage needed
# import <dir> <talk.mp4>     extract edited narration + frames; no raw footage / ASR needed
# demo <NEW dir>              new + action SFX + demo.mp4 (explicit no narration/BGM)
# stills <dir> t1,t2,...       save PNGs in a NEW stills/run-* directory
# audio <dir>                 collect cues and build bgm.wav / sfx.wav
# mix <dir> [music-volume]    build mix.wav; VOICE=none explicitly omits narration
# render <dir> <NEW.mp4> [K]  fresh verified export; SILENT=1 explicitly omits audio
# vert <dir> <NEW.mp4> [K]    requires a separately authored vert.html layout
# seg <dir> <i> <NEW.mp4> [K] safe full fresh render, no cache speedup
# check <file.mp4>            frame count/rate, complete decode, loudness and peak
# auto-capabilities          full catalog semantic fields, capacity and dependencies
# auto-plan <brief> <NEW dir> compare coherent styles and legal mixed routes
# auto-build <plan> <talk> <NEW dir> [--subs-js file] one narration master
# macro-spec <pack> <NEW.json>  manual scaffold with unbound episode cues
# macro-plan <pack> <brief.json> <NEW dir>  semantic/continuity/variety plan (draft exits 2)
# macro-rematch <pack> <spec> <change.json> <NEW dir>  local scene proposals
# macro-apply-rematch <pack> <spec> <review.json> <candidate> <NEW dir>  revalidate and adopt
# macro-build <pack> <spec> <talk.mp4> <NEW dir> [--subs-js file]
# preview <project> <video.mp4> <NEW dir> [--update] verified versioned player
# Overrides: HTML=index.html W=1920 H=1080 FPS=60 END=seconds CHROME=/path/to/chrome
set -euo pipefail
SK="$(cd "$(dirname "$0")/.." && pwd)"
SC="$SK/scripts"
export ADU_MOTION_VIDEO_ROOT="$SK"
PY="$SK/.venv/bin/python"
export NODE_PATH="$SK/node_modules${NODE_PATH:+:$NODE_PATH}"
cmd="${1:-help}"
D="${2:-.}"
end_of() {
  if [ -n "${END:-}" ]; then
    python3 - "$END" <<'PY'
import math, sys
x = float(sys.argv[1])
if not math.isfinite(x) or x <= 0:
    raise SystemExit('END must be finite and positive')
print(x)
PY
  else
    node "$SC/render_project.mjs" "$D/${HTML:-index.html}" --probe | python3 -c 'import json,sys; print(json.load(sys.stdin)["end"])'
  fi
}
case "$cmd" in
auto-capabilities)
  [ "$#" -eq 1 ] || { echo 'Usage: pipeline.sh auto-capabilities' >&2; exit 2; }
  python3 "$SC/auto_templates.py" capabilities
  ;;
auto-plan)
  [ "$#" -eq 3 ] || { echo 'Usage: pipeline.sh auto-plan <brief.json> <NEW directory>' >&2; exit 2; }
  python3 "$SC/auto_templates.py" plan "$2" "$3"
  ;;
auto-build)
  [ "$#" -ge 4 ] || { echo 'Usage: pipeline.sh auto-build <auto_plan.json> <talk.mp4> <NEW project> [--subs-js file]' >&2; exit 2; }
  shift
  python3 "$SC/build_auto_project.py" "$@"
  ;;
preview)
  [ "$#" -ge 4 ] || { echo 'Usage: pipeline.sh preview <project> <video.mp4> <NEW preview directory> [--update]' >&2; exit 2; }
  shift
  python3 "$SC/preview_delivery.py" "$@"
  ;;
macro-plan)
  [ "$#" -eq 4 ] || { echo 'Usage: pipeline.sh macro-plan <pack-id@version|pack-directory> <brief.json> <NEW directory>' >&2; exit 2; }
  python3 "$SC/plan_macro_project.py" "$2" "$3" "$4"
  ;;
macro-rematch)
  [ "$#" -ge 5 ] || { echo 'Usage: pipeline.sh macro-rematch <pack> <spec.json> <change.json> <NEW directory> [--project directory]' >&2; exit 2; }
  shift
  python3 "$SC/rematch_macro_project.py" propose "$@"
  ;;
macro-apply-rematch)
  [ "$#" -ge 6 ] || { echo 'Usage: pipeline.sh macro-apply-rematch <pack> <spec.json> <review.json> <candidate-id> <NEW directory> [--project directory]' >&2; exit 2; }
  shift
  python3 "$SC/rematch_macro_project.py" apply "$@"
  ;;
macro-spec)
  [ "$#" -eq 3 ] || { echo 'Usage: pipeline.sh macro-spec <pack-id@version|pack-directory> <NEW.json>' >&2; exit 2; }
  PACK_DIR="$(python3 "$SC/pack_catalog.py" resolve "$D")"
  python3 "$SC/build_macro_project.py" scaffold "$PACK_DIR" "$3"
  ;;
macro-build)
  [ "$#" -ge 5 ] || { echo 'Usage: pipeline.sh macro-build <pack-id@version|pack-directory> <spec.json> <edited-talk.mp4> <NEW project> [--subs-js file]' >&2; exit 2; }
  PACK_DIR="$(python3 "$SC/pack_catalog.py" resolve "$D")"
  shift 2
  python3 "$SC/build_macro_project.py" build "$PACK_DIR" "$@"
  ;;
packs)
  shift
  python3 "$SC/pack_catalog.py" list "$@"
  ;;
doctor)
  python3 "$SC/doctor.py"
  ;;
setup)
  npm ci --prefix "$SK"
  if [ ! -x "$PY" ]; then
    python3 -m venv "$SK/.venv"
  fi
  "$PY" -m pip -q install -r "$SK/requirements-runtime.txt"
  node --input-type=module - "$SC/chrome.mjs" <<'JS'
import {pathToFileURL} from 'node:url';
const {chrome} = await import(pathToFileURL(process.argv[2]).href);
console.log('chrome:', chrome());
JS
  ffmpeg -version
  ;;
new)
  [ "$#" -eq 2 ] || { echo 'Usage: pipeline.sh new <NEW directory>' >&2; exit 2; }
  python3 - "$SK/template" "$D" <<'PY'
from pathlib import Path
import shutil, sys
src, target = Path(sys.argv[1]), Path(sys.argv[2]).expanduser().absolute()
if target.exists() or target.is_symlink():
    raise SystemExit(f'Refusing existing project path: {target}')
if not target.parent.is_dir():
    raise SystemExit(f'Project parent must already exist: {target.parent}')
shutil.copytree(src, target)
for name in ('sc', 'stills', 'assets'):
    (target / name).mkdir(exist_ok=True)
# Empty scripts leave FACE/TALKMAP/SUBS undefined so existing fallback paths work.
# Generated data tools replace these stubs when media/subtitles become available.
for name in ('talkmap.js', 'face.js', 'subs.js'):
    p = target / name
    if not p.exists():
        p.write_text('// Optional data absent. Generated data may replace this stub.\n')
p = target / 'wall.js'
if not p.exists():
    p.write_text('// Optional video wall data.\nwindow.WALL = [];\n')
print(f'New project: {target}\n36s template demo is ready: local illustration + no narration. For real footage, prepare talkmap.js/talk and set CONFIG.demo=false.')
PY
  ;;
import)
  [ "$#" -eq 3 ] || { echo 'Usage: pipeline.sh import <project> <edited-talk-video>' >&2; exit 2; }
  python3 "$SC/import_talk.py" "$D" "$3" --fps "${FPS:-60}" --size "${TALK_SIZE:-720x1280}"
  ;;
demo)
  [ "$#" -eq 2 ] || { echo 'Usage: pipeline.sh demo <NEW directory>' >&2; exit 2; }
  bash "$0" new "$D"
  python3 - "$D/audio.py" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1]); text = p.read_text()
default = "MUSIC = dict(mode='track', path='', offset=None)"
if text.count(default) != 1:
    raise SystemExit('Demo recipe changed; review its explicit no-BGM binding')
p.write_text(text.replace(default, "MUSIC = dict(mode='none') # Explicit synthetic layout/SFX demo"))
print('Demo only: no narration or background music; action SFX retained.')
PY
  bash "$0" audio "$D"
  VOICE=none bash "$0" mix "$D"
  bash "$0" render "$D" "$D/demo.mp4" "${K:-3}"
  ;;
stills)
  [ "$#" -eq 3 ] || { echo 'Usage: pipeline.sh stills <project> t1,t2,...' >&2; exit 2; }
  mkdir -p "$D/stills"
  STILL_OUT="$D/stills/run-$(date -u +%Y%m%dT%H%M%S)-$$"
  EXTRA=(--stills-dir "$STILL_OUT" --times "$3")
  [ -z "${W:-}" ] || EXTRA+=(--width "$W")
  [ -z "${H:-}" ] || EXTRA+=(--height "$H")
  [ -z "${END:-}" ] || EXTRA+=(--end "$END")
  node "$SC/render_project.mjs" "$D/${HTML:-index.html}" "${EXTRA[@]}"
  ;;
audio)
  [ -x "$PY" ] || { echo 'Python environment is missing; run setup explicitly if installation is wanted.' >&2; exit 2; }
  node "$SC/dump_sfx.mjs" "$D/${HTML:-index.html}" "$D/sfx.json"
  "$PY" "$D/audio.py"
  ;;
mix)
  END_VALUE=$(end_of)
  MIX_HELPER="$D/audio_runtime/mix_recipe.py"
  if [ ! -f "$MIX_HELPER" ]; then
    MIX_HELPER="$SC/mix_recipe.py"
  fi
  VOL=$(python3 "$MIX_HELPER" volume "$D" "${3:-}")
  VOICE_MODE=$(python3 "$MIX_HELPER" voice "$D" "${VOICE:-}")
  case "$VOICE_MODE" in
    none) VOICE_INPUT=(-f lavfi -t "$END_VALUE" -i anullsrc=r=48000:cl=stereo) ;;
    file)
      [ -f "$D/voice.wav" ] || { echo 'Missing voice.wav. Extract your narration first; for an intentional music-only demo use VOICE=none.' >&2; exit 2; }
      VOICE_INPUT=(-i "$D/voice.wav") ;;
    *) echo 'VOICE must be file (default) or none.' >&2; exit 2 ;;
  esac
  for stem in bgm.wav sfx.wav; do
    [ -f "$D/$stem" ] || { echo "Missing $stem; run audio for this project first." >&2; exit 2; }
  done
  if [ -f "$D/showaudio.wav" ]; then
    SHOW=(-i "$D/showaudio.wav")
  else
    SHOW=(-f lavfi -t "$END_VALUE" -i anullsrc=r=44100:cl=stereo)
  fi
  MIX_GRAPH="\
[0:a]apad,highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=120,loudnorm=I=-16:TP=-1.5:LRA=9,asplit=3[v][vsc][vsc2];\
[1:a]volume=1.0[sh0];[sh0][vsc2]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350[sh];\
[2:a]volume=$VOL[b];[b][vsc]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=450[bd];\
[3:a]volume=0.5,highpass=f=60[s];\
[v][sh][bd][s]amix=inputs=4:normalize=0:duration=longest,atrim=0:$END_VALUE,alimiter=limit=0.92:level=false,loudnorm=I=-15.5:TP=-1.2:LRA=9,aresample=48000[out]"
  MIX_EXPLICIT=0
  [ -z "${3:-}${VOICE:-}" ] || MIX_EXPLICIT=1
  MIX_GRAPH=$(python3 "$MIX_HELPER" graph "$D" "$MIX_GRAPH" "$END_VALUE" "$VOL" "$VOICE_MODE" "$MIX_EXPLICIT")
  ffmpeg -y -loglevel error "${VOICE_INPUT[@]}" "${SHOW[@]}" -i "$D/bgm.wav" -i "$D/sfx.wav" -filter_complex "$MIX_GRAPH" -map "[out]" -c:a pcm_s16le "$D/mix.wav"
  python3 "$MIX_HELPER" save "$D" "$END_VALUE" "$VOL" "$VOICE_MODE" "$MIX_GRAPH"
  ffmpeg -hide_banner -i "$D/mix.wav" -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1
  ;;
render|vert)
  [ "$#" -ge 3 ] && [ "$#" -le 4 ] || { echo 'Usage: pipeline.sh render|vert <project> <NEW.mp4> [segments]' >&2; exit 2; }
  ENTRY=index.html; WIDTH=1920; HEIGHT=1080
  if [ "$cmd" = vert ] && [ ! -f "$D/macro_plan.json" ]; then ENTRY=vert.html; WIDTH=1080; HEIGHT=1920; fi
  if [ "$cmd" = vert ] && [ -f "$D/macro_plan.json" ]; then
    python3 -c 'import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); from pack_layout import project_dimensions; w,h=project_dimensions(Path(sys.argv[2])); h>w or sys.exit("vert requires a portrait project layout; rebuild with layout=portrait first")' "$SC" "$D"
  fi
  EXTRA=(--html "${HTML:-$ENTRY}" --fps "${FPS:-60}" --segments "${4:-${K:-5}}")
  if [ ! -f "$D/macro_plan.json" ]; then EXTRA+=(--width "${W:-$WIDTH}" --height "${H:-$HEIGHT}");
  else
    [ -z "${W:-}" ] || EXTRA+=(--width "$W")
    [ -z "${H:-}" ] || EXTRA+=(--height "$H")
  fi
  [ -z "${END:-}" ] || EXTRA+=(--end "$END")
  case "${SILENT:-0}" in
    1) EXTRA+=(--no-audio) ;;
    0) ;;
    *) echo 'SILENT must be 0 or 1.' >&2; exit 2 ;;
  esac
  python3 "$SC/export_project.py" "$D" "$3" "${EXTRA[@]}"
  ;;
seg)
  [ "$#" -ge 4 ] && [ "$#" -le 5 ] || { echo 'Usage: pipeline.sh seg <project> <segment-index> <NEW.mp4> [segments]. A new filename is required; .last_out is never read.' >&2; exit 2; }
  case "$3" in ''|*[!0-9]*) echo 'Segment index must be a nonnegative integer' >&2; exit 2 ;; esac
  case "$4" in *.mp4) ;; *) echo 'A new .mp4 output path is required; old cached output will not be reused.' >&2; exit 2 ;; esac
  echo "Segment $3 requested. Safe fallback: ALL segments will be freshly rendered to the explicit new output. No old parts cache is reused; this command does not provide segment-only acceleration." >&2
  bash "$0" render "$D" "$4" "${5:-${K:-5}}"
  ;;
check)
  ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=width,height,avg_frame_rate,nb_read_frames:format=duration -of compact=p=0 "$D"
  ffmpeg -v error -xerror -i "$D" -map 0:v:0 -map '0:a?' -f null -
  if [ -n "$(ffprobe -v error -select_streams a:0 -show_entries stream=index -of csv=p=0 "$D")" ]; then
    ffmpeg -hide_banner -i "$D" -vn -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1
    ffmpeg -hide_banner -i "$D" -vn -af astats -f null - 2>&1 | grep 'Peak level dB' | tail -1
  else
    echo 'Audio: none (silent video)'
  fi
  ;;
*) sed -n '/^# /p' "$0" ;;
esac
