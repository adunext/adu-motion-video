#!/usr/bin/env python3
"""Discover pack metadata and resolve an explicit pack version without loading JS."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]


def catalog(root):
    entries=[]
    for path in sorted(root.rglob('manifest.json')):
        data=json.loads(path.read_text())
        if not isinstance(data,dict) or not data.get('id') or not isinstance(data.get('scenes'),list): continue
        entries.append({'id':data['id'],'version':data.get('version','legacy-rc.2'),
                        'status':data.get('status','experimental'),'path':str(path.parent.resolve()),
                        'directory':path.parent.relative_to(root).as_posix(),'title':data.get('title',''),
                        'roles':[s.get('role','') for s in data['scenes']],
                        'units':len(data['scenes']),'environment':data.get('environment',{}),
                        'sourceRevision':data.get('sourceRevision')})
    return entries


def resolve(selection, root):
    supplied=Path(selection).expanduser()
    if supplied.is_dir() and (supplied/'manifest.json').is_file(): return supplied.resolve()
    shortcut=root/selection
    if shortcut.is_dir() and (shortcut/'manifest.json').is_file(): return shortcut.resolve()
    ident,sep,version=selection.partition('@')
    found=[p for p in catalog(root) if p['id']==ident and (not sep or p['version']==version)]
    if not found: raise ValueError(f'Unknown pack/version: {selection}; inspect pack_catalog.py list')
    if len(found)!=1: raise ValueError(f'Multiple versions for {ident}; choose an explicit id@version or pack directory')
    return Path(found[0]['path'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT/'packs')
    sub=parser.add_subparsers(dest='command',required=True)
    listing=sub.add_parser('list');listing.add_argument('--role',help='Filter concise semantic metadata only')
    select=sub.add_parser('resolve');select.add_argument('selection')
    args=parser.parse_args()
    try:
        if args.command=='resolve':print(resolve(args.selection,args.root.resolve()))
        else:
            data=catalog(args.root.resolve())
            if args.role:data=[x for x in data if args.role in x['title'] or any(args.role in r for r in x['roles'])]
            print(json.dumps(data,ensure_ascii=False,indent=2))
    except (ValueError,OSError,json.JSONDecodeError) as exc:raise SystemExit(f'Pack catalog failed: {exc}') from exc
