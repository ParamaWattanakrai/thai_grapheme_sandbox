import thai_syl

old_thai = thai_syl.extract('บุรพ', force_cluster=False, sesquisyllable=False)
standard_thai = thai_syl.sound_shift(old_thai, thai_syl.STANDARD_THAI_SOUND_SHIFTS)
print(old_thai)
print(standard_thai)