from thai_syl import Syllable

syllable1 = Syllable.extract('ตำ', force_cluster=False, sesquisyllable=False)
syllable2 = Syllable.extract('รวจ', force_cluster=False, sesquisyllable=False)

syllable2.assimilate_tone(syllable1)
syllable1.sound_shift()
syllable2.sound_shift()

print(syllable1, syllable2)
print(syllable1.reconstruct_text() + syllable2.reconstruct_text())
print(f'{syllable1.main_syllable.tone_split} - {syllable2.main_syllable.assimilated_tone_split}({syllable2.main_syllable.tone_split})')

cases = [
    ('กกิ', False, False),
    ('กกิ', False, True),
    ('กริ่ง', False, False),
    ('กริ่ง', False, True),
    ('หมู', False, False),
    ('หมู', True, False),
    ('หมู', False, True),
    ('แปรง', False, True),
    ('แปรง', False, False),
    ('ครก', False, False),
    ('ถนน', False, True),
    ('เจริญ', False, False),
    ('ไทย', False, False),
    ('เคย', False, False),
]
for text, force_cluster, sesqui in cases:
    syllable = Syllable.extract(text, force_cluster=force_cluster, sesquisyllable=sesqui).sound_shift()
    print(f'{syllable.reconstruct_text()}, {syllable}, cluster {force_cluster}, sesqui {sesqui}, {syllable.main_syllable.vowel_form}')