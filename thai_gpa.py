from dataclasses import replace

from thai_lcc import segment
from thai_syl import Syllable, SyllablePart
import thai_ipa

MAX_SPAN = 4  # widest plausible grapheme-cluster span for one merged text group

# A cluster is "bridge-eligible" if it's a single bare consonant with no
# vowel or tone marks -- i.e. it's ambiguous whether it belongs to the
# previous syllable (as coda) or should also be read as part of the next
# syllable's onset cluster (e.g. the 'ต' in สุจิตรา -> สุ.จิต.ตรา).
_THAI_CONSONANTS = set('กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ')

# Flag combinations to try when extracting a merged span. force_cluster
# controls whether a 2-consonant onset with no explicit yamakkan mark is
# read as a genuine cluster; sesquisyllable controls whether a leading
# 2-consonant onset is instead split into a minor pre-syllable + main.
_EXTRACT_FLAG_COMBOS = [
    (force_cluster, sesquisyllable)
    for force_cluster in (False, True)
    for sesquisyllable in (False, True)
]


def _is_bridge_cluster(cluster: str) -> bool:
    return len(cluster) == 1 and cluster in _THAI_CONSONANTS


def _effective_tone(part: SyllablePart):
    '''The tone SyllablePart.get_ipa() actually emits: assimilated tone
    takes precedence over the syllable's own raw tone when assimilation
    applies (e.g. a sesquisyllable main syllable inheriting its tone
    class from the minor syllable's onset consonant). Scoring against
    the raw .tone field instead of this would silently penalize correct
    assimilated readings.'''
    if part.assimilate_tone and part.assimilated_tone is not None:
        return part.assimilated_tone
    return part.tone


def _score(part: SyllablePart, target: dict) -> float:
    '''Structural match between a predicted SyllablePart and a target
    phoneme dict from thai_ipa.parse. Equal weight per field; None==None
    (e.g. no medial on both sides) counts as a match.'''
    fields = (
        (part.onset, target['initial']),
        (part.medial, target['medial']),
        (part.nucleus, target['nucleus']),
        (part.coda, target['coda']),
        (_effective_tone(part), target['tone']),
    )
    return sum(1 for p, t in fields if p == t) / len(fields)


def _sub_parts(syl: Syllable, use_redup: bool) -> list:
    '''The ordered list of SyllableParts a given extraction actually
    realizes as separate spoken syllables: an optional sesquisyllable
    minor syllable, the main syllable, and an optional reduplicated
    syllable read off the leftover coda.'''
    parts = []
    if syl.minor_syllable.nucleus:
        parts.append(syl.minor_syllable)
    if syl.main_syllable.nucleus:
        parts.append(syl.main_syllable)
    if use_redup and syl.is_reduplicable and syl.is_reduplicatedd_syllable.nucleus:
        parts.append(syl.is_reduplicatedd_syllable)
    return parts


def _candidate_readings(text: str):
    '''Yield (parts, syl) for every distinct reading of `text` worth
    scoring: each extraction-flag combo, crossed with whether we treat
    a reduplicable coda as a real extra syllable or not (both are valid
    Thai readings depending on context, so both must be tried).'''
    seen_signatures = set()
    for force_cluster, sesquisyllable in _EXTRACT_FLAG_COMBOS:
        try:
            syl = Syllable.extract(text, force_cluster=force_cluster, sesquisyllable=sesquisyllable)
            syl.sound_shift()
        except Exception:
            continue

        redup_options = (False, True) if syl.is_reduplicable else (False,)
        for use_redup in redup_options:
            parts = _sub_parts(syl, use_redup)
            if not parts:
                continue
            signature = tuple(p.get_ipa() for p in parts)
            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)
            yield parts, syl


def _wrap(part, text: str) -> Syllable:
    '''Wrap a single realized SyllablePart back into a standalone
    Syllable so each returned item prints/behaves as one syllable,
    regardless of whether it came from a minor, main, or reduplicated
    reading.'''
    return Syllable(text=text, main_syllable=part)


def _with_assimilation_variants(parts: list, wrapped: list, donor_onset_chars):
    '''Given a span's realized parts (already wrapped as standalone
    Syllables), yield both the as-extracted reading and -- if there's a
    preceding syllable to borrow from -- a second reading where the
    first syllable of this span has had its tone assimilated from that
    donor's onset consonant class. This is a distinct mechanism from
    the internal sesquisyllable minor->main link (which extract() /
    sound_shift() already handle on their own): it links two separately
    resolved syllables across a span boundary, e.g. ประ -> โยชน์ in
    ประโยชน์, where โยชน์'s tone is not predictable from its own onset
    at all -- only from ประ's.

    Note: assimilate_tone() mutates the SyllablePart it's called on, so
    the assimilated variant must operate on a fresh copy -- the
    unassimilated variant above is still referenced by the caller and
    must not be silently altered.'''
    yield parts, wrapped

    if donor_onset_chars is None:
        return

    donor = Syllable(text='', main_syllable=SyllablePart(onset_chars=donor_onset_chars))
    assimilated_first = _wrap(replace(wrapped[0].main_syllable), wrapped[0].text)
    assimilated_first.assimilate_tone(donor)
    assimilated_first.sound_shift()  # assimilate_tone only sets the raw
    # tone category (e.g. 'D'); sound_shift converts it to the actual
    # contour symbol (e.g. '˨˩') via the tone table, same as it does
    # for a syllable's own .tone.
    yield parts, [assimilated_first] + wrapped[1:]


def align(text: str, ipa: str) -> list:
    '''
    Aligns Thai graphemes with a Thai IPA transcription into syllables.

    Uses the target IPA as an oracle to resolve segmentation ambiguity,
    rather than guessing cluster-merge decisions blind. Three distinct
    ambiguity patterns are searched:

      1. A merged span of clusters can realize more than one spoken
         syllable on its own, via thai_syl's sesquisyllable (minor
         syllable) and reduplication (coda re-read with its own vowel)
         mechanisms -- e.g. กิจ -> [kit, t͡ɕaʔ] from one extract() call.

      2. A trailing bare consonant can instead be a genuine "bridge":
         shared between the coda of one syllable and the onset cluster
         of the next, when it combines with graphemes that follow it
         rather than standing alone -- e.g. จิต + ตรา, where ต only
         resolves correctly once merged with ร.

      3. A syllable's tone can be unpredictable from its own onset and
         instead assimilated from the *previous* syllable's onset class
         -- e.g. ประ -> โยชน์ in ประโยชน์, via Syllable.assimilate_tone.
         Unlike (1), this links two already-separate syllables across a
         span boundary, so it's tried as an alternate reading of each
         new span's first syllable, conditioned on whichever syllable
         preceded it in the path.

    Every candidate span/flag/reading/assimilation combination is scored
    against the known target syllables from thai_ipa.parse, and the
    highest-scoring full alignment (via memoized search) is returned.
    '''
    clusters = segment(text)
    targets = thai_ipa.parse(ipa)
    n, m = len(clusters), len(targets)

    memo = {}

    def solve(a: int, i: int, prev_onset_chars):
        key = (a, i, prev_onset_chars)
        if key in memo:
            return memo[key]
        if i == m:
            memo[key] = (0.0 if a == n else float('-inf'), [])
            return memo[key]
        if a >= n:
            memo[key] = (float('-inf'), [])
            return memo[key]

        best_score, best_path = float('-inf'), None
        for span_len in range(1, min(MAX_SPAN, n - a) + 1):
            b = a + span_len
            text_chunk = ''.join(clusters[a:b])

            for parts, syl in _candidate_readings(text_chunk):
                k = len(parts)
                if i + k > m:
                    continue
                wrapped_base = [_wrap(p, text_chunk) for p in parts]

                for variant_parts, variant_wrapped in _with_assimilation_variants(
                    parts, wrapped_base, prev_onset_chars
                ):
                    # Weighted sum (not average) so path scores are
                    # comparable across different span/syllable counts:
                    # a 2-syllable span matched perfectly must outscore
                    # two 1-syllable spans matched at 90% each, not lose
                    # to them just because splitting produces more
                    # separately-scored pieces. Total is out of m at the
                    # root, same as before.
                    span_total = sum(
                        _score(s.main_syllable, targets[i + j])
                        for j, s in enumerate(variant_wrapped)
                    )
                    next_prev_onset = variant_wrapped[-1].main_syllable.onset_chars

                    # normal continuation: next span starts fresh at b
                    rest_score, rest_path = solve(b, i + k, next_prev_onset)
                    total = span_total + rest_score
                    if total > best_score:
                        best_score, best_path = total, variant_wrapped + rest_path

                    # bridge continuation: next span reuses clusters[b-1]
                    # (redup and bridge are two different explanations
                    # for the same leftover grapheme -- both get tried)
                    if _is_bridge_cluster(clusters[b - 1]):
                        rest_score, rest_path = solve(b - 1, i + k, next_prev_onset)
                        total = span_total + rest_score
                        if total > best_score:
                            best_score, best_path = total, variant_wrapped + rest_path

        memo[key] = (best_score, best_path if best_path is not None else [])
        return memo[key]

    score, path = solve(0, 0, None)
    if not path or score == float('-inf'):
        raise ValueError(f'Could not align {text!r} with {ipa!r}')

    avg_score = score / m
    if avg_score < 1.0:
        import warnings
        warnings.warn(f'Alignment for {text!r} matched at {avg_score:.0%} field-confidence, not exact')

    return path