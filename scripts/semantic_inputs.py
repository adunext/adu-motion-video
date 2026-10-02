"""Expand a recipe's named semantic fields into its reviewed source bindings.

Paths address dictionaries/lists only. Templates interpolate plain values; they
cannot call code, inspect attributes or alter HTML supplied by the recipe.
"""
import re
from string import Formatter


class SemanticInputError(ValueError):
    pass


def field(data, path):
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*(?:\.(?:[A-Za-z][A-Za-z0-9_]*|[0-9]+))*', path):
        raise SemanticInputError(f'Invalid semantic field path: {path}')
    value = data
    try:
        for part in path.split('.'):
            value = value[int(part)] if isinstance(value, list) and part.isdigit() else value[part]
    except (KeyError, IndexError, TypeError) as exc:
        raise SemanticInputError(f'Missing semantic input {path}') from exc
    return value


def unused_inputs(scene, inputs):
    """Do not silently discard extra list items or misspelled semantic fields."""
    consumed = []
    for slot in scene.get('slots', []):
        if slot.get('inputPath'):
            consumed.append(slot['inputPath'])
        if slot.get('inputTemplate'):
            consumed.extend(name for _, name, _, _ in Formatter().parse(slot['inputTemplate']) if name is not None)

    def leaves(value, prefix=''):
        if isinstance(value, dict) and value:
            for key, child in value.items():
                yield from leaves(child, f'{prefix}.{key}' if prefix else str(key))
        elif isinstance(value, list) and value:
            for index, child in enumerate(value):
                yield from leaves(child, f'{prefix}.{index}')
        else:
            yield prefix

    return [name for name in leaves(inputs) if name and
            not any(name == path or name.startswith(path + '.') for path in consumed)]


def expand_inputs(scene, target):
    inputs = target.get('inputs')
    if inputs is None:
        return target
    if not isinstance(inputs, dict):
        raise SemanticInputError('Scene inputs must be an object')
    unused = unused_inputs(scene, inputs)
    if unused:
        raise SemanticInputError('Unconsumed semantic inputs: ' + ', '.join(unused))
    slots = dict(target.get('slots', {}))
    for slot in scene.get('slots', []):
        path, template = slot.get('inputPath'), slot.get('inputTemplate')
        if path is None and template is None:
            continue
        if slot['id'] in slots:
            raise SemanticInputError(f'{slot["id"]} is supplied through both inputs and slots')
        if path is not None and template is not None:
            raise SemanticInputError(f'{slot["id"]} declares both inputPath and inputTemplate')
        if path is not None:
            slots[slot['id']] = field(inputs, path)
        else:
            pieces = []
            for literal, name, format_spec, conversion in Formatter().parse(template):
                pieces.append(literal)
                if name is not None:
                    if format_spec or conversion:
                        raise SemanticInputError('Semantic templates allow plain field interpolation only')
                    value = field(inputs, name)
                    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
                        raise SemanticInputError(f'{name} needs a plain text or numeric value')
                    pieces.append(str(value))
            slots[slot['id']] = ''.join(pieces)
    return {**target, 'slots': slots}
