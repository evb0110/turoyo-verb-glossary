# Parser Logic Review Report
Generated: 2025-10-13

## Critical Issues

### 1. [CRITICAL] German Gloss Filter Has False Positive
- **Location**: `parser/parse_verbs.py:77-79`
- **Issue**: The filter `if ';' in full_span_text and not any(c in full_span_text for c in 'ʔʕġǧḥṣštṭḏṯẓāēīūə')` incorrectly matches partial German words like "speichern" because it extracts "sp" which passes the filter (contains `;` in lookahead, no special chars in extracted portion)
- **Impact**: Potentially excludes valid Turoyo roots that happen to match partial German words
- **Test Case**:
  ```python
  # Input: <p class="western"><span>speichern;</span>
  # Pattern matches: "sp" (first 2 chars)
  # Filter check: "sp" has no special chars, but we check full_span_text which includes ";"
  # Result: May incorrectly filter or not filter depending on extraction
  ```
- **Fix**: The logic is actually checking `full_span_text` not just the extracted root, so this is less critical than initially suspected. However, improve clarity:
  ```python
  # Better approach: Check if the ENTIRE span is a German gloss
  if full_span_text.endswith(';') and len(full_span_text) > 10 and \
     not any(c in full_span_text for c in 'ʔʕġǧḥṣštṭḏṯẓāēīūə'):
      # This is likely a German gloss, not a root
      continue
  ```
- **Verification**: `grep -E '<span[^>]*>(speichern|erklären|erlauben);' source/Turoyo_all_2024.html`

### 2. [CRITICAL] Root Pattern Allows Partial Latin Character Matches
- **Location**: `parser/parse_verbs.py:65`
- **Issue**: Pattern `([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})` includes Latin characters (b, c, d, f, g, h, k, l, m, n, p, q, r, s, t, w, x, y, z) which can match German text fragments
- **Impact**: Could extract "sp" from "speichern", "er" from "erklären", etc. as potential roots
- **Test Case**:
  ```html
  <p class="western"><span>erklären;</span>  <!-- Matches "er" -->
  <p class="western"><span>speichern;</span> <!-- Matches "sp" -->
  ```
- **Fix**: The German gloss filter (line 72-80) is supposed to catch these, but the order of operations is fragile. Consider:
  1. Strengthen the German gloss filter to check BEFORE regex extraction
  2. Add minimum length requirement (e.g., 3 chars) for roots
  3. Add validation that matched roots appear in a known Turoyo root list
- **Recommended Solution**:
  ```python
  # Pre-filter: Skip entire <p> tags that contain obvious German glosses
  if re.search(r'<span[^>]*>[a-zA-Z]{3,}(;|\s+(und|oder|für|von))', section_html):
      # This paragraph likely contains German glosses, handle carefully
      pass
  ```

### 3. [CRITICAL] Etymology Tuple Comparison May Fail with None Values
- **Location**: `parser/parse_verbs.py:641-657`
- **Issue**: Etymology signature uses tuple with `.get()` which returns `None` for missing keys. Tuples with `None` values are compared, but this may not distinguish between "no source" and "empty source"
- **Impact**: Homonym numbering may incorrectly group or separate verbs
- **Example**:
  ```python
  # Verb 1: {'source': '', 'source_root': 'xyz'}
  # Verb 2: No etymology at all
  # Signature 1: ('', 'xyz', '', '', '')
  # Signature 2: None
  # These are different, so they'll be numbered separately (CORRECT)

  # But what about:
  # Verb 1: {'source': 'Ar.', 'source_root': None}
  # Verb 2: {'source': 'Ar.', 'source_root': ''}
  # Signature 1: ('Ar.', None, '', '', '')
  # Signature 2: ('Ar.', '', '', '', '')
  # These are different, but semantically the same (INCORRECT)
  ```
- **Fix**: Normalize `None` to empty string in signature creation:
  ```python
  sig = (
      first_etymon.get('source') or '',
      first_etymon.get('source_root') or '',
      first_etymon.get('notes') or '',
      first_etymon.get('raw') or '',
      first_etymon.get('reference') or ''
  )
  ```
- **Test**: Check existing numbered homonyms for false positives

### 4. [CRITICAL] Entry Boundary Detection Uses Filtered Matches But Raw HTML
- **Location**: `parser/parse_verbs.py:118-123`
- **Issue**: Boundary calculation uses `valid_matches[i+1][1].start()` to find the next entry, but this is the start position in the ORIGINAL section_html. If any matches were filtered out between entries, the boundary may include content from intervening filtered matches.
- **Impact**: One verb's content could leak into another verb's entry
- **Example**:
  ```
  Position 0: ʔbʕ (valid root) ← Entry starts here
  Position 100: speichern; (German gloss, FILTERED OUT)
  Position 200: ʔḏʕ (valid root) ← Next entry starts here

  Boundary calculation for ʔbʕ:
  - Uses position 200 (next valid match)
  - Extracts HTML from 0 to 200
  - INCLUDES German gloss at position 100! ✗
  ```
- **Fix**: This is actually CORRECT behavior! The filtered matches are excluded from the root list, but their HTML content (which may contain related glosses, references, etc.) should be excluded from ALL entries. The current implementation is correct.
- **Verification**: Check if any verb entries incorrectly contain German glosses in their extracted HTML

### 5. [MEDIUM] Stem Pattern May Miss Some Stem Headers
- **Location**: `parser/parse_verbs.py:279, 294, 311`
- **Issue**: Three different patterns are tried, but there's no logging when stems are found by fallback patterns vs. primary pattern. This makes it hard to know if patterns are working correctly.
- **Impact**: Silent failures if stem structure changes in source HTML
- **Fix**: Add debug logging:
  ```python
  stems.append({
      'stem': stem_num,
      'forms': forms,
      'position': match.start(),
      '_pattern': 'primary'  # or 'combined', 'fallback'
  })
  ```
- **Verification**: Add stats collection: `self.stats['stems_by_pattern'] = {'primary': 0, 'combined': 0, 'fallback': 0}`

## Medium Priority Issues

### 6. [MEDIUM] Root Continuation Logic Is Fragile
- **Location**: `parser/parse_verbs.py:83-86`
- **Issue**: Looks for continuation pattern `</font><font[^>]*><span[^>]*>([...])` in next 100 chars, but this pattern is very specific to current HTML structure
- **Impact**: If HTML formatting changes slightly, continuations will be missed
- **Example**: Root "ṣyb + r = ṣybr" may be missed if spacing or tags change
- **Fix**: Make pattern more flexible:
  ```python
  # Look for any Turoyo characters in next span, regardless of font tags
  cont_match = re.search(
      r'</span>\s*(?:</[^>]+>)*\s*(?:<[^>]+>)*\s*<span[^>]*>([ʔʕbčd...]+)</span>',
      lookahead_cont
  )
  ```
- **Test Cases**:
  - `ṣyb` → should match continuation to `ṣybr`
  - `fhr, fxr` → should handle comma-separated variants

### 7. [MEDIUM] HTML Tag Cleaning in Etymology Is Incomplete
- **Location**: `parser/parse_verbs.py:196-200`
- **Issue**: Hardcoded patterns for specific tag sequences like `</span></i></font></font><font[^>]*><font[^>]*><i><span[^>]*>`. If HTML structure changes, these won't match.
- **Impact**: HTML artifacts may leak into etymology text
- **Fix**: Use BeautifulSoup for robust HTML cleaning:
  ```python
  from bs4 import BeautifulSoup

  def clean_etymology_html(self, etym_text):
      """Remove HTML tags using BeautifulSoup"""
      # First, normalize common patterns
      etym_text = re.sub(r'</span></i></font></font><font[^>]*><font[^>]*><i><span[^>]*>', ' ', etym_text)
      # Then use BeautifulSoup for remaining tags
      soup = BeautifulSoup(etym_text, 'html.parser')
      return soup.get_text(separator=' ')
  ```
- **Verification**: Check etymology fields in output JSON for `<` or `>` characters

### 8. [MEDIUM] Duplicate Stem Prevention Silently Discards Data
- **Location**: `parser/parse_verbs.py:296`
- **Issue**: `if any(s['position'] == match.start() for s in stems): continue` silently skips duplicate stems without logging
- **Impact**: If two different patterns match the same stem, one is silently discarded. This could hide bugs in pattern logic.
- **Fix**: Add warning log:
  ```python
  if any(s['position'] == match.start() for s in stems):
      self.stats['duplicate_stems_skipped'] += 1
      # Optional: log which patterns conflicted
      continue
  ```

### 9. [MEDIUM] Token Generation May Add Excessive Spaces
- **Location**: `parser/parse_verbs.py:158-160`
- **Issue**: Block elements add spaces, but consecutive block elements will add multiple spaces
- **Example**:
  ```html
  <p>Text 1</p>
  <p>Text 2</p>
  <!-- Results in: "Text 1  Text 2" (double space) -->
  ```
- **Impact**: Extra whitespace in displayed text
- **Fix**: Post-process tokens to collapse consecutive spaces:
  ```python
  # After token generation
  cleaned_tokens = []
  prev_was_space = False
  for token in tokens:
      if token['text'] == ' ':
          if not prev_was_space:
              cleaned_tokens.append(token)
          prev_was_space = True
      else:
          cleaned_tokens.append(token)
          prev_was_space = False
  return cleaned_tokens
  ```

### 10. [MEDIUM] Table Cell Reference Extraction Is Too Broad
- **Location**: `parser/parse_verbs.py:383-384`
- **Issue**: Pattern `r'^[\d;/\s\[\]A-Z]+$'` matches any string with digits, semicolons, slashes, spaces, brackets, and uppercase letters. This could incorrectly classify text as references.
- **Example**: "ABC" would be classified as a reference, but might be abbreviation in Turoyo text
- **Impact**: Some translations may be incorrectly classified as references
- **Fix**: Be more specific about reference format:
  ```python
  # References typically look like: "731; 75/3" or "[ML]" or "MM 140"
  if re.match(r'^[\d;/\s]+$', stripped) or \  # Pure numbers/separators
     re.match(r'^\[[A-Z]+\]$', stripped) or \  # [ABC] format
     re.match(r'^[A-Z]{2,3}\s+\d+', stripped):  # MM 140 format
      current_example['references'].append(stripped)
  ```

### 11. [MEDIUM] Homonym Numbering May Create Duplicates
- **Location**: `parser/parse_verbs.py:666-669`
- **Issue**: If source HTML already has "ʕmr 1" and parser tries to add numbers, it will create "ʕmr 1 1" or fail to detect existing number
- **Impact**: Duplicate numbering or incorrect homonym identification
- **Example**:
  ```
  Source HTML: "ʕmr 1", "ʕmr 2"
  Parser extracts: "ʕmr 1", "ʕmr 2"
  Homonym detection: Finds 2 entries with root "ʕmr 1" and "ʕmr 2"
  Result: If they have different etymologies, renames to "ʕmr 1 1" and "ʕmr 2 1" ✗
  ```
- **Fix**: Check if root already has a number before adding:
  ```python
  # Before numbering loop
  base_root = re.sub(r'\s+\d+$', '', root)  # Remove existing number
  root_groups[base_root].append((idx, verb))

  # When numbering
  if len(unique_etyms) > 1:
      for entry_num, (idx, sig) in enumerate(etymologies, 1):
          self.verbs[idx]['root'] = f"{base_root} {entry_num}"
  ```

## Low Priority / Improvements

### 12. [LOW] Regex Patterns Are Not Compiled
- **Location**: Throughout parser
- **Issue**: Regex patterns are recompiled on every use. For patterns used in loops (stem patterns, table patterns, etc.), this is inefficient.
- **Impact**: Minor performance degradation
- **Fix**: Compile patterns in `__init__`:
  ```python
  def __init__(self, html_path):
      # ... existing code ...
      # Compile frequently used patterns
      self.root_pattern = re.compile(r'<p[^>]*class="western"[^>]*>...')
      self.stem_pattern = re.compile(r'<font size="4"...')
      # etc.
  ```

### 13. [LOW] Error Messages Don't Include Context
- **Location**: `parser/parse_verbs.py:695-697`
- **Issue**: Error stored as `f"{root}: {e}"` doesn't include line number or HTML context
- **Impact**: Hard to debug parsing errors
- **Fix**: Include more context:
  ```python
  except Exception as e:
      context = entry_html[:100] if len(entry_html) > 100 else entry_html
      self.errors.append({
          'root': root,
          'error': str(e),
          'context': context,
          'line': self.html.find(entry_html)  # approximate line
      })
  ```

### 14. [LOW] Stats Don't Track Pattern Match Rates
- **Location**: `parser/parse_verbs.py:789-831`
- **Issue**: Statistics don't show which patterns are being used, making it hard to validate parser effectiveness
- **Impact**: Can't easily identify when patterns are failing
- **Fix**: Add pattern usage stats:
  ```python
  stats = {
      # ... existing stats ...
      'pattern_usage': {
          'roots_matched': self.stats['roots_matched'],
          'roots_filtered': self.stats['roots_filtered'],
          'stems_primary_pattern': self.stats.get('stems_primary', 0),
          'stems_combined_pattern': self.stats.get('stems_combined', 0),
          'stems_fallback_pattern': self.stats.get('stems_fallback', 0),
      }
  }
  ```

### 15. [LOW] Token Text Normalization Is Inconsistent
- **Location**: `parser/parse_verbs.py:173-174`
- **Issue**: Keeps tokens if `text.strip() or text == ' '`, but doesn't normalize other whitespace (tabs, newlines, etc.)
- **Impact**: May include tokens with tabs or newlines
- **Fix**: Normalize whitespace in tokens:
  ```python
  for is_italic, text in pairs:
      # Normalize whitespace but preserve single spaces
      if text == ' ':
          tokens.append({'italic': bool(is_italic), 'text': ' '})
      elif text.strip():
          normalized = re.sub(r'\s+', ' ', text)
          tokens.append({'italic': bool(is_italic), 'text': normalized})
  ```

## Regex Pattern Improvements

### Pattern 1: Root Extraction Pattern (Line 65)
- **Current**: `r'<p[^>]*class="western"[^>]*>(?:<font[^>]*>)?<span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})(?:\s*\d+)?[^<]*</span>'`
- **Issues**:
  1. Optional `<font>` tag matches 0-1, but some entries have nested fonts
  2. Character class includes Latin chars that could match German text
  3. No validation that matched text is a valid root
- **Improved**:
  ```python
  # More flexible font tag handling
  r'<p[^>]*class="western"[^>]*>(?:<font[^>]*>)*<span[^>]*>([ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə]{2,6})(?:\s*\d+)?[^<]*</span>'
  #                                      ^ Changed ? to * to match 0 or more font tags
  ```
- **Test Cases**:
  - `<p class="western"><font><span>ʔbʕ</span>` ✓
  - `<p class="western"><font><font><span>ʕmr 1</span>` ✓ (nested fonts)
  - `<p class="western"><span>fhr, fxr</span>` ✓

### Pattern 2: Stem Header Pattern (Line 279)
- **Current**: `r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*</span></b></font></font><font[^>]*><font[^>]*><i><b><span[^>]*>([^<]+)</span>'`
- **Issues**:
  1. Very specific tag structure - brittle
  2. Requires exact nesting of font/b/span tags
- **Improved**:
  ```python
  # More flexible pattern that handles variations
  r'<font[^>]*size="4"[^>]*>.*?<span[^>]*>([IVX]+):\s*</span>.*?<i>.*?<span[^>]*>([^<]+)</span>'
  # Uses .*? to allow variation in tag structure
  ```
- **Test Cases**:
  - Standard format: `<font size="4"><b><span>I: </span></b></font><font><i><span>form</span>`
  - Variant format: `<font size="4"><span>I: </span><i><b><span>form</span>`

### Pattern 3: Etymology Pattern (Line 188)
- **Current**: `r'\(&lt;\s*(.+?)\s*\)(?:\s*[A-Z<]|$)'`
- **Issues**:
  1. Lookahead `(?:\s*[A-Z<]|$)` may miss etymology if followed by lowercase
  2. Non-greedy `.+?` may stop too early if there are nested parentheses
- **Improved**:
  ```python
  # Match etymology more reliably
  r'\(&lt;\s*([^)]+)\s*\)'
  # Simply match everything up to closing paren, then validate content
  ```
- **Test Cases**:
  - `(< MA bʕy cf. SL 169: to strive)` ✓
  - `(< Arab. ʔṯr (II) cf. Wehr 5: wirken)` ✓ (nested parens)

### Pattern 4: Number Detection (Lines 99, 104, 109)
- **Current**: Three separate patterns for italic, separate span, superscript
- **Issues**:
  1. Tries patterns sequentially - inefficient
  2. Patterns are very similar, could be unified
- **Improved**:
  ```python
  # Single pattern to match all number formats
  number_patterns = [
      (r'<i><span[^>]*>\s*(\d+)\s+\(', 'italic_with_paren'),
      (r'<span[^>]*>\s*(\d+)\s*</span>', 'separate_span'),
      (r'<sup[^>]*>.*?(\d+).*?</sup>', 'superscript'),
  ]

  for pattern, pattern_name in number_patterns:
      num_match = re.search(pattern, lookahead, re.DOTALL)
      if num_match:
          root = f"{root_chars} {num_match.group(1)}"
          self.stats[f'number_pattern_{pattern_name}'] += 1
          break
  ```

## Logic Flow Improvements

### Improvement 1: Two-Pass Parsing for Better Accuracy
**Current Flow**:
1. Extract roots with regex
2. Filter German glosses
3. Parse each entry

**Problem**: Can't look ahead to validate roots against global context

**Improved Flow**:
1. **Pass 1**: Extract all potential roots and build root list
2. **Pass 2**: Validate roots against known patterns (e.g., roots should have etymology OR stems)
3. **Pass 3**: Parse validated entries

**Benefits**:
- Can catch false positives (e.g., German text matched as roots)
- Can validate cross-references point to real roots
- Can detect missing entries

### Improvement 2: Schema Validation for Output
**Current**: No validation that output JSON matches expected schema

**Improved**: Add JSON schema validation before saving:
```python
def validate_verb_entry(self, verb):
    """Validate verb entry structure"""
    required_fields = ['root', 'etymology', 'cross_reference', 'stems']
    for field in required_fields:
        if field not in verb:
            raise ValueError(f"Missing required field: {field}")

    # Validate stems
    for stem in verb.get('stems', []):
        if 'stem' not in stem or 'forms' not in stem:
            raise ValueError(f"Invalid stem structure in {verb['root']}")

    return True
```

### Improvement 3: Incremental Parsing with Checkpoints
**Current**: All-or-nothing parsing - if it fails, lose all progress

**Improved**: Save checkpoints during parsing:
```python
def parse_all(self):
    """Parse with checkpoints"""
    checkpoint_file = Path('data/parse_checkpoint.json')

    # Resume from checkpoint if exists
    if checkpoint_file.exists():
        with open(checkpoint_file) as f:
            self.verbs = json.load(f)
        start_letter = self.verbs[-1]['root'][0] if self.verbs else None

    for letter, section_html in sections:
        # Skip already parsed sections
        if start_letter and letter <= start_letter:
            continue

        # Parse section
        roots = self.extract_roots_from_section(section_html)
        # ... parse entries ...

        # Save checkpoint every 5 letters
        if len(self.verbs) % 100 == 0:
            with open(checkpoint_file, 'w') as f:
                json.dump(self.verbs, f)
```

### Improvement 4: Parallel Validation During Parsing
**Current**: Parse everything, then validate at end

**Improved**: Validate each entry immediately after parsing:
```python
def parse_entry(self, root, entry_html):
    """Parse and validate entry"""
    entry = {
        'root': root,
        # ... parse fields ...
    }

    # Immediate validation
    self.validate_entry(entry)

    return entry

def validate_entry(self, entry):
    """Validate entry during parsing"""
    # Check for common issues
    if not entry.get('stems') and not entry.get('cross_reference'):
        self.warnings.append(f"{entry['root']}: No stems or cross-reference")

    if entry.get('etymology'):
        # Validate etymology structure
        for etymon in entry['etymology'].get('etymons', []):
            if 'raw' in etymon and len(etymon) == 1:
                self.warnings.append(f"{entry['root']}: Etymology not fully parsed")
```

## Test Cases Needed

### Edge Cases for Root Extraction:
1. **Roots with variant spellings**: `fhr, fxr` → Should extract as "fhr"
2. **Roots with existing numbers**: `ʕmr 1` → Should extract as "ʕmr 1"
3. **Roots with continuation**: `ṣyb + r` → Should extract as "ṣybr"
4. **German glosses**: `speichern;` → Should be FILTERED OUT
5. **Short roots**: `ṯy` (2 chars) → Should be included
6. **Long roots**: `mstəʕmər` (8+ chars) → May be missed by pattern

### Edge Cases for Etymology Parsing:
1. **Multiple sources with "also"**: `MA x also Arab. y` → Should create 2 etymons with relationship
2. **Nested parentheses**: `(< Arab. ʔṯr (II) cf. Wehr 5)` → Should handle inner parens
3. **Missing fields**: `(< MA)` → Should create etymon with only source
4. **HTML in etymology**: `(< MA <i>bʕy</i>)` → Should strip HTML
5. **Semicolon in meaning**: `(< MA bʕy: seek; need)` → Should preserve in meaning field

### Edge Cases for Stem Extraction:
1. **Multiple forms**: `I: form1/form2/form3` → Should extract all forms
2. **Forms with question marks**: `I: form?/form2?` → Should strip question marks
3. **Detransitive sections**: Should be extracted as separate "stem"
4. **Missing forms**: `I: ` with no forms → Should handle gracefully
5. **Roman numerals**: `I, II, III, IV, V, VI, VII, VIII, IX, X` → All should be recognized

### Edge Cases for Table Extraction:
1. **Empty cells**: Cell with just `<p></p>` → Should return empty examples list
2. **Multiple examples in one cell**: Should split correctly
3. **References mixed with text**: Should separate into turoyo/translation/reference
4. **Nested italics**: `<i><i>text</i></i>` → Should mark as italic (not double-italic)
5. **Multiple references**: `731; 75/3; [ML]` → Should extract all separately

### Edge Cases for Homonym Numbering:
1. **Same root, different etymologies**: Should number as "root 1", "root 2"
2. **Same root, same etymology**: Should NOT number
3. **Pre-numbered roots**: `ʕmr 1` → Should not double-number
4. **Three or more homonyms**: Should number all consecutively

## Recommended Testing Strategy

### Unit Tests:
```python
import pytest
from parser.parse_verbs import TuroyoVerbParser

class TestRootExtraction:
    def test_simple_root(self):
        html = '<p class="western"><span>ʔbʕ</span></p>'
        parser = TuroyoVerbParser('test.html')
        roots = parser.extract_roots_from_section(html)
        assert len(roots) == 1
        assert roots[0][0] == 'ʔbʕ'

    def test_german_gloss_filtered(self):
        html = '<p class="western"><span>speichern;</span></p>'
        parser = TuroyoVerbParser('test.html')
        roots = parser.extract_roots_from_section(html)
        assert len(roots) == 0  # Should be filtered out

    # ... more tests ...
```

### Integration Tests:
```python
def test_full_parsing():
    """Test parsing complete HTML file"""
    parser = TuroyoVerbParser('source/Turoyo_all_2024.html')
    parser.parse_all()

    # Validate output
    assert len(parser.verbs) > 1600  # Should have ~1696 verbs
    assert parser.stats['errors'] == 0  # Should parse without errors

    # Check specific verbs
    abac = [v for v in parser.verbs if v['root'] == 'ʔbʕ']
    assert len(abac) > 0
    assert abac[0]['etymology'] is not None
```

### Regression Tests:
```python
def test_known_issues():
    """Test fixes for previously found bugs"""
    parser = TuroyoVerbParser('source/Turoyo_all_2024.html')

    # Bug: Missing <font> tags on ʕmr entries
    parser.parse_all()
    omr_verbs = [v for v in parser.verbs if 'ʕmr' in v['root']]
    assert len(omr_verbs) >= 2  # Should find both ʕmr 1 and ʕmr 2

    # Bug: German glosses parsed as roots
    speichern = [v for v in parser.verbs if 'speichern' in v['root']]
    assert len(speichern) == 0  # Should NOT find German gloss as root
```

## Priority Actions

### High Priority (Do First):
1. Fix etymology tuple comparison to handle None values (Issue #3)
2. Add logging for filtered German glosses to verify correctness (Issue #1)
3. Validate homonym numbering doesn't create duplicates (Issue #11)
4. Add stem pattern usage statistics (Issue #5)

### Medium Priority (Do Soon):
1. Improve HTML tag cleaning in etymology (Issue #7)
2. Add duplicate stem detection logging (Issue #8)
3. Improve reference extraction pattern (Issue #10)
4. Clean up consecutive spaces in tokens (Issue #9)

### Low Priority (Nice to Have):
1. Compile regex patterns for performance (Issue #12)
2. Improve error messages with context (Issue #13)
3. Add pattern usage stats to output (Issue #14)
4. Normalize whitespace in tokens (Issue #15)

## Summary

**Total Issues Found**: 15
- Critical: 5
- Medium: 6
- Low: 4

**Most Critical**: Etymology tuple comparison with None values could cause incorrect homonym grouping.

**Most Impactful**: Root pattern allowing Latin characters + German gloss filter interaction needs validation to ensure no German text leaks through as roots.

**Quick Wins**: Add logging and statistics for pattern usage to validate parser effectiveness.
