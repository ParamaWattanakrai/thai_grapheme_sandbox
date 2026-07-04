from thai_syl import Syllable

syllable = Syllable.extract('อัคร', force_cluster=False, sesquisyllable=False)
syllable = syllable.sound_shift()

print(syllable['reduplicated_syllable']['tone_split'])
print(syllable.get_ipa(reduplicate=True))