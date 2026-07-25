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


def _candidate_syllables(text: str, prev_syllable: 'Syllable' = None):
    """
    For a chunk of text (one or more merged LTCCs), yield every distinct
    (Syllable, ipa_parts) reading worth trying, from simplest to most exotic:

      - sesquisyllable: always try both False and True (extract() is a no-op
        difference when there's nothing to split, so this never hurts).
      - force_cluster: only tried if the plain default extraction reports
        has_ambiguous_cluster -- force_cluster exists to resolve exactly
        that ambiguity, so there's no reason to try it otherwise.
      - tone assimilation: only tried if a prev_syllable (the syllable group
        immediately preceding this one in the accepted parse) was given and
        its main syllable actually has an onset to donate a class from --
        assimilate_tone() is a no-op otherwise.
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
    default = Syllable.extract(text, force_cluster=False, sesquisyllable=False)
    force_cluster_options = [False, True] if default.has_ambiguous_cluster else [False]

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


def align(text: str, ipa: str) -> list:
    """
    Align Thai text against its IPA transcription, returning the list of
    Syllable objects (one per orthographic syllable-group -- a sesquisyllable
    still yields a single Syllable with both a minor and main part) whose
    combined, sound-shifted IPA reconstructs `ipa` exactly.
    """
    clusters = segment(text)
    targets = thai_ipa.parse(ipa)
    can_merge = _compute_can_merge(clusters)

    n_clusters = len(clusters)
    n_targets = len(targets)

    memo_fail = set()

    def backtrack(ci: int, ti: int, prev: 'Syllable' = None):
        if ci == n_clusters and ti == n_targets:
            return []
        if ci >= n_clusters or ti >= n_targets:
            return None

        # A tone donor is identified purely by its main syllable's onset
        # chars (that's all assimilate_tone() ever reads from it), so that's
        # the only part of `prev` that can change whether this position is
        # reachable -- use it, not object identity, as the memo key.
        donor_key = prev.main_syllable.onset_chars if prev is not None else None
        memo_key = (ci, ti, donor_key)
        if memo_key in memo_fail:
            return None

        max_end = ci + 1
        while max_end < n_clusters and can_merge[max_end]:
            max_end += 1

        for end in range(ci + 1, max_end + 1):
            group_text = ''.join(clusters[ci:end])
            for syl, parts in _candidate_syllables(group_text, prev_syllable=prev):
                n = len(parts)
                if ti + n > n_targets:
                    continue
                expected = [targets[k]['syllable'] for k in range(ti, ti + n)]
                if parts != expected:
                    continue
                rest = backtrack(end, ti + n, syl)
                if rest is not None:
                    return [syl] + rest

        memo_fail.add(memo_key)
        return None

    result = backtrack(0, 0, None)
    if result is None:
        raise ValueError(f"Could not align {text!r} with {ipa!r}")
    return result