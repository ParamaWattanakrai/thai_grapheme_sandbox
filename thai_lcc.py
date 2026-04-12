import re

RE_LTCC = re.sub(r"\s+", '|', ('('+
'''
เy?cีt?ยะ?r?p?f?

เy?cืt?อะ?r?p?f?

เy?cิt?r?cf?

ก็
y?c็t?อr?cf?

[เแ]c?c็t?r?cf?
เc?ct?าะr?p?f?
เy?ct?าะ?r?p?f?

[เ-ไ]หvtf?x
[เ-ไ]umtf?x
[เ-โ]y?ct?ะ?r?p?f?
[เ-ไ]y?ct?r?p?f?

y?ct?[ะาำ]r?p?f?

yc[ิ-ู]t?r?p?f?
c[ิ-ฺํ๎]t?r?f?

y?cืt?r?cf?

y?cัt?cิf?
y?cัt?r?cf?

y?cัt?วะf?

บ่
y?ctr?cf?

y?ฤๅ
y?ฦๅ

cรรc์
y?cr?cf
y?c?p?
[\s+฿ๆ๏๚๛]
'''.replace('f', '(?:cc?[ุิ]?[์])') # Final
    .replace('x', '($|(?=[\s+เ-ไๆ๏๚๛]|c[ะ-ฺ]))') # Exclude
    .replace('r', '(?:c์)') # Foreign 
    .replace('y', '(?:cฺ|c๎)') # Yamakkan: Explicit Cluster Beginning
    .replace('p', '(?:cฺ)') # Pali Coda
    .replace('c', '[ก-ฮ]') # Consonant
    .replace('t', '[่-๋]') # Tone Marker
    .replace('u', '[กจฏฎดตบปอ]') # Unaspirated Consonants
    .replace('v', '[งญณนมย-ว]') # Voiceless Digraphs
    .replace('m', '[ร-ว]') # Medial Consonants
    .strip()
+')'))

PATTERN = re.compile(RE_LTCC)

def segment(text: str) -> list[str]:
    '''
    Segments text into Large Thai Character Clusters (LTCCs)
    '''
    return [token for token in PATTERN.split(text) if token]