from pathlib import Path
import ast
from copy import deepcopy
import hashlib
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from adaptation_audio import (audio_boundary_report, DEFAULT_DURATIONS, DURATION_PARAMETERS,
                              GENERATOR_CONTRACT_SHA256, SFX_REVERB_SECONDS, VARIABLE_DURATION_TYPES)


def plan(native=True, end=10):
    return {'fps': 60, 'end_frame': end * 60, 'scenes': [
        {'id': 'before', 'output_start_frame': 0, 'output_end_frame': 300,
         'source_start': 0, 'source_end': 5},
        {'id': 'after', 'output_start_frame': 300, 'output_end_frame': end * 60,
         'source_start': 5 if native else 30, 'source_end': 5 + end - 5 if native else 30 + end - 5}]}


class AdaptationAudioTest(unittest.TestCase):
    def test_runtime_is_authoritative_and_inputs_are_untouched(self):
        p = plan(); p['sfx'] = [{'at': 1, 'type': 'hit'}]
        cues = {'end': 10, 'sfx': [{'t': 2, 'type': 'chime', 'g': .7, 'p': .2}]}
        baseline = deepcopy((p, cues))
        r = audio_boundary_report(p, cues)
        self.assertEqual((p, cues), baseline)
        self.assertEqual(r['events'][0]['event'], cues['sfx'][0])
        self.assertEqual(r['events'][0]['durationSeconds'], 2.2)
        self.assertEqual(r['events'][0]['potentialTailEnd'], 5.1)
        self.assertTrue(r['coverage']['runtimeCaptureComplete'])
        self.assertEqual(r['mutations'], [])
        self.assertEqual(audio_boundary_report(p, [])['events'], [])

    def test_manifest_reference_is_partial_even_when_empty(self):
        p = plan(); p['audio'] = {'sfxReferenceEvents': [{'t': 3, 'type': 'card'}]}
        r = audio_boundary_report(p)
        self.assertEqual(len(r['events']), 1)
        self.assertFalse(r['coverage']['runtimeCaptureComplete'])
        self.assertIn('runtime-capture-pending', [f['code'] for f in r['findings']])
        self.assertEqual(audio_boundary_report(plan())['status'], 'needs-listening')

    def test_native_overlap_is_information_reordered_overlap_needs_review(self):
        cues = [{'t': 4.8, 'type': 'hit'}]
        normal = audio_boundary_report(plan(), cues)
        changed = audio_boundary_report(plan(False), cues)
        a = next(f for f in normal['findings'] if f['code'] == 'cross-boundary-tail')
        b = next(f for f in changed['findings'] if f['code'] == 'cross-boundary-tail')
        self.assertEqual(a['level'], 'info')
        self.assertEqual(b['level'], 'review')
        self.assertEqual(normal['events'][0]['event'], changed['events'][0]['event'])

    def test_entry_lead_in_is_retained_and_not_assigned_to_outgoing_scene(self):
        r = audio_boundary_report(plan(False), [{'t': 4.85, 'type': 'whoosh'},
                                               {'t': 4.9, 'type': 'card', 'sceneInstanceId': 'after'}])
        self.assertEqual(r['boundaries'][0]['possibleLeadInEvents'], [0, 1])
        self.assertEqual(r['events'][0]['ownership'], 'unknown')
        self.assertEqual(r['events'][1]['sceneInstanceId'], 'after')

    def test_generator_d_parameter_and_fixed_duration_match_actual_dispatch(self):
        r = audio_boundary_report(plan(), [{'t': 0, 'type': 'typing', 'd': 2.4},
                                          {'t': 0, 'type': 'hit', 'd': .1},
                                          {'t': 0, 'type': 'typing', 'd': -1},
                                          {'t': 0, 'type': 'new-custom', 'd': 2},
                                          {'t': 0, 'type': 'chirp'}])
        self.assertEqual([e['durationSeconds'] for e in r['events']], [2.4, 1., None, None, None])
        self.assertEqual(len([f for f in r['findings'] if f['code'] == 'unknown-event-duration']), 3)

    def test_ending_support_is_an_estimate_not_a_claim_of_audible_cut(self):
        r = audio_boundary_report(plan(), [{'t': 9.2, 'type': 'chime'}])
        f = next(f for f in r['findings'] if f['code'] == 'estimated-tail-beyond-output')
        self.assertEqual(f['dryBeyondSeconds'], 1.4)
        self.assertEqual(f['potentialTailBeyondSeconds'], 2.3)
        self.assertIn('does not prove', f['note'])
        self.assertEqual(r['status'], 'needs-listening')

    def test_layered_hits_count_once_but_three_distinct_beats_are_reported(self):
        pair = [{'t': 2, 'type': 'hit'}, {'t': 2, 'type': 'crack'}]
        r = audio_boundary_report(plan(), pair)
        self.assertFalse(any(f['code'] == 'dense-impact-beats' for f in r['findings']))
        r = audio_boundary_report(plan(), pair + [{'t': 2.2, 'type': 'hit'}, {'t': 2.4, 'type': 'stamp'}])
        f = next(f for f in r['findings'] if f['code'] == 'dense-impact-beats')
        self.assertEqual(f['distinctBeats'], 3)
        self.assertEqual(f['eventIndices'], [0, 1, 2, 3])

    def test_malformed_muted_and_outside_events_are_preserved(self):
        events = [None, {'type': 'hit'}, {'t': -.1, 'type': 'whoosh'},
                  {'t': 9.8, 'type': 'chime', 'g': 0}, {'t': 11, 'type': 'hit'}]
        r = audio_boundary_report(plan(), events)
        self.assertEqual([e['event'] for e in r['events']], events)
        self.assertEqual(len([f for f in r['findings'] if f['code'] == 'event-outside-output']), 2)
        self.assertFalse(any(f.get('eventIndex') == 3 for f in r['findings']))
        mismatched = audio_boundary_report(plan(), {'end': 9, 'sfx': []})
        self.assertFalse(mismatched['coverage']['runtimeCaptureComplete'])

    def test_duration_inventory_is_locked_to_actual_generator_code_without_numpy(self):
        tree = ast.parse((ROOT / 'scripts/audiolib.py').read_text())
        gen = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'GEN' for t in n.targets))
        self.assertEqual({k.value for k in gen.keys}, set(DEFAULT_DURATIONS) | set(DURATION_PARAMETERS) | VARIABLE_DURATION_TYPES)
        for key, value in zip(gen.keys, gen.values):
            parameters = [n for n in ast.walk(value) if isinstance(n, ast.Call)
                          and isinstance(n.func, ast.Attribute) and n.func.attr == 'get'
                          and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value == 'd']
            if key.value in DURATION_PARAMETERS:
                self.assertEqual(ast.literal_eval(parameters[0].args[1]), DURATION_PARAMETERS[key.value])
            else:
                self.assertFalse(parameters)
        selected, in_sfx = [], False
        for n in tree.body:
            if isinstance(n, ast.FunctionDef) and n.name == 'whoosh': in_sfx = True
            is_gen = isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'GEN' for t in n.targets)
            if (isinstance(n, ast.FunctionDef) and (in_sfx or n.name in ('T', 'bell', 'glock', 'chip', 'sweep'))
                    or isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ('GEN', 'SR') for t in n.targets)):
                selected.append(n)
            if is_gen: in_sfx = False
        digest = hashlib.sha256('\n'.join(ast.dump(n, include_attributes=False) for n in selected).encode()).hexdigest()
        self.assertEqual(digest, GENERATOR_CONTRACT_SHA256, 'SFX generators changed: re-audit duration support before updating this contract')
        audio_tree = ast.parse((ROOT / 'scripts/macro_audio.py').read_text())
        calls = [n for n in ast.walk(audio_tree) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute) and n.func.attr == 'reverb'
                 and n.args and isinstance(n.args[0], ast.Name) and n.args[0].id == 'sfx']
        self.assertEqual(ast.literal_eval(calls[0].args[1]), SFX_REVERB_SECONDS)


if __name__ == '__main__': unittest.main()
