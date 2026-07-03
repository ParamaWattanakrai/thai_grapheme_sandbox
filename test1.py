import thai_syl

old_thai = thai_syl.extract('หา', force_cluster=False, sesquisyllable=False)
print(old_thai)
standard_thai = thai_syl.sound_shift(old_thai, thai_syl.STANDARD_THAI_SOUND_SHIFTS)
print(standard_thai)

print(thai_syl.get_ipa(standard_thai, reduplicate=True))