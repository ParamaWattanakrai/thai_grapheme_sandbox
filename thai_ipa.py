import re
import warnings

INITIALS = {
    'k', 'kʰ', 'ŋ',
    't͡ɕ', 't͡ɕʰ',
    'd', 't', 'tʰ', 'n',
    'b', 'p', 'pʰ', 'f', 'm',
    'j', 'r', 'l', 'w', 's', 'h', 'ʔ'
}

MEDIALS = {'r', 'l', 'w'}

NUCLEI = {
    'a', 'aː',
    'i', 'iː', 'ɯ', 'ɯː', 'u', 'uː',
    'e', 'eː', 'ɤ', 'ɤː', 'o', 'oː',
    'ɛ', 'ɛː', 'ɔ', 'ɔː',
    'ia̯', 'ɯa̯', 'ua̯'
}

CODAS = {'ʔ', 'k̚', 'p̚', 't̚', 'n', 'm', 'ŋ', 'w', 'j'}

TONES = {'˧', '˨˩', '˦˩', '˦˥', '˨˥'}

OBSTRUENTS = {'ʔ', 'k̚', 'p̚', 't̚'}

TONE_PATTERN = re.compile(r'[˥˦˧˨˩]+$')

SORTED_INITIALS = sorted(INITIALS, key=len, reverse=True)
SORTED_NUCLEI = sorted(NUCLEI, key=len, reverse=True)
SORTED_CODAS = sorted(CODAS, key=len, reverse=True)


def parse(ipa: str) -> list[dict]: 
    '''
    Parses Thai IPA transcription into syllables and their components
    '''
    syls = ipa.split('.')
    results = []

    for syl in syls:
        original = syl

        tone_match = TONE_PATTERN.search(syl)
        tone = tone_match.group() if tone_match else None
        if tone:
            syl = syl[:-len(tone)]

        coda = None
        for c in SORTED_CODAS:
            if syl.endswith(c):
                coda = c
                syl = syl[:-len(c)]
                break

        nucleus = None
        for v in SORTED_NUCLEI:
            if syl.endswith(v):
                nucleus = v
                syl = syl[:-len(v)]
                break

        initial = None
        medial = None
        for i in SORTED_INITIALS:
            if syl.startswith(i):
                initial = i
                rest = syl[len(i):]

                if rest in MEDIALS:
                    medial = rest
                break

        duration = 'long' if 'ː' in nucleus or nucleus in {'ia̯', 'ɯa̯', 'ua̯'} else 'short'

        if coda:
            if coda in OBSTRUENTS:
                sonority = 'dead'
            else:
                sonority = 'live'
        else:
            if duration == 'short':
                warnings.warn(f'Warning: No explicit glottal stop at "{original}"')
                sonority = 'dead'
            else:
                sonority = 'live'

        results.append({
            'syllable': original,
            'initial': initial,
            'medial': medial,
            'nucleus': nucleus,
            'coda': coda,
            'tone': tone,
            'duration': duration,
            'sonority': sonority
        })

    return results