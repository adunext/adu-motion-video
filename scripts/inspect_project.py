#!/usr/bin/env python3
"""Read-only inventory for local HTML/DOM video projects; never executes source."""
import argparse
import json
import os
from pathlib import Path
import re
from html.parser import HTMLParser
from urllib.parse import unquote, urljoin, urlsplit

SOURCE_EXT = {'.html', '.js', '.mjs', '.css', '.py', '.sh', '.json', '.srt'}
SKIP = {'node_modules', '.git', '.venv', '__pycache__'}
NUMBER = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)'
SCENE = re.compile(r'new\s+Scene\(\s*(' + NUMBER + r')\s*,\s*(' + NUMBER + r')\s*,')
END = re.compile(r'(?:window\.)?\bEND\s*=\s*(' + NUMBER + r')\s*;')
PATH = re.compile(r'''["'`]((?:file:///|/(?:Users|Volumes|tmp|private|var|System|Library|opt|home|usr)/|~/)[^"'`\r\n]+)["'`]''')


class Sources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.base = None

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == 'base' and self.base is None and 'href' in attr:
            self.base = attr['href']
        if tag == 'script' and attr.get('src'):
            self.refs.append(attr['src'])
        if tag == 'link' and attr.get('rel') == 'stylesheet' and attr.get('href'):
            self.refs.append(attr['href'])


def safe_path(value):
    """Paths only: never include query strings, fragments, credentials or source lines."""
    value = value.split('?', 1)[0].split('#', 1)[0]
    return re.sub(r'(?i)(?:sk-|bearer\s+|token[=:]|key[=:])[\w.-]+', '[REDACTED]', value)


def inspect(root):
    files, directories = [], {}
    for parent, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not d.startswith('.') and not (Path(parent) / d).is_symlink())
        for name in sorted(names):
            path = Path(parent) / name
            if name.startswith('.') or path.is_symlink() or not path.is_file():
                continue
            relative = path.relative_to(root)
            if len(relative.parts) > 1:
                directories[relative.parts[0]] = directories.get(relative.parts[0], 0) + 1
            if path.suffix.lower() in SOURCE_EXT and path.stat().st_size <= 4_000_000:
                files.append(path)
    texts = {p: p.read_text(encoding='utf-8', errors='replace') for p in files}
    entry = root / 'index.html'
    parser = Sources()
    parser.feed(texts.get(entry, ''))
    active, refs = {entry}, []
    base = urljoin(entry.as_uri(), parser.base) if parser.base is not None else entry.as_uri()
    for ref in parser.refs:
        parts = urlsplit(urljoin(base, ref))
        if parts.scheme != 'file' or parts.netloc not in ('', 'localhost'):
            refs.append({'kind': 'remote', 'host': parts.hostname or '(unknown)'})
            continue
        path = Path(unquote(parts.path)).resolve()
        active.add(path)
        refs.append({'path': safe_path(ref), 'resolved_path': safe_path(os.path.relpath(path, root)), 'exists': path.exists()})
        # A base may reference a sibling source; read only this explicitly linked file.
        if path not in texts and path.is_file() and path.suffix.lower() in SOURCE_EXT and path.stat().st_size <= 4_000_000:
            texts[path] = path.read_text(encoding='utf-8', errors='replace')
            files.append(path)
    scenes, ends, dependencies = [], [], []
    for path, source in texts.items():
        rel = os.path.relpath(path, root)
        for match in SCENE.finditer(source):
            scenes.append({'file': rel, 'line': source.count('\n', 0, match.start()) + 1,
                           'active': path in active, 'start': float(match[1]), 'end': float(match[2])})
        for match in END.finditer(source):
            ends.append({'file': rel, 'active': path in active, 'seconds': float(match[1])})
        seen = set()
        for match in PATH.finditer(source):
            value = safe_path(match[1])
            if value in seen:
                continue
            seen.add(value)
            local = unquote(urlsplit(value).path) if value.startswith('file:') else value
            dynamic = '${' in local or '[REDACTED]' in local
            dependencies.append({'file': rel, 'line': source.count('\n', 0, match.start()) + 1,
                                 'path': value, 'temporary': local.startswith(('/tmp/', '/private/tmp/', '/var/folders/')),
                                 'exists': None if dynamic else Path(local).expanduser().exists(), 'dynamic': dynamic})
    joined = '\n'.join(texts.get(p, '') for p in active)
    renderer = 'custom DOM / renderAt(t)' if 'renderAt' in joined else 'undetermined (static inspection only)'
    return {'project': str(root), 'entry': str(entry) if entry.exists() else None,
            'renderer': renderer, 'entry_references': refs,
            'main_sources': [{'path': os.path.relpath(p, root), 'bytes': p.stat().st_size, 'active': p in active}
                             for p in files if p.parent == root or p in active],
            'end_declarations': ends, 'scenes': scenes,
            'resource_directory_file_counts': directories, 'absolute_path_dependencies': dependencies,
            'limits': 'Static literal scan; computed paths/timings, unused code and media sync require manual review. No project code executed.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    if not root.is_dir():
        parser.error('project must be an existing directory')
    print(json.dumps(inspect(root), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
