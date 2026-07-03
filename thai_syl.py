import re

SANSKRIT_CONSONANTS = {
    'k': ['ก'], 'kʰ': ['ข', 'ฃ'], 'g': ['ค', 'ฅ'], 'ɡʱ': ['ฆ'], 'ŋ': ['ง'],
    't͡ɕ': ['จ'], 't͡ɕʰ': ['ฉ'], 'd͡ʑ': ['ช', 'ซ'], 'd͜ʑʱ': ['ฌ'], 'ɲ': ['ญ'],
    'ʈ': ['ฎ', 'ฏ'], 'ʈʰ': ['ฐ'], 'ɖ': ['ฑ'], 'ɖʱ': ['ฒ'], 'ɳ': [],
    't': ['ด', 'ต'], 'tʰ': ['ถ'], 'd': ['ท'], 'dʱ': ['ธ'], 'n': ['ณ', 'น'],
    'p': ['บ', 'ป'], 'pʰ': ['ผ', 'ฝ'], 'b': ['พ', 'ฟ'], 'bʱ': ['ภ'], 'v': ['ฟ'], 'm': ['ม'],
    'j': ['ย'], 'ɾ': ['ร'], 'l': ['ล'], 'w': ['ว'],
    'ɕ': ['ศ'], 'ʂ': ['ษ'], 's': ['ส'], 'h': ['ห', 'ฮ'], 'ɭ': ['ฬ'], 'ʔ': ['อ']
}

THAI_ONSETS = {
    'k': ['ก'], 'kʰ': ['ข', 'ฃ', 'ค', 'ฅ', 'ฆ'], 'ŋ': ['ง'],
    't͡ɕ': ['จ'], 't͡ɕʰ': ['ฉ', 'ช', 'ฌ'],
    'd': ['ฎ', 'ด'], 't': ['ฏ', 'ต'], 'tʰ': ['ฐ', 'ฑ', 'ฒ', 'ถ', 'ท', 'ธ'], 'n': ['ณ', 'น'],
    'b': ['บ'], 'p': ['ป'], 'pʰ': ['ผ', 'พ', 'ภ'], 'f': ['ฝ', 'ฟ'], 'm': ['ม'],
    'j': ['ญ', 'ย'], 'r': ['ร'], 'l': ['ล', 'ฬ'], 'w': ['ว'],
    's': ['ซ', 'ศ', 'ษ', 'ส'], 'h': ['ห', 'ฮ'], 'ʔ': ['อ']
}

OLD_THAI_ONSETS = {
    'k': ['ก'], 'kʰ': ['ข'], 'x': ['ฃ'], 'g': ['ค', 'ฆ'], 'ɣ': ['ฅ'], 'ŋ': ['ง'],
    't͡ɕ': ['จ'], 't͡ɕʰ': ['ฉ'], 'ʑ': ['ช'], 'z': ['ซ', 'ฌ'], 'ɲ': ['ญ'],
    'ˀd': ['ฎ', 'ด'], 't': ['ฏ', 'ต'], 'tʰ': ['ฐ', 'ถ'], 'd': ['ฑ', 'ฒ', 'ท', 'ธ'], 'n': ['ณ', 'น'],
    'ˀb': ['บ'], 'p': ['ป'], 'pʰ': ['ผ'], 'f': ['ฝ'], 'b': ['พ', 'ภ'], 'v': ['ฟ'], 'm': ['ม'],
    'j': ['ย'], 'r': ['ร'], 'l': ['ล', 'ฬ'], 'w': ['ว'],
    's': ['ศ', 'ษ', 'ส'], 'h': ['ห', 'ฮ'], 'ʔ': ['อ']
}

DIGRAPHS = {
    'ŋ̊': ['หง'], 'ɲ̊': ['หญ'], 'n̥': ['หน'], 'm̥': ['หม'], 'j̊': ['หย'], 'r̥': ['หร'], 'l̥': ['หล'], 'w̥': ['หว'], 'ˀj': ['อย']
}

ONSET_CLUSTERS = {
    'old_thai': ['คร', 'พร', 'กล', 'คล', 'ปล', 'พล', 'มล', 'กว', 'ขว', 'ฃว', 'คว', 'ฅว'], # งว?
    'old_khmer': ['กร', 'ตร', 'ทร', 'ปร', 'ผล', 'สร',
        'คร', 'พร', 'กล', 'คล', 'ปล', 'พล', 'มล', 'กว', 'คว'], # ขว?
    'sanskrit': ['ศร'],
    'invention': ['ขร', 'จร', 'ซร'],
    'foreign': ['บร', 'ดร']
}

CODAS = {
    'k̚': ['ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ'], 'p̚': ['บ', 'ป', 'ผ', 'พ', 'ภ'],
    't̚': ['จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ด', 'ต', 'ถ', 'ท', 'ธ', 'ศ', 'ษ', 'ส'],
    'n': ['ญ', 'ณ', 'น', 'ร', 'ล', 'ฬ'], 'm': ['ม'], 'j': ['ย'], 'w': ['ว'], 'ŋ': ['ง'],
    '': ['']
}

CODA_TYPES = {
    'dead': ['k̚', 'p̚', 't̚', 'ʔ'],
    'live': ['n', 'm', 'j', 'w', 'ŋ', '']
}

CONSONANT_CLASSES = {
    'friction': ['ข', 'ฃ', 'ฉ', 'ฐ', 'ถ', 'ผ', 'ฝ', 'ศ', 'ษ', 'ส', 'ห'],
    'unaspirated': ['ก', 'จ', 'ฏ', 'ต', 'ป'],
    'glottalized': ['ฎ', 'ด', 'บ', 'อ'],
    'voiced': [ 'ค', 'ฅ', 'ฆ', 'ง', 'ช', 'ซ', 'ฌ', 'ญ', 'ฑ', 'ฒ', 'ณ', 'ท', 'ธ', 'น', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ฬ', 'ฮ']
}

STANDARD_THAI_SOUND_SHIFTS = {
    'epentheses': ['ml'],
    'onsets': [(['x'], 'kʰ'), (['ɣ'], 'g'),
        (['ʑ', 'z'], 't͡ɕʰ'), (['ɲ', 'ɲ̊', 'j̊', 'ʔj'], 'j'), (['ˀd'], 'd'), (['d'], 'tʰ'), (['ˀb'], 'b'), (['b'], 'pʰ'), (['v'], 'f'),
        (['ŋ̊'], 'ŋ'), (['m̥'], 'm'), (['r̥'], 'r'), (['l̥'], 'l'), (['w̥'], 'w')],
    'codas': [(['ɰ'], 'j')],
    'tones': {
        'mid': ['A1unaspirated', 'A1glottal', 'A2voiced'],
        'low': ['B1friction', 'B1unaspirated', 'B1glottal',
            'DL1friction', 'DL1unaspirated', 'DL1glottal',
            'DS1friction', 'DS1unaspirated', 'DS1glottal'],
        'falling': ['B2voiced',
            'C1friction', 'C1unaspirated', 'C1glottal',
            'DL2voiced'],
        'high': ['C2glottal',
            'DS2voiced', 'mai_tri'],
        'rising': ['A1friction', 'mai_chattawa'],
    }
}

def get_key(dictionary, value):
    for k, v in dictionary.items():
        if value in v:
            return k

def expand(pattern: str) -> str:
    return (
        pattern
        .replace('f', r'(?:c[ุิ]?[์]?)')  # Final
        .replace('x', r'($|(?=[\s+เ-ไๆ๏๚๛]|c[ะ-ฺ]))')  # Exclude
        .replace('r', r'(?:c์)')  # Foreign
        .replace('y', r'(?:cฺ?|c๎?)')  # Yamakkan
        .replace('p', r'(cฺ?)')  # Pali Coda
        .replace('c', r'[ก-ฮ]')  # Consonant
        .replace('t', r'[่-๋]')  # Tone Marker
        .replace('u', r'[กจฏฎดตบปอ]')  # Unaspirated
        .replace('v', r'[งญณนมย-ว]')  # Sonorants
        .replace('m', r'[ร-ว]')  # Medials
        .strip()
    )

def get_consonants(text: str, vowel_form: tuple[str, str]) -> tuple[str, str]:
    prefix, suffix = vowel_form

    start = len(prefix)

    if suffix:
        suffix_pos = text.rfind(suffix)
        onset_cluster = text[start:suffix_pos]
        coda_cluster = text[suffix_pos + len(suffix):]
    else:
        onset_cluster = text[start:]
        coda_cluster = ''

    return onset_cluster, coda_cluster

def get_vowel(text: str) -> tuple[tuple[str, str], str]:
    if re.fullmatch(expand(r'เy*ct?อะr?p*f?'), text):
        vowel_form = ('เ', 'อะ')
        vowel = 'ɤ'
    elif re.fullmatch(expand(r'เy*ct?าะr?p*f?'), text):
        vowel_form = ('เ', 'าะ')
        vowel = 'ɔ'
    elif re.fullmatch(expand(r'เy*ct?ะr?p*f?'), text):
        vowel_form = ('เ', 'ะ')
        vowel = 'e'
    elif re.fullmatch(expand(r'เy*ct?าr?p*f?'), text):
        vowel_form = ('เ', 'า')
        vowel = 'aw'
    elif re.fullmatch(expand(r'เy*c็t?r?p+f?'), text):
        vowel_form = ('เ', '็')
        vowel = 'e'
    elif re.fullmatch(expand(r'เy*cิt?r?p+f?'), text):
        vowel_form = ('เ', 'ิ')
        vowel = 'e'
    elif re.fullmatch(expand(r'เy*ct?อr?p*f?'), text):
        vowel_form = ('เ', 'อ')
        vowel = 'ɤː'
    elif re.fullmatch(expand(r'เy*ct?ยr?p*f?'), text):
        vowel_form = ('เ', 'ย')
        vowel = 'ɤːj'
    elif re.fullmatch(expand(r'โy*ct?ะr?p*f?'), text):
        vowel_form = ('โ', 'ะ')
        vowel = 'o'
    elif re.fullmatch(expand(r'แy*ct?ะr?p*f?'), text):
        vowel_form = ('แ', 'ะ')
        vowel = 'ɛ'
    elif re.fullmatch(expand(r'แy*c็t?r?p+f?'), text):
        vowel_form = ('แ', '็')
        vowel = 'ɛ'
    elif re.fullmatch(expand(r'เy*cีt?ยะr?p*f?'), text):
        vowel_form = ('เ', 'ียะ')
        vowel = 'ia̯ː'
    elif re.fullmatch(expand(r'เy*cีt?ยr?p*f?'), text):
        vowel_form = ('เ', 'ีย')
        vowel = 'ia̯'
    elif re.fullmatch(expand(r'เy*cืt?อะr?p*f?'), text):
        vowel_form = ('เ', 'ือะ')
        vowel = 'ɯa̯ː'
    elif re.fullmatch(expand(r'เy*cืt?อ?r?p*f?'), text):
        vowel_form = ('เ', 'ือ')
        vowel = 'ɯa̯'

    elif re.fullmatch(expand(r'y*ct?ะr?p*f?'), text):
        vowel_form = ('', 'ะ')
        vowel = 'a'
    elif re.fullmatch(expand(r'y*cัt?r?p+f?'), text):
        vowel_form = ('', 'ั')
        vowel = 'a'
    elif re.fullmatch(expand(r'y*ct?าr?p*f?'), text):
        vowel_form = ('', 'า')
        vowel = 'aː'
    elif re.fullmatch(expand(r'y*cิt?r?p*f?'), text):
        vowel_form = ('', 'ิ')
        vowel = 'i'
    elif re.fullmatch(expand(r'y*cีt?r?p*f?'), text):
        vowel_form = ('', 'ี')
        vowel = 'iː'
    elif re.fullmatch(expand(r'y*cือt?r?p*f?'), text):
        vowel_form = ('', 'ือ')
        vowel = 'ɯː'
    elif re.fullmatch(expand(r'y*cืt?r?p*f?'), text):
        vowel_form = ('', 'ื')
        vowel = 'ɯ'
    elif re.fullmatch(expand(r'y*cึt?r?p*f?'), text):
        vowel_form = ('', 'ึ')
        vowel = 'ɯː'
    elif re.fullmatch(expand(r'y*cุt?r?p*f?'), text):
        vowel_form = ('', 'ุ')
        vowel = 'u'
    elif re.fullmatch(expand(r'y*cูt?r?p*f?'), text):
        vowel_form = ('', 'ู')
        vowel = 'uː'
    elif re.fullmatch(expand(r'y*c็t?อr?p+f?'), text):
        vowel_form = ('', '็อ')
        vowel = 'ɔ'
    elif re.fullmatch(expand(r'y*cัt?วะf?'), text):
        vowel_form = ('', 'ัวะ')
        vowel = 'ua̯'
    elif re.fullmatch(expand(r'y*cัt?วf?'), text):
        vowel_form = ('', 'ัว')
        vowel = 'ua̯'
    elif re.fullmatch(expand(r'y*ฤp*f?'), text):
        vowel_form = ('', 'ฤ')
        vowel = 'rɯ'
    elif re.fullmatch(expand(r'y*ฦp*f?'), text):
        vowel_form = ('', 'ฦ')
        vowel = 'lɯ'

    elif re.fullmatch(expand(r'y*ct?รรp*f?'), text):
        vowel_form = ('', 'รร')
        vowel = 'a'
    elif re.fullmatch(expand(r'y*ct?อr?p*f?'), text):
        vowel_form = ('', 'อ')
        vowel = 'ɔː'
    elif re.fullmatch(expand(r'y*ct?วr?p*f?'), text):
        vowel_form = ('', 'ว')
        vowel = 'ua̯'

    elif re.fullmatch(expand(r'เy*ct?r?p*f?'), text):
        vowel_form = ('เ', '')
        vowel = 'eː'
    elif re.fullmatch(expand(r'โy*ct?r?p*f?'), text):
        vowel_form = ('โ', '')
        vowel = 'oː'
    elif re.fullmatch(expand(r'แy*ct?r?p*f?'), text):
        vowel_form = ('แ', '')
        vowel = 'ɛː'
    elif re.fullmatch(expand(r'ไy*ct?r?p*f?'), text):
        vowel_form = ('ไ', '')
        vowel = 'aj'
    elif re.fullmatch(expand(r'ใy*ct?r?p*f?'), text):
        vowel_form = ('ใ', '')
        vowel = 'aɰ'

    elif re.fullmatch(expand(r'y*cp+f?'), text):
        vowel_form = ('', '')
        vowel = 'o, ɔː'
    elif re.fullmatch(expand(r'y*cf?'), text):
        vowel_form = ('', '')
        vowel = 'a'

    return vowel_form, vowel

def get_onset(onset_cluster: str, force_cluster: bool=False, dictionary: dict=OLD_THAI_ONSETS) -> tuple[str, bool]:
    onset_letter = onset_cluster[0]
    onset = get_key(dictionary, onset_letter)
    cluster_type = None

    if len(onset_cluster) == 2 and onset_cluster[1] in ['ร', 'ล', 'ว']:
        cluster_type = get_key(ONSET_CLUSTERS, onset_cluster)
        if cluster_type in ['old_thai', 'old_khmer'] or \
            (force_cluster and cluster_type in ['foreign']) or \
            onset_cluster == 'ขร':
            onset = get_key(dictionary, onset_cluster[0]) + get_key(dictionary, onset_cluster[1])
        elif onset_cluster == 'ทร':
                onset = 'z'

    if len(onset_cluster) == 2 and ((onset_cluster == 'อย')  or \
        (onset_cluster[0] == 'ห' and get_key(CONSONANT_CLASSES, onset_cluster[1]) == 'voiced')):
        onset = get_key(DIGRAPHS, onset_cluster)
    
    return onset, cluster_type

def get_coda(coda_cluster: str) -> str:
    coda_letter = ''
    if len(coda_cluster) >= 3 and coda_cluster[0] in ['ร', 'ห'] and coda_cluster[2] != '์':
        coda_letter = coda_cluster[1]
    elif len(coda_cluster) >= 2 and coda_cluster[1] != '์':
        coda_letter = coda_cluster[0]
    elif len(coda_cluster) == 1:
        coda_letter = coda_cluster[0]

    return get_key(CODAS, coda_letter)

def get_proto_tone(tone_marker: str, syllable_type: str, vowel_duration: str) -> str:
    if tone_marker == '':
        if syllable_type == 'live':
            proto_tone = 'A'
        elif vowel_duration == 'short':
            proto_tone = 'DS'
        else:
            proto_tone = 'DL'
    elif tone_marker == '่':
        proto_tone = 'B'
    elif tone_marker == '้':
        proto_tone = 'C'
    elif tone_marker in ['๊', '๋']:
        proto_tone = None
    
    return proto_tone

def extract(text: str, force_cluster: bool=False, sesquisyllable: bool=False) -> dict:
    vowel_form, vowel = get_vowel(text)
    onset_cluster, coda_cluster = get_consonants(text, vowel_form)

    ambiguous_cluster = False
    if not vowel_form[1] and len(onset_cluster) > 1:
        if re.search(expand(r't'), text):
            onset_cluster, coda_cluster = re.split(expand(r't'), onset_cluster)
        elif len(onset_cluster) > 2 and onset_cluster[2] in ['ิ', 'ุ', '์']:
            onset_cluster, coda_cluster = onset_cluster[:1], onset_cluster[1:]
        elif onset_cluster[1] == '๎':
            onset_cluster, coda_cluster = onset_cluster[:3], onset_cluster[3:]
            onset_cluster = re.sub(expand(r'๎'), '', onset_cluster)
            coda_cluster = re.sub(expand(r'ฺ'), '', coda_cluster)
        elif 'ฺ' in onset_cluster:
            if onset_cluster[1] == 'ฺ':
                onset_cluster, coda_cluster = onset_cluster[:3], onset_cluster[3:]
            else:
                onset_cluster, coda_cluster = onset_cluster[:1], onset_cluster[1:]
            onset_cluster = re.sub(expand(r'ฺ'), '', onset_cluster)
            coda_cluster = re.sub(expand(r'ฺ'), '', coda_cluster)
        elif sesquisyllable:
            onset_cluster, coda_cluster = onset_cluster[:2], onset_cluster[2:]
        else:
            if force_cluster:
                onset_cluster, coda_cluster = onset_cluster[:2], onset_cluster[2:]
            elif not (((onset_cluster[1] in ['ร', 'ล'] and \
                onset_cluster[0] in ['ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ต', 'ป', 'พ']) or \
                onset_cluster[1] == 'ว' and onset_cluster[0] in ['ก', 'ข', 'ฃ', 'ค', 'ฅ']) or \
                (onset_cluster[1] in ['จ', 'ซ', 'ท', 'ศ', 'ส'] and onset_cluster[1] == 'ร') or \
                (onset_cluster[0] == 'ห' and get_key(CONSONANT_CLASSES, onset_cluster[1]) == 'voiced')):
                onset_cluster, coda_cluster = onset_cluster[:1], onset_cluster[1:]
            else:
                ambiguous_cluster = True
                onset_cluster, coda_cluster = onset_cluster[:1], onset_cluster[1:]

    tone_marker = "".join(re.findall(expand(r't'), text))
    onset_cluster = re.sub(expand(r't'), '', onset_cluster)

    consonant_class = get_key(CONSONANT_CLASSES, onset_cluster[0])

    minor_consonant = None
    minor_syllable = None
    if sesquisyllable:
        minor_consonant = onset_cluster[0]
        minor_syllable = get_key(OLD_THAI_ONSETS, minor_consonant) + 'ə'
        onset_cluster = onset_cluster[1:]

    onset, cluster_type = get_onset(onset_cluster, force_cluster=force_cluster)

    coda = get_coda(coda_cluster)

    epenthesizable = False
    if coda_cluster and not '์' in coda_cluster:
        epenthesizable = True

    if vowel == 'o, ɔː':
        if re.fullmatch(expand(r'รf?'), coda_cluster):
            vowel = 'ɔː'
            coda = 'n'
        else:
            vowel = 'o'
    
    if vowel[-1] in ['j', 'w', 'm', 'ɰ']:
        coda = vowel[1]
        vowel = vowel[0]

    if vowel[-1] != 'ː':
        vowel_duration = 'short'
    else:
        vowel_duration = 'long'

    if vowel_duration == 'short' and not coda:
        coda = 'ʔ'
    
    syllable_type = get_key(CODA_TYPES, coda)
    proto_tone = get_proto_tone(tone_marker, syllable_type, vowel_duration)
    if not proto_tone:
        gedney_tone = None
    elif consonant_class in ['friction', 'unaspirated', 'glottalized']:
        gedney_tone = proto_tone + '1'
    else:
        gedney_tone = proto_tone + '2'

    return {
        'vowel_form': vowel_form, 'minor_consonant': minor_consonant,'onset_cluster': onset_cluster, 'tone_marker': tone_marker, 'coda_cluster': coda_cluster,
        'consonant_class': consonant_class, 'vowel_duration': vowel_duration, 'syllable_type': syllable_type,
        'minor_syllable': minor_syllable,'onset': onset, 'vowel': vowel, 'coda': coda, 'gedney_tone': gedney_tone, 'tone': proto_tone,
        'ambiguous_cluster': ambiguous_cluster, 'epenthesizable': epenthesizable
    }

def merge_sounds(sound: str, dictionary: list[tuple[list[str], str]]) -> str:
    print(dictionary)
    for old_sounds, new_sound in dictionary:
        for old_sound in old_sounds:
            sound = sound.replace(old_sound, new_sound)
    return sound

def sound_shift(old_syllable: dict, dialect: dict=STANDARD_THAI_SOUND_SHIFTS) -> dict:
    syllable = old_syllable.copy()
    if dialect.get('epentheses'):
        for epenthesis in dialect['epentheses']:
            if syllable['onset'] == epenthesis:
                syllable['minor_consonant'] = onset_cluster[0]
                syllable['minor_syllable'] = get_key(OLD_THAI_ONSETS, minor_consonant) + 'ə'
                syllable['onset_cluster'] = onset_cluster[1:]
    
    if dialect.get('onsets'):
        syllable['onset'] = merge_sounds(syllable['onset'], dialect['onsets'])

    if dialect.get('vowels'):
        syllable['vowel'] = merge_sounds(syllable['vowel'], dialect['vowels'])

    if dialect.get('codas'):
        syllable['coda'] = merge_sounds(syllable['coda'], dialect['codas'])

    if dialect.get('tones'):
        if syllable['tone_marker'] == '๊':
            tone_split = 'mai_tri'
        elif syllable['tone_marker'] == '๋':
            tone_split = 'mai_chattawa'
        else:
            tone_split = syllable['gedney_tone'] + syllable['consonant_class']
        for tone, tone_splits in dialect['tones'].items():
            if tone_split in tone_splits:
                syllable['tone'] = tone

    return syllable