import thai_syl

old_thai = thai_syl.extract('แมลง', force_cluster=True, sesquisyllable=False)
print(old_thai)
standard_thai = thai_syl.sound_shift(old_thai, thai_syl.STANDARD_THAI_SOUND_SHIFTS)
print(standard_thai)