from thai_syl import Syllable

syllable = Syllable.extract('ขลัง', force_cluster=False, sesquisyllable=False)
syllable.sound_shift()

print(syllable.main_syllable.onset_chars)
print(syllable.get_ipa(reduplicate=True))
print(syllable.reconstruct_text())