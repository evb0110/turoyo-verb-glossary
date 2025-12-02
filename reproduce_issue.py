
import re
from collections import defaultdict

class MockRun:
    def __init__(self, text, italic=False, size=None):
        self.text = text
        self.italic = italic
        self.font = type('obj', (object,), {'size': type('obj', (object,), {'pt': size})})

class MockPara:
    def __init__(self, text, runs=None):
        self.text = text
        self.runs = runs if runs else [MockRun(text)]

class FixedDocxParser:
    def __init__(self):
        self.verbs = []
        self.stats = defaultdict(int)

    def extract_stem_info(self, text):
        match = re.match(r'^([IVX]+|Pa\.|Af\.|Št\.|Šaf\.):\s*(.+)', text.strip())

        if not match:
            return None, [], ''

        stem_num = match.group(1)
        forms_text = match.group(2).strip()
        forms_match = re.match(r'^(\S+(?:\s*\([^)]+\))?(?:/\S+(?:\s*\([^)]+\))?)*)', forms_text)
        if forms_match:
            forms_str = forms_match.group(1)
            forms = [f.strip() for f in forms_str.split('/') if f.strip()]
            # Extract gloss text after forms (if any)
            gloss_text = forms_text[forms_match.end():].strip()
            return stem_num, forms, gloss_text
        return None, [], ''

    def tokenize_paragraph_runs(self, para, target_text):
        tokens = []
        full_text = para.text
        start_pos = full_text.find(target_text)

        if start_pos == -1:
            return tokens

        end_pos = start_pos + len(target_text)
        current_pos = 0

        for run in para.runs:
            run_text = run.text
            run_len = len(run_text)
            run_end = current_pos + run_len

            if run_end > start_pos and current_pos < end_pos:
                overlap_start = max(0, start_pos - current_pos)
                overlap_end = min(run_len, end_pos - current_pos)
                text_fragment = run_text[overlap_start:overlap_end]

                if text_fragment:
                    tokens.append({
                        'italic': bool(run.italic),
                        'text': text_fragment
                    })

            current_pos = run_end
            if current_pos >= end_pos:
                break

        return tokens

parser = FixedDocxParser()
text = "I: qərfle/qoraf to break (a pencil)"
# Mock runs: "I: " (regular), "qərfle/qoraf" (italic), " to break (a pencil)" (regular)
runs = [
    MockRun("I: ", False),
    MockRun("qərfle/qoraf", True),
    MockRun(" to break (a pencil)", False)
]
para = MockPara(text, runs)

print(f"Testing text: '{text}'")
stem_num, forms, gloss_text = parser.extract_stem_info(text)
print(f"Stem: {stem_num}")
print(f"Forms: {forms}")
print(f"Gloss text: '{gloss_text}'")

if gloss_text:
    tokens = parser.tokenize_paragraph_runs(para, gloss_text)
    print(f"Tokens: {tokens}")
else:
    print("No gloss text extracted")
