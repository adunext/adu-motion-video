"""Exercise preview publication against real decoded SDR media and evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from color_management import export_plan, fingerprint_file, image_plan
from export_project import probe, sources, verify_frame_clock
from preview_delivery import publish


def run(arguments):
    result = subprocess.run([str(x) for x in arguments], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-4000:])
    return result.stdout


def tree_bytes(directory):
    return {p.relative_to(directory).as_posix(): p.read_bytes()
            for p in sorted(directory.rglob("*")) if p.is_file()}


class PreviewDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="adu-preview-delivery-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / "private-project"
        self.project.mkdir()
        (self.project / "index.html").write_text(
            '<body style="background:#bf7e5b"><script>window.END=.2;window.READY=Promise.resolve();window.renderAt=t=>{};</script>')
        self.output = self.base / "preview"
        self.video = self.export("first.mp4", "0xbf7e5b")

    def export(self, filename, color):
        video = self.base / filename
        run(["ffmpeg", "-n", "-v", "error", "-f", "lavfi", "-i",
             f"color=c={color}:s=64x64:r=30:d=0.2", "-vf",
             "setparams=range=limited:colorspace=bt709:color_primaries=bt709:color_trc=bt709",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-color_range", "tv",
             "-colorspace", "bt709", "-color_trc", "bt709", "-color_primaries", "bt709", video])
        identity = fingerprint_file(video)
        record = {"schema": "adu-motion-video-export/v1", "created_utc": "2026-10-03T12:00:00+08:00",
                  "project": str(self.project), "entry": str(self.project / "index.html"), "output": str(video),
                  "output_sha256": identity["sha256"], "output_size_bytes": identity["sizeBytes"],
                  "fps": 30, "frames": 6, "width": 64, "height": 64, "duration": .2, "audio": None,
                  "reused_segments": False, "verification": "complete media decode",
                  "segments": [{"index": 0, "first_frame": 0, "end_frame_exclusive": 6, "frames": 6}],
                  "frame_clock": verify_frame_clock(video, 6, 30), "color": export_plan(),
                  "source_sha256": sources(self.project), "streams": probe(video)["streams"]}
        Path(str(video) + ".manifest.json").write_text(json.dumps(record))
        return video

    def change_manifest(self, video, change):
        path = Path(str(video) + ".manifest.json")
        record = json.loads(path.read_text())
        change(record)
        path.write_text(json.dumps(record))

    def assert_no_staging(self):
        self.assertEqual(list(self.base.glob(".adu-preview-*")), [])

    def test_new_preview_binds_verified_real_sha_without_private_paths(self):
        # Include a real input-color receipt with deliberately private provenance;
        # publication must use the portable verification result, not leak it.
        source = self.export("private-input.mp4", "0x328a95")
        color = image_plan(source)
        (self.project / "import.json").write_text(json.dumps({"source": "/private/owner/original.mov", "color": color}))
        self.change_manifest(self.video, lambda record: record.update(source_sha256=sources(self.project)))
        original = self.video.read_bytes()
        project_before = tree_bytes(self.project)
        result = publish(self.project, self.video, self.output)
        digest = hashlib.sha256(original).hexdigest()
        record = json.loads((self.output / "delivery.json").read_text())
        self.assertEqual(result["version"], digest)
        self.assertEqual(record["version"], digest)
        self.assertEqual(record["verification"]["output_sha256"], digest)
        self.assertEqual(record["verification"]["status"], "verified")
        self.assertTrue(record["verification"]["importedColor"]["present"])
        self.assertEqual(record["media"], f"video-{digest}.mp4")
        self.assertEqual((self.output / record["media"]).read_bytes(), original)
        for filename in ("delivery.json", "index.html", "player.js"):
            body = (self.output / filename).read_text()
            self.assertNotIn(str(self.base), body)
            self.assertNotIn("/private/owner", body)
        self.assertEqual(tree_bytes(self.project), project_before)
        self.assertEqual(self.video.read_bytes(), original)
        self.assert_no_staging()

    def test_update_keeps_old_immutable_video_and_moves_current_pointer(self):
        first = publish(self.project, self.video, self.output)
        old_media = self.output / first["media"]
        old_bytes = old_media.read_bytes()
        (self.output / "owner-note.txt").write_text("Keep this local note")
        next_video = self.export("second.mp4", "0x3170b5")
        updated = publish(self.project, next_video, self.output, update=True)
        self.assertNotEqual(first["version"], updated["version"])
        record = json.loads((self.output / "delivery.json").read_text())
        self.assertEqual(record["version"], updated["version"])
        self.assertEqual(record["media"], updated["media"])
        self.assertEqual(record["verification"]["output_sha256"], updated["version"])
        self.assertEqual(old_media.read_bytes(), old_bytes)
        self.assertEqual((self.output / updated["media"]).read_bytes(), next_video.read_bytes())
        self.assertEqual(len(list(self.output.glob("video-*.mp4"))), 2)
        self.assertEqual((self.output / "owner-note.txt").read_text(), "Keep this local note")
        self.assert_no_staging()

    def test_old_exports_without_identity_or_clock_never_create_a_preview(self):
        evidence = Path(str(self.video) + ".manifest.json")
        original = evidence.read_bytes()
        for key in ("output_sha256", "frame_clock"):
            with self.subTest(missing=key):
                evidence.write_bytes(original)
                self.change_manifest(self.video, lambda record: record.pop(key))
                changed_evidence = evidence.read_bytes()
                with self.assertRaises(ValueError):
                    publish(self.project, self.video, self.output)
                self.assertFalse(self.output.exists())
                self.assertEqual(evidence.read_bytes(), changed_evidence)
                self.assert_no_staging()
        evidence.unlink()
        with self.assertRaises((ValueError, OSError)):
            publish(self.project, self.video, self.output)
        self.assertFalse(self.output.exists())
        self.assertFalse(evidence.exists())

    def test_changed_video_rejected_before_new_preview_is_created(self):
        self.video.write_bytes(self.video.read_bytes() + b"changed-after-export")
        with self.assertRaisesRegex(ValueError, "Video bytes"):
            publish(self.project, self.video, self.output)
        self.assertFalse(self.output.exists())
        self.assert_no_staging()

    def test_invalid_update_does_not_pollute_existing_preview_or_advance_pointer(self):
        publish(self.project, self.video, self.output)
        before = tree_bytes(self.output)
        next_video = self.export("changed.mp4", "0x2255aa")
        valid_video = next_video.read_bytes()
        next_video.write_bytes(valid_video + b"changed-after-export")
        with self.assertRaisesRegex(ValueError, "Video bytes"):
            publish(self.project, next_video, self.output, update=True)
        self.assertEqual(tree_bytes(self.output), before)
        next_video.write_bytes(valid_video)
        self.change_manifest(next_video, lambda record: record.pop("output_sha256"))
        with self.assertRaisesRegex(ValueError, "output_sha256"):
            publish(self.project, next_video, self.output, update=True)
        self.assertEqual(tree_bytes(self.output), before)
        self.assert_no_staging()

    def test_existing_output_is_never_overwritten_without_update(self):
        publish(self.project, self.video, self.output)
        before = tree_bytes(self.output)
        next_video = self.export("newer.mp4", "0x808080")
        with self.assertRaisesRegex(ValueError, "Refusing existing preview"):
            publish(self.project, next_video, self.output)
        self.assertEqual(tree_bytes(self.output), before)
        manual = self.base / "user-directory"
        manual.mkdir(); (manual / "index.html").write_text("User page")
        with self.assertRaisesRegex(ValueError, "Refusing existing preview"):
            publish(self.project, self.video, manual)
        self.assertEqual(tree_bytes(manual), {"index.html": b"User page"})
        self.assert_no_staging()

    def test_changed_immutable_published_video_is_not_repaired_silently(self):
        first = publish(self.project, self.video, self.output)
        media = self.output / first["media"]
        media.write_bytes(media.read_bytes() + b"changed-in-preview")
        before = tree_bytes(self.output)
        with self.assertRaisesRegex(ValueError, "immutable preview media changed"):
            publish(self.project, self.video, self.output, update=True)
        self.assertEqual(tree_bytes(self.output), before)
        self.assert_no_staging()


if __name__ == "__main__":
    unittest.main()
