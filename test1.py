from thai_syl import Syllable

syllable = Syllable.extract('เขมร', force_cluster=False, sesquisyllable=True)
# syllable.sound_shift()

print(syllable.reduplicated_syllable.vowel_form)
print(syllable.get_ipa(reduplicate=True))
print(syllable.reconstruct_text())