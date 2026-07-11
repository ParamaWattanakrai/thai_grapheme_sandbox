from thai_syl import Syllable

syllable = Syllable.extract('ขรุ', force_cluster=False, sesquisyllable=False)
syllable.sound_shift()

print(syllable.get_ipa(assimilate_tone=True, reduplicate=True))
print(syllable.reconstruct_text())