
import re

def test_header_detection(text):
    print(f"Testing: '{text}'")
    # Logic from is_stem_header
    if re.match(r'^(Detransitive|Action Noun|Infinitiv):?$', text, re.IGNORECASE):
        print("  -> MATCH (is_stem_header)")
    else:
        print("  -> NO MATCH (is_stem_header)")

    # Logic from main loop normalization
    if re.match(r'^(Detransitive|Action Noun|Infinitiv):?$', text, re.IGNORECASE):
        para_text = text
        if re.match(r'^Detransitive', para_text, re.IGNORECASE):
            para_text = 'Detransitive'
        elif re.match(r'^Action Noun', para_text, re.IGNORECASE):
            para_text = 'Action Noun'
        elif re.match(r'^Infinitiv', para_text, re.IGNORECASE):
            para_text = 'Infinitiv'
        print(f"  -> NORMALIZED: '{para_text}'")

print("--- Testing Valid Headers ---")
test_header_detection("Detransitive")
test_header_detection("Detransitive:")
test_header_detection("detransitive")
test_header_detection("Action Noun")
test_header_detection("Action Noun:")
test_header_detection("Infinitiv")
test_header_detection("Infinitiv:")

print("\n--- Testing Invalid Headers ---")
test_header_detection("Detransitive extra")
test_header_detection("Not a header")
