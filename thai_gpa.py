# ควบไม่แท้
import thai_ipa

from enum import Enum

class State(Enum):
    START = 0
    INITIAL = 1
    FINAL = 2

# INITIALS = {
#     'k': ['ก'], 'kʰ': ['ข', 'ฃ', 'ค', 'ฅ', 'ฆ'], 'ŋ': ['ง', 'หง'],
#     't͡ɕ': ['จ'], 't͡ɕʰ': ['ช', 'ฌ'],
#     'd': ['ฎ', 'ด'], 't': ['ฏ', 'ต'], 'tʰ': ['ฐ', 'ฑ', 'ฒ', 'ถ', 'ท', 'ธ'], 'n': ['ณ', 'น', 'หน'],
#     'b': ['บ'], 'p': ['ป'], 'pʰ': ['ผ', 'พ', 'ภ'], 'f': ['ฝ', 'ฟ'], 'm': ['ม', 'หม'],
#     'j': ['ญ', 'ย', 'หญ', 'หย', 'อย'], 'r': ['ร', 'หร'], 'l': ['ล', 'ฬ', 'หล'], 'w': ['ว', 'หว'],
#     's': ['ซ', 'ศ', 'ษ', 'ส'], 'h': ['ห', 'ฮ'], 'ʔ': ['อ']
# }

INITIALS = {
    'k': ['ก'], 'kʰ': ['ข', 'ฃ', 'ค', 'ฅ', 'ฆ'], 'ŋ': ['ง'],
    't͡ɕ': ['จ'], 't͡ɕʰ': ['ช', 'ฌ'],
    'd': ['ฎ', 'ด'], 't': ['ฏ', 'ต'], 'tʰ': ['ฐ', 'ฑ', 'ฒ', 'ถ', 'ท', 'ธ'], 'n': ['ณ', 'น'],
    'b': ['บ'], 'p': ['ป'], 'pʰ': ['ผ', 'พ', 'ภ'], 'f': ['ฝ', 'ฟ'], 'm': ['ม'],
    'j': ['ญ', 'ย'], 'r': ['ร'], 'l': ['ล', 'ฬ'], 'w': ['ว'],
    's': ['ซ', 'ศ', 'ษ', 'ส'], 'h': ['ห', 'ฮ'], 'ʔ': ['อ']
}

MEDIALS = {'ร': ['r'], 'ล': ['l'], 'ว': ['w']}

CODAS = {
    'k̚': ['ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ'], 'p̚': ['บ', 'ป', 'ผ', 'พ', 'ภ'],
    't̚': ['จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ด', 'ต', 'ถ', 'ท', 'ธ', 'ศ', 'ษ', 'ส'],
    'n': ['ญ', 'ณ', 'น', 'ร', 'ล', 'ฬ'], 'm': ['ม'], 'ŋ': ['ง'], 'w': ['ว'], 'j': ['ย'],
}

VOWELS = {'ะ','า','ิ','ี','ึ','ื','ุ','ู','เ','แ','โ','ใ','ไ','็','ั','ำ'}

TONE_MARKERS = {'่', '้', '๊', '๋'}

DIACRITICS = {'ฺ', '๎'}

FRONT_VOWELS = {'เ','แ','โ','ใ','ไ'}

def align(text: str, ipa: str) -> list[dict]:
    '''
    Aligns Thai grapheme with Thai IPA transcription into syllables and assign each grapheme roles
    '''
    result = []

    i = -1

    for phoneme in thai_ipa.parse(ipa):
        # If phoneme == final cluster then reduplication
        syllable = {}

        state = State.START

        while i < len(text) - 1:
            i += 1
            char = text[i]
            next_char = text[i + 1]

            if state == State.START:
                # if not ('ก' <= char <= 'ฮ' or \
                #     'ะ' <= char <= 'ฺ' or \
                #     'เ' <= char <= '๎'):
                #     break
                if char in FRONT_VOWELS:
                    syllable['char'].append({char: ['vowel']})
                    continue
                if next_char == 'ร' and \
                (phoneme['initial'] == 't͡ɕ' and char == 'จ') or \
                (phoneme['initial'] == 's' and (char == 'ซ' or char == 'ท' or char == 'ศ' or char == 'ส')):
                    syllable['char'].append({char: ['initial']})
                    syllable['char'].append({next_char: ['medial']})
                    i += 1
                    state = State.INITIAL
                    continue
                if (char == 'ห' and phoneme['initial'] != 'h') or \
                (char == 'อ' and phoneme['initial'] != 'ʔ') and \
                (next_char in INITIALS[phoneme['initial']]):
                    syllable['char'].append({char: ['leading']})
                    syllable['char'].append({next_char: ['initial']})
                    i += 1
                    state = State.INITIAL
                    continue
                if char in DIACRITICS:
                    syllable['char'].append({char: ['diacritic']})
                    continue
                if char in INITIALS[phoneme['initial']]:
                    syllable['char'].append({char: ['initial']})
                    state = State.INITIAL
                    continue

            if state == State.INITIAL:
                if char in MEDIALS[phoneme['medial']]:
                    syllable['char'].append({char: ['medial']})
                    continue
                if char in VOWELS:
                    syllable['char'].append({char: ['vowel']})
                    continue
                if char in TONE_MARKERS:
                    syllable['char'].append({char: ['tone_marker']})
                    continue
                if char in CODAS[phoneme['coda']]:
                    syllable['char'].append({char: ['final']})
                    state = State.FINAL
                    continue
            
            if state == State.FINAL:
                if char in DIACRITICS:
                    syllable['char'].append({char: ['diacritic']})

        result.append(syllable)
    return result