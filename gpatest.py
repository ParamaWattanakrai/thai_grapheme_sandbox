import thai_gpa

syllables = thai_gpa.align('ทาส', 'tʰaːt˦˩.saʔ˨˩.')
print(syllables)
print(syllables[0].get_ipa(apply_irregularities=False))

# 'การขัดกันของผลประโยชน์', 'kaːn˧.kʰat˨˩.kan˧.kʰɔːŋ˨˥.pʰon˨˥.praʔ˨˩.joːt˨˩'
# 'การตลาด', 'kaːn˧.taʔ˨˩.laːt˨˩'
# 'การเจริญทำ', 'kaːn˧.t͡ɕaʔ˨˩.rɤːn˧.tʰam˧'
# 'กฎหมายรัฐธรรมนูญ', 'kot˨˩.maːj˨˥.rat˦˥.tʰaʔ˨˩.tʰam˧.maʔ˦˥.nuːn˧'
# 'ชาติพันธุ์', 't͡ɕʰaːt˦˩.tiʔ˨˩.pʰan˧'
# 'กษัตริย์', 'kaʔ˨˩.sat˨˩'
# 'สุจิตรา', 'suʔ˨˩.t͡ɕit˨˩.traː˧'
# 'ตำรวจ', 'tam˧.ruət˨˩'
# 'ประชาธิปไตย', 'praʔ˨˩.t͡ɕʰaː˧.tʰip˦˥.paʔ˨˩.taj˧'
# 'จมูก', 't͡ɕa˨˩.muːk˨˩'
# 'กรณี', 'kɔː˧.raʔ˦˥.niː˧'
# 'เล่น', 'len˦˩'
# 'ไหม', 'maj˦˥'
# 'ฤทธิ์', 'rit˦˥'