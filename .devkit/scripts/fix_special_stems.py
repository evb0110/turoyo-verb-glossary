#!/usr/bin/env python3
"""
Fix parser to extract Action Noun and standalone Detransitive sections.

This script modifies parse_docx_production.py to:
1. Recognize "Action Noun" and "Infinitiv" as stem headers
2. Extract forms from the line following these special headers
3. Extract gloss from the second line following
"""

import re

def main():
    parser_file = 'parser/parse_docx_production.py'

    with open(parser_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix 1: Add Action Noun and Infinitiv to is_stem_header method
    old_is_stem = '''        if not has_stem:
            if text.startswith('Detransitive'):
                return True

            # BUGFIX: Detect freeform stem lines'''

    new_is_stem = '''        if not has_stem:
            if text.startswith('Detransitive'):
                return True

            # BUGFIX: Recognize "Action Noun" and "Infinitiv" as stem headers
            if text in ['Action Noun', 'Infinitiv']:
                return True

            # BUGFIX: Detect freeform stem lines'''

    content = content.replace(old_is_stem, new_is_stem)

    # Fix 2: Replace the Detransitive handling with comprehensive special stem handling
    # Find the start: "elif 'Detransitive' in para.text and current_verb:"
    start_marker = "elif 'Detransitive' in para.text and current_verb:"
    start_idx = content.find(start_marker)

    if start_idx == -1:
        print("ERROR: Could not find Detransitive handling section")
        return 1

    # Find the end: the line "self.stats['stems_parsed'] += 1" after the start
    # followed by another elif or similar structure
    search_start = start_idx + len(start_marker)

    # Look for "self.stats['stems_parsed'] += 1" after Detransitive section
    end_marker = "self.stats['stems_parsed'] += 1"
    temp_idx = content.find(end_marker, search_start)

    if temp_idx == -1:
        print("ERROR: Could not find end marker")
        return 1

    # Find end of that line
    end_idx = content.find('\n', temp_idx) + 1

    # Back up to find "else:" before "if self.is_stem_header"
    # We need to find "else:\n                    # Check if next element"
    else_marker = "\n                else:\n                    # Check if next element is a table"
    else_idx = content.find(else_marker, start_idx, end_idx + 200)

    if else_idx == -1:
        print("ERROR: Could not find else marker")
        return 1

    # Extract old section from elif to end of stems_parsed line
    old_section = content[start_idx:end_idx]

    # Create new section
    new_section = '''else:
                    # Check if next element is a table (for detecting implicit stems)
                    next_elem_is_table = False
                    if idx + 1 < len(elements) and elements[idx + 1][0] == 'table':
                        next_elem_is_table = True

                    if self.is_stem_header(para, next_elem_is_table):
                        # CRITICAL FIX: Reset idioms flag when we encounter a stem marker
                        self.in_idioms_section = False

                        para_text = para.text.strip()

                        # BUGFIX: Handle special stem types (Detransitive, Action Noun, Infinitiv)
                        if para_text in ['Detransitive', 'Action Noun', 'Infinitiv']:
                            # Look ahead for forms and gloss in next paragraphs
                            forms = []
                            label_gloss = ''

                            # Find next non-empty paragraphs
                            for j in range(idx + 1, min(idx + 4, len(elements))):
                                if elements[j][0] != 'para':
                                    break

                                next_p = elements[j][1]
                                next_text = next_p.text.strip()

                                if not next_text:
                                    continue

                                # Check if this is a stem header (stop looking)
                                if self.is_stem_header(next_p, False):
                                    break

                                # First non-empty para after header: check if it's forms
                                if not forms:
                                    # Pattern: "nqil/mənqəl" or "nqolo" (Turoyo forms)
                                    # Include both special and basic ASCII vowels
                                    turoyo_chars = r'ʔʕbčdfgġǧhḥklmnpqrsṣštṭvwxyzžḏṯẓāēīūəaeiou\\u0300-\\u036F'
                                    forms_pattern = rf'^[{turoyo_chars}]+(?:/[{turoyo_chars}]+)*$'

                                    if re.match(forms_pattern, next_text):
                                        # Extract forms (split by /)
                                        forms = [f.strip() for f in next_text.split('/') if f.strip()]
                                        continue

                                # Second non-empty para (or first if no forms): gloss
                                if not label_gloss:
                                    label_gloss = next_text
                                    break

                            # Create stem entry
                            current_stem = {
                                'stem': para_text,
                                'forms': forms,
                                'conjugations': {}
                            }

                            # Add label_gloss_tokens if gloss found
                            if label_gloss:
                                # Check if gloss has italic formatting
                                has_italic = False
                                for j in range(idx + 1, min(idx + 4, len(elements))):
                                    if elements[j][0] == 'para':
                                        p = elements[j][1]
                                        if label_gloss in p.text:
                                            has_italic = any(r.italic for r in p.runs if r.text.strip())
                                            break

                                current_stem['label_gloss_tokens'] = [{
                                    'italic': has_italic,
                                    'text': label_gloss
                                }]

                            if current_verb is not None:
                                current_verb['stems'].append(current_stem)
                                self.stats['stems_parsed'] += 1
                                if para_text == 'Detransitive':
                                    self.stats['detransitive_entries'] += 1

                        else:
                            # Regular stem (I, II, Pa., Af., etc.)
                            stem_num, forms = self.extract_stem_info(para.text)
                            if stem_num and current_verb is not None:
                                current_stem = {
                                    'stem': stem_num,
                                    'forms': forms,
                                    'conjugations': {}
                                }
                                current_verb['stems'].append(current_stem)
                                self.stats['stems_parsed'] += 1'''

    # Replace from elif through the end of the old stem handling
    # We keep everything before elif and everything after
    content = content[:start_idx] + new_section + '\n' + content[end_idx:]

    # Write back
    with open(parser_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Parser updated successfully!")
    print("   - Added 'Action Noun' and 'Infinitiv' recognition")
    print("   - Added forms extraction for special stem types")
    print("   - Added gloss extraction for special stem types")
    return 0

if __name__ == '__main__':
    exit(main())
