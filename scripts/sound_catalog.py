"""Owned synthesis recipes and measured per-event support, no sampled recordings."""
import hashlib
import numpy as np
import audiolib as A

VERSION = 'adu-sound-recipes/2'
FAMILIES = {
    'paper': dict(character='paper motion and contact', cutoffHz=6200),
    'editorial': dict(character='restrained page and margin', cutoffHz=6200),
    'instrument': dict(character='typing, check and delivery', cutoffHz=None),
    'sticker': dict(character='contact, stamp and level change', cutoffHz=None),
    'depth': dict(character='depth entrance and inspection', cutoffHz=None),
    'kinetic': dict(character='word impact and rhythmic cards', cutoffHz=None),
    'performance': dict(character='object motion and response', cutoffHz=None),
}


def measure(event):
    dry = A.render_event(event)
    wet = A.render_event(event, wet=True)
    peak = np.max(np.abs(dry), axis=1)
    audible = np.flatnonzero(peak > max(1e-8, peak.max()*1e-3))
    return dict(recipe=event['type'], version=VERSION, eventId=A.event_identity(event),
                sampleRate=A.SR, drySamples=len(dry), wetSamples=len(wet),
                drySupportSeconds=len(dry)/A.SR, wetSupportSeconds=len(wet)/A.SR,
                attackThresholdDb=-60, attackSeconds=int(audible[0])/A.SR if len(audible) else None,
                peakSeconds=int(np.argmax(peak))/A.SR,
                drySha256=hashlib.sha256(dry.tobytes()).hexdigest(),
                wetSha256=hashlib.sha256(wet.tobytes()).hexdigest(),
                license='Owned synthesis code; repository LICENSE applies; no source commercial recording',
                family=event.get('soundFamily','performance'),
                review='Buffer support and threshold measurements; continuous listening required')
