import thai_syl

old_thai = thai_syl.extract('ใหม่', force_cluster=True, sesquisyllable=False)
standard_thai = thai_syl.sound_shift(old_thai, thai_syl.STANDARD_THAI_SOUND_SHIFTS)
print(old_thai)