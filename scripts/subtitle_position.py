"""Shared spatial configuration; no cue or narration clock modification."""
import math


def resolve_position(value, width, height):
    if value is None:
        return dict(bottomRatio=.18, leftRatio=.15, rightRatio=.15) if height > width else None
    if not isinstance(value, dict) or set(value) - {'bottomRatio', 'leftRatio', 'rightRatio'}:
        raise ValueError('subtitlePosition only accepts bottomRatio/leftRatio/rightRatio')
    default = dict(bottomRatio=.18 if height > width else .08, leftRatio=.15 if height > width else .06, rightRatio=.15 if height > width else .06)
    result = {**default, **value}
    for key, number in result.items():
        if isinstance(number, bool) or not isinstance(number, (float, int)) or not math.isfinite(number) or not 0 <= number < 1:
            raise ValueError('subtitlePosition.' + key + ' must be a finite ratio in [0,1)')
    if result['leftRatio'] + result['rightRatio'] >= .9:
        raise ValueError('subtitlePosition leaves insufficient reading width')
    return result
