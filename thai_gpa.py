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
        if re.search(r'[ะำ์]', cluster):
            can_merge[i + 1] = False
    return can_merge


def _candidate_syllables(text: str, prev_syllable: 'Syllable' = None, next_cluster: str = None):
    """
    For a chunk of text (one or more merged LTCCs), yield every distinct
    (Syllable, ipa_parts) reading worth trying, from simplest to most exotic:

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

    ipa_parts is the list of surface IPA syllable strings this reading
    would produce (1 to 3 entries: minor?, main, reduplicated?), already
    sound-shifted.
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

                minor_ipa = syl.minor_syllable.get_ipa() if syl.minor_syllable.nucleus else None
                main_ipa = syl.main_syllable.get_ipa()
                redup_ipa = syl.reduplicated_syllable.get_ipa() if syl.reduplicated_syllable.nucleus else None

                redup_options = [False, True] if (syl.is_reduplicable and redup_ipa) else [False]
                for redup in redup_options:
                    parts = ([minor_ipa] if minor_ipa else []) + [main_ipa] + ([redup_ipa] if redup else [])

                    dedup_key = tuple(parts)
                    if dedup_key in seen:
                        continue
                    seen.add(dedup_key)

                    result = copy.deepcopy(syl)
                    result.is_reduplicated = redup
                    yield result, parts

    if next_cluster:
        donor = Syllable.extract(next_cluster, force_cluster=False, sesquisyllable=False)
        vowel_syl = Syllable.extract(text, force_cluster=False, sesquisyllable=False)
        vowel_syl.assimilate_vowel(donor)
        if vowel_syl.is_vowel_assimilated:
            vowel_syl.sound_shift()
            parts = [vowel_syl.main_syllable.get_ipa()]
            dedup_key = tuple(parts)
            if dedup_key not in seen:
                seen.add(dedup_key)
                yield vowel_syl, parts


def align_all(text: str, ipa: str) -> list:
    """
    Align Thai text against its IPA transcription, returning EVERY distinct
    way of parsing `text` into a sequence of Syllable objects (one per
    orthographic syllable-group -- a sesquisyllable still counts as a single
    Syllable with both a minor and main part) whose combined, sound-shifted
    IPA reconstructs `ipa` exactly.

    Ambiguity is inherent here, not a bug to resolve down to one answer: the
    same surface IPA can genuinely arise from more than one valid grouping.
    In กฐิน, for instance, ก can either be folded into a single sesquisyllable
    Syllable together with ฐิน (minor+main in one object), or stand as its
    own standalone syllable that donates its tone class to ฐิน next door via
    assimilate_tone() -- both are legitimate readings of the same word, and
    both come back here.
    """
    clusters = segment(text)
    targets = thai_ipa.parse(ipa)
    can_merge = _compute_can_merge(clusters)

    n_clusters = len(clusters)
    n_targets = len(targets)

    # (ci, ti, donor_key) -> list of continuations (list[list[Syllable]]),
    # each a way to complete the parse from that state onward. Reachability
    # from here only ever depends on position and the donor's class (see
    # donor_key below), never on how we got here, so this is safe to cache
    # and reuse across different outer paths that land on the same state.
    memo: dict = {}

    def backtrack(ci: int, ti: int, prev: 'Syllable' = None) -> list:
        if ci == n_clusters and ti == n_targets:
            return [[]]
        if ci >= n_clusters or ti >= n_targets:
            return []

        # A tone donor is identified purely by its main syllable's onset
        # chars (that's all assimilate_tone() ever reads from it), so that's
        # the only part of `prev` that can change what's reachable here.
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
            for syl, parts in _candidate_syllables(group_text, prev_syllable=prev, next_cluster=next_cluster):
                n = len(parts)
                if ti + n > n_targets:
                    continue
                expected = [targets[k]['syllable'] for k in range(ti, ti + n)]
                if parts != expected:
                    continue
                for rest in backtrack(end, ti + n, syl):
                    solutions.append([syl] + rest)

        memo[memo_key] = solutions
        return solutions

    solutions = backtrack(0, 0, None)
    if not solutions:
        raise ValueError(f"Could not align {text!r} with {ipa!r}")

    # Different search paths can land on structurally identical parses
    # (same group texts, same flags) -- collapse those down.
    seen = set()
    unique_solutions = []
    for sol in solutions:
        key = tuple(
            (s.text, s.is_reduplicated, bool(s.minor_syllable.nucleus))
            for s in sol
        )
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
    return sum(1 for s in solution if s.is_tone_assimilated or s.is_vowel_assimilated)


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