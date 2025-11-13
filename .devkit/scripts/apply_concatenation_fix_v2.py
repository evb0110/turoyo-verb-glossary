#!/usr/bin/env python3
"""
Apply improved concatenated examples splitting fix to parser
"""

# Read the current parser file
with open('parser/parse_docx_production.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the split_concatenated_examples method
old_method_start = '    def split_concatenated_examples(self, examples):'
old_method_end = '        return split_examples\n\n    def _extract_reference_groups(self, tokens):'

# Find the method
start_idx = content.find(old_method_start)
end_idx = content.find(old_method_end)

if start_idx == -1 or end_idx == -1:
    print('ERROR: Could not find split_concatenated_examples method')
    exit(1)

# Define the improved method
new_method = '''    def split_concatenated_examples(self, examples):
        """AGENT 4 FIX: Split concatenated examples within single paragraphs

        Pattern: Multiple examples concatenated in one paragraph
        Example: "5) example1 ʻtrans1ʼ; 444; prs 249/8; example2, 'trans2' 269"

        Detection: After translation quote + semicolon + optional tokens + ref + semicolon,
                  if substantial Turoyo text follows, it's a new example

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
            # translation (quote) -> ; -> (optional tokens) -> ref -> ; -> substantial turoyo
            split_points = []

            for i in range(len(tokens) - 1):
                # Look for: translation followed by semicolon
                if tokens[i].get('kind') != 'translation':
                    continue

                # Next must be semicolon or very short turoyo then semicolon
                if i + 1 >= len(tokens):
                    continue

                semicolon_idx = i + 1
                if tokens[semicolon_idx].get('kind') == 'punct' and tokens[semicolon_idx].get('value') == ';':
                    # Good, found semicolon right after translation
                    pass
                else:
                    # Skip this translation - no immediate semicolon
                    continue

                # Now look ahead for: (optional short tokens) -> ref -> ; -> turoyo with substantial content
                # Search within next 10 tokens
                for j in range(semicolon_idx + 1, min(semicolon_idx + 11, len(tokens))):
                    # Found a reference
                    if tokens[j].get('kind') == 'ref':
                        # Check if next token is semicolon
                        if j + 1 < len(tokens) and tokens[j + 1].get('kind') == 'punct' and tokens[j + 1].get('value') == ';':
                            # Check if next token after semicolon is substantial turoyo or translation
                            if j + 2 < len(tokens):
                                next_token = tokens[j + 2]
                                next_kind = next_token.get('kind', '')
                                next_value = next_token.get('value', '').strip()

                                # If next is substantial turoyo (10+ chars, has letters) or translation
                                if next_kind == 'translation':
                                    # Definitely a new example
                                    split_points.append(j + 2)
                                    break
                                elif next_kind == 'turoyo' and len(next_value) >= 5:
                                    # Check if it has Turoyo characters (not just spaces/refs)
                                    turoyo_chars = sum(1 for c in next_value if c.isalpha())
                                    if turoyo_chars >= 3:
                                        # This is substantial new content
                                        split_points.append(j + 2)
                                        break

            # If no split points, keep example as is
            if not split_points:
                split_examples.append(example)
                continue

            # Split tokens at split points
            split_points = [0] + split_points + [len(tokens)]
            for k in range(len(split_points) - 1):
                start = split_points[k]
                end = split_points[k + 1]
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

# Replace the method
content = content[:start_idx] + new_method + content[end_idx:]

# Update version to V2.1.3b
content = content.replace('V2.1.3', 'V2.1.3b')

# Write the updated content
with open('parser/parse_docx_production.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Successfully applied improved concatenation fix V2')
print('   - Improved split_concatenated_examples() method')
print('   - Now handles optional tokens between translation and ref')
print('   - Updated version header to V2.1.3b')
