"""Local rematching cannot rewrite the film or adopt stale media evidence."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from adaptation import _digest, manifest_digest, profile_digest, validate_adapted_spec
from adapt_project import AdaptError
from rematch import apply_rematch, propose_rematch, spec_digest


class RematchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="adu-rematch-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.manifest = {"id": "test", "version": "1.0.0", "fps": 60,
                         "scenes": [self.source(sid) for sid in "abc"]}
        self.profile = {"schema": "adu-adaptation-profile/1", "id": "test-adaptation", "version": "1",
                        "pack": {"id": "test", "version": "1.0.0"},
                        "scenes": [self.contract(sid) for sid in "abc"]}
        segments = [{"id": name, "text": f"本期已确认原文{name}", "intent": "evidence", "phases": ["claim", "proof"],
                     "counts": {"facts": 1}, "anchors": {"evidence": {"frame": 60}}, "durationFrames": 240}
                    for name in ("left", "target", "right")]
        self.spec = {"pack": "test", "version": "1.0.0", "fps": 60, "brand": "本期品牌",
                     "music": {"mode": "synth", "gain": .35}, "mix": {"voiceGain": .8}, "fadeEndSeconds": 0,
                     "faceTracking": {"mode": "fixed", "cx": .4, "cy": .3, "h": .2},
                     "customGlobal": {"keep": ["字幕", "全部用户参数"]},
                     "scenes": [{"id": segment["id"], "sceneId": "a", "startFrame": index * 240,
                                 "endFrame": (index + 1) * 240, "slots": {"headline": "用户标题" + segment["id"]},
                                 "cues": {"proof": {"frame": index * 240 + 60}}, "note": "保留局部注释"}
                                for index, segment in enumerate(segments)],
                     "adaptation": {"schema": "adu-adapted-spec/1", "profileId": "test-adaptation", "profileVersion": "1",
                                    "segments": segments, "ready": True, "validationStage": "bound-media", "editorNote": "已校对"}}
        self.refresh()

    @staticmethod
    def source(sid):
        return {"id": sid, "sourceBlockSha256": sid * 64, "source": {"start": 0, "end": 4},
                "minFrames": 120, "maxHoldFrames": 120,
                "cues": [{"id": "proof", "at": 1, "kind": "semantic", "required": True}],
                "slots": [{"id": "headline", "type": "text", "required": True, "maxChars": 30}],
                "motionWindows": [{"id": "entry", "start": .5, "end": 1.5, "anchorCue": "proof"}],
                "sfx": [{"at": 1, "type": "hit", "d": .2}]}

    @staticmethod
    def contract(sid):
        return {"sceneId": sid, "sourceBlockSha256": sid * 64, "intents": ["evidence"],
                "requiredPhases": ["claim", "proof"], "effects": ["orbit" if sid == "b" else "card"],
                "energy": 2, "cardinality": {"facts": {"min": 1, "max": 2}},
                "entry": {"mode": "independent"}, "exit": {}, "cueRoles": {"proof": "evidence"},
                "splitPolicy": {"mode": "atomic", "reason": "reviewed full choreography"},
                "audio": {"mode": "source-remap", "tailPolicy": "preserve"}}

    def refresh(self):
        self.profile["pack"]["manifestDigest"] = manifest_digest(self.manifest)
        self.spec["adaptation"]["profileDigest"] = profile_digest(self.profile)
        (self.directory / "profile.json").write_text(json.dumps(self.profile))

    def request(self, **patch):
        return {"schema": "adu-local-rematch/1", "baseSpecDigest": spec_digest(self.spec), "segmentId": "target",
                "candidates": {"b": {"slots": {"headline": "明确提供的新组标题"}}}, **patch}

    def propose(self, request=None, **options):
        return propose_rematch(self.manifest, self.profile, self.spec, request or self.request(), self.directory, **options)

    def apply(self, bundle, sid="b", **options):
        return apply_rematch(self.manifest, self.profile, self.spec, bundle, sid, self.directory, **options)

    @staticmethod
    def choice(bundle, sid="b"):
        return next(row for row in bundle["candidates"] if row["candidateId"] == sid)

    @staticmethod
    def rehash(row):
        row["proposalDigest"] = spec_digest(row["proposalSpec"])
        row["candidateDigest"] = _digest({key: value for key, value in row.items() if key != "candidateDigest"})

    def assert_preserved(self, result):
        self.assertEqual(self.spec["scenes"][0], result["scenes"][0])
        self.assertEqual(self.spec["scenes"][2], result["scenes"][2])
        self.assertEqual(self.spec["adaptation"]["segments"], result["adaptation"]["segments"])
        self.assertEqual({k: v for k, v in self.spec.items() if k not in {"scenes", "adaptation"}},
                         {k: v for k, v in result.items() if k not in {"scenes", "adaptation"}})
        self.assertEqual(result["scenes"][1]["startFrame"], 240)
        self.assertEqual(result["scenes"][1]["endFrame"], 480)
        self.assertEqual(result["scenes"][1]["id"], "target")
        self.assertEqual(result["scenes"][1]["note"], "保留局部注释")

    def test_explicit_local_choice_is_ranked_without_mutation_and_passes_existing_full_validator(self):
        request = self.request()
        before = deepcopy((self.manifest, self.profile, self.spec, request))
        bundle = self.propose(request)
        bundle_before = deepcopy(bundle)
        self.assertEqual(bundle["rankedCandidateIds"][0], "b")
        self.assertEqual([row["candidateId"] for row in bundle["candidates"]], ["a", "b"])
        result = self.apply(bundle)
        self.assert_preserved(result)
        self.assertEqual(result["scenes"][1]["slots"]["headline"], "明确提供的新组标题")
        self.assertTrue(validate_adapted_spec(self.manifest, result, self.directory, self.directory)["ready"])
        self.assertEqual(before, (self.manifest, self.profile, self.spec, request))
        self.assertEqual(bundle, bundle_before)
        result["scenes"][0]["slots"]["headline"] = "returned object is independent"
        self.assertEqual(before[2], self.spec)

    def test_empty_candidates_keeps_original_and_explicit_same_scene_cannot_rewrite_user_text(self):
        bundle = self.propose(self.request(candidates={}))
        self.assertEqual([row["sceneId"] for row in bundle["candidates"]], ["a"])
        result = self.apply(bundle, "a")
        self.assertEqual(result["scenes"][1]["slots"], self.spec["scenes"][1]["slots"])
        blocked = self.propose(self.request(candidates={"a": {"slots": {"headline": "悄悄改写"}}}))
        self.assertEqual(self.choice(blocked, "a")["status"], "rejected")
        self.assertIn("user content", str(self.choice(blocked, "a")["reasons"]))

    def test_global_baseline_drift_and_profile_drift_are_rejected(self):
        bundle = self.propose()
        self.spec["mix"]["voiceGain"] = .9
        with self.assertRaisesRegex(AdaptError, "baseSpecDigest"):
            self.apply(bundle)
        with self.assertRaisesRegex(AdaptError, "baseSpecDigest"):
            self.propose(bundle["request"])
        self.spec["mix"]["voiceGain"] = .8
        self.profile["scenes"][1]["effects"] = ["new-unreviewed-effect"]
        with self.assertRaisesRegex(AdaptError, "profileDigest"):
            self.apply(bundle)

    def test_modified_proposals_cannot_be_adopted_even_when_their_hashes_are_recomputed(self):
        bundle = self.propose()
        for change in (lambda spec: spec["adaptation"]["segments"][1].update(text="伪造台词"),
                       lambda spec: spec["scenes"][0]["slots"].update(headline="改到其它组"),
                       lambda spec: spec["scenes"][1].update(endFrame=500),
                       lambda spec: spec.update(music={"mode": "mute"}),
                       lambda spec: spec["adaptation"].update(editorNote="改审计备注")):
            modified = deepcopy(bundle); row = self.choice(modified)
            change(row["proposalSpec"]); self.rehash(row)
            with self.assertRaisesRegex(AdaptError, "bundle changed or stale"):
                self.apply(modified)

    def test_candidate_identity_hash_and_request_metadata_are_rechecked(self):
        bundle = self.propose()
        with self.assertRaisesRegex(AdaptError, "candidateId"):
            self.apply(bundle, "unknown")
        bad = deepcopy(bundle); self.choice(bad)["candidateDigest"] = "0" * 64
        with self.assertRaisesRegex(AdaptError, "Candidate digest"):
            self.apply(bad)
        bad = deepcopy(bundle); bad["segmentId"] = "left"
        with self.assertRaisesRegex(AdaptError, "bundle changed or stale"):
            self.apply(bad)
        bad = deepcopy(bundle); bad["request"]["segmentId"] = "left"
        with self.assertRaisesRegex(AdaptError, "requestDigest"):
            self.apply(bad)

    def test_locked_target_cannot_be_proposed_or_late_applied(self):
        bundle = self.propose()
        self.spec["scenes"][1]["locked"] = True
        with self.assertRaisesRegex(AdaptError, "Locked"):
            self.propose()
        with self.assertRaisesRegex(AdaptError, "baseSpecDigest"):
            self.apply(bundle)

    def test_left_and_right_dependency_checks_reject_a_locally_valid_alternative(self):
        self.spec["scenes"][2]["sceneId"] = "c"
        self.profile["scenes"][0]["exit"] = {"requiresNext": ["a", "c"]}
        self.profile["scenes"][2]["entry"] = {"mode": "match-cut", "requiresPrevious": ["a"]}
        self.refresh()
        bundle = self.propose()
        self.assertEqual(self.choice(bundle, "a")["status"], "ready")
        candidate = self.choice(bundle)
        self.assertEqual(candidate["status"], "rejected")
        self.assertIn("requiresNext", str(candidate["reasons"]))
        self.assertIn("requiresPrevious", str(candidate["reasons"]))
        with self.assertRaisesRegex(AdaptError, "Only a ready"):
            self.apply(bundle)

    def test_missing_current_media_may_be_filled_without_touching_text_or_other_relative_paths(self):
        self.manifest["scenes"][0]["slots"].append({"id": "visual", "type": "image", "required": False})
        (self.directory / "proof.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 9"/>')
        self.spec["scenes"][0]["slots"]["visual"] = "proof.svg"
        self.refresh()
        result = self.apply(self.propose(self.request(candidates={}, bindings={"visual": "proof.svg"})), "a")
        self.assert_preserved(result)
        self.assertEqual(result["scenes"][0]["slots"]["visual"], "proof.svg")
        self.assertEqual(result["scenes"][1]["slots"]["visual"], str((self.directory / "proof.svg").resolve()))
        self.assertEqual(result["scenes"][1]["slots"]["headline"], "用户标题target")
        for bindings in ({"headline": "不是媒体"}, {"unknown": "proof.svg"}):
            with self.assertRaisesRegex(AdaptError, "visual media slots"):
                self.propose(self.request(bindings=bindings))

    def test_needs_binding_is_visible_but_cannot_be_promoted_by_a_ready_flag(self):
        self.manifest["scenes"][1]["slots"].append({"id": "visual", "type": "image", "required": True})
        self.refresh()
        bundle = self.propose()
        row = self.choice(bundle)
        self.assertEqual(row["status"], "needs-binding"); self.assertIn("slot visual", str(row["missing"]))
        self.assertNotIn("proposalSpec", row)
        with self.assertRaisesRegex(AdaptError, "Only a ready"):
            self.apply(bundle)
        row["status"] = "ready"; row["proposalSpec"] = deepcopy(self.spec); self.rehash(row)
        with self.assertRaisesRegex(AdaptError, "bundle changed or stale"):
            self.apply(bundle)

    def test_unconsumed_semantic_array_items_and_media_settings_are_rejected(self):
        self.manifest["scenes"][1]["slots"][0]["inputPath"] = "items.0.label"
        self.refresh()
        request = self.request(candidates={"b": {"inputs": {"items": [{"label": "明确标题"}, {"label": "不能静默丢弃"}]}}})
        with self.assertRaisesRegex(AdaptError, "Unconsumed candidate inputs: items.1.label"):
            self.propose(request)
        request["candidates"]["b"]["inputs"]["items"].pop()
        self.assertEqual(self.choice(self.propose(request))["status"], "ready")
        self.manifest["scenes"][1]["slots"].append({"id": "visual", "type": "image", "required": False})
        self.refresh()
        with self.assertRaisesRegex(AdaptError, "Unconsumed media settings"):
            self.propose(self.request(candidates={"b": {"slots": {"headline": "标题", "visual": {"path": "x.png", "unused": ["hidden.png"]}}}}))

    def test_unrelated_missing_media_also_blocks_adoption(self):
        self.manifest["scenes"][0]["slots"].append({"id": "visual", "type": "image", "required": False})
        self.spec["scenes"][0]["slots"]["visual"] = "missing.png"
        self.refresh()
        candidate = self.choice(self.propose())
        self.assertEqual(candidate["status"], "needs-binding")
        self.assertIn("left", str(candidate["missing"]))
        self.assertTrue(any(item["kind"] == "missing" for item in candidate["mediaEvidence"]))

    def test_new_attachment_requires_an_explicit_destination_in_every_adoptable_candidate(self):
        (self.directory / "proof.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 9"/>')
        self.manifest["scenes"][0]["slots"].append({"id": "visual", "type": "image", "required": False})
        self.manifest["scenes"][1]["slots"].append({"id": "differentSlot", "type": "image", "required": False, "inputPath": "proof"})
        self.refresh()
        request = self.request(bindings={"visual": "proof.svg"})
        bundle = self.propose(request)
        self.assertEqual(self.choice(bundle, "a")["status"], "ready")
        self.assertEqual(self.choice(bundle)["status"], "needs-binding")
        self.assertEqual(self.choice(bundle)["unconsumedRequestBindings"][0]["slotId"], "visual")
        request["candidates"]["b"]["inputs"] = {"proof": "proof.svg"}
        candidate = self.choice(self.propose(request))
        self.assertEqual(candidate["status"], "ready")
        self.assertEqual(candidate["mediaBindings"][0]["slotId"], "differentSlot")
        self.assertEqual(candidate["mediaBindings"][0]["consumesRequestBindings"], ["visual"])
        self.assertEqual(candidate["consumedInputs"][0]["input"], "proof")
        self.assertEqual(candidate["unconsumedRequestBindings"], [])

    def test_match_cut_requires_explicit_identity_but_does_not_claim_pixel_lineage(self):
        for source in self.manifest["scenes"][:2]:
            source["slots"].append({"id": "visual", "type": "image", "required": False})
        self.profile["scenes"][1]["entry"] = {"mode": "match-cut", "requiresPrevious": ["a"], "continuityBindings": [
            {"previousSceneId": "a", "previousSlot": "visual", "slot": "visual", "requireEntityId": True}]}
        for name, color in (("left.svg", "red"), ("different.svg", "blue")):
            (self.directory / name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 9"><rect width="16" height="9" fill="{color}"/></svg>')
        self.spec["scenes"][0]["slots"]["visual"] = {"path": "left.svg", "entityId": "work-1"}
        self.refresh()
        request = self.request(); request["candidates"]["b"]["slots"]["visual"] = {"path": "different.svg"}
        self.assertEqual(self.choice(self.propose(request))["status"], "needs-binding")
        request["candidates"]["b"]["slots"]["visual"]["entityId"] = "work-2"
        self.assertEqual(self.choice(self.propose(request))["status"], "rejected")
        request["candidates"]["b"]["slots"]["visual"]["entityId"] = "work-1"
        candidate = self.choice(self.propose(request))
        self.assertEqual(candidate["status"], "ready")
        self.assertNotEqual(candidate["mediaEvidence"][0]["sha256"], candidate["mediaEvidence"][1]["sha256"])
        self.assertNotIn("lineageVerified", candidate)

    def test_current_candidate_and_new_binding_cannot_silently_discard_conflicting_media(self):
        for name in ("one.svg", "two.svg"):
            (self.directory / name).write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 9"/>')
        self.manifest["scenes"][0]["slots"].append({"id": "visual", "type": "image", "required": False, "inputPath": "proof"})
        self.refresh()
        for explicit in ({"slots": {"visual": "one.svg"}}, {"inputs": {"proof": "one.svg"}}):
            with self.subTest(explicit=explicit):
                request = self.request(candidates={"a": explicit}, bindings={"visual": "two.svg"})
                before = deepcopy(request)
                bundle = self.propose(request)
                candidate = self.choice(bundle, "a")
                self.assertEqual(candidate["status"], "rejected")
                self.assertIn("Conflicting candidate and request bindings: visual", candidate["reasons"])
                self.assertNotIn("proposalSpec", candidate)
                with self.assertRaisesRegex(AdaptError, "Only a ready"):
                    self.apply(bundle, "a")
                self.assertEqual(request, before)
                request["bindings"]["visual"] = {"path": str((self.directory / "one.svg").resolve())}
                bundle = self.propose(request)
                candidate = self.choice(bundle, "a")
                self.assertEqual(candidate["status"], "ready")
                self.assertEqual(len(candidate["mediaBindings"][0]["origins"]), 2)
                self.assertEqual(candidate["unconsumedRequestBindings"], [])
                self.assert_preserved(self.apply(bundle, "a"))

    def test_imported_narration_and_color_baseline_are_bound_including_missing_files(self):
        from PIL import Image
        project = self.directory / "project"; project.mkdir()
        (project / "talk").mkdir()
        (project / "talkmap.js").write_text("window.TALK_MAP=[];")
        Image.new("RGB", (16, 9), "red").save(project / "talk" / "f_0001.jpg")
        for source in self.manifest["scenes"]:
            source["slots"].append({"id": "presenter", "type": "talk", "required": True})
        self.refresh()
        for name in ("voice.wav", "import.json"):
            for mutation in ("replace", "create", "delete"):
                with self.subTest(file=name, mutation=mutation):
                    target = project / name
                    target.unlink(missing_ok=True)
                    if mutation != "create":
                        target.write_bytes(b"reviewed baseline")
                    bundle = self.propose(project=project)
                    candidate = self.choice(bundle)
                    self.assertEqual(candidate["status"], "ready")
                    record = next(item for item in candidate["mediaEvidence"] if item["path"] == str(target.resolve()))
                    self.assertEqual(record["kind"], "missing" if mutation == "create" else "file")
                    self.assert_preserved(self.apply(bundle, project=project))
                    if mutation == "delete":
                        target.unlink()
                    else:
                        target.write_bytes(b"different baseline")
                    with self.assertRaisesRegex(AdaptError, "media evidence"):
                        self.apply(bundle, project=project)
                    target.unlink(missing_ok=True)

    def test_preimport_context_is_explicit_and_cannot_be_changed_when_applying(self):
        for source in self.manifest["scenes"]:
            source["slots"].append({"id": "presenter", "type": "talk", "required": True})
        self.refresh()
        bundle = self.propose(allow_pending_talk=True)
        self.assertEqual(self.choice(bundle)["status"], "ready")
        self.assertTrue(self.choice(bundle)["deferred"])
        self.assertEqual(self.apply(bundle, allow_pending_talk=True)["adaptation"]["validationStage"], "pre-import")
        with self.assertRaisesRegex(AdaptError, "bundle changed or stale"):
            self.apply(bundle)

    def test_directory_media_bytes_are_bound_even_when_the_frame_count_stays_the_same(self):
        from PIL import Image
        frames = self.directory / "frames"; frames.mkdir()
        Image.new("RGB", (16, 9), "red").save(frames / "f_0001.jpg")
        self.manifest["scenes"][1]["slots"].append({"id": "sequence", "type": "sequence", "required": True})
        self.refresh()
        request = self.request(); request["candidates"]["b"]["slots"]["sequence"] = {"path": "frames", "glob": "*.jpg"}
        bundle = self.propose(request)
        self.assertEqual(self.choice(bundle)["status"], "ready")
        Image.new("RGB", (16, 9), "blue").save(frames / "f_0001.jpg")
        with self.assertRaisesRegex(AdaptError, "media evidence"):
            self.apply(bundle)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "real FFmpeg media checks require FFmpeg")
    def test_real_video_length_aspect_and_same_path_content_replacement(self):
        def video(name, duration, color, dimensions="160x90"):
            path = self.directory / name
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                            f"color=c={color}:s={dimensions}:r=30:d={duration}", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)],
                           check=True, capture_output=True)
            return path
        long = video("long.mp4", 5, "red")
        short = video("short.mp4", 1, "blue")
        portrait = video("portrait.mp4", 5, "blue", "90x160")
        self.manifest["scenes"][1]["slots"].append({"id": "video", "type": "video", "required": True, "aspect": "16:9",
            "sourceAsset": "media/proof", "playback": {"start": 0, "end": 4, "rate": 1, "fps": 30, "terminalHoldSeconds": 0}})
        self.refresh()
        request = self.request()
        for path, status in ((short, "rejected"), (portrait, "rejected"), (long, "ready")):
            request["candidates"]["b"]["slots"]["video"] = {"path": str(path), "offset": 0}
            candidate = self.choice(self.propose(request)); self.assertEqual(candidate["status"], status, candidate["reasons"])
        bundle = self.propose(request)
        self.assert_preserved(self.apply(bundle))
        video("long.mp4", 5, "blue")
        with self.assertRaisesRegex(AdaptError, "media evidence"):
            self.apply(bundle)


if __name__ == "__main__":
    unittest.main()
