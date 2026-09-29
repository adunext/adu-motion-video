"""Meaningful checks for adapting a complete authored scene to new speech."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from adapt_project import AdaptError, compile_plan, write_plan  # noqa: E402


class AdaptProjectTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {
            "id": "sample", "fps": 60, "width": 1920, "height": 1080,
            "scenes": [{
                "id": "full_scene", "source": {"start": 0, "end": 4}, "minFrames": 120,
                "cues": [
                    {"id": "headline", "at": 1, "kind": "word", "lockAfterFrames": 12},
                    {"id": "result", "at": 3, "kind": "word", "lockAfterFrames": 12},
                ],
                "slots": [{"id": "title", "type": "text", "required": True, "maxChars": 12}],
                "sfx": [{"at": 1, "type": "hit"}, {"at": 3, "type": "ding"}],
            }],
        }

    def test_repeats_full_scene_with_independent_word_cues_and_protected_motion(self):
        spec = {
            "pack": "sample", "fps": 60,
            "transcript": [{"id": "a", "start": .9, "end": 2, "text": "新的模型来了",
                            "words": [{"text": "新的", "start": .9, "end": 1.15},
                                      {"text": "模型", "start": 1.15, "end": 1.6},
                                      {"text": "来了", "start": 1.6, "end": 2.0}]}],
            "scenes": [
                {"sceneId": "full_scene", "id": "first", "start": 0, "end": 6,
                 "cues": {"headline": {"phrase": "模型"}, "result": {"at": 4}},
                 "slots": {"title": "模型突破"}},
                {"sceneId": "full_scene", "id": "second", "duration": 4,
                 "cues": {"headline": {"at": 7}, "result": {"at": 9}},
                 "slots": {"title": "下一步"}},
            ],
        }
        plan = compile_plan(self.manifest, spec)
        self.assertEqual(plan["durationFrames"], 600)
        self.assertEqual([s["source_scene_index"] for s in plan["scenes"]], [0, 0])
        first, second = plan["scenes"]
        self.assertEqual(first["source_scene_id"], "full_scene")
        self.assertEqual(first["output_start_frame"], 0)
        self.assertEqual(first["output_end_frame"], 360)
        self.assertEqual(first["texts"], {"title": "模型突破"})
        self.assertEqual(first["cues"][0]["outputFrame"], 69)  # spoken word, not subtitle-line start
        self.assertIn({"source": 1.2, "output_frame": 81}, first["time_map"])
        self.assertEqual(first["sfx"][0]["outputFrame"], 69)
        self.assertEqual(second["output_start_frame"], 360)
        self.assertEqual(second["cues"][0]["outputFrame"], 420)
        self.assertEqual(plan["voiceClock"], "output")

    def test_subtitle_substring_without_word_times_must_be_explicit(self):
        spec = {"pack": "sample", "transcript": [{"id": "1", "start": 0.5, "end": 2,
                                                        "text": "新的模型来了"}],
                "scenes": [{"sceneId": "full_scene", "end": 5,
                            "cues": {"headline": {"phrase": "模型"}, "result": {"at": 3}},
                            "slots": {"title": "模型"}}]}
        with self.assertRaisesRegex(AdaptError, "word timings or an explicit at"):
            compile_plan(self.manifest, spec)

    def test_rejects_reordered_cues_and_missing_media(self):
        bad = {"pack": "sample", "scenes": [{"sceneId": "full_scene", "end": 4,
                                              "cues": {"headline": {"at": 3}, "result": {"at": 1}},
                                              "slots": {"title": "测试"}}]}
        with self.assertRaisesRegex(AdaptError, "Cue order"):
            compile_plan(self.manifest, bad)
        self.manifest["scenes"][0]["slots"].append({"id": "screenshot", "type": "image", "required": True})
        bad["scenes"][0]["cues"] = {"headline": {"at": 1}, "result": {"at": 3}}
        with self.assertRaisesRegex(AdaptError, "Missing required slot"):
            compile_plan(self.manifest, bad)

    def test_protected_action_cannot_be_crushed_and_existing_plan_is_preserved(self):
        bad = {"pack": "sample", "scenes": [{"sceneId": "full_scene", "endFrame": 120,
                                              "cues": {"headline": {"frame": 58}, "result": {"frame": 60}},
                                              "slots": {"title": "测试"}}]}
        with self.assertRaisesRegex(AdaptError, "Protected action windows overlap"):
            compile_plan(self.manifest, bad)
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "plan.json"
            dest.write_text("existing plan", encoding="utf-8")
            with self.assertRaisesRegex(AdaptError, "Refusing existing plan"):
                write_plan(dest, {"schemaVersion": 1}, replace=False)
            self.assertEqual(dest.read_text(encoding="utf-8"), "existing plan")

    def test_audio_events_copy_per_scene_instance_without_double_mixing_sfx(self):
        spec = {"pack": "sample", "scenes": [
            {"sceneId": "full_scene", "id": "one", "end": 4,
             "cues": {"headline": {"at": 1}, "result": {"at": 3}},
             "slots": {"title": "甲"}},
            {"sceneId": "full_scene", "id": "two", "end": 8,
             "cues": {"headline": {"at": 5}, "result": {"at": 7}},
             "slots": {"title": "乙"}},
        ]}
        audio = {"sfxEvents": [{"t": 1, "type": "hit", "g": .8}],
                 "gainEnvelopeDb": [{"at": 0, "db": -10}, {"at": 4, "db": -20}],
                 "synthBed": {"sections": [{"start": 0, "end": 4, "mode": "rhythm"}]},
                 "musicEvents": {"subDrops": [1], "crashes": [3],
                                 "openingBellArpeggio": {"at": 1.5, "notes": [72, 76], "spacing": .06},
                                 "endingElectricPiano": [{"start": 3.5, "notes": [60, 64]}],
                                 "risers": [{"start": 2, "end": 3}]},
                 "externalTrack": {"optional": True,
                                   "darkBand": {"sourceStart": 1, "sourceEnd": 3, "cutoffHz": 900}}}
        plan = compile_plan(self.manifest, spec, audio_timeline=audio)
        self.assertEqual(len(plan["audio"]["sfxReferenceEvents"]), 2)
        self.assertEqual(len(plan["sfx"]), 4)  # manifest scene events, not audio-timeline duplicates
        self.assertEqual([x["startFrame"] for x in plan["audio"]["sections"]], [0, 240])
        self.assertEqual([x["endFrame"] for x in plan["audio"]["sections"]], [240, 480])
        self.assertEqual(len(plan["audio"]["hits"]), 4)
        self.assertEqual(len(plan["audio"]["dark"]), 2)
        self.assertEqual({event["type"] for event in plan["audio"]["specialEvents"]},
                         {"openingBellArpeggio", "endingElectricPiano", "riser"})
        self.assertEqual(plan["audio"]["sections"][0]["sourceSectionIndex"], 0)
        self.assertEqual(plan["audio"]["sections"][1]["originalStart"], 0)
        self.assertEqual(plan["audio"]["sfxMixSource"], "runtime-scene-S-only")

    def test_legacy_sec_hits_and_special_events_normalize_without_old_wav(self):
        spec = {"pack": "sample", "scenes": [{"sceneId": "full_scene", "end": 4,
                 "cues": {"headline": {"at": 1}, "result": {"at": 3}},
                 "slots": {"title": "新标题"}}]}
        audio = {"sourceSampleRate": 44100,
                 "SEC": [{"start": 0, "end": 2, "mode": "chip"},
                         {"start": 2, "end": 4, "mode": "pad"}],
                 "ENV": [], "HITS": {"drop": [1], "riser": [[2.5, 3.5]], "crash": []},
                 "DARK": [],
                 "specialEvents": [{"at": 1.5, "type": "chip-resolution", "note": "short tone"}],
                 "fade": {"start": 3.5, "end": 4, "curve": "power"}}
        plan = compile_plan(self.manifest, spec, audio_timeline=audio)
        mapped = plan["audio"]
        self.assertEqual([part["sourceSectionIndex"] for part in mapped["sections"]], [0, 1])
        self.assertEqual(mapped["hits"][0]["kind"], "subDrops")
        self.assertEqual({event["type"] for event in mapped["specialEvents"]},
                         {"riser", "chip-resolution"})
        self.assertEqual(mapped["fade"][0]["startFrame"], 210)
        self.assertEqual(mapped["sampleRate"], 44100)

    def test_wall_allows_variable_contiguous_sprite_count(self):
        self.manifest["scenes"][0]["slots"].append({"id": "wall", "type": "wall-sprites",
                                                      "sourceAsset": "sc/wall/{000..388}.jpg"})
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            for i in range(27):
                (folder / f"{i:03d}.jpg").write_bytes(b"x")
            spec = {"pack": "sample", "scenes": [{"sceneId": "full_scene", "end": 4,
                    "cues": {"headline": {"at": 1}, "result": {"at": 3}},
                    "slots": {"title": "展墙", "wall": str(folder)}}]}
            with patch("adapt_project.probe_media", return_value={"width": 512, "height": 288}):
                plan = compile_plan(self.manifest, spec)
                self.assertEqual(plan["scenes"][0]["slots"]["wall"]["count"], 27)
                (folder / "013.jpg").rename(folder / "099.jpg")
                with self.assertRaisesRegex(AdaptError, "contiguous"):
                    compile_plan(self.manifest, spec)

    def test_full_pack_wall_requires_complete_grid_and_truthful_unique_count(self):
        self.manifest["assetDefinitions"] = {"wall": {"originalItems": 389}}
        self.manifest["scenes"][0]["slots"].append({"id": "wall", "type": "wall-sprites"})
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            spec = {"pack": "sample", "scenes": [{"sceneId": "full_scene", "end": 4,
                    "cues": {"headline": {"at": 1}, "result": {"at": 3}},
                    "slots": {"title": "展墙", "wall": str(folder)}}]}
            for i in range(27):
                (folder / f"{i:03d}.jpg").write_bytes(b"x")
            with self.assertRaisesRegex(AdaptError, "389 prepared sprite sheets"):
                compile_plan(self.manifest, spec)
            for i in range(27, 389):
                (folder / f"{i:03d}.jpg").write_bytes(b"x")
            (folder / "wall-meta.json").write_text(
                json.dumps({"uniqueWorks": 27, "displayTiles": 389}))
            (folder / "index.json").write_text(
                json.dumps([{"slug": f"work_{i % 27:03d}"} for i in range(389)]))
            with patch("adapt_project.probe_media", return_value={"width": 512, "height": 288}):
                plan = compile_plan(self.manifest, spec)
                self.assertEqual(plan["scenes"][0]["slots"]["wall"]["count"], 389)
                self.assertEqual(plan["scenes"][0]["slots"]["wall"]["uniqueWorks"], 27)
                (folder / "wall-meta.json").write_text(
                    json.dumps({"uniqueWorks": 389, "displayTiles": 389}))
                with self.assertRaisesRegex(AdaptError, "does not match 27 distinct"):
                    compile_plan(self.manifest, spec)

    def test_prepared_sequence_requires_builder_frame_names(self):
        self.manifest["assetDefinitions"] = {"demo": {"originalFrames": 3}}
        self.manifest["scenes"][0]["slots"].append({"id": "demo", "type": "sequence"})
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            for i in range(3):
                (folder / f"shot_{i}.jpg").write_bytes(b"x")
            spec = {"pack": "sample", "scenes": [{"sceneId": "full_scene", "end": 4,
                    "cues": {"headline": {"at": 1}, "result": {"at": 3}},
                    "slots": {"title": "录屏", "demo": str(folder)}}]}
            with self.assertRaisesRegex(AdaptError, "contiguous prepared JPEG"):
                compile_plan(self.manifest, spec)
            for i in range(1, 4):
                (folder / f"f_{i:04d}.jpg").write_bytes(b"x")
            with patch("adapt_project.probe_media", return_value={"width": 1280, "height": 720}):
                plan = compile_plan(self.manifest, spec)
                self.assertEqual(plan["scenes"][0]["slots"]["demo"]["count"], 6)

    def test_max_hold_limits_only_allowed_extra_and_audio_defaults_to_44100(self):
        self.manifest["scenes"][0]["maxHoldFrames"] = 30
        spec = {"pack": "sample", "scenes": [{"sceneId": "full_scene", "end": 4.5,
                "cues": {"headline": {"at": 1}, "result": {"at": 3}},
                "slots": {"title": "展墙"}}]}
        plan = compile_plan(self.manifest, spec, audio_timeline={"SEC": []})
        self.assertEqual(plan["audio"]["sampleRate"], 44100)
        spec["scenes"][0]["end"] = 5
        with self.assertRaisesRegex(AdaptError, "hold frames"):
            compile_plan(self.manifest, spec)

    def test_both_authored_full_packs_compile_all_motion_windows_and_score_events(self):
        root = Path(__file__).resolve().parents[1]
        for name, count in (("anim3", 12), ("anim4", 9)):
            with self.subTest(pack=name):
                folder = root / "packs" / name
                manifest = json.loads((folder / "manifest.json").read_text())
                audio = json.loads((folder / "audio_timeline.json").read_text())
                scenes = []
                for source in manifest["scenes"]:
                    scenes.append({
                        "id": source["id"] + "-01", "sceneId": source["id"],
                        "durationFrames": round(
                            (source["source"]["end"] - source["source"]["start"]) * manifest["fps"]),
                        "cues": {cue["id"]: {"at": cue["at"]} for cue in source["cues"]},
                        "slots": {},
                    })
                # Slot/media validation has focused tests above. Here we check
                # every real authored action window and both score schemas.
                with patch("adapt_project.slot_bindings", return_value=({}, [])):
                    plan = compile_plan(manifest, {"pack": manifest["id"], "scenes": scenes},
                                        audio_timeline=audio)
                self.assertEqual(len(plan["scenes"]), count)
                self.assertEqual(plan["fidelity"], "motion-windows")
                self.assertEqual(plan["audio"]["sampleRate"], 44100)
                self.assertTrue(plan["audio"]["sections"])
                self.assertTrue(plan["audio"]["specialEvents"])

    def test_full_action_window_keeps_original_speed_and_rejects_conflicting_words(self):
        source = self.manifest["scenes"][0]
        source["motionWindows"] = [{"id": "headline_action", "start": .5, "end": 1.8,
                                    "anchorCue": "headline"}]
        source["cues"].append({"id": "middle_word", "at": 1.5, "kind": "beat"})
        spec = {"pack": "sample", "requireMotionWindows": True,
                "scenes": [{"sceneId": "full_scene", "end": 6,
                            "cues": {"headline": {"at": 2}, "result": {"at": 5}},
                            "slots": {"title": "动作完整"}}]}
        plan = compile_plan(self.manifest, spec)
        window = plan["scenes"][0]["motionWindows"][0]
        self.assertEqual(window["outputStartFrame"], 90)
        self.assertEqual(window["outputEndFrame"], 168)
        self.assertEqual(plan["scenes"][0]["cues"][1]["outputFrame"], 150)
        self.assertEqual(plan["scenes"][0]["cues"][2]["outputFrame"], 300)
        self.assertEqual(plan["fidelity"], "motion-windows")
        spec["scenes"][0]["cues"]["middle_word"] = {"at": 3.3}
        with self.assertRaisesRegex(AdaptError, "cannot keep original action speed"):
            compile_plan(self.manifest, spec)

    def test_full_scene_motion_cannot_be_stretched_and_must_change_is_checked(self):
        source = self.manifest["scenes"][0]
        source["motionWindows"] = [{"id": "continuous_performance", "start": 0, "end": 4}]
        source["slots"][0].update({"mustChange": True, "sourceText": "旧标题"})
        spec = {"pack": "sample", "requireMotionWindows": True,
                "scenes": [{"sceneId": "full_scene", "end": 4,
                            "cues": {"headline": {"at": 1}, "result": {"at": 3}},
                            "slots": {"title": "旧标题"}}]}
        with self.assertRaisesRegex(AdaptError, "original placeholder"):
            compile_plan(self.manifest, spec)
        spec["scenes"][0]["slots"]["title"] = "新标题"
        self.assertEqual(compile_plan(self.manifest, spec)["fidelity"], "motion-windows")
        spec["scenes"][0]["end"] = 6
        with self.assertRaisesRegex(AdaptError, "cannot keep original action speed"):
            compile_plan(self.manifest, spec)


if __name__ == "__main__":
    unittest.main()
