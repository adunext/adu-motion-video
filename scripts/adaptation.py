"""Version-locked semantic selection above the existing full-scene compiler.

Profiles describe reviewed capabilities, not new animation. Missing episode
content stays missing; action clocks and media checks belong to adapt_project.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

from adapt_project import (AdaptError, cue_binding, following_tail_issue, frame_of, integer, media_clocks, number,
                           read_json, require, slot_bindings, target_span,
                           timed_scene, transcript_rows)
from semantic_inputs import SemanticInputError, expand_inputs

PROFILE_SCHEMA = "adu-adaptation-profile/1"
BRIEF_SCHEMA = "adu-adaptation-brief/1"
SPEC_SCHEMA = "adu-adapted-spec/1"


def _digest(value: dict) -> str:
    try:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (ValueError, TypeError) as exc:
        raise AdaptError(f"Cannot hash non-JSON contract: {exc}") from exc
    return hashlib.sha256(raw).hexdigest()


def profile_digest(profile: dict) -> str:
    return _digest(profile)


def manifest_digest(manifest: dict) -> str:
    return _digest(manifest)


def _strings(value, name, *, nonempty=False):
    require(isinstance(value, list) and all(isinstance(x, str) and x.strip() for x in value),
            f"{name} must be an array of nonempty strings")
    require(len(value) == len(set(value)), f"{name} must not repeat values")
    require(not nonempty or bool(value), f"{name} must not be empty")
    return value


def validate_profile(profile: dict, manifest: dict) -> dict:
    require(isinstance(profile, dict) and profile.get("schema") == PROFILE_SCHEMA,
            f"Profile schema must be {PROFILE_SCHEMA}")
    for key in ("id", "version"):
        require(isinstance(profile.get(key), str) and profile[key].strip(), f"Profile needs {key}")
    pack = profile.get("pack", {})
    require(isinstance(pack, dict), "Profile pack must be an object")
    require(pack.get("id") == manifest.get("id") and pack.get("version") == manifest.get("version"),
            "Profile pack id/version differs from frozen manifest")
    require(pack.get("manifestDigest") == manifest_digest(manifest),
            "Profile manifestDigest mismatch; frozen manifest drift requires a reviewed profile")
    sources = {s["id"]: s for s in manifest.get("scenes", [])}
    scenes = profile.get("scenes")
    require(isinstance(scenes, list) and scenes, "Profile needs nonempty scenes")
    seen = set()
    for scene in scenes:
        require(isinstance(scene, dict), "Profile scenes must be objects")
        sid = scene.get("sceneId")
        require(sid in sources and sid not in seen, f"Unknown/repeated profile scene {sid}")
        seen.add(sid)
        source = sources[sid]
        digest = scene.get("sourceBlockSha256")
        require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is not None
                and digest == source.get("sourceBlockSha256"),
                f"{sid}: sourceBlockSha256 mismatch or missing source hash")
        _strings(scene.get("intents"), f"{sid}.intents", nonempty=True)
        _strings(scene.get("requiredPhases"), f"{sid}.requiredPhases")
        _strings(scene.get("effects"), f"{sid}.effects", nonempty=True)
        require(integer(scene.get("energy"), f"{sid}.energy", minimum=1) <= 3,
                f"{sid}.energy must be 1..3")
        counts = scene.get("cardinality", {})
        require(isinstance(counts, dict), f"{sid}.cardinality must be an object")
        for name, limits in counts.items():
            require(isinstance(limits, dict), f"{sid}.cardinality.{name} must be an object")
            lo = integer(limits.get("min"), f"{sid}.{name}.min")
            hi = integer(limits.get("max"), f"{sid}.{name}.max")
            require(lo <= hi, f"{sid}.{name} cardinality min exceeds max")
        entry, exit_ = scene.get("entry", {}), scene.get("exit", {})
        require(isinstance(entry, dict) and entry.get("mode") in
                {"independent", "native-transition", "match-cut"}, f"{sid}: invalid entry mode")
        require(isinstance(exit_, dict), f"{sid}.exit must be an object")
        for block, key in ((entry, "requiresPrevious"), (exit_, "requiresNext")):
            ids = _strings(block.get(key, []), f"{sid}.{key}")
            require(set(ids) <= set(sources), f"{sid}.{key} references unknown scenes")
        if entry["mode"] == "match-cut":
            require(bool(entry.get("requiresPrevious")), f"{sid}: dependent entry needs requiresPrevious")
        bindings = entry.get("continuityBindings", [])
        require(isinstance(bindings, list), f"{sid}.continuityBindings must be an array")
        slots = {s["id"] for s in source.get("slots", [])}
        for binding in bindings:
            require(isinstance(binding, dict), f"{sid}: continuity binding must be an object")
            previous = binding.get("previousSceneId")
            require(previous in sources and previous in entry.get("requiresPrevious", []),
                    f"{sid}: continuity previousSceneId must be a permitted predecessor")
            previous_slots = {s["id"] for s in sources[previous].get("slots", [])}
            require(binding.get("previousSlot") in previous_slots and binding.get("slot") in slots,
                    f"{sid}: continuity binding references unknown slot")
            require(binding.get("requireEntityId") is True,
                    f"{sid}: continuity bindings must require explicit entityId")
        cue_roles = scene.get("cueRoles", {})
        require(isinstance(cue_roles, dict), f"{sid}.cueRoles must be an object")
        cues = {c["id"]: c for c in source.get("cues", [])}
        required = {c["id"] for c in cues.values()
                    if c.get("required", c.get("kind") in {"word", "semantic"})}
        require(required <= set(cue_roles) <= set(cues), f"{sid}: cueRoles must map every required cue and no unknown cue")
        require(all(isinstance(x, str) and x.strip() for x in cue_roles.values()),
                f"{sid}: cue roles need nonempty semantic names")
        split = scene.get("splitPolicy", {})
        require(isinstance(split, dict) and split.get("mode") == "atomic" and split.get("reason"),
                f"{sid}: only reviewed atomic full-scene splitPolicy is supported")
        audio = scene.get("audio", {})
        require(isinstance(audio, dict) and audio.get("mode") == "source-remap"
                and audio.get("tailPolicy") == "preserve", f"{sid}: audio must preserve source-remap and tails")
    require(all(set(s.get("entry", {}).get("requiresPrevious", [])) <= seen
                and set(s.get("exit", {}).get("requiresNext", [])) <= seen for s in scenes),
            "Profile dependencies must reference profiled scenes")
    return {"ready": True, "profileId": profile["id"], "profileDigest": profile_digest(profile),
            "manifestDigest": manifest_digest(manifest), "sceneCount": len(scenes)}


def _segment(segment: dict) -> None:
    require(isinstance(segment, dict), "Every brief segment must be an object")
    for name in ("id", "text", "intent"):
        require(isinstance(segment.get(name), str) and segment[name].strip(), f"Segment needs nonempty {name}")
    _strings(segment.get("phases", []), f"{segment['id']}.phases")
    integer(segment.get("durationFrames"), f"{segment['id']}.durationFrames", minimum=1)
    require(isinstance(segment.get("counts", {}), dict), f"{segment['id']}.counts must be an object")
    for name, value in segment.get("counts", {}).items():
        integer(value, f"{segment['id']}.counts.{name}")
    require(isinstance(segment.get("anchors", {}), dict), f"{segment['id']}.anchors must be an object")
    require(isinstance(segment.get("candidates", {}), dict), f"{segment['id']}.candidates must be an object")
    _strings(segment.get("preferredScenes", []), f"{segment['id']}.preferredScenes")
    if "energy" in segment:
        require(integer(segment["energy"], f"{segment['id']}.energy", minimum=1) <= 3,
                f"{segment['id']}.energy must be 1..3")


def candidate_segment(segment: dict, sid: str) -> dict:
    """An Agent may supply a different truthful expression for a different group.

    Timing, identity and original narration stay fixed. The selected annotation
    is persisted and revalidated; this is not automatic keyword classification.
    """
    interpretations = segment.get("candidateInterpretations", {})
    require(isinstance(interpretations, dict), "candidateInterpretations must be an object")
    override = interpretations.get(sid, {})
    require(isinstance(override, dict) and set(override) <= {"intent", "phases", "counts", "anchors", "energy"},
            f"{sid}: interpretation may only change intent/phases/counts/anchors/energy")
    result = {**segment, **deepcopy(override)}
    _segment(result)
    return result


def _semantic_rejections(contract: dict, segment: dict) -> list[str]:
    reasons = []
    if segment["intent"] not in contract["intents"]:
        reasons.append(f"intent {segment['intent']!r} is not supported")
    phases = iter(segment.get("phases", []))
    if not all(any(actual == wanted for actual in phases) for wanted in contract["requiredPhases"]):
        reasons.append("required semantic phases missing or out of order: " + " → ".join(contract["requiredPhases"]))
    for name, limits in contract.get("cardinality", {}).items():
        count = segment.get("counts", {}).get(name)
        if count is None:
            reasons.append(f"cardinality {name} needs an explicit count")
        elif not limits["min"] <= count <= limits["max"]:
            reasons.append(f"cardinality {name}={count} is outside {limits['min']}..{limits['max']}")
    return reasons


def _cues(source: dict, contract: dict, segment: dict, start: int, fps: int) -> tuple[dict, list[str]]:
    cues, missing = {}, []
    for cue in source.get("cues", []):
        role = contract.get("cueRoles", {}).get(cue["id"])
        anchor = segment.get("anchors", {}).get(role)
        if anchor is None:
            if cue.get("required", cue.get("kind") in {"word", "semantic"}):
                missing.append(f"anchor {role} ({cue['id']})")
            continue
        if isinstance(anchor, str):
            anchor = {"phrase": anchor}
        require(isinstance(anchor, dict), f"{segment['id']}.anchors.{role} must use at/frame/phrase/line")
        bound = deepcopy(anchor)
        if "frame" in bound:
            bound["frame"] = start + integer(bound["frame"], f"{segment['id']}.anchors.{role}.frame")
        elif "at" in bound:
            # Reuse the core parser for numeric/finite checks and rounding.
            bound = {"frame": start + cue_binding(bound, [], 0, segment["durationFrames"] / fps,
                                                  fps, f"{segment['id']}.{role}")}
        cues[cue["id"]] = bound
    return cues, missing


def _evaluate(manifest, source, source_index, contract, segment, target, start, end,
              fps, transcript, spec_dir, project, allow_pending_talk=False):
    """Keep timing and slot validation independent so a draft explains both."""
    segment = candidate_segment(segment, source["id"])
    rejected, missing = _semantic_rejections(contract, segment), []
    if rejected:
        # minFrames is an authored hard bound, not a reading-time estimate.
        if end - start < source.get("minFrames", 1):
            rejected.append(f"{source['id']} needs at least {source['minFrames']} frames, got {end - start}")
        return {"sceneId": source["id"], "status": "rejected", "reasons": rejected}
    cues, missing_cues = _cues(source, contract, segment, start, fps)
    missing.extend(missing_cues)
    missing.extend(contract.get("unmetRequirements", []))
    target = {**deepcopy(target), "id": segment["id"], "sceneId": source["id"],
              "startFrame": start, "endFrame": end, "cues": cues}
    require(isinstance(target.get("slots", {}), dict), f"{segment['id']}.slots must be an object")
    expanded = target
    expanded_ok = True
    try:
        expanded = expand_inputs(source, target)
    except SemanticInputError as exc:
        (missing if str(exc).startswith("Missing semantic input ") else rejected).append(str(exc))
        expanded_ok = False
    if expanded_ok:
        # Persist expanded bindings, so a spec can be saved in another directory.
        # Identity metadata survives while concrete media paths become absolute.
        target.pop("inputs", None)
        target["slots"] = deepcopy(expanded.get("slots", {}))
        for slot in source.get("slots", []):
            if slot.get("type") not in {"image", "video", "audio", "sequence", "wall", "wall-sprites"}:
                continue
            value = target["slots"].get(slot["id"])
            raw = value.get("path") if isinstance(value, dict) else value
            if isinstance(raw, str) and raw.strip():
                path = Path(raw).expanduser()
                path = (path if path.is_absolute() else spec_dir / path).resolve()
                target["slots"][slot["id"]] = {**value, "path": str(path)} if isinstance(value, dict) else str(path)
                review = value.get("colorReviewFile") if isinstance(value, dict) else None
                if isinstance(review, str) and review.strip():
                    review_path = Path(review).expanduser()
                    target["slots"][slot["id"]]["colorReviewFile"] = str(
                        (review_path if review_path.is_absolute() else spec_dir / review_path).resolve())
        expanded = target
    values, details, deferred = {}, [], []
    declared = source.get("slots", [])
    pending_talk = set()
    if allow_pending_talk and project is None:
        for slot in declared:
            if slot.get("type") != "talk":
                continue
            value = expanded.get("slots", {}).get(slot["id"])
            if value is not None and value is not True and value != "@talk":
                rejected.append(f"{source['id']}.{slot['id']} must use @talk after the edited narration is imported")
                continue
            pending_talk.add(slot["id"])
            deferred.append({"sceneId": source["id"], "instanceId": segment["id"], "slot": slot["id"],
                             "check": "imported-narration", "stage": "after-macro-build-import",
                             "reason": "本期 talk 在 macro-build 导入后验证；当前仅通过导入前检查"})
    absent = [s["id"] for s in declared if s.get("required", True)
              and expanded.get("slots", {}).get(s["id"]) is None
              and not (s.get("type") == "talk" and (project is not None or s["id"] in pending_talk))]
    missing.extend(f"slot {sid}" for sid in absent)
    def record_slot_error(exc):
        # Missing prepared assets are actionable binding work, never ready.
        message = str(exc)
        if any(word in message for word in ("Missing ", "missing", "needs --project", "import the edited narration")):
            missing.append(message)
        else:
            rejected.append(message)
    # Check each supplied slot even after a different supplied media path fails.
    # Neither an unbound slot nor a missing file may conceal invalid new text.
    supplied = expanded.get("slots", {})
    declared_ids = {s["id"] for s in declared}
    unknown = {k: v for k, v in supplied.items() if k not in declared_ids}
    if unknown:
        try:
            slot_bindings({**source, "slots": []}, {**expanded, "slots": unknown}, spec_dir, project)
        except AdaptError as exc:
            record_slot_error(exc)
    for slot in declared:
        sid = slot["id"]
        if sid in pending_talk or (supplied.get(sid) is None and not (slot.get("type") == "talk" and project is not None)):
            continue
        try:
            bound, information = slot_bindings({**source, "slots": [slot]},
                                               {**expanded, "slots": {sid: supplied[sid]} if sid in supplied else {}},
                                               spec_dir, project, manifest.get("assetDefinitions"))
            values.update(bound)
            details.extend(information)
        except AdaptError as exc:
            record_slot_error(exc)
    planned = None
    try:
        if manifest.get("requireMotionWindows"):
            require(bool(source.get("motionWindows")), f"{source['id']} has no authored motionWindows")
        planned = timed_scene(source, target, source_index, start, end, fps,
                              manifest.get("fps", 60), transcript, values, details)
        if not missing and not rejected:
            planned["mediaClocks"] = media_clocks(source, planned, fps)
    except AdaptError as exc:
        if not (missing_cues and str(exc).startswith("Bind semantic cue ")):
            rejected.append(str(exc))
    return {"sceneId": source["id"], "status": "rejected" if rejected else "needs-binding" if missing else "ready",
            "reasons": rejected, "missing": missing, "target": target, "expanded": expanded,
            "planned": planned, "contract": contract, "deferred": deferred}


def _seam(previous, current) -> tuple[list[str], list[str]]:
    """A join can require source choreography and identity, never path equality."""
    rejected, missing = [], []
    entry = current["contract"].get("entry", {})
    sid = current["sceneId"]
    previous_id = previous["sceneId"] if previous else None
    required = entry.get("requiresPrevious", [])
    if required and previous_id not in required:
        rejected.append(f"{sid} requiresPrevious {required}; found {previous_id or 'video start'}")
    if previous:
        if (current["contract"].get("styleId") and previous["contract"].get("styleId") != current["contract"]["styleId"]
                and entry["mode"] != "independent"):
            rejected.append(f"{sid}: cross-style entry needs an independently reviewed opening")
        required_next = previous["contract"].get("exit", {}).get("requiresNext", [])
        if required_next and sid not in required_next:
            rejected.append(f"{previous_id} requiresNext {required_next}; found {sid}")
    for binding in entry.get("continuityBindings", []):
        if previous_id != binding["previousSceneId"]:
            continue
        left = previous["expanded"].get("slots", {}).get(binding["previousSlot"])
        right = current["expanded"].get("slots", {}).get(binding["slot"])
        a = left.get("entityId") if isinstance(left, dict) else None
        b = right.get("entityId") if isinstance(right, dict) else None
        label = f"{previous_id}.{binding['previousSlot']} → {sid}.{binding['slot']}"
        if not isinstance(a, str) or not a.strip() or not isinstance(b, str) or not b.strip():
            missing.append(f"continuity {label} needs explicit matching entityId")
        elif a != b:
            rejected.append(f"continuity {label} entityId mismatch: {a!r} != {b!r}")
    return rejected, missing


def _sequence_cost(path: list[dict], candidate: dict, segment: dict) -> float:
    segment = candidate_segment(segment, candidate["sceneId"])
    cost = len(candidate.get("missing", [])) * 1000.0
    sid, contract = candidate["sceneId"], candidate["contract"]
    prior = [c["sceneId"] for c in path]
    cost += prior.count(sid) * 3
    if path:
        cost += 12 if prior[-1] == sid else 0
        cost += 4 * len(set(path[-1]["contract"]["effects"]) & set(contract["effects"]))
        if contract.get("styleId") and path[-1]["contract"].get("styleId") != contract["styleId"]:
            cost += 30  # prefer a coherent film after hard constraints pass
    if len(path) >= 2 and all(c["contract"]["energy"] == 3 for c in path[-2:]) and contract["energy"] == 3:
        cost += 10
    if segment.get("preferredScenes") and sid not in segment["preferredScenes"]:
        cost += 1
    if "energy" in segment:
        cost += abs(segment["energy"] - contract["energy"])
    return cost


def audio_diagnostics(planned: list[dict], fps: int) -> dict:
    """Report only observed event spans; unknown generator/reverb tails stay unknown.

    No duration table is guessed across packs. A caller with the exact frozen
    audio.py can append generator/tail evidence to this conservative report.
    """
    events, unknown = [], []
    for scene in planned:
        for event in scene.get("sfx", []):
            duration = event.get("duration", event.get("d"))
            row = {"sceneId": scene["id"], "type": event.get("type"), "frame": event["outputFrame"]}
            if isinstance(duration, (int, float)) and not isinstance(duration, bool) and duration >= 0:
                row["declaredDurationSeconds"] = duration
                row["crossesSceneEnd"] = event["outputFrame"] + duration * fps > scene["endFrame"]
            else:
                row["duration"] = "unknown"
                unknown.append(row)
            events.append(row)
    frames = sorted(e["frame"] for e in events)
    dense = [{"frame": frame, "eventsInQuarterSecond": sum(frame <= other < frame + fps / 4 for other in frames)}
             for frame in sorted(set(frames))]
    return {"policy": "preserve-source-events-and-tails", "eventCount": len(events), "events": events,
            "observedSource": "manifest-scene-sfx-only",
            "runtimeEventCoverage": "unknown-until-frozen-runtime-events-are-inspected",
            "denseWindows": [window for window in dense if window["eventsInQuarterSecond"] >= 4],
            "unknownDurationCount": len(unknown), "preRoll": "unknown-without-exact-audio-timeline",
            "reverbTail": "unknown-without-exact-audio-generator",
            "reviewRequired": True, "note": "No event is removed or shortened. Build/render must inspect the frozen audio source and listen continuously."}


def narration_issues(value, total_frames: int, fps: int) -> list[str]:
    if value is None:
        return []
    frames = frame_of(number(value, "narrationDuration", positive=True), fps, "narrationDuration")
    if frames != total_frames:
        return [f"narrationDuration resolves to {frames} frames, but segments cover {total_frames}; "
                "match the edited narration exactly by revising complete segments, never loop animations or freeze the presenter"]
    return []


def rhythm_diagnostics(path: list[dict], segments: list[dict], fps: int) -> dict:
    """Describe repetition and extended reading; never invent semantic alternatives."""
    ids = [c["sceneId"] for c in path]
    usage, findings = {}, []
    for i, sid in enumerate(ids):
        row = usage.setdefault(sid, {"sceneId": sid, "count": 0, "durationFrames": 0})
        row["count"] += 1
        row["durationFrames"] += segments[i]["durationFrames"]
    for row in usage.values():
        row["segmentShare"] = row["count"] / len(ids)
        if row["count"] >= 3 and row["segmentShare"] >= .6:
            findings.append({"code": "dominant-scene", **row,
                             "suggestion": "同一镜头组占比高；检查表达是否反复，补充语义相符的候选或另做经过核验的变体。"})
    def runs(values, minimum):
        start = 0
        while start < len(values):
            end = start + 1
            while end < len(values) and values[end] == values[start]:
                end += 1
            if end - start >= minimum:
                yield start, end
            start = end
    for start, end in runs(ids, 2):
        findings.append({"code": "adjacent-scene-repeat", "sceneId": ids[start],
                         "segmentIds": [s["id"] for s in segments[start:end]],
                         "suggestion": "连续重复同组；先核对是否应合并表达，或提供不同但语义成立的候选。"})
    # Alternating two/three groups can still become a mechanical long loop.
    for period in (2, 3):
        start = 0
        while start + 3 * period <= len(ids):
            pattern = ids[start:start + period]
            if len(set(pattern)) <= 1 or ids[start:start + 3 * period] != pattern * 3:
                start += 1
                continue
            end = start + 3 * period
            while end < len(ids) and ids[end] == pattern[(end - start) % period]:
                end += 1
            findings.append({"code": "repeated-scene-cycle", "pattern": pattern,
                             "segmentIds": [s["id"] for s in segments[start:end]],
                             "suggestion": "两三组轮换仍形成固定循环；增加有内容依据的证据段、阅读段或已验证的新编舞。"})
            start = end
    effects = sorted({effect for c in path for effect in c["contract"]["effects"]})
    for effect in effects:
        membership = [effect in c["contract"]["effects"] for c in path]
        for start, end in runs(membership, 3):
            if membership[start]:
                findings.append({"code": "repeated-effect-family", "effect": effect,
                                 "segmentIds": [s["id"] for s in segments[start:end]],
                                 "suggestion": "连续使用相同动作家族；检查人物构图、动作强弱与证据节奏，避免只换标题。"})
    for i, c in enumerate(path):
        for gap in (c.get("planned") or {}).get("intervals", []):
            added = (gap["endFrame"] - gap["startFrame"]) / fps - (gap["sourceEnd"] - gap["sourceStart"])
            if added > 4:
                findings.append({"code": "extended-reading-hold", "segmentIds": [segments[i]["id"]],
                                 "addedSeconds": round(added, 6),
                                 "suggestion": "停留区增加超过四秒；检查真实阅读需求及人物、证据视频的连续性，不自动重播动作。"})
    return {"sceneUsage": list(usage.values()), "segmentCount": len(ids),
            "uniqueSceneCount": len(usage), "reviewRequired": bool(findings), "findings": findings,
            "policy": "review-only; preserve semantics, action clocks and audio; no random alternatives"}


def plan_adaptation(manifest: dict, profile: dict, brief: dict, spec_dir: Path,
                    *, project: Path | None = None, beam_width: int = 64,
                    allow_pending_talk: bool = False) -> dict:
    validate_profile(profile, manifest)
    require(isinstance(brief, dict) and brief.get("schema") == BRIEF_SCHEMA,
            f"Brief schema must be {BRIEF_SCHEMA}")
    from pack_layout import resolve_layout
    try:
        resolve_layout(manifest, brief)
    except ValueError as exc:
        raise AdaptError(str(exc)) from exc
    fps = integer(brief.get("fps", manifest.get("fps", 60)), "brief.fps", minimum=1)
    require(fps <= 240, "Frame rate above 240 is unsupported")
    segments = brief.get("segments")
    require(isinstance(segments, list) and segments, "Brief needs nonempty segments")
    for segment in segments:
        _segment(segment)
    require(len({s["id"] for s in segments}) == len(segments), "Brief segment ids must be unique")
    require(1 <= integer(beam_width, "beam_width", minimum=1) <= 512, "beam_width must be 1..512")
    spec_dir = Path(spec_dir)
    transcript = transcript_rows(brief.get("transcript"), spec_dir)
    sources = {s["id"]: (i, s) for i, s in enumerate(manifest["scenes"])}
    total_frames = sum(s["durationFrames"] for s in segments)
    blocking = narration_issues(brief.get("narrationDuration"), total_frames, fps)
    candidates, segment_reports, offset = [], [], 0
    for segment in segments:
        end = offset + segment["durationFrames"]
        options = []
        for contract in profile["scenes"]:
            sid = contract["sceneId"]
            source_index, source = sources[sid]
            supplied = segment.get("candidates", {}).get(sid, {})
            require(isinstance(supplied, dict), f"{segment['id']}.candidates.{sid} must be an object")
            target = {key: deepcopy(supplied[key]) for key in ("inputs", "slots") if key in supplied}
            option = _evaluate(manifest, source, source_index, contract, segment, target,
                               offset, end, fps, transcript, spec_dir, project, allow_pending_talk)
            tail = following_tail_issue(source, end, total_frames, fps, manifest.get("fps", 60), segment["id"])
            if tail:
                option["reasons"].append(tail)
                option["status"] = "rejected"
            options.append(option)
        candidates.append([c for c in options if c["status"] != "rejected"])
        segment_reports.append({"segmentId": segment["id"], "candidates": [
            {key: c[key] for key in ("sceneId", "status", "reasons", "missing", "deferred") if key in c} for c in options]})
        offset = end
    # Whole-sequence beam search retains alternatives for future entry/exit locks.
    states = [(0.0, [], [])]
    seam_rejections = set()
    truncated = False
    for segment, options in zip(segments, candidates):
        next_states = []
        for score, path, deficits in states:
            for option in options:
                rejected, missing = _seam(path[-1] if path else None, option)
                if rejected:
                    seam_rejections.update(rejected)
                    continue
                next_states.append((score + _sequence_cost(path, option, segment) + len(missing) * 1000,
                                    path + [option], deficits + missing))
        # Completeness is lexicographic, never a finite diversity penalty.
        # On long films a cumulative repeat cost can exceed 1000 and otherwise
        # make an unbound variant beat an entirely ready sequence.
        next_states.sort(key=lambda s: (sum(len(c.get("missing", [])) for c in s[1]) + len(s[2]),
                                        s[0], tuple(c["sceneId"] for c in s[1])))
        truncated |= len(next_states) > beam_width
        states = next_states[:beam_width]
    complete = []
    for state in states:
        required = state[1][-1]["contract"].get("exit", {}).get("requiresNext", [])
        if required:
            seam_rejections.add(f"{state[1][-1]['sceneId']} requiresNext {required}; found video end")
        else:
            complete.append(state)
    selected = complete[0] if complete else None
    path = selected[1] if selected else []
    missing = ([m for c in path for m in c.get("missing", [])] + selected[2]) if selected else []
    brand = brief.get("brand")
    if not (isinstance(brand, str) and brand.strip()):
        missing.append("brand")
    ready = bool(selected) and not missing and not blocking
    deferred = [item for c in path for item in c.get("deferred", [])]
    selection = []
    for index, candidate in enumerate(path):
        _, seam_missing = _seam(path[index - 1] if index else None, candidate)
        seam_cost = len(seam_missing) * 1000
        cost = _sequence_cost(path[:index], candidate, segments[index]) + seam_cost
        selection.append({"segmentId": segments[index]["id"], "sceneId": candidate["sceneId"],
                          "intent": candidate_segment(segments[index], candidate["sceneId"])["intent"], "effects": candidate["contract"]["effects"],
                          "energy": candidate["contract"]["energy"], "incrementalCost": cost,
                          "missingBindingCost": len(candidate.get("missing", [])) * 1000,
                          "missingSeamCost": seam_cost})
    clean_segments = [{k: deepcopy(v) for k, v in s.items() if k != "candidates"} for s in segments]
    spec = {"pack": manifest["id"], "version": manifest["version"], "fps": fps,
            "scenes": [c["target"] for c in path],
            "adaptation": {"schema": SPEC_SCHEMA, "profileId": profile["id"],
                           "profileVersion": profile["version"], "profileDigest": profile_digest(profile),
                           "segments": clean_segments, "ready": ready,
                           "validationStage": "pre-import" if deferred else "bound-media"}}
    for key in ("layout", "brand", "transcript", "narrationDuration", "faceTracking", "presenterLabel", "subtitlePreset",
                "music", "monoFontFile", "externalFontFiles", "progressRail", "fadeEndSeconds", "mix", "colorReviewFile"):
        if key in brief:
            spec[key] = deepcopy(brief[key])
    if isinstance(spec.get("transcript"), str):
        raw = Path(spec["transcript"]).expanduser()
        spec["transcript"] = str((raw if raw.is_absolute() else spec_dir / raw).resolve())
    report = {"schema": "adu-adaptation-report/1", "ready": ready,
              "status": "blocked" if blocking or not selected else "ready" if ready else "needs-binding",
              "profileId": profile["id"], "profileDigest": profile_digest(profile),
              "selectedScenes": [c["sceneId"] for c in path], "segments": segment_reports,
              "selection": selection, "score": selected[0] if selected else None,
              "validationStage": "pre-import" if deferred else "bound-media", "deferred": deferred,
              "missing": missing, "blocking": blocking, "seamRejections": sorted(seam_rejections),
              "durationFrames": total_frames, "durationSeconds": total_frames / fps,
              "rhythm": rhythm_diagnostics(path, segments, fps),
              "search": {"algorithm": "bounded-sequence-beam", "beamWidth": beam_width, "truncated": truncated,
                         "priority": "binding-completeness-before-variety"},
              "audio": audio_diagnostics([c["planned"] for c in path if c["planned"]], fps)}
    if not selected:
        report["reason"] = "No complete feasible sequence within the bounded search; revise semantics, narration duration, anchors, or scene dependencies. No static fallback was inserted."
    return {"spec": spec, "report": report}


def load_profile(manifest: dict, profiles_root: Path, profile_id: str | None = None,
                 version: str | None = None) -> dict:
    """Resolve a reviewed sidecar or hydrate an extracted embedded capability map."""
    embedded = manifest.get("adaptationProfile")
    if isinstance(embedded, dict) and (profile_id is None or embedded.get("id") == profile_id) \
            and (version is None or embedded.get("version") == version):
        profile = deepcopy(embedded)
        profile["pack"] = {"id": manifest.get("id"), "version": manifest.get("version"),
                           "manifestDigest": manifest_digest(manifest)}
        sources = {s["id"]: s for s in manifest.get("scenes", [])}
        for scene in profile.get("scenes", []):
            if scene.get("sceneId") in sources and "sourceBlockSha256" not in scene:
                scene["sourceBlockSha256"] = sources[scene["sceneId"]].get("sourceBlockSha256")
        validate_profile(profile, manifest)
        return profile
    root = Path(profiles_root)
    paths = [root] if root.is_file() else sorted(root.rglob("*.json")) if root.is_dir() else []
    matches = []
    for path in paths:
        value = read_json(path)
        if (value.get("schema") == PROFILE_SCHEMA
                and (profile_id is None or value.get("id") == profile_id)
                and (version is None or value.get("version") == version)
                and value.get("pack", {}).get("id") == manifest.get("id")
                and value.get("pack", {}).get("version") == manifest.get("version")):
            matches.append(value)
    require(len(matches) == 1, f"Unknown or ambiguous adaptation profile {profile_id}@{version}")
    return matches[0]


def validate_adapted_spec(manifest: dict, spec: dict, spec_dir: Path, profiles_root: Path,
                          *, project: Path | None = None, allow_pending_talk: bool = False) -> dict:
    """Recompute every check; a stored ready/passed flag conveys no authority."""
    metadata = spec.get("adaptation")
    if metadata is None:
        return {"applicable": False, "ready": True, "status": "legacy"}
    require(isinstance(metadata, dict) and metadata.get("schema") == SPEC_SCHEMA,
            f"adaptation schema must be {SPEC_SCHEMA}")
    require(isinstance(metadata.get("profileId"), str) and isinstance(metadata.get("profileVersion"), str),
            "Adaptation metadata needs profileId and profileVersion")
    profile = load_profile(manifest, profiles_root, metadata["profileId"], metadata["profileVersion"])
    validate_profile(profile, manifest)
    require(metadata.get("profileDigest") == profile_digest(profile), "Adaptation profileDigest mismatch; replan against the reviewed profile")
    require(spec.get("pack") == manifest.get("id") and spec.get("version") == manifest.get("version"),
            "Adapted spec pack/version differs from reviewed manifest")
    segments, targets = metadata.get("segments"), spec.get("scenes")
    require(isinstance(segments, list) and segments and isinstance(targets, list)
            and len(segments) == len(targets), "Blocked draft: every segment needs one complete selected scene")
    fps = integer(spec.get("fps", manifest.get("fps", 60)), "spec.fps", minimum=1)
    require(fps <= 240, "Frame rate above 240 is unsupported")
    transcript = transcript_rows(spec.get("transcript"), Path(spec_dir))
    contracts = {s["sceneId"]: s for s in profile["scenes"]}
    sources = {s["id"]: (i, s) for i, s in enumerate(manifest["scenes"])}
    for segment in segments:
        _segment(segment)
    total_frames = sum(integer(s.get("durationFrames"), "segment.durationFrames", minimum=1) for s in segments)
    offset, path, errors, seen = 0, [], narration_issues(spec.get("narrationDuration"), total_frames, fps), set()
    for index, (segment, target) in enumerate(zip(segments, targets)):
        require(segment["id"] not in seen and isinstance(target, dict) and target.get("id") == segment["id"],
                "Adapted target order/identity differs from its segment; replan")
        seen.add(segment["id"])
        sid = target.get("sceneId")
        require(sid in contracts, f"{sid}: scene is not in the reviewed adaptation profile")
        start, end = target_span(target, offset, fps, index)
        require(end - start == segment["durationFrames"], f"{segment['id']}: changed scene duration differs from segment; replan")
        source_index, source = sources[sid]
        expected_cues, _ = _cues(source, contracts[sid], candidate_segment(segment, sid), start, fps)
        require(target.get("cues", {}) == expected_cues,
                f"{segment['id']}: changed cue bindings differ from semantic anchors; replan")
        evaluated = _evaluate(manifest, source, source_index, contracts[sid], segment, target,
                              start, end, fps, transcript, Path(spec_dir), project, allow_pending_talk)
        errors.extend(f"{segment['id']}: {reason}" for reason in evaluated.get("reasons", []) + evaluated.get("missing", []))
        if evaluated["status"] == "rejected" and "contract" not in evaluated:
            # Still include the declared source for dependency diagnostics.
            evaluated.update(contract=contracts[sid], expanded=target)
        rejected, missing = _seam(path[-1] if path else None, evaluated)
        errors.extend(rejected + missing)
        tail = following_tail_issue(source, end, total_frames, fps, manifest.get("fps", 60), segment["id"])
        if tail:
            errors.append(tail)
        path.append(evaluated)
        offset = end
    if path[-1]["contract"].get("exit", {}).get("requiresNext"):
        errors.append(f"{path[-1]['sceneId']}: requiresNext is unsatisfied at video end")
    require(isinstance(spec.get("brand"), str) and spec["brand"].strip(), "Adapted spec needs brand")
    require(not errors, "Adaptation validation blocked: " + "; ".join(errors))
    return {"applicable": True, "ready": True, "status": "revalidated",
            "validationStage": "pre-import" if any(c.get("deferred") for c in path) else "bound-media",
            "deferred": [item for c in path for item in c.get("deferred", [])],
            "profileId": profile["id"], "profileDigest": profile_digest(profile),
            "selectedScenes": [c["sceneId"] for c in path],
            "rhythm": rhythm_diagnostics(path, segments, fps),
            "audio": audio_diagnostics([c["planned"] for c in path if c.get("planned")], fps)}
