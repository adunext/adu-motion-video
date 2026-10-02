"""Reviewable, version-bound replacement of exactly one complete scene.

No model, render or write side effects. The existing compiler remains the
authority for authored motion, media length and seams; ranking cannot relax it.
"""
from copy import deepcopy
import hashlib
from pathlib import Path
from string import Formatter

from adaptation import (
    SPEC_SCHEMA, _cues, _digest, _evaluate, _seam, _segment, _sequence_cost,
    audio_diagnostics, manifest_digest, profile_digest, validate_profile,
)
from adapt_project import AdaptError, IMAGE_EXT, integer, require, target_span, transcript_rows
from semantic_inputs import SemanticInputError, expand_inputs, field

REQUEST_SCHEMA = "adu-local-rematch/1"
BUNDLE_SCHEMA = "adu-local-rematch-bundle/1"
MEDIA_TYPES = {"image", "video", "audio", "sequence", "wall", "wall-sprites"}
# Local attachments may not silently replace narration or sound design.
ATTACHMENT_TYPES = MEDIA_TYPES - {"audio"}


def spec_digest(spec: dict) -> str:
    return _digest(spec)


def _structure(manifest, profile, spec):
    validate_profile(profile, manifest)
    require(isinstance(spec, dict), "Current spec must be an object")
    metadata = spec.get("adaptation")
    require(isinstance(metadata, dict) and metadata.get("schema") == SPEC_SCHEMA,
            "Local rematch requires an adapted spec with reviewed semantic segments")
    require(metadata.get("profileId") == profile["id"] and metadata.get("profileVersion") == profile["version"],
            "Adaptation profile identity mismatch")
    require(metadata.get("profileDigest") == profile_digest(profile), "Adaptation profileDigest mismatch")
    require(spec.get("pack") == manifest["id"] and spec.get("version") == manifest["version"],
            "Adapted spec pack/version mismatch")
    segments, scenes = metadata.get("segments"), spec.get("scenes")
    require(isinstance(segments, list) and segments and isinstance(scenes, list) and len(segments) == len(scenes),
            "Every segment must already have one complete selected scene")
    fps = integer(spec.get("fps", manifest.get("fps", 60)), "spec.fps", minimum=1)
    require(fps <= 240, "Frame rate above 240 is unsupported")
    require(isinstance(spec.get("brand"), str) and spec["brand"].strip(), "Adapted spec needs brand")
    contracts = {scene["sceneId"]: scene for scene in profile["scenes"]}
    sources = {scene["id"]: (index, scene) for index, scene in enumerate(manifest["scenes"])}
    seen, spans, offset = set(), [], 0
    for index, (segment, target) in enumerate(zip(segments, scenes)):
        _segment(segment)
        require(segment["id"] not in seen and isinstance(target, dict) and target.get("id") == segment["id"],
                "Adapted target order/identity differs from its segment")
        seen.add(segment["id"])
        sid = target.get("sceneId")
        require(sid in contracts, f"{sid}: scene is not in the reviewed adaptation profile")
        start, end = target_span(target, offset, fps, index)
        require(end - start == segment["durationFrames"], f"{segment['id']}: changed duration differs from segment")
        expected, _ = _cues(sources[sid][1], contracts[sid], segment, start, fps)
        require(target.get("cues", {}) == expected, f"{segment['id']}: cue bindings differ from semantic anchors")
        spans.append((start, end)); offset = end
    return segments, contracts, sources, spans, fps


def _whole_plan(manifest, profile, spec, spec_dir, project, allow_pending_talk):
    """Same full-plan checks as validate_adapted_spec, with an in-memory profile.

    Do not load or synthesize a profile on disk. Return separate deficits so a
    missing attachment stays a non-adoptable draft instead of a generic error.
    """
    segments, contracts, sources, spans, fps = _structure(manifest, profile, spec)
    transcript = transcript_rows(spec.get("transcript"), spec_dir)
    path, reasons, missing = [], [], []
    for segment, target, (start, end) in zip(segments, spec["scenes"], spans):
        sid = target["sceneId"]
        source_index, source = sources[sid]
        evaluated = _evaluate(manifest, source, source_index, contracts[sid], segment, target,
                              start, end, fps, transcript, spec_dir, project, allow_pending_talk)
        reasons.extend(f"{segment['id']}: {item}" for item in evaluated.get("reasons", []))
        missing.extend(f"{segment['id']}: {item}" for item in evaluated.get("missing", []))
        # Semantic rejection returns early; seams still need its declared identity.
        evaluated.setdefault("contract", contracts[sid]); evaluated.setdefault("expanded", target)
        bad, absent = _seam(path[-1] if path else None, evaluated)
        reasons.extend(bad); missing.extend(absent); path.append(evaluated)
    if path[-1]["contract"].get("exit", {}).get("requiresNext"):
        reasons.append(f"{path[-1]['sceneId']}: requiresNext is unsatisfied at video end")
    return path, list(dict.fromkeys(reasons)), list(dict.fromkeys(missing)), fps


def _input_leaves(value, prefix=""):
    if isinstance(value, dict) and value:
        for key, child in value.items():
            yield from _input_leaves(child, f"{prefix}.{key}" if prefix else str(key))
    elif isinstance(value, list) and value:
        for index, child in enumerate(value):
            yield from _input_leaves(child, f"{prefix}.{index}")
    else:
        yield prefix


def _explicit_candidate(source, candidate):
    require(isinstance(candidate, dict) and not set(candidate) - {"inputs", "slots"},
            f"{source['id']}: candidates may contain only explicit inputs/slots")
    if "inputs" in candidate:
        require(isinstance(candidate["inputs"], dict), "Candidate inputs must be an object")
        consumed = []
        for slot in source.get("slots", []):
            if slot.get("inputPath"):
                consumed.append(slot["inputPath"])
            if slot.get("inputTemplate"):
                consumed.extend(name for _, name, _, _ in Formatter().parse(slot["inputTemplate"]) if name is not None)
        unused = [name for name in _input_leaves(candidate["inputs"]) if name and
                  not any(name == path or name.startswith(path + ".") for path in consumed)]
        require(not unused, f"Unconsumed candidate inputs: {', '.join(unused)}")
    slots = candidate.get("slots", {})
    require(isinstance(slots, dict), "Candidate slots must be an object")
    # Expand before checking media settings; extra items must not disappear in a
    # named input mapping. Missing inputs are subsequently reported by _evaluate.
    try:
        supplied = expand_inputs(source, candidate).get("slots", {})
    except SemanticInputError:
        supplied = slots
    for slot in source.get("slots", []):
        value = supplied.get(slot["id"])
        if slot.get("type") not in MEDIA_TYPES or not isinstance(value, dict):
            continue
        allowed = {"path", "entityId"}
        if slot.get("type") == "video":
            allowed.add("colorReviewFile")
        if slot.get("type") == "video" and slot.get("playback"):
            allowed.add("offset")
        if slot.get("type") in {"sequence", "wall", "wall-sprites"}:
            allowed.add("glob")
        require(not set(value) - allowed,
                f"Unconsumed media settings for {source['id']}.{slot['id']}: {sorted(set(value) - allowed)}")


def _media_identity(value, spec_dir):
    values = deepcopy(value) if isinstance(value, dict) else {"path": value}
    for name in ("path", "colorReviewFile"):
        if isinstance(values.get(name), str):
            raw = Path(values[name]).expanduser()
            values[name] = str((raw if raw.is_absolute() else spec_dir / raw).resolve())
    return values


def _consumption(source, expanded, requested, bindings, original_id, segment_id, spec_dir):
    """Expose where explicit inputs go; never silently discard a new attachment."""
    media, consumed = [], []

    supplied = requested.get(source["id"], {})
    for slot in source.get("slots", []):
        sid = slot["id"]
        origins = []
        if "inputs" in supplied:
            paths = ([slot["inputPath"]] if slot.get("inputPath") else [])
            if slot.get("inputTemplate"):
                paths.extend(name for _, name, _, _ in Formatter().parse(slot["inputTemplate"]) if name is not None)
            for path in paths:
                try:
                    field(supplied["inputs"], path)
                except SemanticInputError:
                    continue
                consumed.append({"input": path, "segmentId": segment_id, "sceneId": source["id"], "slotId": sid})
                origins.append(f"request.candidates.{source['id']}.inputs.{path}")
        if sid in supplied.get("slots", {}):
            origins.append(f"request.candidates.{source['id']}.slots.{sid}")
        if source["id"] == original_id and sid in bindings:
            origins.append(f"request.bindings.{sid}")
        if slot.get("type") in MEDIA_TYPES and sid in expanded.get("slots", {}):
            media.append({"segmentId": segment_id, "sceneId": source["id"], "slotId": sid, "type": slot["type"],
                          "value": deepcopy(expanded["slots"][sid]), "origins": origins or ["currentSpec"]})
    unconsumed = []
    for sid, value in bindings.items():
        requested_value = _media_identity(value, spec_dir)
        destinations = [row for row in media if row["type"] in ATTACHMENT_TYPES
                        and all(_media_identity(row["value"], spec_dir).get(key) == item for key, item in requested_value.items())]
        if not destinations:
            unconsumed.append({"slotId": sid, "value": deepcopy(value),
                               "reason": "New request binding has no explicit destination in this candidate"})
        else:
            for row in destinations:
                row.setdefault("consumesRequestBindings", []).append(sid)
    return media, consumed, unconsumed


def _file_evidence(path, cache):
    path = path.resolve()
    if not path.exists():
        return {"path": str(path), "kind": "missing"}
    if not path.is_file():
        return {"path": str(path), "kind": "not-file"}
    before = path.stat()
    stamp = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
    if (str(path), stamp) not in cache:
        sha = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                sha.update(block)
        after = path.stat()
        require(stamp == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns),
                f"Media changed during rematch validation: {path}")
        cache[(str(path), stamp)] = {"path": str(path), "kind": "file", "sizeBytes": after.st_size, "sha256": sha.hexdigest()}
    return cache[(str(path), stamp)]


def _media_evidence(manifest, spec, path, spec_dir, project, cache):
    sources = {scene["id"]: scene for scene in manifest["scenes"]}
    evidence = {}

    def file(raw):
        value = Path(raw).expanduser()
        value = (value if value.is_absolute() else spec_dir / value).resolve()
        record = _file_evidence(value, cache)
        evidence[(str(value), "file")] = record

    def directory(raw, pattern, extra=()):
        value = Path(raw).expanduser()
        value = (value if value.is_absolute() else spec_dir / value).resolve()
        if not value.exists():
            evidence[(str(value), pattern)] = {"path": str(value), "kind": "missing", "glob": pattern}
            return
        if not value.is_dir():
            evidence[(str(value), pattern)] = {"path": str(value), "kind": "not-directory", "glob": pattern,
                                               "fileEvidence": _file_evidence(value, cache)}
            return
        entries = sorted({p for p in value.glob(pattern) if p.is_file() and p.suffix.lower() in IMAGE_EXT})
        rows = [{"name": str(p.relative_to(value)), **{k: v for k, v in _file_evidence(p, cache).items() if k != "path"}} for p in entries]
        for name in extra:
            rows.append({"name": name, **{k: v for k, v in _file_evidence(value / name, cache).items() if k != "path"}})
        evidence[(str(value), pattern)] = {"path": str(value), "kind": "directory", "glob": pattern,
                                           "fileCount": len(entries), "inventoryDigest": _digest({"files": rows})}

    for evaluated in path:
        target = evaluated["expanded"]
        for slot in sources[evaluated["sceneId"]].get("slots", []):
            kind = slot.get("type")
            value = target.get("slots", {}).get(slot["id"])
            if kind == "talk" and project is not None:
                file(project / "talkmap.js"); directory(project / "talk", "**/*.jpg")
            elif kind in MEDIA_TYPES:
                if isinstance(value, dict) and isinstance(value.get("colorReviewFile"), str):
                    file(value["colorReviewFile"])
                raw = value.get("path") if isinstance(value, dict) else value
                if not isinstance(raw, str) or not raw.strip():
                    continue
                if kind in {"sequence", "wall", "wall-sprites"}:
                    pattern = value.get("glob", "*.jpg" if kind == "wall-sprites" else "*") if isinstance(value, dict) else "*.jpg" if kind == "wall-sprites" else "*"
                    directory(raw, pattern, ("wall-meta.json", "index.json") if kind == "wall-sprites" else ())
                else:
                    file(raw)
    # Preserve the content behind global inputs, not only their path strings.
    # Include missing files too: a late narration import changes the reviewed
    # audio/color baseline even when the existing talk frames are unchanged.
    if project is not None:
        file(project / "voice.wav")
        file(project / "import.json")
    for key in ("transcript", "monoFontFile", "colorReviewFile"):
        if isinstance(spec.get(key), str) and spec[key].strip():
            file(spec[key])
    music = spec.get("music")
    if isinstance(music, dict) and isinstance(music.get("path"), str):
        file(music["path"])
    fonts = spec.get("externalFontFiles", {})
    if isinstance(fonts, dict):
        for value in fonts.values():
            if isinstance(value, str):
                file(value)
    return [deepcopy(evidence[key]) for key in sorted(evidence)]


def propose_rematch(manifest, profile, spec, request, spec_dir, *, project=None, allow_pending_talk=False):
    """Return explicit local alternatives without changing the supplied spec."""
    spec_dir = Path(spec_dir)
    project = Path(project) if project is not None else None
    segments, contracts, sources, spans, fps = _structure(manifest, profile, spec)
    require(isinstance(request, dict) and request.get("schema") == REQUEST_SCHEMA, f"Request schema must be {REQUEST_SCHEMA}")
    require(not set(request) - {"schema", "baseSpecDigest", "segmentId", "candidates", "bindings"}, "Unknown local rematch request fields")
    require(request.get("baseSpecDigest") == spec_digest(spec), "baseSpecDigest mismatch; current spec changed")
    indices = [i for i, segment in enumerate(segments) if segment["id"] == request.get("segmentId")]
    require(len(indices) == 1, "Unknown local rematch segmentId")
    index = indices[0]; segment = segments[index]; original = spec["scenes"][index]
    require(not original.get("locked") and not segment.get("locked"), "Locked segment cannot be rematched")
    requested = request.get("candidates", {})
    require(isinstance(requested, dict), "candidates must map sceneId to explicit inputs/slots")
    require(all(sid in contracts for sid in requested), "Candidate scene is outside the reviewed profile")
    bindings = request.get("bindings", {})
    require(isinstance(bindings, dict), "bindings must be a slot object for the current scene")
    original_source = sources[original["sceneId"]][1]
    media_ids = {slot["id"] for slot in original_source.get("slots", []) if slot.get("type") in ATTACHMENT_TYPES}
    require(set(bindings) <= media_ids, "bindings may only supply declared visual media slots of the current scene")
    _explicit_candidate(original_source, {"slots": bindings})
    for sid, candidate in requested.items():
        _explicit_candidate(sources[sid][1], candidate)

    candidates, cache = [], {}
    for sid in dict.fromkeys([original["sceneId"], *requested]):
        source = sources[sid][1]
        target = deepcopy(original)
        local_reasons = []
        if sid == original["sceneId"]:
            supplied = requested.get(sid, {})
            try:
                additions = expand_inputs(source, supplied).get("slots", {})
                conflicts = [key for key in bindings if key in additions and
                             _media_identity(additions[key], spec_dir) != _media_identity(bindings[key], spec_dir)]
                require(not conflicts, f"Conflicting candidate and request bindings: {', '.join(sorted(conflicts))}")
                original_slots = expand_inputs(source, original).get("slots", {})
                protected = {slot["id"] for slot in source.get("slots", []) if slot.get("type") not in ATTACHMENT_TYPES}
                changed = [key for key in protected if key in additions and key in original_slots and additions[key] != original_slots[key]]
                require(not changed, f"Current scene user content must be preserved: {', '.join(sorted(changed))}")
                target.pop("inputs", None)
                target["slots"] = {**deepcopy(original_slots), **deepcopy(additions), **deepcopy(bindings)}
            except (AdaptError, SemanticInputError) as exc:
                local_reasons.append(str(exc))
        else:
            target.pop("inputs", None); target.pop("slots", None)
            target.update(deepcopy(requested[sid]))
        target["sceneId"] = sid
        target["cues"], _ = _cues(source, contracts[sid], segment, spans[index][0], fps)
        proposal = deepcopy(spec); proposal["scenes"][index] = target
        path, reasons, missing, _ = _whole_plan(manifest, profile, proposal, spec_dir, project, allow_pending_talk)
        reasons = local_reasons + reasons
        media_bindings, consumed_inputs, unconsumed = _consumption(source, path[index]["expanded"], requested, bindings,
                                                                 original["sceneId"], segment["id"], spec_dir)
        missing.extend(f"Unconsumed request binding {item['slotId']}; explicitly map this media to the candidate" for item in unconsumed)
        media = _media_evidence(manifest, proposal, path, spec_dir, project, cache)
        ready = not reasons and not missing
        row = {"candidateId": sid, "sceneId": sid, "status": "rejected" if reasons else "needs-binding" if missing else "ready",
               "reasons": reasons, "missing": missing, "effects": deepcopy(contracts[sid]["effects"]),
               "score": sum(_sequence_cost(path[:i], item, segments[i]) for i, item in enumerate(path)),
               "mediaEvidence": media, "mediaEvidenceDigest": _digest({"media": media}),
               "mediaBindings": media_bindings, "consumedInputs": consumed_inputs, "unconsumedRequestBindings": unconsumed}
        if ready:
            # Only the target may normalize its semantic inputs/media paths.
            proposal["scenes"][index] = deepcopy(path[index]["target"])
            metadata = proposal["adaptation"]
            metadata["ready"] = True
            metadata["validationStage"] = "pre-import" if any(item.get("deferred") for item in path) else "bound-media"
            metadata["localRematch"] = {"schema": "adu-local-rematch-receipt/1", "baseSpecDigest": request["baseSpecDigest"],
                                        "requestDigest": _digest(request), "segmentId": segment["id"],
                                        "fromSceneId": original["sceneId"], "toSceneId": sid, "profileDigest": profile_digest(profile)}
            row.update(proposalSpec=proposal, proposalDigest=spec_digest(proposal),
                       deferred=[deepcopy(check) for item in path for check in item.get("deferred", [])],
                       audio=audio_diagnostics([item["planned"] for item in path if item.get("planned")], fps))
        row["candidateDigest"] = _digest(row)
        candidates.append(row)
    return {"schema": BUNDLE_SCHEMA, "baseSpecDigest": spec_digest(spec), "profileDigest": profile_digest(profile),
            "manifestDigest": manifest_digest(manifest), "segmentId": segment["id"], "request": deepcopy(request),
            "requestDigest": _digest(request), "context": {"project": str(project.resolve()) if project else None, "allowPendingTalk": allow_pending_talk},
            "candidates": candidates, "rankedCandidateIds": [row["candidateId"] for row in sorted(candidates, key=lambda row: (row["status"] != "ready", row["score"], row["candidateId"]))]}


def apply_rematch(manifest, profile, current_spec, bundle, candidate_id, spec_dir, *, project=None, allow_pending_talk=False):
    """Recompute, reject stale/tampered data, then return a separate spec object."""
    require(isinstance(bundle, dict) and bundle.get("schema") == BUNDLE_SCHEMA, f"Bundle schema must be {BUNDLE_SCHEMA}")
    require(bundle.get("baseSpecDigest") == spec_digest(current_spec), "baseSpecDigest mismatch; current spec changed")
    require(bundle.get("profileDigest") == profile_digest(profile), "Bundle profileDigest mismatch")
    require(bundle.get("manifestDigest") == manifest_digest(manifest), "Bundle manifestDigest mismatch")
    require(isinstance(bundle.get("request"), dict) and bundle.get("requestDigest") == _digest(bundle["request"]), "Bundle requestDigest mismatch")
    rows = bundle.get("candidates")
    require(isinstance(rows, list) and all(isinstance(row, dict) for row in rows), "Bundle candidates must be objects")
    choices = [row for row in rows if row.get("candidateId") == candidate_id]
    require(len(choices) == 1, "Unknown or duplicate candidateId")
    chosen = choices[0]
    require(chosen.get("candidateDigest") == _digest({key: value for key, value in chosen.items() if key != "candidateDigest"}), "Candidate digest mismatch")
    require(chosen.get("status") == "ready" and isinstance(chosen.get("proposalSpec"), dict), "Only a ready candidate may be applied")
    require(chosen.get("proposalDigest") == spec_digest(chosen["proposalSpec"]), "Proposal digest mismatch")
    fresh = propose_rematch(manifest, profile, current_spec, bundle["request"], spec_dir,
                            project=project, allow_pending_talk=allow_pending_talk)
    require(_digest(fresh) == _digest(bundle), "Rematch bundle changed or stale (including media evidence); regenerate proposals")
    selected = next(row for row in fresh["candidates"] if row["candidateId"] == candidate_id)
    require(selected["status"] == "ready", "Candidate is no longer ready")
    result = deepcopy(selected["proposalSpec"])
    index = next(i for i, segment in enumerate(current_spec["adaptation"]["segments"]) if segment["id"] == bundle["segmentId"])
    require(all(scene == result["scenes"][i] for i, scene in enumerate(current_spec["scenes"]) if i != index), "Non-target scenes changed")
    require({k: v for k, v in current_spec.items() if k not in {"scenes", "adaptation"}} ==
            {k: v for k, v in result.items() if k not in {"scenes", "adaptation"}}, "Global settings changed")
    require(current_spec["adaptation"]["segments"] == result["adaptation"]["segments"], "Semantic segments changed")
    return result
