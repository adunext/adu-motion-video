#!/bin/bash
# adu-motion-video: explicit local workflow; setup is the only install command.
# setup                       install dependencies only when explicitly requested
# new <dir>                   copy template into a NEW directory (existing paths rejected)
# stills <dir> t1,t2,...       save PNGs in a NEW stills/run-* directory
# audio <dir>                 collect audio cues and build bgm.wav / sfx.wav
# mix <dir> [music-volume]    rebuild mix.wav using the established mix recipe
# render <dir> <NEW.mp4> [K]  fresh K segments + verified concat/mux + manifest
# vert <dir> <NEW.mp4> [K]    same checks; requires an authored vert.html
# seg <dir> <i> <NEW.mp4> [K] safe fallback: full fresh render, no cache speedup
# check <file.mp4>           dimensions, frame count/rate, decode, loudness and peak
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
setup)
  if [ ! -d "$SK/node_modules/playwright-core" ]; then
    npm install --prefix "$SK" playwright-core@1.58
  fi
  if [ ! -x "$PY" ]; then
    python3 -m venv "$SK/.venv"
  fi
  "$PY" -m pip -q install numpy pillow opencv-python-headless scipy
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
print(f'New project: {target}; add real talk footage before rendering.')
PY
  ;;
stills)
  [ "$#" -eq 3 ] || { echo 'Usage: pipeline.sh stills <project> t1,t2,...' >&2; exit 2; }
  mkdir -p "$D/stills"
  STILL_OUT="$D/stills/run-$(date -u +%Y%m%dT%H%M%S)-$$"
  EXTRA=(--stills-dir "$STILL_OUT" --times "$3" --width "${W:-1920}" --height "${H:-1080}")
  [ -z "${END:-}" ] || EXTRA+=(--end "$END")
  node "$SC/render_project.mjs" "$D/${HTML:-index.html}" "${EXTRA[@]}"
  ;;
audio)
  [ -x "$PY" ] || { echo 'Python environment is missing; run setup explicitly if installation is wanted.' >&2; exit 2; }
  node "$SC/dump_sfx.mjs" "$D/index.html" "$D/sfx.json"
  "$PY" "$D/audio.py"
  ;;
mix)
  END_VALUE=$(end_of)
  VOL=${3:-0.50}
  python3 - "$VOL" <<'PY'
import math, sys
v = float(sys.argv[1])
if not math.isfinite(v) or v < 0:
    raise SystemExit('Music volume must be a finite nonnegative number')
PY
  if [ -f "$D/showaudio.wav" ]; then
    SHOW=(-i "$D/showaudio.wav")
  else
    SHOW=(-f lavfi -t "$END_VALUE" -i anullsrc=r=44100:cl=stereo)
  fi
  ffmpeg -y -loglevel error -i "$D/voice.wav" "${SHOW[@]}" -i "$D/bgm.wav" -i "$D/sfx.wav" -filter_complex "\
[0:a]apad,highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=120,loudnorm=I=-16:TP=-1.5:LRA=9,asplit=3[v][vsc][vsc2];\
[1:a]volume=1.0[sh0];[sh0][vsc2]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350[sh];\
[2:a]volume=$VOL[b];[b][vsc]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=450[bd];\
[3:a]volume=0.5,highpass=f=60[s];\
[v][sh][bd][s]amix=inputs=4:normalize=0:duration=longest,atrim=0:$END_VALUE,alimiter=limit=0.92[out]" -map "[out]" -c:a pcm_s16le "$D/mix.wav"
  ffmpeg -hide_banner -i "$D/mix.wav" -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1
  ;;
render|vert)
  [ "$#" -ge 3 ] && [ "$#" -le 4 ] || { echo 'Usage: pipeline.sh render|vert <project> <NEW.mp4> [segments]' >&2; exit 2; }
  ENTRY=index.html; WIDTH=1920; HEIGHT=1080
  if [ "$cmd" = vert ]; then ENTRY=vert.html; WIDTH=1080; HEIGHT=1920; fi
  EXTRA=(--html "$ENTRY" --width "$WIDTH" --height "$HEIGHT" --fps "${FPS:-60}" --segments "${4:-${K:-5}}")
  [ -z "${END:-}" ] || EXTRA+=(--end "$END")
  python3 "$SC/export_project.py" "$D" "$3" "${EXTRA[@]}"
  ;;
seg)
  [ "$#" -ge 4 ] && [ "$#" -le 5 ] || { echo 'Usage: pipeline.sh seg <project> <segment-index> <NEW.mp4> [segments]. A new filename is required; .last_out is never read.' >&2; exit 2; }
  case "$3" in ''|*[!0-9]*) echo 'Segment index must be a nonnegative integer' >&2; exit 2 ;; esac
  case "$4" in *.mp4) ;; *) echo 'A new .mp4 output path is required; old cached output will not be reused.' >&2; exit 2 ;; esac
  echo "Segment $3 requested. Safe fallback: ALL segments will be freshly rendered to the explicit new output. No old parts cache is reused; this command does not provide segment-only acceleration." >&2
  "$0" render "$D" "$4" "${5:-${K:-5}}"
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
*) sed -n '2,12p' "$0" ;;
esac
