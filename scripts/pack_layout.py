"""Explicit output geometry, independent of authored source/audio clocks."""
from pathlib import Path
import hashlib
import json
import shutil


def resolve_layout(manifest: dict, spec: dict) -> dict:
    name = spec.get('layout', 'landscape')
    if name not in ('landscape', 'portrait'):
        raise ValueError('layout must be landscape or portrait')
    variants = manifest.get('layouts', {})
    variant = variants.get(name)
    if variant is None:
        if name == 'portrait':
            raise ValueError('This frozen pack has no portrait contract; select its portrait candidate version')
        variant = {'width': manifest.get('width', 1920), 'height': manifest.get('height', 1080)}
    width, height = variant.get('width'), variant.get('height')
    if any(type(v) is not int or v <= 0 for v in (width, height)):
        raise ValueError('Layout dimensions must be positive integers')
    if name == 'portrait' and not height > width:
        raise ValueError('Portrait contract needs height > width')
    return {'name': name, 'width': width, 'height': height,
            'runtime': variant.get('runtime'), 'stylesheet': variant.get('stylesheet')}


def install_layout(pack_dir: Path, manifest: dict, plan: dict, stage: Path) -> tuple[str, str, list[str]]:
    layout = plan['layout']
    files = []
    for key in ('runtime', 'stylesheet'):
        relative = layout.get(key)
        if not relative:
            continue
        if not isinstance(relative, str) or Path(relative).is_absolute() or '..' in Path(relative).parts:
            raise ValueError('Layout asset must be a local pack file')
        source = pack_dir / relative
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if manifest.get('files', {}).get(relative) != digest:
            raise ValueError('Layout asset differs from its frozen fingerprint: ' + relative)
        target = stage / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        files.append(relative)
    if layout['name'] == 'portrait' and not layout.get('runtime'):
        raise ValueError('Portrait build requires a frozen runtime; legacy sidecar-only packs need their layout command')
    configuration = ('\nCONFIG.width=' + str(layout['width']) + ';CONFIG.height=' + str(layout['height']) + ';\n'
                     'window.PACK_LAYOUT=' + json.dumps({**layout, 'pack': manifest['id']}) + ';\n')
    if layout.get('runtime') == 'showcase-layout.js':
        configuration += 'window.SHOWCASE_LAYOUT={...window.PACK_LAYOUT,layout:window.PACK_LAYOUT.name};\n'
    css = '<link rel="stylesheet" href="' + layout['stylesheet'] + '">' if layout.get('stylesheet') else ''
    script = '<script src="' + layout['runtime'] + '"></script>' if layout.get('runtime') else ''
    with (stage / 'config.js').open('a') as handle:
        handle.write(configuration)
    return css, script, files


def project_dimensions(project: Path) -> tuple[int, int] | None:
    for name in ('showcase-layout.json', 'macro_plan.json'):
        path = project / name
        if path.is_file():
            data = json.loads(path.read_text())
            dimensions = (data.get('width'), data.get('height'))
            if any(type(v) is not int or v <= 0 for v in dimensions):
                raise ValueError(name + ' needs positive integer dimensions')
            return dimensions
    return None
