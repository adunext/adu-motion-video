#!/usr/bin/env python3
"""Apply a verified source distribution to one explicitly selected older install.

The payload and transform come from the reviewed v3.14.1 compatibility candidate.
Only the two declared runtime files are managed; project configuration is untouched.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile

def upgrade_renderer(source):
    imported="import { createSignature } from './output-signature.mjs';"
    if source.count(imported)>1:raise ValueError('Duplicate managed signature import')
    if imported not in source:
        anchor="import { chrome } from './chrome.mjs';"
        if source.count(anchor)!=1 or any('import ' in line and 'createSignature' in line for line in source.splitlines()):
            raise ValueError('Unknown legacy renderer import layout; no source files written')
        source=source.replace(anchor,anchor+'\n'+imported)
    if source.count(imported)!=1:raise ValueError('Managed signature import was not installed')
    source=source.replace('if (signature) await signature.before();','if (signature) await signature.before(t);')
    anchor="    const configFile = path.join(path.dirname(opt.entry), 'output-signature.json');"
    end="    if (opt['stills-dir']) {"
    if source.count(anchor)!=1 or source.count(end)!=1:raise ValueError('Unknown legacy managed configuration region; no source files written')
    a=source.index(anchor);b=source.index(end,a)
    managed="""    // motiongit-managed-output: restored during each managed source update.
    const configFile = path.join(path.dirname(opt.entry), 'output-signature.json');
    const config = fs.existsSync(configFile) ? JSON.parse(fs.readFileSync(configFile, 'utf8')) : { schema: 'adu-output-signature/1', enabled: true };
    if (config.schema !== 'adu-output-signature/1' || typeof config.enabled !== 'boolean') throw Error('Invalid output-signature.json');
    { // Official managed output is restored even for a historical enabled:false.
      const base = path.dirname(opt.entry);
      if (config.assets !== undefined && typeof config.assets !== 'string') throw Error('Signature asset directory must be a relative string');
      const assets = config.assets === undefined ? undefined : path.resolve(base, config.assets);
      if (config.assets !== undefined && (path.isAbsolute(config.assets) || path.relative(base, assets).startsWith('..'))) throw Error('Signature assets must be inside the project');
      const selector = await page.locator('#stage').count() ? '#stage' : 'body';
      // SUBS is the already bound current production transcript. Never CONFIG.brand.
      const inputs = await page.evaluate(() => ({captions:typeof SUBS!=='undefined'?SUBS.map(row=>({text:row.text??row[(window.CONFIG?.subtitleLanguage??document.documentElement.lang).startsWith('en')?'en':'zh']})):[]}));
      signature = await createSignature(page, { requireContentHeader:true, header:config.header, branding:config.branding, inputs, width: opt.width, height: opt.height, duration: timelineEnd, fps: opt.fps, selector, mode: 'dom', assets });
    }
"""
    # A prior managed comment belongs to this region too; do not duplicate it.
    preceding='    // motiongit-managed-output: restored during each managed source update.\n'
    if source[:a].endswith(preceding):a-=len(preceding)
    return source[:a]+managed+source[b:]


def replace_managed_files(updates, *, replace=os.replace):
    originals={}
    staged={}
    committed=[]
    for target in updates:
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ValueError('Managed target must be a regular file: '+str(target))
        originals[target]=(target.read_bytes(),stat.S_IMODE(target.stat().st_mode)) if target.exists() else None
    def stage(target,body,mode):
        temporary=None
        try:
            with tempfile.NamedTemporaryFile(prefix='.motiongit-update-',dir=target.parent,delete=False)as handle:
                temporary=Path(handle.name)
                handle.write(body);handle.flush();os.fsync(handle.fileno());os.chmod(temporary,mode)
        except BaseException:
            if temporary is not None:temporary.unlink(missing_ok=True)
            raise
        return temporary
    try:
        for target,body in updates.items():
            original=originals[target];staged[target]=stage(target,body,original[1] if original else 0o644)
        try:
            for target,temporary in staged.items():
                replace(temporary,target);committed.append(target)
        except BaseException:
            errors=[]
            for target in reversed(committed):
                original=originals[target]
                try:
                    if original is None:target.unlink(missing_ok=True)
                    else:
                        rollback=stage(target,*original)
                        try:os.replace(rollback,target)
                        finally:rollback.unlink(missing_ok=True)
                except BaseException as error:errors.append(str(error))
            if errors:raise RuntimeError('Managed source update failed and restoration was incomplete: '+'; '.join(errors))
            raise
    finally:
        for temporary in staged.values():temporary.unlink(missing_ok=True)


def update_source(installed_source, distribution=None):
    distribution=Path(distribution) if distribution is not None else Path(__file__).resolve().parents[1]
    metadata=json.loads((distribution/'source-update.json').read_text(encoding='utf-8'))
    managed={'scripts/render_project.mjs','scripts/output-signature.mjs'}
    if metadata.get('profile')!='motiongit.legacy-source-update/1' or set(metadata.get('sha256',{}))!=managed:
        raise ValueError('Invalid source update manifest')
    payload={}
    for name,digest in metadata['sha256'].items():
        source=distribution/name
        if source.is_symlink() or not source.is_file() or not isinstance(digest,str) or not re.fullmatch('[a-f0-9]{64}',digest):
            raise ValueError('Invalid source update payload: '+name)
        body=source.read_bytes()
        if hashlib.sha256(body).hexdigest()!=digest:
            raise ValueError('Official source payload differs: '+name)
        payload[name]=body
    installed=Path(installed_source).expanduser()
    scripts=installed/'scripts'
    if installed.is_symlink() or not installed.is_dir() or scripts.is_symlink() or not scripts.is_dir():
        raise ValueError('Select a regular installed source directory')
    entry=scripts/'render_project.mjs'
    if entry.is_symlink() or not entry.is_file():
        raise ValueError('Installed renderer must be a regular file')
    # Validate both complete results before either file is replaced. Keep source
    # customizations outside the precisely identified managed renderer region.
    text=upgrade_renderer(entry.read_text(encoding='utf-8')).encode()
    updates={scripts/'output-signature.mjs':payload['scripts/output-signature.mjs'],entry:text}
    changed=[str(target.relative_to(installed)) for target,body in updates.items() if not target.exists() or target.read_bytes()!=body]
    replace_managed_files(updates)
    return {'profile':'motiongit.legacy-source-update-result/1','updated':changed,
            'sha256':{name:hashlib.sha256((installed/name).read_bytes()).hexdigest() for name in sorted(managed)},
            'projectsWritten':False,'configurationWritten':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('installed_source',type=Path,help='Explicit path to the older installed source; projects are not an update target')
    args=parser.parse_args()
    print(json.dumps(update_source(args.installed_source),ensure_ascii=False))


if __name__=='__main__':
    try: main()
    except (OSError,ValueError) as error:
        raise SystemExit(str(error))
