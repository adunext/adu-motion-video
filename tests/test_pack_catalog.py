import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from pack_catalog import resolve,catalog


class CatalogTest(unittest.TestCase):
    def test_new_routes_enter_without_a_whitelist_and_versions_do_not_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for version in ('1.0.0','1.1.0'):
                pack=root/'new-route'/version;pack.mkdir(parents=True)
                (pack/'manifest.json').write_text(json.dumps({'id':'new-route','version':version,
                    'status':'candidate','scenes':[{'id':'cause','role':'主体推动结果'}]}))
            self.assertEqual(len(catalog(root)),2)
            self.assertEqual(resolve('new-route@1.0.0',root),(root/'new-route/1.0.0').resolve())
            with self.assertRaisesRegex(ValueError,'Multiple versions'):resolve('new-route',root)


if __name__=='__main__':unittest.main()
