from thai_syl import Syllable

syllable = Syllable.extract('มาร', force_cluster=False, sesquisyllable=False)
syllable.sound_shift()

print(syllable.reduplicated_syllable.vowel_form)
print(syllable.get_ipa(reduplicate=True))
print(syllable.reconstruct_text())