from thai_lcc import segment
from thai_syl import Syllable
import thai_ipa

def align(text: str, ipa: str) -> list[Syllable]:
    '''
    Aligns Thai grapheme with Thai IPA transcription into syllables and assign each grapheme roles
    '''
    clusters = segment(text)
    phonemes = thai_ipa.parse(ipa)

    syllables = []
    for cluster in clusters:
        syllable = Syllable.extract(cluster, force_cluster=False, sesquisyllable=False)
        syllable.sound_shift()
        syllables.append(syllable)
    return syllables