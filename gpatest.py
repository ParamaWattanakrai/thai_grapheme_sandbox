import thai_gpa

syllables = thai_gpa.align('กิจการ', 'kit˨˩.t͡ɕaʔ˨˩.kaːn˧')
for syllable in syllables:
    print(syllable)

# print(thai_gpa.align('สุจิตรา', 'suʔ˨˩.t͡ɕit˨˩.traː˧'))