import re

RE_LTCC = re.sub(r"\s+", '|', ('('+
r'''
เy*cีt?ยะ?r?p*f?

เy*cืt?อะ?r?p*f?

เy*cิt?r?cf?

ก็
y*c็t?อr?cf?

[เแ]c?c็t?r?cf?
เc?ct?าะr?p*f?
เy*ct?าะ?r?p*f?

[เ-ไ]หvtf?x
[เ-ไ]umtf?x
[เ-โ]y*ct?ะ?r?p*f?
[เ-ไ]y*ct?r?p*f?

y*ct?[ะาำ]r?p*f?

y*c[ิ-ู]t?r?p*f?
c[ิ-ฺํ๎]t?r?f?

y*cืt?r?cf?

y*cัt?cิf?
y*cัt?cุf?
y*cัt?r?cf?

y*cัt?วะf?

บ่
(?<=[เ-ไ]ห)vt
(?<=[เ-ไ]u)mt
y*ctr?cf?

y*ฤๅ?
y*ฦๅ?

cรรc์
y*cr?cf
y*c?p*
[\s+฿ๆ๏๚๛]
'''.replace('f', r'(?:cc?[ุิ]?์)') # Final
    .replace('x', r'($|(?=[\s+เ-ไๆ๏๚๛]|c[ะ-ฺ]))') # Exclude
    .replace('r', r'(?:c์)') # Foreign
    .replace('y', r'(?:cฺ|c๎)') # Yamakkan: Explicit Cluster Beginning
    .replace('p', r'(?:cฺ)') # Pali Coda
    .replace('c', r'[ก-ฮ]') # Consonant
    .replace('t', r'[่-๋]') # Tone Marker
    .replace('u', r'[กจฏฎดตบปอ]') # Unaspirated Consonants
    .replace('v', r'[งญณนมย-ว]') # Voiceless Digraphs
    .replace('m', r'[ร-ว]') # Medial Consonants
    .strip()
+')'))

PATTERN = re.compile(RE_LTCC)

def segment(text: str) -> list[str]:
    '''
    Segments text into Large Thai Character Clusters (LTCCs)
    '''
    return [token for token in PATTERN.split(text) if token]