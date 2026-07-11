from thai_syl import Syllable

syllable1 = Syllable.extract('ตำ', force_cluster=False, sesquisyllable=False)
syllable2 = Syllable.extract('รวจ', force_cluster=False, sesquisyllable=False)

syllable2.assimilate_from(syllable1)
syllable1.sound_shift()
syllable2.sound_shift()

print(syllable1.get_ipa() + syllable2.get_ipa())
print(syllable1.reconstruct_text() + syllable2.reconstruct_text())
print(f'{syllable1.main_syllable.tone_split} - {syllable2.main_syllable.assimilated_tone_split}({syllable2.main_syllable.tone_split})')