import re
from dataclasses import replace

from thai_lcc import segment
from thai_syl import Syllable, SyllablePart
import thai_ipa

def align(text: str, ipa: str) -> list:
    clusters = segment(text)
    phonemes = thai_ipa.parse(ipa)

    units = []
    for cluster in clusters:
        syllable = Syllable.extract(cluster, force_cluster=False, sesquisyllable=False)
        front, behind = True, True
        if re.match(r'^[เ-ไ]', cluster) or \
            len(syllable.main_syllable.onset_chars) > 1:
            front = False
        if re.search(r'[ะำ]', cluster):
            behind = False
        units.append(syllable, front, behind)