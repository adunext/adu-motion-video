"""Capability selection must never trade meaning, motion or joins for variety."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from adaptation import (AdaptError, audio_diagnostics, load_profile, manifest_digest,
                        plan_adaptation, profile_digest, validate_adapted_spec,
                        validate_profile)


class AdaptationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.manifest = {"id": "test", "version": "1.0.0", "fps": 60,
                         "scenes": [self.source("a"), self.source("b")]}
        self.profile = {"schema": "adu-adaptation-profile/1", "id": "test-adaptation", "version": "1",
                        "pack": {"id": "test", "version": "1.0.0"},
                        "scenes": [self.contract("a", "card"), self.contract("b", "orbit")]}
        self.refresh()

    def source(self, sid):
        return {"id": sid, "sourceBlockSha256": ("a" if sid == "a" else "b") * 64,
                "source": {"start": 0, "end": 4}, "minFrames": 120, "maxHoldFrames": 120,
                "cues": [{"id": "proof", "at": 1, "kind": "semantic", "required": True}],
                "slots": [{"id": "headline", "type": "text", "required": True, "maxChars": 12}],
                "motionWindows": [{"id": "entry", "start": .5, "end": 1.5, "anchorCue": "proof"}],
                "sfx": [{"at": 1, "type": "hit", "d": .2}]}

    def contract(self, sid, effect):
        return {"sceneId": sid, "sourceBlockSha256": ("a" if sid == "a" else "b") * 64,
                "intents": ["evidence"], "requiredPhases": ["claim", "proof"], "effects": [effect],
                "energy": 2, "cardinality": {"facts": {"min": 1, "max": 2}},
                "entry": {"mode": "independent"}, "exit": {}, "cueRoles": {"proof": "evidence"},
                "splitPolicy": {"mode": "atomic", "reason": "authored entry and payoff"},
                "audio": {"mode": "source-remap", "tailPolicy": "preserve"}}

    def refresh(self):
        self.profile["pack"]["manifestDigest"] = manifest_digest(self.manifest)
        (self.directory / "profile.json").write_text(json.dumps(self.profile))

    def segment(self, sid="one"):
        return {"id": sid, "text": "新的证据支持结论", "intent": "evidence", "phases": ["claim", "proof"],
                "durationFrames": 240, "counts": {"facts": 1}, "anchors": {"evidence": {"frame": 60}},
                "candidates": {"a": {"slots": {"headline": "新证据"}}, "b": {"slots": {"headline": "新结果"}}}}

    def brief(self, *segments):
        return {"schema": "adu-adaptation-brief/1", "brand": "New episode", "fps": 60,
                "segments": list(segments or [self.segment()])}

    def plan(self, brief=None):
        return plan_adaptation(self.manifest, self.profile, brief or self.brief(), self.directory)

    def validate(self, spec):
        return validate_adapted_spec(self.manifest, spec, self.directory, self.directory)

    def test_unknown_profile_hash_scene_drift_and_legacy(self):
        spec = self.plan()["spec"]
        self.assertTrue(self.validate(spec)["ready"])
        bad = deepcopy(spec)
        bad["adaptation"]["profileId"] = "unknown"
        with self.assertRaisesRegex(AdaptError, "Unknown"):
            self.validate(bad)
        bad = deepcopy(spec)
        bad["adaptation"]["profileDigest"] = "0" * 64
        with self.assertRaisesRegex(AdaptError, "profileDigest"):
            self.validate(bad)
        self.manifest["scenes"][0]["sourceBlockSha256"] = "c" * 64
        with self.assertRaisesRegex(AdaptError, "manifestDigest"):
            validate_profile(self.profile, self.manifest)
        self.profile["pack"]["manifestDigest"] = manifest_digest(self.manifest)
        with self.assertRaisesRegex(AdaptError, "sourceBlockSha256"):
            validate_profile(self.profile, self.manifest)
        self.assertFalse(validate_adapted_spec(self.manifest, {"scenes": []}, self.directory,
                                             self.directory)["applicable"])

    def test_missing_cue_cannot_guess_original_time_or_build(self):
        segment = self.segment()
        segment["anchors"] = {}
        result = self.plan(self.brief(segment))
        self.assertFalse(result["report"]["ready"])
        self.assertEqual(result["spec"]["scenes"][0]["cues"], {})
        self.assertIn("anchor evidence", " ".join(result["report"]["missing"]))
        result["spec"]["adaptation"]["ready"] = True  # forged success does not help
        with self.assertRaisesRegex(AdaptError, "anchor evidence"):
            self.validate(result["spec"])

    def test_phase_order_and_cardinality_are_hard_constraints(self):
        for key, value in (("phases", ["proof", "claim"]), ("counts", {"facts": 3})):
            segment = self.segment()
            segment[key] = value
            result = self.plan(self.brief(segment))
            self.assertEqual(result["report"]["status"], "blocked")
            self.assertEqual(result["spec"]["scenes"], [])
            self.assertTrue(all(c["status"] == "rejected" for c in result["report"]["segments"][0]["candidates"]))

    def test_missing_candidate_binding_does_not_change_semantic_eligibility(self):
        segment = self.segment()
        segment["candidates"] = {"b": {"slots": {"headline": "误选标题"}}}
        self.profile["scenes"][1]["intents"] = ["other"]
        self.refresh()
        result = self.plan(self.brief(segment))
        self.assertEqual(result["report"]["selectedScenes"], ["a"])
        self.assertFalse(result["report"]["ready"])
        self.assertIn("slot headline", result["report"]["missing"])

    def test_imported_narration_is_checked_by_existing_talk_binding(self):
        for source in self.manifest["scenes"]:
            source["slots"].append({"id": "presenter", "type": "talk", "required": True})
        self.refresh()
        self.assertFalse(self.plan()["report"]["ready"])
        project = self.directory / "project"
        (project / "talk").mkdir(parents=True)
        (project / "talkmap.js").write_text("window.TALK_MAP=[];")
        # This fixture exercises the core imported-narration contract, which
        # checks talk-map/frame existence; it is not a decoded-media QA claim.
        (project / "talk/f_0001.jpg").write_bytes(b"frame-existence-fixture")
        result = plan_adaptation(self.manifest, self.profile, self.brief(), self.directory, project=project)
        self.assertTrue(result["report"]["ready"])
        self.assertTrue(validate_adapted_spec(self.manifest, result["spec"], self.directory,
                                             self.directory, project=project)["ready"])
        (project / "talkmap.js").unlink()
        with self.assertRaisesRegex(AdaptError, "import the edited narration"):
            validate_adapted_spec(self.manifest, result["spec"], self.directory, self.directory, project=project)

    def test_explicit_pre_import_mode_defers_talk_then_requires_real_import(self):
        for source in self.manifest["scenes"]:
            source["slots"].append({"id": "presenter", "type": "talk", "required": True})
        self.refresh()
        result = plan_adaptation(self.manifest, self.profile, self.brief(), self.directory,
                                 allow_pending_talk=True)
        self.assertTrue(result["report"]["ready"])
        self.assertEqual(result["report"]["validationStage"], "pre-import")
        self.assertEqual(result["report"]["deferred"][0]["check"], "imported-narration")
        spec = result["spec"]
        preflight = validate_adapted_spec(self.manifest, spec, self.directory, self.directory,
                                         allow_pending_talk=True)
        self.assertTrue(preflight["ready"])
        self.assertTrue(preflight["deferred"])
        with self.assertRaisesRegex(AdaptError, "slot presenter"):
            self.validate(spec)
        project = self.directory / "imported"
        project.mkdir()
        with self.assertRaisesRegex(AdaptError, "import the edited narration"):
            validate_adapted_spec(self.manifest, spec, self.directory, self.directory,
                                  project=project, allow_pending_talk=True)
        (project / "talk").mkdir()
        (project / "talkmap.js").write_text("window.TALK_MAP=[];")
        (project / "talk/f_0001.jpg").write_bytes(b"frame-existence-fixture")
        final = validate_adapted_spec(self.manifest, spec, self.directory, self.directory, project=project)
        self.assertTrue(final["ready"])
        self.assertEqual(final["validationStage"], "bound-media")
        self.assertEqual(final["deferred"], [])

    def test_pre_import_mode_does_not_ignore_bad_talk_or_other_media(self):
        for source in self.manifest["scenes"]:
            source["slots"].append({"id": "presenter", "type": "talk", "required": True})
        self.refresh()
        brief = self.brief()
        for candidate in brief["segments"][0]["candidates"].values():
            candidate["slots"]["presenter"] = "old-source-talk.mp4"
        result = plan_adaptation(self.manifest, self.profile, brief, self.directory, allow_pending_talk=True)
        self.assertEqual(result["report"]["status"], "blocked")
        self.assertIn("must use @talk", str(result["report"]["segments"]))
        for candidate in brief["segments"][0]["candidates"].values():
            candidate["slots"]["presenter"] = "@talk"
        for source in self.manifest["scenes"]:
            source["slots"].append({"id": "evidence", "type": "image", "required": True})
        self.refresh()
        result = plan_adaptation(self.manifest, self.profile, brief, self.directory, allow_pending_talk=True)
        self.assertFalse(result["report"]["ready"])
        self.assertIn("slot evidence", result["report"]["missing"])

    def test_missing_media_does_not_hide_invalid_provided_text_or_unknown_slots(self):
        for source in self.manifest["scenes"]:
            source["slots"].extend([{"id": "presenter", "type": "talk", "required": True},
                                    {"id": "evidence", "type": "image", "required": True}])
        self.refresh()
        for change in ({"headline": "too-long-new-episode-headline"}, {"not_a_slot": "value"}):
            brief = self.brief()
            for candidate in brief["segments"][0]["candidates"].values():
                candidate["slots"].update(evidence=None, **change)
            result = plan_adaptation(self.manifest, self.profile, brief, self.directory, allow_pending_talk=True)
            self.assertEqual(result["report"]["status"], "blocked")
            for candidate in result["report"]["segments"][0]["candidates"]:
                self.assertEqual(candidate["status"], "rejected")
                self.assertTrue(candidate["reasons"])
                self.assertIn("slot evidence", candidate["missing"])

    def test_missing_file_before_text_slot_does_not_hide_capacity_rejection(self):
        for source in self.manifest["scenes"]:
            source["slots"].insert(0, {"id": "evidence", "type": "image", "required": True})
        self.refresh()
        brief = self.brief()
        for candidate in brief["segments"][0]["candidates"].values():
            candidate["slots"].update(evidence="missing-recording.svg", headline="too-long-new-episode-headline")
        result = self.plan(brief)
        self.assertEqual(result["report"]["status"], "blocked")
        for candidate in result["report"]["segments"][0]["candidates"]:
            self.assertIn("chars", str(candidate["reasons"]))
            self.assertIn("Missing image file", str(candidate["missing"]))

    def test_non_greedy_selection_sees_future_repetition(self):
        first, second = self.segment("one"), self.segment("two")
        # A greedy tie breaker chooses a first. Only a supports final-only, so
        # sequence optimization must choose b then a to avoid adjacent repeats.
        self.profile["scenes"][0]["intents"].append("final-only")
        second["intent"] = "final-only"
        self.refresh()
        result = self.plan(self.brief(first, second))
        self.assertEqual(result["report"]["selectedScenes"], ["b", "a"])
        self.assertTrue(result["report"]["ready"])
        self.assertEqual(result["report"]["selection"][0]["effects"], ["orbit"])
        self.assertEqual(result["report"]["score"], sum(s["incrementalCost"] for s in result["report"]["selection"]))
        self.assertTrue(self.validate(result["spec"])["ready"])

    def test_diversity_never_replaces_required_meaning(self):
        self.profile["scenes"][1]["intents"] = ["unrelated"]
        self.refresh()
        result = self.plan(self.brief(self.segment("one"), self.segment("two"), self.segment("three")))
        self.assertEqual(result["report"]["selectedScenes"], ["a", "a", "a"])
        self.assertTrue(result["report"]["ready"])

    def test_unsafe_entry_exit_and_entity_handoff(self):
        self.profile["scenes"][0]["intents"] = ["setup"]
        self.profile["scenes"][0]["exit"] = {"requiresNext": ["b"]}
        self.profile["scenes"][1]["entry"] = {
            "mode": "match-cut", "requiresPrevious": ["a"], "continuityBindings": [
                {"previousSceneId": "a", "previousSlot": "visual", "slot": "visual", "requireEntityId": True}]}
        for source in self.manifest["scenes"]:
            source["slots"].append({"id": "visual", "type": "image", "required": True})
        for name in ("prepared-one.svg", "prepared-two.svg"):
            (self.directory / name).write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"/>')
        self.refresh()
        first, second = self.segment("one"), self.segment("two")
        first["intent"] = "setup"
        first["candidates"]["a"]["slots"]["visual"] = {"path": "prepared-one.svg", "entityId": "real-work"}
        second["candidates"]["b"]["slots"]["visual"] = {"path": "prepared-two.svg", "entityId": "real-work"}
        result = self.plan(self.brief(first, second))
        self.assertTrue(result["report"]["ready"])
        self.assertEqual(result["report"]["selectedScenes"], ["a", "b"])
        self.assertTrue(Path(result["spec"]["scenes"][0]["slots"]["visual"]["path"]).is_absolute())
        self.assertTrue(self.validate(result["spec"])["ready"])
        self.assertEqual(self.plan(self.brief(second))["report"]["status"], "blocked")
        self.assertEqual(self.plan(self.brief(first))["report"]["status"], "blocked")
        second["candidates"]["b"]["slots"]["visual"]["entityId"] = "different-work"
        self.assertEqual(self.plan(self.brief(first, second))["report"]["status"], "blocked")
        del second["candidates"]["b"]["slots"]["visual"]["entityId"]
        result = self.plan(self.brief(first, second))
        self.assertFalse(result["report"]["ready"])
        self.assertIn("entityId", " ".join(result["report"]["missing"]))

    def test_manually_changed_plan_is_rechecked_not_trusted(self):
        spec = self.plan()["spec"]
        for mutation, message in (
            (lambda s: s["scenes"][0].update(endFrame=241), "duration"),
            (lambda s: s["scenes"][0]["cues"]["proof"].update(frame=61), "anchors"),
            (lambda s: s["adaptation"]["segments"][0].update(intent="unrelated"), "intent"),
            (lambda s: s["scenes"][0]["slots"].update(headline="超过十二个字符而不能合法塞进标题里面"), "chars"),
        ):
            changed = deepcopy(spec)
            mutation(changed)
            with self.assertRaisesRegex(AdaptError, message):
                self.validate(changed)

    def test_substring_cue_without_word_times_is_not_estimated(self):
        brief = self.brief()
        brief["segments"][0]["anchors"] = {"evidence": {"phrase": "支持"}}
        brief["transcript"] = [{"start": 1, "end": 2, "text": "新证据支持结论"}]
        result = self.plan(brief)
        self.assertEqual(result["report"]["status"], "blocked")
        self.assertIn("word timings", str(result["report"]["segments"]))

    def test_real_dark_3d_full_window_rejects_compression_above_minframes(self):
        manifest = json.loads((ROOT / "packs/dark-3d-showcase/1.1.1-candidate/manifest.json").read_text())
        profile = load_profile(manifest, ROOT / "adaptation-profiles")
        for sid in ("s02", "s03"):
            source = next(s for s in manifest["scenes"] if s["id"] == sid)
            contract = next(s for s in profile["scenes"] if s["sceneId"] == sid)
            duration = round((source["source"]["end"] - source["source"]["start"]) * 60) - 60
            self.assertGreater(duration, source["minFrames"])
            segment = {"id": "shortened", "text": "本期真实新文案", "intent": contract["intents"][0],
                       "phases": contract["requiredPhases"], "durationFrames": duration,
                       "counts": {name: limits["min"] for name, limits in contract["cardinality"].items()},
                       "anchors": {contract["cueRoles"][cue["id"]]: {"frame": round((cue["at"] - source["source"]["start"]) * 60)}
                                   for cue in source["cues"] if cue["id"] in contract["cueRoles"]}}
            result = plan_adaptation(manifest, profile, self.brief(segment), self.directory)
            candidate = next(c for c in result["report"]["segments"][0]["candidates"] if c["sceneId"] == sid)
            self.assertEqual(candidate["status"], "rejected")
            self.assertTrue(any("motion window" in reason or "outside selected scene" in reason
                                for reason in candidate["reasons"]), candidate)

    def test_embedded_profile_hydrates_after_final_manifest(self):
        embedded = deepcopy(self.profile)
        embedded.pop("pack")
        for scene in embedded["scenes"]:
            scene.pop("sourceBlockSha256")
        self.manifest["adaptationProfile"] = embedded
        hydrated = load_profile(self.manifest, self.directory / "no-sidecars")
        self.assertEqual(hydrated["pack"]["manifestDigest"], manifest_digest(self.manifest))
        self.assertTrue(validate_profile(hydrated, self.manifest)["ready"])

    def test_embedded_profile_cannot_silently_rebind_an_existing_source_hash(self):
        self.manifest["adaptationProfile"] = deepcopy(self.profile)
        self.manifest["adaptationProfile"].pop("pack")
        self.manifest["scenes"][0]["sourceBlockSha256"] = "c" * 64
        with self.assertRaisesRegex(AdaptError, "sourceBlockSha256"):
            load_profile(self.manifest, self.directory / "no-sidecars")

    def test_audio_diagnostic_preserves_unknown_and_crossing_tail(self):
        report = audio_diagnostics([{"id": "one", "endFrame": 120, "sfx": [
            {"outputFrame": 110, "type": "long", "d": 1},
            {"outputFrame": 110, "type": "unknown"},
            {"outputFrame": 111, "type": "unknown"},
            {"outputFrame": 112, "type": "unknown"}]}], 60)
        self.assertEqual(report["eventCount"], 4)
        self.assertTrue(report["events"][0]["crossesSceneEnd"])
        self.assertEqual(report["unknownDurationCount"], 3)
        self.assertTrue(report["denseWindows"])


if __name__ == "__main__":
    unittest.main()
