import re
import copy

from thai_lcc import segment
from thai_syl import Syllable
import thai_ipa


def _compute_can_merge(clusters: list) -> list:
    """
    For each cluster, determine whether it is allowed to merge with the
    cluster(s) in front of it (i.e. be a non-initial member of a syllable
    group), rather than being forced to start a new syllable.

    can_merge[i] == False means cluster i can never be swallowed into a
    preceding group -- it must begin a new syllable group.
    """
    can_merge = [True] * (len(clusters) + 1)  # Can merge with cluster in front
    for i, cluster in enumerate(clusters):
        syllable = Syllable.extract(cluster, force_cluster=False, sesquisyllable=False)
        if re.match(r'^[เ-ไ]', cluster) or len(syllable.onset_chars) > 1:
            can_merge[i] = False
        if re.search(r'[ะำ]', cluster):
            can_merge[i + 1] = False
    return can_merge


def _candidate_syllables(text: str, prev_syllable: 'Syllable' = None, next_cluster: str = None):
    """
    For a chunk of text (one or more merged LTCCs), yield every distinct
    (Syllable, part_objs) reading worth trying, from simplest to most exotic:

      - sesquisyllable: always try both False and True (extract() is a no-op
        difference when there's nothing to split, so this never hurts).
      - force_cluster: always tried both ways. has_ambiguous_cluster only
        gets set for *unrecognized* onset combos -- a recognized old_thai
        or old_khmer cluster (e.g. ปล in แปล) takes a different branch in
        extract() entirely, defaulting to an onset+coda split with no
        has_ambiguous_cluster flag at all, even though force_cluster=True
        still produces a genuinely different, valid reading (the actual
        pl- cluster). Since that flag can't be trusted to catch every case
        where force_cluster matters, there's no reliable gate cheaper than
        just trying both -- extract() is cheap enough that this costs
        nothing to always do.
      - tone assimilation: only tried if a prev_syllable (the syllable group
        immediately preceding this one in the accepted parse) was given and
        its main syllable actually has an onset to donate a class from --
        assimilate_tone() is a no-op otherwise.
      - vowel assimilation: assimilate_vowel() looks the opposite direction
        from assimilate_tone() -- it's the *following* syllable that
        triggers it (e.g. the ร in กร-ณี licensing ก to read as กอ instead
        of กะ), which this function can't see on its own since it only ever
        gets handed the current group's own text. next_cluster is that
        lookahead: the single following LTCC cluster, unmerged, extracted
        on its own and handed to assimilate_vowel() as the candidate donor.
        It's a no-op unless the conditions actually hold (bare single-ร
        donor, bare vowel-less single-consonant self), so this is safe to
        always offer when a next_cluster is available.
      - is_reduplicated: only tried if the resulting Syllable reports
        is_reduplicable (and actually produced a reduplicated syllable).
        Syllable.extract() itself now falls back to the longest matching
        prefix and folds whatever's left over into the reduplicated
        syllable, so this covers both bare-coda redup (ม -> ma) and
        borrowed-vowel redup (ต+รา -> traː) without any help from here --
        thai_gpa just has to hand it the full merged group text.

    part_objs is the list of SyllablePart references (minor?, main,
    reduplicated?) this reading is built from, in order -- references into
    `result` itself, not copies, so the caller can compare them against a
    target and set irregular_vowel/irregular_tone directly when needed.
    """
    force_cluster_options = [False, True]

    can_assimilate = bool(prev_syllable is not None and prev_syllable.main_syllable.onset_chars)

    seen = set()
    for sesqui in (False, True):
        for force_cluster in force_cluster_options:
            base = Syllable.extract(text, force_cluster=force_cluster, sesquisyllable=sesqui)

            for assimilated in ([False, True] if can_assimilate else [False]):
                syl = copy.deepcopy(base)
                if assimilated:
                    syl.assimilate_tone(prev_syllable)
                syl.sound_shift()

                has_minor = bool(syl.minor_syllable.nucleus)
                has_redup = bool(syl.is_reduplicable and syl.reduplicated_syllable.nucleus)

                redup_options = [False, True] if has_redup else [False]
                for redup in redup_options:
                    parts = (
                        ([syl.minor_syllable] if has_minor else [])
                        + [syl.main_syllable]
                        + ([syl.reduplicated_syllable] if redup else [])
                    )
                    dedup_key = tuple(p.get_ipa(apply_irregularities=False) for p in parts)
                    if dedup_key in seen:
                        continue
                    seen.add(dedup_key)

                    result = copy.deepcopy(syl)
                    result.is_reduplicated = redup
                    result_parts = (
                        ([result.minor_syllable] if has_minor else [])
                        + [result.main_syllable]
                        + ([result.reduplicated_syllable] if redup else [])
                    )
                    yield result, result_parts

    if next_cluster:
        donor = Syllable.extract(next_cluster, force_cluster=False, sesquisyllable=False)
        vowel_syl = Syllable.extract(text, force_cluster=False, sesquisyllable=False)
        vowel_syl.assimilate_vowel(donor)
        if vowel_syl.is_vowel_assimilated:
            vowel_syl.sound_shift()
            dedup_key = (vowel_syl.main_syllable.get_ipa(apply_irregularities=False),)
            if dedup_key not in seen:
                seen.add(dedup_key)
                yield vowel_syl, [vowel_syl.main_syllable]


def _effective_nucleus(p: 'SyllablePart'):
    return p.assimilated_nucleus if (p.assimilate_vowel and p.assimilated_nucleus is not None) else p.nucleus


def _effective_coda(p: 'SyllablePart'):
    return p.assimilated_coda if (p.assimilate_vowel and p.assimilated_nucleus is not None) else p.coda


def _effective_tone(p: 'SyllablePart'):
    if p.assimilate_vowel and p.assimilated_nucleus is not None:
        return p.assimilated_vowel_tone if p.assimilated_vowel_tone is not None else p.tone
    return p.assimilated_tone if (p.assimilate_tone and p.assimilated_tone is not None) else p.tone


def _strip_length(nucleus):
    return nucleus.rstrip('ː') if nucleus else nucleus


def _lenient_match(part_objs: list, target_slice: list):
    """
    Fallback comparison used only once the strict pass has found no
    complete solution anywhere in the word. Unlike the strict pass (which
    requires an exact string match), this allows each part's coda, nucleus,
    and tone to independently differ from its target -- never onset or
    medial, since those aren't the kind of thing that goes irregular on
    their own. A word can need more than one irregularity at once (เจน is
    spelled with the long-eː เ pattern and its class/coda would regularly
    give ˧, but it's actually said with both a short e AND tone ˦˩), so
    each is checked independently rather than requiring at most one to be
    off. thai_ipa.parse() already hands back onset/medial/nucleus/coda/tone
    as separate fields, so this can tell exactly which respects are off
    rather than falling back to fuzzy string distance. A nucleus mismatch is
    further split: if stripping the length mark makes both sides equal,
    it's the same vowel just spoken short/long (irregular_vowel_duration);
    otherwise it's a genuinely different vowel (irregular_vowel). Coda
    mismatches cover borrowed-word codas that skip standard Thai
    neutralization -- ออสเตรีย's -s (ส would regularly neutralize to -t),
    ครัช's -t͡ɕʰ (ช would regularly neutralize to -t), and dark-l -w
    (ล would regularly neutralize to -n).

    Returns a list of (part, kind, value) irregularities to apply if every
    part's onset/medial match exactly (the list is empty when coda,
    nucleus, and tone also matched exactly -- still a valid, just
    non-irregular, lenient match), or None if any part's onset/medial don't
    match -- too different to call "irregular".
    """
    irregularities = []
    for p, t in zip(part_objs, target_slice):
        onset_ok = (p.onset or '') == (t['initial'] or '')
        medial_ok = (p.medial or '') == (t['medial'] or '')
        if not (onset_ok and medial_ok):
            return None

        if (_effective_coda(p) or '') != (t['coda'] or ''):
            irregularities.append((p, 'coda', t['coda']))

        p_nucleus = _effective_nucleus(p)
        if p_nucleus != t['nucleus']:
            if _strip_length(p_nucleus) == _strip_length(t['nucleus']):
                duration = 'long' if (t['nucleus'] or '').endswith('ː') else 'short'
                irregularities.append((p, 'duration', duration))
            else:
                irregularities.append((p, 'vowel', t['nucleus']))

        if _effective_tone(p) != t['tone']:
            irregularities.append((p, 'tone', t['tone']))

    return irregularities


def align_all(text: str, ipa: str) -> list:
    """
    Align Thai text against its IPA transcription, returning EVERY distinct
    way of parsing `text` into a sequence of Syllable objects (one per
    orthographic syllable-group -- a sesquisyllable still counts as a single
    Syllable with both a minor and main part) whose combined IPA
    reconstructs `ipa` exactly.

    Ambiguity is inherent here, not a bug to resolve down to one answer: the
    same surface IPA can genuinely arise from more than one valid grouping.
    In กฐิน, for instance, ก can either be folded into a single sesquisyllable
    Syllable together with ฐิน (minor+main in one object), or stand as its
    own standalone syllable that donates its tone class to ฐิน next door via
    assimilate_tone() -- both are legitimate readings of the same word, and
    both come back here.

    Some words just don't have a regular explanation at all -- เล่น is
    spelled with the long-eː เ pattern but is actually said with a short e;
    ฤทธิ์'s ฤ mechanically gives rɯ but is actually said ri. For those, this
    runs a second, lenient pass that only ever engages when the strict pass
    finds no complete solution anywhere in the word: it allows a syllable to
    differ from its target in exactly one of (nucleus, tone) -- never
    onset/medial/coda, which aren't the kind of thing that goes irregular on
    their own -- and records the target's actual value as irregular_vowel or
    irregular_tone on that syllable. Since the only way to ever reach this
    fallback is to already have the correct target IPA in hand, whatever it
    records is by construction the true pronunciation, not a guess -- which
    is why get_ipa() applies these by default.
    """
    clusters = segment(text)
    targets = thai_ipa.parse(ipa)
    can_merge = _compute_can_merge(clusters)

    n_clusters = len(clusters)
    n_targets = len(targets)

    def run(strict: bool) -> list:
        # (ci, ti, donor_key) -> list of continuations (list[list[Syllable]]),
        # each a way to complete the parse from that state onward.
        # Reachability from here only ever depends on position and the
        # donor's class (see donor_key below), never on how we got here, so
        # this is safe to cache and reuse across different outer paths that
        # land on the same state. Strict and lenient runs get their own
        # memo, since what's reachable differs between them.
        memo: dict = {}

        def backtrack(ci: int, ti: int, prev: 'Syllable' = None) -> list:
            if ci == n_clusters and ti == n_targets:
                return [[]]
            if ci >= n_clusters or ti >= n_targets:
                return []

            donor_key = prev.main_syllable.onset_chars if prev is not None else None
            memo_key = (ci, ti, donor_key)
            if memo_key in memo:
                return memo[memo_key]

            solutions = []
            max_end = ci + 1
            while max_end < n_clusters and can_merge[max_end]:
                max_end += 1

            for end in range(ci + 1, max_end + 1):
                group_text = ''.join(clusters[ci:end])
                next_cluster = clusters[end] if end < n_clusters else None
                for syl, part_objs in _candidate_syllables(group_text, prev_syllable=prev, next_cluster=next_cluster):
                    n = len(part_objs)
                    if ti + n > n_targets:
                        continue
                    target_slice = targets[ti:ti + n]

                    if strict:
                        parts = [p.get_ipa(apply_irregularities=False) for p in part_objs]
                        expected = [t['syllable'] for t in target_slice]
                        if parts != expected:
                            continue
                    else:
                        irregularities = _lenient_match(part_objs, target_slice)
                        if irregularities is None:
                            continue
                        for part, kind, value in irregularities:
                            if kind == 'vowel':
                                part.irregular_vowel = value
                            elif kind == 'duration':
                                part.irregular_vowel_duration = value
                            elif kind == 'coda':
                                part.irregular_coda = value
                            else:
                                part.irregular_tone = value
                        if irregularities:
                            syl.is_irregular = True

                    for rest in backtrack(end, ti + n, syl):
                        solutions.append([syl] + rest)

            memo[memo_key] = solutions
            return solutions

        return backtrack(0, 0, None)

    solutions = run(strict=True)
    if not solutions:
        solutions = run(strict=False)
    if not solutions:
        raise ValueError(f"Could not align {text!r} with {ipa!r}")

    # Different search paths can land on structurally identical parses
    # (same group texts, same flags, same irregularities) -- collapse those
    # down.
    def _signature(s: 'Syllable') -> tuple:
        return (
            s.text, s.is_reduplicated, bool(s.minor_syllable.nucleus),
            s.main_syllable.irregular_vowel, s.main_syllable.irregular_vowel_duration, s.main_syllable.irregular_tone, s.main_syllable.irregular_coda,
            s.minor_syllable.irregular_vowel, s.minor_syllable.irregular_vowel_duration, s.minor_syllable.irregular_tone, s.minor_syllable.irregular_coda,
            s.reduplicated_syllable.irregular_vowel, s.reduplicated_syllable.irregular_vowel_duration, s.reduplicated_syllable.irregular_tone, s.reduplicated_syllable.irregular_coda,
        )

    seen = set()
    unique_solutions = []
    for sol in solutions:
        key = tuple(_signature(s) for s in sol)
        if key in seen:
            continue
        seen.add(key)
        unique_solutions.append(sol)

    return unique_solutions


def _solution_cost(solution: list) -> int:
    """
    Preference score for choosing among multiple valid parses of the same
    IPA -- lower is better. assimilate_tone() lets a syllable borrow its
    tone class from an unrelated donor across a syllable boundary, which is
    the only way to explain some words (ประโยชน์: ปร is a genuine onset
    cluster, so ประ can't be split into a minor syllable at all, and โยชน์
    only gets the right tone by reaching back across the boundary to ป).
    But when a plain sesquisyllable Syllable -- one object, minor_syllable
    populated -- already explains the same IPA without reaching outside
    itself, that's the more direct reading and should win. Counting
    is_tone_assimilated occurrences captures exactly that: it's True only
    on syllables that had to borrow a class from a neighbor, never on a
    minor_syllable-based reading (that's a different, self-contained
    mechanism).
    """
    return sum(1 for s in solution if s.is_tone_assimilated or s.is_vowel_assimilated or s.is_irregular)


def evaluate(text: str, ipa: str) -> tuple:
    """
    Align `text` against `ipa` and return (reconstructed_text, reconstructed_ipa)
    for the whole word -- reconstructed_text should equal `text` and
    reconstructed_ipa should equal `ipa` when alignment succeeded, making
    this convenient for scoring against a dataset of (text, ipa) pairs.
    """
    result = align(text, ipa)
    reconstructed_text = ''.join(s.reconstruct_text() for s in result)
    reconstructed_ipa = '.'.join(s.get_ipa(is_reduplicated=s.is_reduplicated) for s in result)
    return reconstructed_text, reconstructed_ipa


def align(text: str, ipa: str) -> list:
    """
    Align Thai text against its IPA transcription, returning ONE list of
    Syllable objects whose combined, sound-shifted IPA reconstructs `ipa`
    exactly. Among multiple valid parses, prefers ones that explain a
    syllable's tone via its own minor_syllable over ones that reach across
    a syllable boundary via assimilate_tone() -- the latter is only chosen
    when it's the only valid explanation available. Use align_all() to see
    every valid reading, unranked.
    """
    solutions = align_all(text, ipa)
    return min(solutions, key=_solution_cost)