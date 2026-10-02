import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from adapt_project import AdaptError, compile_plan
from adaptation import load_profile, manifest_digest, validate_profile
from extract_authored_pack import attach_adaptation_profile, extract
from plan_macro_project import plan, resolve_project_paths


class AdaptationIntakeTest(unittest.TestCase):
    def fixture(self):
        manifest = json.loads((ROOT / 'packs/classic-performance/1.0.0/manifest.json').read_text())
        descriptor = json.loads((ROOT / 'adaptation-profiles/classic-performance/1.0.0.json').read_text())
        descriptor.pop('pack')
        return manifest, descriptor

    def test_extraction_contract_binds_every_actual_unit_and_manifest(self):
        manifest, descriptor = self.fixture()
        for item in descriptor['scenes']:
            item.pop('sourceBlockSha256')
        attach_adaptation_profile(manifest, descriptor)
        profile = load_profile(manifest, Path('/nonexistent'))
        self.assertEqual(profile['pack']['manifestDigest'], manifest_digest(manifest))
        self.assertEqual(validate_profile(profile, manifest)['sceneCount'], 3)
        self.assertNotIn('pack', manifest['adaptationProfile'])

    def test_missing_partial_and_false_source_contracts_reject(self):
        for issue in ('missing', 'partial', 'hash', 'phase', 'seam'):
            with self.subTest(issue=issue):
                manifest, descriptor = self.fixture()
                if issue == 'missing': descriptor = None
                if issue == 'partial': descriptor['scenes'].pop()
                if issue == 'hash': descriptor['scenes'][0]['sourceBlockSha256'] = '0' * 64
                if issue == 'phase': descriptor['scenes'][0]['requiredPhases'] = 'claim'
                if issue == 'seam': descriptor['scenes'][0]['entry'] = {'mode': 'match-cut', 'requiresPrevious': ['absent']}
                with self.assertRaises(ValueError): attach_adaptation_profile(manifest, descriptor)
        manifest, _ = self.fixture()
        attach_adaptation_profile(manifest, None, legacy=True)
        self.assertEqual(manifest['adaptationStatus'], 'unprofiled-legacy')

    def test_unprofiled_new_extraction_fails_without_source_io_or_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proposal = root / 'proposal.json'
            proposal.write_text(json.dumps({'id': 'fixture', 'version': '0.1.0', 'sourceRevision': 'frozen'}))
            with self.assertRaisesRegex(ValueError, 'adaptationProfile'):
                extract(root / 'absent-source', proposal, root / 'output')
            self.assertFalse((root / 'output').exists())

    def test_cli_planning_preserves_input_and_reports_draft_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = ROOT / 'examples/adaptation/01-method-introduction.brief.json'
            before = brief.read_bytes()
            result = plan(ROOT / 'packs/classic-performance/1.0.0', brief, root / 'draft')
            self.assertFalse(result['ready'])
            self.assertEqual(result['scenes'], ['claim-into-container', 'decompose-and-consolidate'])
            self.assertTrue((root / 'draft/report.md').is_file())
            spec = json.loads((root / 'draft/spec.json').read_text())
            manifest, _ = self.fixture()
            with self.assertRaises(AdaptError): compile_plan(manifest, spec, spec_dir=root / 'draft')
            with self.assertRaisesRegex(AdaptError, 'existing'):
                plan(ROOT / 'packs/classic-performance/1.0.0', brief, root / 'draft')
            self.assertEqual(before, brief.read_bytes())

    def test_global_episode_paths_survive_spec_relocation(self):
        brief = {'music': {'mode': 'track', 'path': 'sound.mp3'}, 'monoFontFile': 'mono.ttf',
                 'externalFontFiles': {'title': 'title.woff2', 'missing': ''}}
        before = copy.deepcopy(brief)
        resolved = resolve_project_paths(brief, Path('/episode'))
        self.assertEqual(resolved['music']['path'], '/episode/sound.mp3')
        self.assertEqual(resolved['externalFontFiles']['title'], '/episode/title.woff2')
        self.assertEqual(resolved['externalFontFiles']['missing'], '')
        self.assertEqual(before, brief)


if __name__ == '__main__': unittest.main()
