from thai_syl import Syllable

syllable = Syllable.extract('ตลาด', force_cluster=False, sesquisyllable=True)
syllable.sound_shift()

print(syllable.get_ipa(assimilate_tone=False, reduplicate=True))
print(syllable.reconstruct_text())