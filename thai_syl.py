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
    'old_thai': ['ขร', 'คร', 'พร', 'กล', 'คล', 'ปล', 'พล', 'มล', 'กว', 'ขว', 'ฃว', 'คว', 'ฅว'],
    'old_khmer': ['กร', 'ตร', 'ทร', 'ปร', 'ขล', 'ผล', 'สร',
        'คร', 'พร', 'กล', 'คล', 'ปล', 'พล', 'มล', 'กว', 'คว'],
    'sanskrit': ['ศร',
        'กร', 'ตร', 'ทร', 'ปร', 'ผล', 'สร',
        'คร', 'พร', 'กล', 'คล', 'ปล', 'พล', 'มล', 'กว', 'คว'],
    'orthography': ['จร', 'ซร'],
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
        '˧': [('A1', 'unaspirated'), ('A1', 'glottalized'), ('A2', 'voiced')],
        '˨˩': [('B1', 'friction'), ('B1', 'unaspirated'), ('B1', 'glottalized'),
            ('DL1', 'friction'), ('DL1', 'unaspirated'), ('DL1', 'glottalized'),
            ('DS1', 'friction'), ('DS1', 'unaspirated'), ('DS1', 'glottalized')],
        '˦˩': [('B2', 'voiced'),
            ('C1', 'friction'), ('C1', 'unaspirated'), ('C1', 'glottalized'),
            ('DL2', 'voiced')],
        '˦˥': [('C2', 'voiced'),
            ('DS2', 'voiced'), 'mai_tri'],
        '˨˥': [('A1', 'friction'), 'mai_chattawa'],
    }
}

def get_key(dictionary: dict, value: Any) -> Optional[str]:
    for k, v in dictionary.items():
        if value in v:
            return k
    return None

def get_tone_key(dictionary: dict, tone_split: Tuple[str, str]) -> Optional[str]:
    for k, v in dictionary.items():
        for entry in v:
            if entry == tone_split or (isinstance(entry, str) and entry == tone_split[0]):
                return k
    return None

def expand(pattern: str) -> str:
    return (
        pattern
        .replace('f', r'(?:c[ะิุ]?[์]?)')
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
class SyllablePart:
    vowel_form: Optional[Tuple[str, str]] = None
    onset_chars: Optional[str] = None
    tone_marker: Optional[str] = None
    coda_chars: Optional[str] = None
    syllable: Optional[str] = None
    onset: Optional[str] = None
    medial: Optional[str] = None
    vowel: Optional[str] = None
    coda: Optional[str] = None
    vowel_duration: Optional[str] = None
    coda_type: Optional[str] = None
    consonant_class: Optional[str] = None
    tone_split: Optional[Tuple[str, str]] = None
    tone: Optional[str] = None
    assimilated_consonant_class: Optional[str] = None
    assimilated_tone_split: Optional[Tuple[str, str]] = None
    assimilated_tone: Optional[str] = None
    cluster_type: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def get_ipa(self, assimilate_tone: bool = True) -> str:
        if not self.onset and not self.vowel:
            return ""
        tone = (self.assimilated_tone if assimilate_tone and self.assimilated_tone is not None else self.tone)
        return (self.onset or '') + (self.medial or '') + (self.vowel or '') + (self.coda or '') + (tone or '')

@dataclass
class Syllable:
    text: str
    ambiguous_cluster: bool = False
    reduplicable: bool = False
    
    minor_syllable: SyllablePart = field(default_factory=SyllablePart)
    main_syllable: SyllablePart = field(default_factory=SyllablePart)
    reduplicated_syllable: SyllablePart = field(default_factory=SyllablePart)

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    @classmethod
    def extract(cls, text: str, force_cluster: bool = False, sesquisyllable: bool = False) -> 'Syllable':
        vowel_form, vowel = cls._get_vowel(text)
        onset_chars, coda_chars = cls._get_consonants(text, vowel_form)

        # AMBIGUOUS CLUSTER
        ambiguous_cluster = False
        cluster_type = None
        if not vowel_form[1] and len(onset_chars) > 1:
            if re.search(expand(r't'), text):
                split_result = re.split(expand(r't'), onset_chars, maxsplit=1)
                onset_chars = split_result[0]
                coda_chars = split_result[1] if len(split_result) > 1 else ''
            elif len(onset_chars) > 2 and onset_chars[2] in ['ิ', 'ุ', '์']:
                onset_chars, coda_chars = onset_chars[:1], onset_chars[1:]
            elif onset_chars[1] == '๎':
                onset_chars, coda_chars = onset_chars[:3], onset_chars[3:]
                onset_chars = re.sub(expand(r'๎'), '', onset_chars)
                coda_chars = re.sub(expand(r'ฺ'), '', coda_chars)
            elif 'ฺ' in onset_chars:
                if onset_chars[1] == 'ฺ':
                    onset_chars, coda_chars = onset_chars[:3], onset_chars[3:]
                else:
                    onset_chars, coda_chars = onset_chars[:1], onset_chars[1:]
                onset_chars = re.sub(expand(r'ฺ'), '', onset_chars)
                coda_chars = re.sub(expand(r'ฺ'), '', coda_chars)
            elif sesquisyllable:
                onset_chars, coda_chars = onset_chars[:2], onset_chars[2:]
            else:
                cluster_type = get_key(ONSET_CLUSTERS, onset_chars)
                if force_cluster:
                    onset_chars, coda_chars = onset_chars[:2], onset_chars[2:]
                elif cluster_type in ['old_thai', 'old_khmer'] or (force_cluster and cluster_type in ['foreign']):
                    onset_chars, coda_chars = onset_chars[:1], onset_chars[1:]
                else:
                    ambiguous_cluster = True
                    onset_chars, coda_chars = onset_chars[:1], onset_chars[1:]

        tone_marker = ''.join(re.findall(expand(r't'), text))
        onset_chars = re.sub(expand(r't'), '', onset_chars)
        coda_chars = re.sub(expand(r't'), '', coda_chars)

        # MINOR
        minor_part = SyllablePart()
        if sesquisyllable and len(onset_chars) > 1:
            m_onset_chars = onset_chars[0]
            m_onset = get_key(OLD_THAI_ONSETS, m_onset_chars)
            m_class = get_key(CONSONANT_CLASSES, m_onset_chars)
            m_tone_split, m_old_tone = cls._get_tones('', m_class, 'dead', 'short')
            
            minor_part = SyllablePart(
                vowel_form=('', ''),
                onset_chars=m_onset_chars,
                onset=m_onset,
                medial=None,
                vowel='a',
                coda='ʔ',
                vowel_duration='short',
                coda_type='dead',
                consonant_class=m_class,
                tone_split=m_tone_split,
                tone=m_old_tone,
            )
            onset_chars = onset_chars[1:]

        # MAIN
        m_onset, m_medial, cluster_type_mapped, m_vowel, m_coda, m_vowel_duration, m_coda_type, m_consonant_class, m_tone_split, m_old_tone = cls._process_phonemes(
            vowel_form, onset_chars, coda_chars, tone_marker, vowel, force_cluster=force_cluster
        )
        
        assimilated_consonant_class = None
        assimilated_tone_split = None
        assimilated_tone = None
        if minor_part.onset_chars:
            assimilated_consonant_class = minor_part.consonant_class
            assimilated_tone_split, assimilated_tone = cls._get_tones(
                tone_marker, 
                assimilated_consonant_class, 
                m_coda_type, 
                m_vowel_duration
            )
        
        main_part = SyllablePart(
            vowel_form=vowel_form,
            onset_chars=onset_chars,
            tone_marker=tone_marker,
            coda_chars=coda_chars,
            onset=m_onset,
            medial=m_medial,
            vowel=m_vowel,
            coda=m_coda,
            vowel_duration=m_vowel_duration,
            coda_type=m_coda_type,
            consonant_class=m_consonant_class,
            tone_split=m_tone_split,
            tone=m_old_tone,
            assimilated_consonant_class=assimilated_consonant_class,
            assimilated_tone_split=assimilated_tone_split,
            assimilated_tone=assimilated_tone,
            cluster_type=cluster_type_mapped if cluster_type_mapped else cluster_type
        )

        # REDUPLICATION
        redup_part = SyllablePart()
        reduplicable = False
        if coda_chars and '์' not in coda_chars:
            reduplicable = True
            if len(coda_chars) > 1 and coda_chars[0] in ['ร', 'ห']:
                redup_text = coda_chars[1:]
            else:
                redup_text = coda_chars
                
            r_vowel_form, r_raw_vowel = cls._get_vowel(redup_text)
            r_coda_chars = ''
            if r_vowel_form != ('', ''):
                r_onset_chars, _ = cls._get_consonants(redup_text, r_vowel_form)
            else:
                r_onset_chars = redup_text
                r_raw_vowel = 'a'

            r_onset, r_medial, r_cluster_type, r_vowel, r_coda, r_vowel_duration, r_coda_type, r_consonant_class, r_tone_split, r_old_tone = cls._process_phonemes(
                r_vowel_form, r_onset_chars, '', '', r_raw_vowel, force_cluster=True
            )

            redup_part = SyllablePart(
                vowel_form=r_vowel_form,
                onset_chars=r_onset_chars,
                coda_chars=r_coda_chars,
                onset=r_onset,
                medial=r_medial,
                vowel=r_vowel,
                coda=r_coda,
                vowel_duration=r_vowel_duration,
                coda_type=r_coda_type,
                consonant_class=r_consonant_class,
                tone_split=r_tone_split,
                tone=r_old_tone,
                cluster_type=r_cluster_type
            )

        return cls(
            text=text,
            ambiguous_cluster=ambiguous_cluster, 
            reduplicable=reduplicable,
            minor_syllable=minor_part,
            main_syllable=main_part,
            reduplicated_syllable=redup_part
        )

    @classmethod
    def _process_phonemes(cls, vowel_form, onset_chars, coda_chars, tone_marker, raw_vowel, force_cluster=False):
        onset, medial, cluster_type = cls._get_onset(onset_chars, force_cluster=force_cluster)
        coda = cls._get_coda(coda_chars)
        vowel = raw_vowel
        
        if vowel == 'o, ɔː':
            if coda_chars and re.fullmatch(expand(r'รf?'), coda_chars):
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
        
        if onset_chars and len(onset_chars) >= 1:
            consonant_class = get_key(CONSONANT_CLASSES, onset_chars[0])
        else:
            consonant_class = get_key(CONSONANT_CLASSES, vowel_form[1]) if vowel_form and len(vowel_form) > 1 and vowel_form[1] else None

        coda_type = get_key(CODA_TYPES, coda if coda else '')

        tone_split, old_tone = cls._get_tones(
            tone_marker,
            consonant_class,
            coda_type,
            vowel_duration
        )
        
        return onset, medial, cluster_type, vowel, coda, vowel_duration, coda_type, consonant_class, tone_split, old_tone

    @classmethod
    def _get_vowel(cls, text: str) -> Tuple[Tuple[str, str], str]:
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
            (r'y*cัt?p*cิ?f?', ('', 'ั'), 'a'),
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

    @classmethod
    def _get_consonants(cls, text: str, vowel_form: Tuple[str, str]) -> Tuple[str, str]:
        pre_vowel, post_vowel = vowel_form
        pattern = rf'^{pre_vowel}(.*?){post_vowel}$'
        match = re.search(pattern, text)
        if match:
            return match.group(1), ''

        pattern = rf'^{pre_vowel}(.+?){post_vowel}(.+)$'
        match = re.search(pattern, text)
        if match:
            return match.group(1), match.group(2)

        return text, ''

    @classmethod
    def _get_onset(cls, onset_chars: str, force_cluster: bool = False) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        if not onset_chars:
            return None, None, None

        cleaned_onset_chars = re.sub(expand(r'[์ฺ๎]'), '', onset_chars)

        cluster_type = get_key(ONSET_CLUSTERS, cleaned_onset_chars)

        if len(cleaned_onset_chars) == 2 and (cluster_type in ['old_thai', 'old_khmer'] or force_cluster):
            cluster_type = cluster_type if cluster_type else 'foreign'
            return get_key(OLD_THAI_ONSETS, cleaned_onset_chars[0]), get_key(OLD_THAI_ONSETS, cleaned_onset_chars[1]), cluster_type

        digraph = get_key(DIGRAPHS, cleaned_onset_chars)
        if digraph:
            return digraph, None, cluster_type
        if len(cleaned_onset_chars) > 0:
            return get_key(OLD_THAI_ONSETS, cleaned_onset_chars[0]), None, cluster_type
        
        return None, None, cluster_type

    @classmethod
    def _get_coda(cls, coda_chars: str) -> Optional[str]:
        if not coda_chars:
            return None

        if len(coda_chars) > 1:
            if coda_chars[1] == '์':
                return get_key(CODAS, coda_chars[0])
            elif coda_chars[1] == 'ฺ' and len(coda_chars) > 2:
                return get_key(CODAS, coda_chars[2])
            elif coda_chars[0] == 'ร':
                return get_key(CODAS, coda_chars[1])

        return get_key(CODAS, coda_chars[0])
        
    @classmethod
    def _get_tones(cls, tone_marker: str, consonant_class: Optional[str], coda_type: Optional[str], duration: str) -> Tuple[Optional[Tuple[str, str]], Optional[str]]:
        old_tone = None
        tone_split = None

        if tone_marker == '่':
            old_tone = 'B'
        elif tone_marker == '้':
            old_tone = 'C'
        elif tone_marker == '๊':
            old_tone = 'mai_tri'
        elif tone_marker == '๋':
            old_tone = 'mai_chattawa'

        elif coda_type == 'live' or coda_type == '':
            old_tone = 'A'
        elif coda_type == 'dead':
            old_tone = 'D'

        if consonant_class:
            split_num = '1' if consonant_class in ['friction', 'unaspirated', 'glottalized'] else '2'

            if old_tone == 'D':
                box = f'D{"S" if duration == "short" else "L"}{split_num}'
            elif old_tone in ('mai_tri', 'mai_chattawa'):
                box = old_tone
            else:
                box = f'{old_tone}{split_num}'

            tone_split = (box, consonant_class)

        return tone_split, old_tone

    def get_ipa(self, assimilate_tone: bool = True, reduplicate: bool = False) -> str:
        parts = []
        if self.minor_syllable.vowel:
            parts.append(self.minor_syllable.get_ipa(assimilate_tone=assimilate_tone))
        if self.main_syllable.vowel:
            parts.append(self.main_syllable.get_ipa(assimilate_tone=assimilate_tone))
        if reduplicate and self.reduplicable and self.reduplicated_syllable.vowel:
            parts.append(self.reduplicated_syllable.get_ipa(assimilate_tone=assimilate_tone))
        return '.'.join(parts)
    
    def reconstruct_text(self) -> str:
        minor = self.minor_syllable.onset_chars if self.minor_syllable.onset_chars else ''

        tone_marker = self.main_syllable.tone_marker if self.main_syllable.tone_marker else ''
        if any(ch in self.main_syllable.vowel_form[1] for ch in ['ิ', 'ุ']):
            onset_tone = self.main_syllable.onset_chars
            vowel_tone = self.main_syllable.vowel_form[1] + tone_marker
        else:
            onset_tone = self.main_syllable.onset_chars + tone_marker
            vowel_tone = self.main_syllable.vowel_form[1]
        
        text = self.main_syllable.vowel_form[0] + minor + onset_tone + vowel_tone + \
            ((self.reduplicated_syllable.onset_chars + self.reduplicated_syllable.vowel_form[1]) if self.reduplicable else self.main_syllable.coda_chars)

        return text

    def assimilate_from(self, other: 'Syllable') -> None:
        donor = other.main_syllable
        if not donor.onset_chars:
            return

        donor_class = get_key(CONSONANT_CLASSES, donor.onset_chars[0])
        
        tone_marker = self.main_syllable.tone_marker if self.main_syllable.tone_marker else ''
        coda_type = self.main_syllable.coda_type
        duration = self.main_syllable.vowel_duration

        tone_split, tone = self._get_tones(tone_marker, donor_class, coda_type, duration)

        self.main_syllable.assimilated_consonant_class = donor_class
        self.main_syllable.assimilated_tone_split = tone_split
        self.main_syllable.assimilated_tone = tone

    def sound_shift(self, dialect: Dict[str, Any] = STANDARD_THAI_SOUND_SHIFTS) -> None:
        minor = self.minor_syllable
        main = self.main_syllable

        if dialect.get('epentheses') and main.medial and main.onset:
            for epenthesis in dialect['epentheses']:
                if main.onset + main.medial == epenthesis:
                    minor.text = main.onset_chars[0]
                    minor.onset_chars = minor.text
                    minor.vowel_form = ('', '')
                    minor.coda_chars = ''
                    minor.tone_marker = ''
                    minor.vowel = 'a'
                    minor.coda = 'ʔ'
                    minor.vowel_duration = 'short'
                    minor.onset = get_key(OLD_THAI_ONSETS, minor.text)
                    
                    minor_class = get_key(CONSONANT_CLASSES, minor.text)
                    minor.coda_type = 'dead'
                    minor.consonant_class = minor_class
                    minor.tone_split, minor.tone = self._get_tones('', minor_class, minor.coda_type, minor.vowel_duration)
                    
                    main.onset_chars = main.onset_chars[1:]
                    main.onset = main.medial
                    main.medial = None

                    main.assimilated_consonant_class = minor_class
                    main.assimilated_tone_split, main.assimilated_tone = self._get_tones(
                        main.tone_marker if main.tone_marker else '', 
                        minor_class, 
                        main.coda_type, 
                        main.vowel_duration
                    )
        
        for p in [minor, main, self.reduplicated_syllable]:
            if not p.vowel:
                continue

            if dialect.get('onsets') and p.onset:
                for onsets, sound_shift in dialect['onsets']:
                    if p.onset in onsets:
                        p.onset = sound_shift
                        break
            if dialect.get('medials') and p.onset:
                for onsets, sound_shift in dialect['medials']:
                    if p.onset in onsets:
                        p.onset = sound_shift
                        break
            if dialect.get('codas') and p.coda:
                for codas, sound_shift in dialect['codas']:
                    if p.coda in codas:
                        p.coda = sound_shift
                        break
            if dialect.get('tones') and p.tone_split:
                p.tone = get_tone_key(dialect['tones'], p.tone_split)
            if dialect.get('tones') and p.assimilated_tone_split:
                p.assimilated_tone = get_tone_key(dialect['tones'], p.assimilated_tone_split)