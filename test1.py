from thai_syl import Syllable

syllable = Syllable.extract('เจริ่ญ', force_cluster=False, sesquisyllable=True)
syllable.sound_shift()

print(syllable.reduplicated_syllable.tone_split)
print(syllable.reduplicated_syllable.gedney_tone)
print(syllable.reduplicated_syllable.tone)
print(syllable.main_syllable.vowel_form)
print(syllable.get_ipa(reduplicate=True))
print(syllable.reconstruct_text())