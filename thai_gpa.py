import re
from dataclasses import replace

from thai_lcc import segment
from thai_syl import Syllable, SyllablePart
import thai_ipa

def align(text: str, ipa: str) -> list:
    clusters = segment(text)
    phonemes = thai_ipa.parse(ipa)

    can_merge = [True] * (len(clusters) + 1) # Can merge with cluster in front 
    for i, cluster in enumerate(clusters):
        syllable = Syllable.extract(cluster, force_cluster=False, sesquisyllable=False)
        if re.match(r'^[เ-ไ]', cluster) or \
            len(syllable.onset_chars) > 1:
            can_merge[i] = False
        if re.search(r'[ะำ์]', cluster):
            can_merge[i + 1] = False
    print(clusters)
    print(can_merge)