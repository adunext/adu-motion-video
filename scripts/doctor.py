#!/usr/bin/env python3
"""Read-only preflight for the public local rendering workflow; installs nothing."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from color_management import engine

ROOT = Path(__file__).resolve().parent.parent
failures = []


def report(name, okay, detail, fix=''):
    print(f'{"OK" if okay else "MISSING"}  {name}: {detail}')
    if not okay:
        failures.append(name)
        if fix:
            print(f'         Next: {fix}')


def command(args):
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=30, cwd=ROOT)
        return proc.returncode == 0, (proc.stdout or proc.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)


report('Python', sys.version_info >= (3, 10), sys.version.split()[0], 'Install Python 3.10+ and run this command with python3.')
for tool in ('node', 'npm', 'ffmpeg', 'ffprobe'):
    path = shutil.which(tool)
    okay, version = command([tool, '--version' if tool in ('node', 'npm') else '-version']) if path else (False, 'not on PATH')
    if tool == 'node' and okay:
        okay = int(version.lstrip('v').split('.')[0]) >= 18
    fix = 'Install Node.js 18+ (includes npm).' if tool in ('node', 'npm') else 'Install FFmpeg (must include ffprobe and libx264).'
    report(tool, okay, version.splitlines()[0] if version else 'not on PATH', fix)
if shutil.which('ffmpeg'):
    okay, encoders = command(['ffmpeg', '-hide_banner', '-encoders'])
    report('H.264 encoder', okay and 'libx264' in encoders, 'libx264 available' if 'libx264' in encoders else 'libx264 unavailable', 'Install a FFmpeg build with libx264.')
    try:
        color = engine()
        report('Color conversion', True, color['engine'] + ' / sRGB images / limited BT.709 video')
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        report('Color conversion', False, str(exc), 'Install FFmpeg 9+ with libswscale color mapping and colorspace.')
if shutil.which('node'):
    js = """import {createRequire} from 'node:module';
import {chrome} from './scripts/chrome.mjs';
const require = createRequire(import.meta.url);
let code = 0;
try {console.log('Playwright: ' + require('playwright-core/package.json').version);} catch {console.log('Playwright: missing; run bash scripts/pipeline.sh setup'); code = 1;}
try {console.log('Browser: ' + chrome());} catch(e) {console.log('Browser: ' + e.message); code = 1;}
process.exitCode = code;
"""
    okay, detail = command(['node', '--input-type=module', '-e', js])
    report('Browser runtime', okay, detail, 'Run setup for Playwright; install Chrome or set CHROME if a browser is missing.')
python = ROOT / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
modules = ['numpy', 'PIL', 'cv2', 'scipy']
if python.is_file():
    okay, detail = command([str(python), '-c', 'import importlib.util,json; print(json.dumps([m for m in ' + repr(modules) + ' if importlib.util.find_spec(m) is None]))'])
    missing = json.loads(detail) if okay else modules
    report('Audio/alignment Python packages', okay and not missing, ', '.join(missing) + ' missing' if missing else 'ready', 'bash scripts/pipeline.sh setup')
else:
    report('Audio/alignment Python packages', False, 'skill .venv not created', 'bash scripts/pipeline.sh setup (silent rendering does not require this environment)')
print('Platforms: Windows (via WSL), macOS, Linux; Bash workflow. Optional automatic face tracking: macOS Vision + Swift; use reviewed fixed crops elsewhere. Native Windows shell workflow is not tested.')
print('This checks installed tools only. It does not validate fonts, media, animation quality or GPU behavior; run the demo next.')
sys.exit(1 if failures else 0)
