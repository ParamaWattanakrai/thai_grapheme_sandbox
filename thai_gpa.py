from thai_syl import Syllable
import thai_ipa

def align(text: str, ipa: str) -> list[dict]:
    '''
    Aligns Thai grapheme with Thai IPA transcription into syllables and assign each grapheme roles
    '''
    for phoneme in thai_ipa.parse(ipa):
        print(phoneme)
    # return result