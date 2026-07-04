from thai_syl import Syllable

syllable = Syllable.extract('อัฐิ', force_cluster=False, sesquisyllable=False)
syllable = syllable.sound_shift()

print(syllable['reduplicated_syllable']['tone_split'])
print(syllable['main_syllable']['vowel_form'])
print(syllable.get_ipa(reduplicate=True))