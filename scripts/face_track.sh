#!/bin/bash
# Local Vision face tracking; macOS + Swift required. No media is uploaded.
# Usage: face_track.sh PROJECT (after align_talk.py creates talk/CLIP/)
set -euo pipefail
[ "$#" -eq 1 ] || { echo 'Usage: face_track.sh PROJECT' >&2; exit 2; }
[ "$(uname -s)" = Darwin ] || { echo 'Face tracking requires macOS Vision and Swift.' >&2; exit 2; }
D="$1"
HERE="$(cd "$(dirname "$0")" && pwd)"
FACE_WORK=$(mktemp -d "${TMPDIR:-/tmp}/adu-face.XXXXXX")
trap 'rm -rf "$FACE_WORK"' EXIT
swiftc -O "$HERE/face_track.swift" -o "$FACE_WORK/face"
python3 - "$D" "$FACE_WORK" <<'PY'
import json
from pathlib import Path
import subprocess
import sys
project, work = map(Path, sys.argv[1:])
if not (project / 'talk').is_dir():
    raise SystemExit('Expected PROJECT/talk after alignment.')
result = {}
for clip in sorted((project / 'talk').iterdir()):
    if not clip.is_dir():
        continue
    output = subprocess.run([str(work / 'face'), str(clip), '15'], check=True, capture_output=True, text=True)
    rows = [line.split() for line in output.stdout.splitlines() if 'none' not in line]
    frames = [int(row[0][2:7]) for row in rows]
    def smooth(values):
        return [round(sum(values[max(0, i - 2):i + 3]) / len(values[max(0, i - 2):i + 3]), 4) for i in range(len(values))]
    result[clip.name] = dict(f=frames, cx=smooth([float(r[1]) for r in rows]), cy=smooth([float(r[2]) for r in rows]), h=smooth([float(r[4]) for r in rows]))
(project / 'face.js').write_text('const FACE=' + json.dumps(result, separators=(',', ':')) + ';\n')
print('face.js samples:', {key: len(value['f']) for key, value in result.items()})
PY
