#!/usr/bin/env python3
"""Cross-platform workflow. Windows: python scripts/pipeline.py <command>.

macOS/Linux: python3 scripts/pipeline.py <command>. Existing Bash entry remains.
All children use argument arrays, UTF-8 and this installation's interpreter.
"""
from __future__ import annotations
import json
import importlib.util
import re
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'


def venv_python(root=ROOT, windows=None):
    windows = os.name == 'nt' if windows is None else windows
    relative = Path('Scripts/python.exe') if windows else Path('bin/python')
    for directory in [root / '.venv', root / ('.venv-windows' if windows else '.venv-posix')]:
        candidate = directory / relative
        if candidate.is_file():
            return candidate
    return None


def environment():
    env = os.environ.copy()
    env.update(PYTHONUTF8='1', PYTHONIOENCODING='utf-8', ADU_MOTION_VIDEO_ROOT=str(ROOT),
               ADU_PYTHON=str(venv_python() or sys.executable))
    env['NODE_PATH'] = str(ROOT / 'node_modules') + (os.pathsep + env['NODE_PATH'] if env.get('NODE_PATH') else '')
    return env


def run(args, *, capture=False):
    result = subprocess.run([str(a) for a in args], env=environment(),
                            capture_output=capture, text=capture, encoding='utf-8' if capture else None)
    if result.returncode:
        if capture:
            print(result.stderr or result.stdout, file=sys.stderr)
        raise SystemExit(result.returncode)
    return result.stdout if capture else None


def py(script, *args, capture=False):
    return run([venv_python() or sys.executable, '-X', 'utf8', script, *args], capture=capture)


def node(script, *args, capture=False):
    return run(['node', script, *args], capture=capture)


def project_end(project):
    if os.environ.get('END'):
        value = float(os.environ['END'])
    else:
        value = float(json.loads(node(SCRIPTS / 'render_project.mjs', project / os.environ.get('HTML', 'index.html'),
                                      '--probe', capture=True))['end'])
    if not math.isfinite(value) or value <= 0:
        raise ValueError('END must be finite and positive')
    return value


def new_project(destination):
    if destination.exists() or destination.is_symlink() or not destination.parent.is_dir():
        raise ValueError('New project must not exist and its parent must already exist')
    shutil.copytree(ROOT / 'template', destination)
    for name in ('sc', 'stills', 'assets'):
        (destination / name).mkdir(exist_ok=True)
    for name in ('talkmap.js', 'face.js', 'subs.js', 'wall.js'):
        file = destination / name
        if not file.exists():
            file.write_text('// Optional data absent.\n', encoding='utf-8')
    from font_policy import install
    css, _ = install({}, {}, destination, destination)
    file = destination / 'style.css'
    file.write_text(css + file.read_text(encoding='utf-8'), encoding='utf-8')


def setup():
    npm = shutil.which('npm')
    if not npm:
        raise ValueError('Install Node.js with npm first')
    if os.name == 'nt':
        # npm.cmd cannot be passed to CreateProcess; execute npm's JS entry
        # directly rather than sending user paths through cmd.exe quoting.
        directory = Path(npm).parent
        cli = next((p for p in [directory / 'node_modules/npm/bin/npm-cli.js',
                               directory.parent / 'lib/node_modules/npm/bin/npm-cli.js'] if p.is_file()), None)
        if not cli:
            raise ValueError('npm JS entry not found; use a standard Node.js installation')
        run(['node', cli, 'ci', '--prefix', ROOT])
    else:
        run([npm, 'ci', '--prefix', ROOT])
    python = venv_python()
    if not python:
        directory = ROOT / '.venv'
        if directory.exists():
            directory = ROOT / ('.venv-windows' if os.name == 'nt' else '.venv-posix')
        run([sys.executable, '-X', 'utf8', '-m', 'venv', directory])
        python = venv_python()
    run([python, '-X', 'utf8', '-m', 'pip', 'install', '-r', ROOT / 'requirements-runtime.txt'])
    py(SCRIPTS / 'doctor.py')


def mix(project, explicit_volume=None, voice=None):
    helper = project / 'audio_runtime/mix_recipe.py'
    if not helper.is_file(): helper = SCRIPTS / 'mix_recipe.py'
    module_spec = importlib.util.spec_from_file_location('adu_project_mix_recipe', helper)
    recipe = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(recipe)
    effective_volume, effective_voice, graph, save = (getattr(recipe, name) for name in
                                                    ('effective_volume', 'effective_voice', 'graph', 'save'))
    end = project_end(project)
    volume = effective_volume(project, explicit_volume)
    voice = effective_voice(project, voice or os.environ.get('VOICE'))
    for name in ('bgm.wav', 'sfx.wav'):
        if not (project / name).is_file():
            raise ValueError('Missing ' + name + '; run audio first')
    silence = ['-f', 'lavfi', '-t', end, '-i', 'anullsrc=r=48000:cl=stereo']
    if voice == 'file' and not (project / 'voice.wav').is_file():
        raise ValueError('Missing voice.wav; use VOICE=none only for intentional narration-free projects')
    voice_input = ['-i', project / 'voice.wav'] if voice == 'file' else silence
    show_input = ['-i', project / 'showaudio.wav'] if (project / 'showaudio.wav').is_file() else silence
    fallback = (f'[0:a]apad,highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=120,loudnorm=I=-16:TP=-1.5:LRA=9,asplit=3[v][vsc][vsc2];'
                f'[1:a]volume=1.0[sh0];[sh0][vsc2]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350[sh];'
                f'[2:a]volume={volume}[b];[b][vsc]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=450[bd];'
                f'[3:a]volume=0.5,highpass=f=60[s];[v][sh][bd][s]amix=inputs=4:normalize=0:duration=longest,atrim=0:{end},alimiter=limit=0.92:level=false,loudnorm=I=-15.5:TP=-1.2:LRA=9,aresample=48000[out]')
    filter_graph = graph(project, fallback, end, volume, voice, explicit_volume is not None or bool(os.environ.get('VOICE')))
    run(['ffmpeg', '-y', '-loglevel', 'error', *voice_input, *show_input, '-i', project / 'bgm.wav',
         '-i', project / 'sfx.wav', '-filter_complex', filter_graph, '-map', '[out]', '-c:a', 'pcm_s16le', project / 'mix.wav'])
    save(project, end, volume, voice, filter_graph)
    audio_metrics(project / 'mix.wav', peaks=False)


def audio_metrics(file, *, peaks=True):
    """Preserve loudness/peak diagnostics without grep or shell pipelines."""
    for filter_name, pattern in [('ebur128', r'^\s+I:.*$'), ('astats', r'^.*Peak level dB:.*$')]:
        if filter_name == 'astats' and not peaks: continue
        result = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(file), '-vn', '-af', filter_name,
                                 '-f', 'null', '-'], env=environment(), capture_output=True,
                                text=True, encoding='utf-8', errors='replace')
        if result.returncode: raise ValueError(result.stderr)
        rows = re.findall(pattern, result.stderr, re.MULTILINE)
        if not rows: raise ValueError('Missing ' + filter_name + ' audio diagnostic')
        print(rows[-1].strip())


def render(project, output, segments='5', portrait=False):
    html = 'index.html'; extra = []
    if (project / 'macro_plan.json').is_file():
        from pack_layout import project_dimensions
        width, height = project_dimensions(project)
        if portrait and height <= width:
            raise ValueError('vert requires a portrait project layout; rebuild with layout=portrait first')
    elif portrait:
        html = 'vert.html'; extra = ['--width', '1080', '--height', '1920']
    else:
        extra = ['--width', '1920', '--height', '1080']
    for key, flag in [('W', '--width'), ('H', '--height'), ('END', '--end')]:
        if os.environ.get(key):
            if flag in extra:
                at = extra.index(flag); del extra[at:at + 2]
            extra.extend([flag, os.environ[key]])
    silent = os.environ.get('SILENT', '0')
    if silent not in {'0', '1'}:
        raise ValueError('SILENT must be 0 or 1')
    if silent == '1': extra.append('--no-audio')
    py(SCRIPTS / 'export_project.py', project, output, '--html', os.environ.get('HTML', html),
       '--fps', os.environ.get('FPS', '60'), '--segments', segments, *extra)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ('help', '--help', '-h'):
        print(__doc__ + '\nCommands: doctor, setup, packs, new, import, demo, stills, audio, mix, render, vert, seg, check,\n'
              'auto-capabilities, auto-plan, auto-build, macro-spec, macro-plan, macro-build,\n'
              'macro-rematch, macro-apply-rematch, preview, repair-plan, repair-apply')
        return
    command, *args = args
    direct = {'doctor': ('doctor.py', []), 'packs': ('pack_catalog.py', ['list']),
              'auto-capabilities': ('auto_templates.py', ['capabilities']),
              'auto-plan': ('auto_templates.py', ['plan']), 'auto-build': ('build_auto_project.py', []),
              'macro-plan': ('plan_macro_project.py', []), 'macro-rematch': ('rematch_macro_project.py', ['propose']),
              'macro-apply-rematch': ('rematch_macro_project.py', ['apply']), 'preview': ('preview_delivery.py', []),
              'repair-plan': ('repair_talk.py', ['plan']), 'repair-apply': ('repair_talk.py', ['apply'])}
    if command in direct:
        script, prefix = direct[command]; py(SCRIPTS / script, *prefix, *args); return
    if command == 'setup':
        if args: raise ValueError('setup accepts no arguments')
        setup(); return
    if command in ('macro-build', 'macro-spec'):
        if len(args) < 2: raise ValueError(command + ' needs a pack and paths')
        from pack_catalog import resolve
        py(SCRIPTS / 'build_macro_project.py', 'build' if command == 'macro-build' else 'scaffold',
           resolve(args[0], ROOT / 'packs'), *args[1:]); return
    if not args: raise ValueError(command + ' needs a project/file path')
    project = Path(args[0]).expanduser().resolve()
    if command == 'new' and len(args) == 1: new_project(project)
    elif command == 'import' and len(args) >= 2:
        py(SCRIPTS / 'import_talk.py', *args, '--fps', os.environ.get('FPS', '60'), '--size', os.environ.get('TALK_SIZE', '720x1280'))
    elif command == 'audio' and len(args) == 1:
        node(SCRIPTS / 'dump_sfx.mjs', project / os.environ.get('HTML', 'index.html'), project / 'sfx.json')
        py(project / 'audio.py')
    elif command == 'mix' and len(args) in (1, 2): mix(project, args[1] if len(args) == 2 else None)
    elif command in ('render', 'vert') and len(args) in (2, 3): render(project, args[1], args[2] if len(args) == 3 else os.environ.get('K', '5'), command == 'vert')
    elif command == 'seg' and len(args) in (3, 4):
        if not args[1].isdigit(): raise ValueError('Segment index must be a nonnegative integer')
        print('Rendering all segments freshly; no old cache reused.')
        render(project, args[2], args[3] if len(args) == 4 else '5')
    elif command == 'stills' and len(args) == 2:
        parent = project / 'stills'; parent.mkdir(exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix='run-', dir=parent))
        output.rmdir()  # renderer owns the new output directory
        extra = [value for k, flag in [('W', '--width'), ('H', '--height'), ('END', '--end')]
                 if os.environ.get(k) for value in (flag, os.environ[k])]
        node(SCRIPTS / 'render_project.mjs', project / os.environ.get('HTML', 'index.html'), '--stills-dir', output, '--times', args[1], *extra)
    elif command == 'check' and len(args) == 1:
        run(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', project])
        run(['ffmpeg', '-v', 'error', '-xerror', '-i', project, '-map', '0:v:0', '-map', '0:a?', '-f', 'null', '-'])
        streams = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_streams', '-of', 'json', project], capture=True))['streams']
        if streams: audio_metrics(project)
        else: print('Audio: none (silent video)')
    elif command == 'demo' and len(args) == 1:
        new_project(project)
        audio = project / 'audio.py'; text = audio.read_text(encoding='utf-8')
        old = "MUSIC = dict(mode='track', path='', offset=None)"
        if text.count(old) != 1: raise ValueError('Demo music recipe differs; review explicit no-BGM binding')
        audio.write_text(text.replace(old, "MUSIC = dict(mode='none')"), encoding='utf-8')
        main(['audio', str(project)]); mix(project, voice='none'); render(project, project / 'demo.mp4', os.environ.get('K', '3'))
    else: raise ValueError('Unknown command or invalid arguments; run --help')


if __name__ == '__main__':
    # Python 3.10-3.14 on Windows can otherwise decode source as a legacy code
    # page. Enable UTF-8 before importing the rest of the source workflow.
    if not sys.flags.utf8_mode:
        raise SystemExit(subprocess.call([sys.executable, '-X', 'utf8', __file__, *sys.argv[1:]], env=environment()))
    try:
        main()
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr); raise SystemExit(1)
