from thai_syl import Syllable

# 1. Parse a Thai word into its linguistic components
syllable = Syllable.extract("อนา", sesquisyllable=True)

# Access main syllable sub-properties using string keys
print(f"Onset: {syllable['minor_syllable']['consonant']}")
print(f"Onset: {syllable['minor_syllable']['onset']}")   
print(f"Onset: {syllable['main_syllable']['onset']}")   
print(f"Onset: {syllable['main_syllable']['onset']}")    # Output: k
print(f"Medial: {syllable['main_syllable']['medial']}")  # Output: w
print(f"Vowel: {syllable['main_syllable']['vowel']}")    # Output: aː
print(f"Coda: {syllable['main_syllable']['coda']}")      # Output: m

# 2. Apply historical sound shifts (e.g., to Modern Standard Thai)
syllable = syllable.sound_shift()

# 3. Generate the International Phonetic Alphabet (IPA) representation
ipa_output = syllable.get_ipa()
print(f"IPA: {ipa_output}")