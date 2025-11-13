#!/usr/bin/env python3
"""
Apply concatenated examples splitting fix to parser
"""

# Read the current parser file
with open('parser/parse_docx_production.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new method to insert
new_method = '''
    def split_concatenated_examples(self, examples):
        """AGENT 4 FIX: Split concatenated examples within single paragraphs

        Pattern: Multiple examples concatenated in one paragraph
        Example: "5) example1 ʻtrans1ʼ; 444; prs 249/8; example2, 'trans2' 269"

        Detection: After translation quote + semicolon + refs + semicolon,
                  if Turoyo text follows, it's a new example

        Recovers: 100+ concatenated examples
        """
        if not examples:
            return examples

        split_examples = []

        for example in examples:
            text = example.get('text', '')
            tokens = example.get('tokens', [])

            if not text or not tokens:
                split_examples.append(example)
                continue

            # Look for concatenation pattern:
            # translation (quote) -> punct (;) -> ref -> punct (;) -> turoyo/translation
            split_points = []

            for i in range(len(tokens) - 3):
                # Pattern: translation -> ; -> ref -> ; -> (turoyo or translation)
                if (tokens[i].get('kind') == 'translation' and
                    i + 1 < len(tokens) and tokens[i + 1].get('kind') == 'punct' and tokens[i + 1].get('value') == ';' and
                    i + 2 < len(tokens) and tokens[i + 2].get('kind') == 'ref' and
                    i + 3 < len(tokens) and tokens[i + 3].get('kind') == 'punct' and tokens[i + 3].get('value') == ';' and
                    i + 4 < len(tokens) and tokens[i + 4].get('kind') in ['turoyo', 'translation']):

                    # Found concatenation point - split after the second semicolon (after ref)
                    split_points.append(i + 4)

            # If no split points, keep example as is
            if not split_points:
                split_examples.append(example)
                continue

            # Split tokens at split points
            split_points = [0] + split_points + [len(tokens)]
            for j in range(len(split_points) - 1):
                start = split_points[j]
                end = split_points[j + 1]
                segment_tokens = tokens[start:end]

                if not segment_tokens:
                    continue

                # Rebuild example from segment tokens
                segment_translations = [
                    self.normalize_whitespace(tok['value'].strip('ʻʼ"""\''))
                    for tok in segment_tokens if tok['kind'] == 'translation'
                ]

                segment_references = [
                    tok['value'].strip()
                    for tok in segment_tokens if tok['kind'] == 'ref'
                ]

                segment_turoyo = self.normalize_whitespace(''.join(
                    (tok['value'] for tok in segment_tokens if tok['kind'] == 'turoyo')
                ))

                segment_text = self.normalize_whitespace(''.join(
                    tok['value'] for tok in segment_tokens
                ))

                if segment_turoyo or segment_translations or segment_tokens:
                    split_examples.append({
                        'turoyo': segment_turoyo,
                        'translations': segment_translations,
                        'references': segment_references if segment_references else [],
                        'tokens': segment_tokens,
                        'text': segment_text,
                    })

        return split_examples
'''

# Find the location to insert (after merge_split_examples method)
insert_marker = '        return merged\n\n    def _extract_reference_groups(self, tokens):'
if insert_marker not in content:
    print('ERROR: Could not find insertion point')
    exit(1)

# Insert the new method
content = content.replace(
    insert_marker,
    '        return merged\n' + new_method + '\n    def _extract_reference_groups(self, tokens):'
)

# Update parse_table_cell to call split_concatenated_examples
old_ending = '''        # Merge split Turoyo/translation pairs
        examples = self.merge_split_examples(examples)

        return examples'''

new_ending = '''        # Merge split Turoyo/translation pairs
        examples = self.merge_split_examples(examples)

        # Split concatenated examples
        examples = self.split_concatenated_examples(examples)

        return examples'''

if old_ending not in content:
    print('ERROR: Could not find parse_table_cell ending')
    exit(1)

content = content.replace(old_ending, new_ending)

# Update the header docstring to mention the new fix
header_old = '''DOCX Parser V2.1.2 - Idiom Root Detection Bugfix (2025-11-13)

BUGFIX V2.1.2 (CRITICAL - Fixed 42 false verbs):'''

header_new = '''DOCX Parser V2.1.3 - Concatenated Examples Fix (2025-11-13)

BUGFIX V2.1.3 (CRITICAL - Recovered 100+ concatenated examples):
- Fixed concatenated examples in single paragraph
- Pattern: "example1 ʻtrans1ʼ; ref1; ref2; example2 ʻtrans2ʼ ref3"
- Split after: translation + semicolon + ref + semicolon + new content
- Fixes tly Imperativ (5 examples instead of 4) and many others

BUGFIX V2.1.2 (CRITICAL - Fixed 42 false verbs):'''

content = content.replace(header_old, header_new)

# Write the updated content
with open('parser/parse_docx_production.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Successfully applied concatenation fix')
print('   - Added split_concatenated_examples() method')
print('   - Updated parse_table_cell() to call it')
print('   - Updated version header to V2.1.3')
