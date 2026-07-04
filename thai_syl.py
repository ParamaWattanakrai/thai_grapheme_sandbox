import re
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Any

SANSKRIT_CONSONANTS = {
    'k': ['ก'], 'kʰ': ['ข', 'ฃ'], 'g': ['ค', 'ฅ'], 'ɡʱ': ['ฆ'], 'ŋ': ['ง'],
    't͡ɕ': ['จ'], 't͡ɕʰ': ['ฉ'], 'd͡ʑ': ['ช', 'ซ'], 'd͜ʑʱ': ['ฌ'], 'ɲ': ['ญ'],
    'ʈ': ['ฎ', 'ฏ'], 'ʈʰ': ['ฐ'], 'ɖ': ['ฑ'], 'ɖʱ': ['ฒ'], 'ɳ': ['ณ'],
    't': ['ด', 'ต'], 'tʰ': ['ถ'], 'd': ['ท'], 'dʱ': ['ธ'], 'n': ['น'],
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
    'sanskrit': ['ศร',
        'กร', 'ตร', 'ทร', 'ปร', 'ผล', 'สร',
        'คร', 'พร', 'กล', 'คล', 'ปล', 'พล', 'มล', 'กว', 'คว'],
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
    'voiced': [ 'ค', 'ฅ', 'ฆ', 'ง', 'ช', 'ซ', 'ฌ', 'ญ', 'ฑ', 'ฒ', 'ณ', 'ท', 'ธ', 'น', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ฬ', 'ฮ', 'ฤ', 'ฦ']
}

STANDARD_THAI_SOUND_SHIFTS = {
    'epentheses': ['ml'],
    'onsets': [(['x', 'g', 'ɣ'], 'kʰ'),
        (['ʑ', 'z'], 't͡ɕʰ'), (['ɲ', 'ɲ̊', 'j̊', 'ʔj'], 'j'), (['ˀd'], 'd'), (['d'], 'tʰ'), (['ˀb'], 'b'), (['b'], 'pʰ'), (['v'], 'f'),
        (['ŋ̊'], 'ŋ'), (['m̥'], 'm'), (['r̥'], 'r'), (['l̥'], 'l'), (['w̥'], 'w')],
    'codas': [(['ɰ'], 'j')],
    'tones': {
        '˧': ['A1unaspirated', 'A1glottalized', 'A2voiced'],
        '˨˩': ['B1friction', 'B1unaspirated', 'B1glottalized',
            'DL1friction', 'DL1unaspirated', 'DL1glottalized',
            'DS1friction', 'DS1unaspirated', 'DS1glottalized'],
        '˦˩': ['B2voiced',
            'C1friction', 'C1unaspirated', 'C1glottalized',
            'DL2voiced'],
        '˦˥': ['C2voiced',
            'DS2voiced', 'mai_tri'],
        '˨˥': ['A1friction', 'mai_chattawa'],
    }
}

def get_key(dictionary: dict, value: Any) -> Optional[str]:
    for k, v in dictionary.items():
        if value in v:
            return k
    return None

def expand(pattern: str) -> str:
    return (
        pattern
        .replace('f', r'(?:c[ุิ]?[์]?)')
        .replace('x', r'($|(?=[\s+เ-ไๆ๏๚๛]|c[ะ-ฺ]))')
        .replace('r', r'(?:c์)')
        .replace('y', r'(?:cฺ?|c๎?)')
        .replace('p', r'(cฺ?)')
        .replace('c', r'[ก-ฮ]')
        .replace('t', r'[่-๋]')
        .replace('u', r'[กจฏฎดตบปอ]')
        .replace('v', r'[งญณนมย-ว]')
        .replace('m', r'[ร-ว]')
        .strip()
    )

@dataclass
class MinorSyllable:
    consonant: Optional[str] = None
    onset: Optional[str] = None
    syllable: Optional[str] = None
    tone_split: Optional[str] = None
    gedney_tone: Optional[str] = None
    tone: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

@dataclass
class CoreSyllable:
    onset_cluster: Optional[str] = None
    coda_cluster: Optional[str] = None
    onset: Optional[str] = None
    medial: Optional[str] = None
    vowel: Optional[str] = None
    coda: Optional[str] = None
    tone_split: Optional[str] = None
    gedney_tone: Optional[str] = None
    tone: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

@dataclass
class ReduplicatedSyllable:
    cluster: Optional[str] = None
    onset: Optional[str] = None
    medial: Optional[str] = None
    vowel: Optional[str] = None
    tone_split: Optional[str] = None
    gedney_tone: Optional[str] = None
    tone: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

@dataclass
class Syllable:
    text: str
    vowel_form: Tuple[str, str]
    tone_marker: str
    vowel_duration: str
    syllable_type: Optional[str]
    cluster_type: Optional[str] = None
    ambiguous_cluster: bool = False
    reduplicable: bool = False
    
    minor_syllable: MinorSyllable = field(default_factory=MinorSyllable)
    main_syllable: CoreSyllable = field(default_factory=CoreSyllable)
    reduplicated_syllable: ReduplicatedSyllable = field(default_factory=ReduplicatedSyllable)

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    @classmethod
    def extract(cls, text: str, force_cluster: bool = False, sesquisyllable: bool = False) -> 'Syllable':
        vowel_form, vowel = cls._get_vowel(text)
        onset_cluster, coda_cluster = cls._get_consonants(text, vowel_form)

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
                cluster_type = get_key(ONSET_CLUSTERS, onset_cluster)
                if force_cluster:
                    onset_cluster, coda_cluster = onset_cluster[:2], onset_cluster[2:]
                elif cluster_type in ['old_thai', 'old_khmer'] or (force_cluster and cluster_type in ['foreign']) or onset_cluster == 'ขร':
                    onset_cluster, coda_cluster = onset_cluster[:1], onset_cluster[1:]
                else:
                    ambiguous_cluster = True
                    onset_cluster, coda_cluster = onset_cluster[:1], onset_cluster[1:]

        tone_marker = "".join(re.findall(expand(r't'), text))
        onset_cluster = re.sub(expand(r't'), '', onset_cluster)

        minor_consonant, minor_onset, minor_syl_text = None, None, None
        minor_tone_split, minor_gedney_tone, minor_old_tone = None, None, None
        if sesquisyllable:
            minor_consonant = onset_cluster[0]
            minor_onset = get_key(OLD_THAI_ONSETS, minor_consonant)
            minor_syl_text = minor_onset + 'aʔ' if minor_onset else 'aʔ'
            onset_cluster = onset_cluster[1:]
            
            minor_class = get_key(CONSONANT_CLASSES, minor_consonant)
            minor_tone_split, minor_gedney_tone, minor_old_tone = cls._get_tones('', minor_class, 'dead', 'short')

        if len(onset_cluster) >= 1:
            consonant_class = get_key(CONSONANT_CLASSES, onset_cluster[0])
        else:
            consonant_class = get_key(CONSONANT_CLASSES, vowel_form[1])

        onset, medial, cluster_type = cls._get_onset(onset_cluster, force_cluster=force_cluster)
        coda = cls._get_coda(coda_cluster)

        reduplicable = False
        reduplicated_cluster = None
        if coda_cluster and '์' not in coda_cluster:
            reduplicable = True
            if len(coda_cluster) > 1 and coda_cluster[0] in ['ร', 'ห']:
                reduplicated_cluster = coda_cluster[1:]
            else:
                reduplicated_cluster = coda_cluster

        if vowel == 'o, ɔː':
            if re.fullmatch(expand(r'รf?'), coda_cluster):
                vowel = 'ɔː'
                coda = 'n'
            else:
                vowel = 'o'

        if vowel and vowel[0] in ['r', 'l']:
            medial = vowel[0]
            vowel = vowel[1:]
        if vowel and vowel[-1] in ['j', 'w', 'm', 'ɰ']:
            coda = vowel[-1]
            vowel = vowel[:-1]
        if not onset and medial:
            onset = medial
            medial = None

        if vowel and vowel[-1] != 'ː' and len(vowel) == 1:
            vowel_duration = 'short'
        else:
            vowel_duration = 'long'

        if vowel_duration == 'short' and not coda:
            coda = 'ʔ'

        syllable_type = get_key(CODA_TYPES, coda if coda else '')
        main_tone_split, main_gedney_tone, main_old_tone = cls._get_tones(tone_marker, consonant_class, syllable_type, vowel_duration)

        reduplicated_onset, reduplicated_medial, reduplicated_vowel = None, None, None
        redup_tone_split, redup_gedney_tone, redup_old_tone = None, None, None
        if reduplicable and reduplicated_cluster:
            reduplicated_vowel_form, r_vowel = cls._get_vowel(reduplicated_cluster)
            if reduplicated_vowel_form != ('', ''):
                reduplicated_onset_cluster, _ = cls._get_consonants(reduplicated_cluster, reduplicated_vowel_form)
                reduplicated_vowel = r_vowel
            else:
                reduplicated_onset_cluster = reduplicated_cluster
                reduplicated_vowel = 'aʔ'
            reduplicated_onset, reduplicated_medial, _ = cls._get_onset(reduplicated_onset_cluster)
            
            if reduplicated_onset_cluster:
                redup_class = get_key(CONSONANT_CLASSES, reduplicated_onset_cluster[0])
                redup_duration = 'short' if reduplicated_vowel == 'aʔ' else 'long'
                redup_tone_split, redup_gedney_tone, redup_old_tone = cls._get_tones('', redup_class, 'live', redup_duration)

        return cls(
            text=text, vowel_form=vowel_form, tone_marker=tone_marker,
            vowel_duration=vowel_duration, syllable_type=syllable_type,
            cluster_type=cluster_type, ambiguous_cluster=ambiguous_cluster, reduplicable=reduplicable,
            minor_syllable=MinorSyllable(
                consonant=minor_consonant, onset=minor_onset, syllable=minor_syl_text,
                tone_split=minor_tone_split, gedney_tone=minor_gedney_tone, tone=minor_old_tone
            ),
            main_syllable=CoreSyllable(
                onset_cluster=onset_cluster, coda_cluster=coda_cluster, onset=onset, medial=medial, vowel=vowel, coda=coda,
                tone_split=main_tone_split, gedney_tone=main_gedney_tone, tone=main_old_tone
            ),
            reduplicated_syllable=ReduplicatedSyllable(
                cluster=reduplicated_cluster, onset=reduplicated_onset, medial=reduplicated_medial, vowel=reduplicated_vowel,
                tone_split=redup_tone_split, gedney_tone=redup_gedney_tone, tone=redup_old_tone
            )
        )

    @staticmethod
    def _get_consonants(text: str, vowel_form: Tuple[str, str]) -> Tuple[str, str]:
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

    @staticmethod
    def _get_vowel(text: str) -> Tuple[Tuple[str, str], str]:
        patterns = [
            (r'เy*ct?อะr?p*f?', ('เ', 'อะ'), 'ɤ'),
            (r'เy*ct?าะr?p*f?', ('เ', 'าะ'), 'ɔ'),
            (r'เy*ct?ะr?p*f?', ('เ', 'ะ'), 'e'),
            (r'เy*ct?าr?p*f?', ('เ', 'า'), 'aw'),
            (r'เy*c็t?r?p+f?', ('เ', '็'), 'e'),
            (r'เy*cิt?r?p+f?', ('เ', 'ิ'), 'e'),
            (r'เy*ct?อr?p*f?', ('เ', 'อ'), 'ɤː'),
            (r'เy*ct?ยr?p*f?', ('เ', 'ย'), 'ɤːj'),
            (r'โy*ct?ะr?p*f?', ('โ', 'ะ'), 'o'),
            (r'แy*ct?ะr?p*f?', ('แ', 'ะ'), 'ɛ'),
            (r'แy*c็t?r?p+f?', ('แ', '็'), 'ɛ'),
            (r'เy*cีt?ยะr?p*f?', ('เ', 'ียะ'), 'ia̯ː'),
            (r'เy*cีt?ยr?p*f?', ('เ', 'ีย'), 'ia̯'),
            (r'เy*cืt?อะr?p*f?', ('เ', 'ือะ'), 'ɯa̯ː'),
            (r'เy*cืt?อ?r?p*f?', ('เ', 'ือ'), 'ɯa̯'),
            (r'y*ct?ะr?p*f?', ('', 'ะ'), 'a'),
            (r'y*cัt?r?p+f?', ('', 'ั'), 'a'),
            (r'y*ct?าr?p*f?', ('', 'า'), 'aː'),
            (r'y*ct?ำr?f?', ('', 'ำ'), 'am'),
            (r'y*cิt?r?p*f?', ('', 'ิ'), 'i'),
            (r'y*cีt?r?p*f?', ('', 'ี'), 'iː'),
            (r'y*cือt?r?p*f?', ('', 'ือ'), 'ɯː'),
            (r'y*cืt?r?p*f?', ('', 'ื'), 'ɯ'),
            (r'y*cึt?r?p*f?', ('', 'ึ'), 'ɯː'),
            (r'y*cุt?r?p*f?', ('', 'ุ'), 'u'),
            (r'y*cูt?r?p*f?', ('', 'ู'), 'uː'),
            (r'y*c็t?อr?p+f?', ('', '็อ'), 'ɔ'),
            (r'y*cัt?วะf?', ('', 'ัวะ'), 'ua̯'),
            (r'y*cัt?วf?', ('', 'ัว'), 'ua̯'),
            (r'y*ฤp*f?', ('', 'ฤ'), 'rɯ'),
            (r'y*ฦp*f?', ('', 'ฦ'), 'lɯ'),
            (r'y*ct?รรp*f?', ('', 'รร'), 'a'),
            (r'y*ct?อr?p*f?', ('', 'อ'), 'ɔː'),
            (r'y*ct?วr?p*f?', ('', 'ว'), 'ua̯'),
            (r'เy*ct?r?p*f?', ('เ', ''), 'eː'),
            (r'โy*ct?r?p*f?', ('โ', ''), 'oː'),
            (r'แy*ct?r?p*f?', ('แ', ''), 'ɛː'),
            (r'ไy*ct?r?p*f?', ('ไ', ''), 'aj'),
            (r'ใy*ct?r?p*f?', ('ใ', ''), 'aɰ'),
            (r'y*cp+f?', ('', ''), 'o, ɔː'),
            (r'y*cf?', ('', ''), 'a')
        ]
        for pat, form, val in patterns:
            if re.fullmatch(expand(pat), text):
                return form, val
        return ('', ''), 'a'

    @staticmethod
    def _get_onset(onset_cluster: str, force_cluster: bool = False, dictionary: dict = OLD_THAI_ONSETS) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        if not onset_cluster:
            return None, None, None
        onset_letter = onset_cluster[0]
        onset = get_key(dictionary, onset_letter)
        medial = None
        cluster_type = None

        if len(onset_cluster) == 2:
            cluster_type = get_key(ONSET_CLUSTERS, onset_cluster)
            if cluster_type in ['old_thai', 'old_khmer'] or (force_cluster and cluster_type in ['foreign']) or onset_cluster == 'ขร':
                onset = get_key(dictionary, onset_cluster[0])
                medial = get_key(dictionary, onset_cluster[1])
            elif onset_cluster == 'ทร':
                onset = 'z'

        if len(onset_cluster) == 2 and ((onset_cluster == 'อย') or (onset_cluster[0] == 'ห' and get_key(CONSONANT_CLASSES, onset_cluster[1]) == 'voiced')):
            onset = get_key(DIGRAPHS, onset_cluster)

        return onset, medial, cluster_type

    @staticmethod
    def _get_coda(coda_cluster: str) -> Optional[str]:
        coda_letter = None
        if len(coda_cluster) >= 3 and coda_cluster[0] in ['ร', 'ห'] and coda_cluster[2] != '์':
            coda_letter = coda_cluster[1]
        elif len(coda_cluster) >= 2 and coda_cluster[1] != '์':
            if coda_cluster[0] in ['ร', 'ห']:
                coda_letter = coda_cluster[1]
            else:
                coda_letter = coda_cluster[0]
        elif len(coda_cluster) == 1:
            coda_letter = coda_cluster[0]

        if not coda_letter:
            return None
        return get_key(CODAS, coda_letter)

    @staticmethod
    def _get_tones(tone_marker: str, consonant_class: str, syllable_type: str, vowel_duration: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        old_tone = None
        if not tone_marker:
            if syllable_type == 'live':
                old_tone = 'A'
            elif syllable_type == 'dead':
                if vowel_duration == 'short':
                    old_tone = 'DS'
                elif vowel_duration == 'long':
                    old_tone = 'DL'
        elif tone_marker == '่':
            old_tone = 'B'
        elif tone_marker == '้':
            old_tone = 'C'

        gedney_tone = None
        if old_tone and consonant_class:
            if consonant_class in ['friction', 'unaspirated', 'glottalized']:
                gedney_tone = old_tone + '1'
            elif consonant_class == 'voiced':
                gedney_tone = old_tone + '2'

        if tone_marker == '๊':
            tone_split = 'mai_tri'
        elif tone_marker == '๋':
            tone_split = 'mai_chattawa'
        else:
            tone_split = (gedney_tone + consonant_class) if gedney_tone and consonant_class else None

        return tone_split, gedney_tone, old_tone

    def sound_shift(self, dialect: dict = STANDARD_THAI_SOUND_SHIFTS) -> 'Syllable':
        kwargs = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        
        minor = kwargs['minor_syllable']
        main = kwargs['main_syllable']
        redup = kwargs['reduplicated_syllable']

        if dialect.get('epentheses') and main.medial and main.onset:
            for epenthesis in dialect['epentheses']:
                if main.onset + main.medial == epenthesis:
                    minor.consonant = main.onset_cluster[0]
                    minor_onset = get_key(OLD_THAI_ONSETS, minor.consonant)
                    minor.syllable = minor_onset + 'aʔ' if minor_onset else 'aʔ'
                    main.onset_cluster = main.onset_cluster[1:]
                    main.onset = main.medial
                    main.medial = None
                    
                    minor_class = get_key(CONSONANT_CLASSES, minor.consonant)
                    minor.tone_split, minor.gedney_tone, minor.tone = self._get_tones('', minor_class, 'dead', 'short')

        if dialect.get('onsets'):
            main.onset = self._merge_sounds(main.onset, dialect['onsets'])
            main.medial = self._merge_sounds(main.medial, dialect['onsets'])
            redup.onset = self._merge_sounds(redup.onset, dialect['onsets'])

        if dialect.get('vowels'):
            main.vowel = self._merge_sounds(main.vowel, dialect['vowels'])
            redup.vowel = self._merge_sounds(redup.vowel, dialect['vowels'])

        if dialect.get('codas'):
            main.coda = self._merge_sounds(main.coda, dialect['codas'])

        if dialect.get('tones'):
            for part in [minor, main, redup]:
                if part.tone_split:
                    for tone, tone_splits in dialect['tones'].items():
                        if part.tone_split in tone_splits:
                            part.tone = tone

        return Syllable(**kwargs)

    @staticmethod
    def _merge_sounds(sound: Optional[str], dictionary: list[Tuple[list[str], str]]) -> Optional[str]:
        if not sound:
            return None
        for old_sounds, new_sound in dictionary:
            for old_sound in old_sounds:
                sound = sound.replace(old_sound, new_sound)
        return sound

    def get_ipa(self, reduplicate: bool = False) -> str:
        ipa = ((self.minor_syllable.syllable or '') + (self.minor_syllable.tone or '') + ('.' if self.minor_syllable.syllable else '')) + \
              (self.main_syllable.onset or '') + (self.main_syllable.medial or '') + (self.main_syllable.vowel or '') + (self.main_syllable.coda or '') + (self.main_syllable.tone or '')
        if reduplicate and self.reduplicable:
            ipa = ipa + '.' + (self.reduplicated_syllable.onset or '') + (self.reduplicated_syllable.medial or '') + (self.reduplicated_syllable.vowel or '') + (self.reduplicated_syllable.tone or '')
        return ipa