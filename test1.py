from thai_syl import Syllable

syllable = Syllable.extract('คลั่ง', force_cluster=False, sesquisyllable=False)
syllable.sound_shift()

print(syllable.main_syllable.onset_chars)
print(syllable.get_ipa(is_reduplicated=False))
print(syllable.reconstruct_text())