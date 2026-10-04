"""Narration ownership is exclusive; visual supporting references are reusable.

This validates declared evidence, never infers polarity, causal meaning or word
timestamps. Legacy briefs remain readable and report their missing source proof.
"""
import hashlib
from pathlib import Path

from adapt_project import require

SCHEMA = 'adu-content-evidence/1'


def text_identity(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def from_text(text, units, *, source_kind='supplied-transcript'):
    """Create stable references to exact character spans; timing is optional."""
    require(isinstance(text, str) and text, 'Evidence requires original narration text')
    identity = text_identity(text)
    result = []
    for item in units:
        a, b = item['start'], item['end']
        require(type(a) is int and type(b) is int and 0 <= a < b <= len(text), 'Invalid evidence text span')
        result.append({**item, 'id': f'{identity[:16]}:{a}:{b}', 'text': text[a:b]})
    return dict(schema=SCHEMA, text=text, textSha256=identity, sourceKind=source_kind, units=result)


def validate_coverage(evidence, segments):
    if evidence is None:
        return dict(status='source-unrecorded', ownership='not verified',
                    nextAction='Bind original transcript and exclusive ownershipRefs; assistant checks meaning, negation, conditions, entities and units.')
    require(isinstance(evidence, dict) and evidence.get('schema') == SCHEMA, 'Invalid contentEvidence schema')
    text = evidence.get('text')
    require(isinstance(text, str) and text and evidence.get('textSha256') == text_identity(text), 'Narration text identity changed')
    units = evidence.get('units')
    require(isinstance(units, list) and units, 'Evidence requires narration units')
    seen, offset, ordered = set(), 0, []
    for unit in units:
        require(isinstance(unit, dict), 'Evidence unit must be an object')
        a, b, ref = unit.get('start'), unit.get('end'), unit.get('id')
        require(type(a) is int and type(b) is int and a == offset and a < b <= len(text), 'Evidence units must cover the original text in order without gaps')
        require(ref == f'{evidence["textSha256"][:16]}:{a}:{b}' and ref not in seen, 'Unstable or duplicate narration reference')
        require(unit.get('text') == text[a:b], f'{ref}: original text differs')
        seen.add(ref); ordered.append(ref); offset = b
    require(offset == len(text), 'Evidence drops narration tail')
    owned, displays = [], []
    for segment in segments:
        refs = segment.get('ownershipRefs')
        require(isinstance(refs, list) and refs and all(r in seen for r in refs), f'{segment["id"]}: missing or unknown ownershipRefs')
        owned.extend(refs)
        supporting = segment.get('supportingRefs', {})
        require(isinstance(supporting, dict), 'supportingRefs must map display fields to references')
        for field, values in supporting.items():
            require(isinstance(values, list) and values and all(r in seen for r in values), f'{segment["id"]}.{field}: unknown supporting reference')
            displays.append(dict(segmentId=segment['id'], field=field, refs=values))
    expected = evidence.get("scopeRefs", ordered)
    require(isinstance(expected, list) and expected and all(r in seen for r in expected) and len(expected) == len(set(expected)), "Invalid evidence scope")
    require([r for r in ordered if r in set(expected)] == expected, "Evidence scope reordered narration")
    require(owned == expected, 'Narration ownership has missing, repeated or reordered units')
    for asset in evidence.get('assets', []):
        require(isinstance(asset, dict) and isinstance(asset.get('path'), str), 'Evidence asset requires path')
        path = Path(asset['path'])
        require(path.is_absolute() and path.is_file(), 'Evidence asset must identify an existing absolute file')
        with path.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        require(digest == asset.get('sha256'), 'Evidence asset identity changed: ' + asset.get('id', path.name))
    fact_checks=validate_fact_bindings(evidence,segments,seen)
    return dict(factChecks=fact_checks,status='declared-source-verified' if expected == ordered else 'partial-composition-scope-verified', textSha256=evidence['textSha256'],
                units=len(units), ownedUnits=len(owned), displayEvidence=displays,
                semanticReview='assistant must verify polarity, conditions, numbers, units and compared entities; no semantic classifier')


def derive_from_transcript(brief, segments, directory, fps):
    """Derive sentence references only when whole timed cues have one owner.

    Crossing a segment boundary without reliable word times is intentionally
    unrecorded: an assistant must revise ownership, not guess which words moved.
    """
    from copy import deepcopy
    from adapt_project import transcript_rows
    if brief.get('contentEvidence') is not None or not brief.get('transcript'):
        return brief,segments,None
    cues=transcript_rows(brief['transcript'],Path(directory));owners=[];cursor=0
    ranges=[]
    for segment in segments:
        end=cursor+segment['durationFrames'];ranges.append((cursor/fps,end/fps));cursor=end
    for cue in cues:
        matches=[i for i,(a,b) in enumerate(ranges) if a<=cue['start'] and cue['end']<=b+1e-9]
        if len(matches)!=1:return brief,segments,'Complete transcript cue crosses a segment boundary; sentence-level ownership needs review'
        owners.append(matches[0])
    # Empty ownership is not fabricated for a silent/director-only segment.
    if set(owners)!=set(range(len(segments))):return brief,segments,'Some segments lack complete transcript cues; original source coverage not inferred'
    text='';units=[]
    for cue in cues:
        start=len(text);text+=cue['text']+'\n';units.append(dict(start=start,end=len(text),cueId=cue['id'],time=dict(clock=brief.get('narrationClock','edited-narration'),start=cue['start'],end=cue['end'])))
    evidence=from_text(text,units,source_kind='derived-whole-transcript-cues')
    if isinstance(brief['transcript'],str):
        path=Path(brief['transcript']);path=(path if path.is_absolute() else Path(directory)/path).resolve()
        with path.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
        evidence['assets']=[dict(id='original-transcript',path=str(path),sha256=digest)]
    result=deepcopy(brief);items=deepcopy(segments)
    for i,segment in enumerate(items):segment['ownershipRefs']=[u['id'] for u,owner in zip(evidence['units'],owners) if owner==i]
    result['contentEvidence']=evidence;result['segments']=items
    return result,items,None


def validate_fact_bindings(evidence,segments,refs):
    """Check declared counts/entities/units against actual structured input.

    Facts are authored from the quoted source; this checks consumption and
    contradictions, not automatic truth or entailment of the spoken sentence.
    """
    import math
    from semantic_inputs import field,SemanticInputError
    facts={}
    for fact in evidence.get('facts',[]):
        require(isinstance(fact,dict) and fact.get('id') and fact['id'] not in facts,'Fact needs a distinct stable id')
        require(fact.get('supportingRefs') and all(r in refs for r in fact['supportingRefs']),'Fact requires known original source references')
        kind,value=fact.get('type'),fact.get('value')
        require(kind in {'count','number','entity'},'Fact type must be count, number or entity')
        if kind=='count':require(type(value) is int and value>=0,'Count fact must be a nonnegative integer')
        if kind=='number':require(type(value) in {int,float} and math.isfinite(value) and isinstance(fact.get('unit'),str) and fact['unit'],'Numeric fact needs value and explicit unit')
        if kind=='entity':require(isinstance(value,str) and value,'Entity fact requires stable identity')
        facts[fact['id']]=fact
    used=set();checks=[]
    for segment in segments:
        for path,fact_id in segment.get('factBindings',{}).items():
            require(fact_id in facts,'Unknown fact '+str(fact_id));fact=facts[fact_id]
            try:value=field(segment,path)
            except SemanticInputError as exc:raise ValueError(str(exc)) from exc
            require(value==fact['value'],f'{segment["id"]}.{path}: fact {fact_id} differs ({value!r} vs {fact["value"]!r})')
            used.add(fact_id);checks.append(dict(segmentId=segment['id'],field=path,fact=fact_id,value=value,unit=fact.get('unit')))
    if 'scopeRefs' not in evidence:require(used==set(facts),'Unconsumed declared facts: '+', '.join(sorted(set(facts)-used)))
    return checks
