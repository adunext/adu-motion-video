"""No browser or encoder is needed to check the installed source update path."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('source_update',ROOT/'scripts/update_source.py')
update=importlib.util.module_from_spec(spec)
spec.loader.exec_module(update)


class SourceUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='motiongit-source-update-test-')
        self.addCleanup(self.temporary.cleanup)
        self.base=Path(self.temporary.name)
        self.installed=self.base/'installed';(self.installed/'scripts').mkdir(parents=True)
        self.renderer=self.installed/'scripts/render_project.mjs'
        self.module=self.installed/'scripts/output-signature.mjs'
        self.renderer.write_bytes((ROOT/'scripts/render_project.mjs').read_bytes()+b'\n// retain unrelated source edit\n')
        self.module.write_bytes(b'// altered official runtime')
        (self.installed/'project').mkdir()
        (self.installed/'project/output-signature.json').write_text('{"schema":"adu-output-signature/1","enabled":false}')
        (self.installed/'project/config.json').write_text('{"user":"preserve"}')
        (self.installed/'unrelated.txt').write_text('keep')

    def snapshot(self):
        return {str(p.relative_to(self.installed)):p.read_bytes() for p in self.installed.rglob('*') if p.is_file()}

    def test_restores_changed_and_empty_module_and_retains_configuration(self):
        initial=self.snapshot()
        for body in [b'user altered official code',b'']:
            self.module.write_bytes(body)
            result=update.update_source(self.installed)
            self.assertIn('scripts/output-signature.mjs',result['updated'])
            self.assertFalse(result['projectsWritten']);self.assertFalse(result['configurationWritten'])
            self.assertEqual(self.module.read_bytes(),(ROOT/'scripts/output-signature.mjs').read_bytes())
            current=self.snapshot()
            for name in initial:
                if name!='scripts/output-signature.mjs':self.assertEqual(current[name],initial[name])

    def test_repeated_update_is_current(self):
        update.update_source(self.installed)
        first=self.snapshot()
        self.assertEqual(update.update_source(self.installed)['updated'],[])
        self.assertEqual(self.snapshot(),first)

    def test_unknown_renderer_fails_before_writing(self):
        self.renderer.write_text('const unknown=true;')
        before=self.snapshot()
        with self.assertRaises(ValueError):update.update_source(self.installed)
        self.assertEqual(self.snapshot(),before)

    def test_invalid_new_distribution_fails_before_writing(self):
        distribution=self.base/'invalid-new-source';(distribution/'scripts').mkdir(parents=True)
        shutil.copyfile(ROOT/'source-update.json',distribution/'source-update.json')
        for name in ['render_project.mjs','output-signature.mjs']:
            shutil.copyfile(ROOT/'scripts'/name,distribution/'scripts'/name)
        (distribution/'scripts/output-signature.mjs').write_bytes(b'bad download')
        before=self.snapshot()
        with self.assertRaises(ValueError):update.update_source(self.installed,distribution)
        self.assertEqual(self.snapshot(),before)

    @unittest.skipUnless(hasattr(os,'symlink'),'symlinks unavailable')
    def test_symlinked_scripts_are_rejected(self):
        scripts=self.installed/'scripts';moved=self.base/'moved-scripts';scripts.rename(moved);scripts.symlink_to(moved,target_is_directory=True)
        before=(moved/'output-signature.mjs').read_bytes()
        with self.assertRaises(ValueError):update.update_source(self.installed)
        self.assertEqual((moved/'output-signature.mjs').read_bytes(),before)

    def test_partial_failure_restores_every_managed_file(self):
        before=self.snapshot();replace=os.replace;calls=[]
        def fail_second(source,target):
            calls.append(target)
            if len(calls)==2:raise OSError('simulated second replacement failure')
            return replace(source,target)
        replace_files=update.replace_managed_files
        with patch.object(update,'replace_managed_files',side_effect=lambda files:replace_files(files,replace=fail_second)):
            with self.assertRaises(OSError):update.update_source(self.installed)
        self.assertEqual(self.snapshot(),before)
        self.assertEqual(list((self.installed/'scripts').glob('.motiongit-update-*')),[])

    def test_normal_pipeline_entry_uses_this_distribution(self):
        result=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts/pipeline.py'),'update-source',str(self.installed)],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        self.assertEqual(result.returncode,0,result.stderr)
        report=json.loads(result.stdout)
        self.assertEqual(report['profile'],'motiongit.legacy-source-update-result/1')
        self.assertEqual(report['sha256']['scripts/output-signature.mjs'],'06792ac6b237bfe911f9ba58a459e5d3b957774e4ee97a3f240f45338e9993cc')
        self.assertTrue(self.renderer.read_text().endswith('// retain unrelated source edit\n'))

    def test_managed_payload_is_bound_to_reviewed_candidate(self):
        expected={'scripts/output-signature.mjs':'06792ac6b237bfe911f9ba58a459e5d3b957774e4ee97a3f240f45338e9993cc',
                  'scripts/render_project.mjs':'f78b2499e918b5f344cfbaf0a877f2b3fa7e225511ec732cc4c9d827b7e1c899'}
        self.assertEqual(json.loads((ROOT/'source-update.json').read_text())['sha256'],expected)
        for name,digest in expected.items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)


if __name__=='__main__':unittest.main()
