# Critical Parser Fixes - Quick Reference

## Fix #1: Etymology Tuple Comparison (HIGH PRIORITY)

**Location**: `parser/parse_verbs.py` line 641-657

**Problem**: `None` vs `''` treated as different in etymology comparison

**Current Code**:

```python
sig = (
    first_etymon.get('source', ''),
    first_etymon.get('source_root', ''),
    first_etymon.get('notes', ''),
    first_etymon.get('raw', ''),
    first_etymon.get('reference', '')
)
```

**Fixed Code**:

```python
sig = (
    first_etymon.get('source') or '',
    first_etymon.get('source_root') or '',
    first_etymon.get('notes') or '',
    first_etymon.get('raw') or '',
    first_etymon.get('reference') or ''
)
```

**Why**: `.get('key', '')` returns `''` if key is missing, but `.get('key')` returns `None`. If key exists but value is `None`, the first returns `None` while second with `or ''` normalizes to `''`.

---

## Fix #2: Homonym Double-Numbering (HIGH PRIORITY)

**Location**: `parser/parse_verbs.py` line 623-674

**Problem**: Pre-numbered roots (e.g., "ʕmr 1") get numbered again → "ʕmr 1 1"

**Current Code**:

```python
def add_homonym_numbers(self):
    root_groups = defaultdict(list)
    for idx, verb in enumerate(self.verbs):
        root_groups[verb['root']].append((idx, verb))
    # ... continues with root_groups['ʕmr 1'] and root_groups['ʕmr 2'] separately
```

**Fixed Code**:

```python
def add_homonym_numbers(self):
    root_groups = defaultdict(list)
    for idx, verb in enumerate(self.verbs):
        # Strip existing numbers to group homonyms correctly
        base_root = re.sub(r'\s+\d+$', '', verb['root'])
        root_groups[base_root].append((idx, verb))

    numbered_count = 0
    for base_root, entries in root_groups.items():
        if len(entries) <= 1:
            continue

        # Extract etymology signatures
        etymologies = []
        for idx, verb in entries:
            etym = verb.get('etymology')
            if etym and 'etymons' in etym and etym['etymons']:
                first_etymon = etym['etymons'][0]
                sig = (
                    first_etymon.get('source') or '',
                    first_etymon.get('source_root') or '',
                    first_etymon.get('notes') or '',
                    first_etymon.get('raw') or '',
                    first_etymon.get('reference') or ''
                )
            else:
                sig = None
            etymologies.append((idx, sig))

        # Check if etymologies differ
        unique_etyms = set(sig for _, sig in etymologies)

        # Only number if there are DIFFERENT etymologies
        if len(unique_etyms) > 1:
            print(f"   ℹ️  Found homonyms for '{base_root}' with {len(unique_etyms)} different etymologies")
            for entry_num, (idx, sig) in enumerate(etymologies, 1):
                old_root = self.verbs[idx]['root']
                self.verbs[idx]['root'] = f"{base_root} {entry_num}"
                print(f"      {old_root} → {self.verbs[idx]['root']} (etymology: {sig[0] if sig else 'None'})")
            numbered_count += len(entries)

    if numbered_count > 0:
        self.stats['homonyms_numbered'] = numbered_count
        print(f"   ✅ Auto-numbered {numbered_count} homonym entries")
```

**Key Changes**:

1. Line 4-5: Extract base root without number using `re.sub(r'\s+\d+$', '', verb['root'])`
2. Line 7: Use `base_root` as dictionary key instead of `verb['root']`
3. Line 33: Assign `f"{base_root} {entry_num}"` instead of `f"{root} {entry_num}"`

---

## Fix #3: German Gloss Pre-Filtering (MEDIUM PRIORITY)

**Location**: `parser/parse_verbs.py` line 61 (add before root extraction)

**Problem**: German glosses like "speichern;" match root pattern as "sp"

**Add This Code** (before line 67 `for match in re.finditer(root_pattern...)`):

```python
# Pre-filter: Remove obvious German gloss paragraphs before root extraction
# Pattern: <p><span>germanword;</span></p> where germanword is Latin chars only
german_gloss_paragraph = r'<p[^>]*class="western"[^>]*>(?:<font[^>]*>)*<span[^>]*>[a-z]{3,}[^<]*;[^<]*</span>'
section_html = re.sub(german_gloss_paragraph, '<!-- FILTERED GERMAN GLOSS -->', section_html, flags=re.IGNORECASE)
```

**Alternative** (more aggressive, use if above doesn't work):

```python
# Pre-filter: Remove paragraphs that end with semicolon and have no Turoyo characters
def has_turoyo_chars(text):
    return any(c in text for c in 'ʔʕġǧḥṣštṭḏṯẓāēīūə')

# Split into paragraphs and filter
paragraphs = re.split(r'(<p[^>]*class="western"[^>]*>.*?</p>)', section_html, flags=re.DOTALL)
filtered = []
for para in paragraphs:
    if '<p' in para and '<span' in para:
        span_text = re.search(r'<span[^>]*>([^<]+)</span>', para)
        if span_text and ';' in span_text.group(1) and not has_turoyo_chars(span_text.group(1)):
            filtered.append('<!-- FILTERED GERMAN GLOSS -->')
            continue
    filtered.append(para)
section_html = ''.join(filtered)
```

---

## Fix #4: Add Pattern Usage Logging (LOW PRIORITY)

**Location**: Various locations where patterns match

**Add** to each pattern match section:

```python
# In parse_stems() - Primary pattern (line 282)
stems.append({
    'stem': stem_num,
    'forms': forms,
    'position': match.start(),
    '_pattern': 'primary'  # ADD THIS
})
self.stats['stem_pattern_primary'] += 1  # ADD THIS

# In parse_stems() - Combined pattern (line 304)
stems.append({
    'stem': stem_num,
    'forms': forms,
    'position': match.start(),
    '_pattern': 'combined'  # ADD THIS
})
self.stats['stem_pattern_combined'] += 1  # ADD THIS

# In parse_stems() - Fallback pattern (line 331)
stems.append({
    'stem': stem_num,
    'forms': forms,
    'position': match.start(),
    '_pattern': 'fallback'  # ADD THIS
})
self.stats['stem_pattern_fallback'] += 1  # ADD THIS
```

**Update stats output** (line 863):

```python
print("=" * 80)
print("✅ PARSING COMPLETE!")
print("=" * 80)
print(f"📚 Total verbs: {len(parser.verbs)}")
print(f"📖 Total stems: {parser.stats['stems_parsed']}")
print(f"   • Primary pattern: {parser.stats.get('stem_pattern_primary', 0)}")
print(f"   • Combined pattern: {parser.stats.get('stem_pattern_combined', 0)}")
print(f"   • Fallback pattern: {parser.stats.get('stem_pattern_fallback', 0)}")
print(f"🔗 Cross-references: {parser.stats.get('cross_references', 0)}")
print(f"❓ Uncertain entries: {parser.stats.get('uncertain_entries', 0)}")
print(f"🔢 Homonyms numbered: {parser.stats.get('homonyms_numbered', 0)}")
print("=" * 80)
```

---

## Testing Checklist (Legacy HTML Pipeline Deprecation)

The legacy HTML validation steps have been retired. Use the DOCX parser and validation workflow described in `PARSING.md` and `.devkit/analysis` instead.

---

## Quick Apply Script

Save this as `apply_critical_fixes.sh`:

```bash
#!/bin/bash

echo "Applying critical parser fixes..."

# Backup original
cp parser/parse_verbs.py parser/parse_verbs.py.backup

# Apply Fix #1: Etymology tuple comparison
sed -i '' 's/first_etymon.get(\x27source\x27, \x27\x27)/first_etymon.get(\x27source\x27) or \x27\x27/g' parser/parse_verbs.py
sed -i '' 's/first_etymon.get(\x27source_root\x27, \x27\x27)/first_etymon.get(\x27source_root\x27) or \x27\x27/g' parser/parse_verbs.py
sed -i '' 's/first_etymon.get(\x27notes\x27, \x27\x27)/first_etymon.get(\x27notes\x27) or \x27\x27/g' parser/parse_verbs.py
sed -i '' 's/first_etymon.get(\x27raw\x27, \x27\x27)/first_etymon.get(\x27raw\x27) or \x27\x27/g' parser/parse_verbs.py
sed -i '' 's/first_etymon.get(\x27reference\x27, \x27\x27)/first_etymon.get(\x27reference\x27) or \x27\x27/g' parser/parse_verbs.py

echo "✅ Applied Fix #1: Etymology tuple comparison"
echo "⚠️  Fix #2 (homonym numbering) requires manual editing - see CRITICAL_FIXES.md"
echo ""
echo "Backup saved to: parser/parse_verbs.py.backup"
```

---

## Summary

**Must Fix** (before next production parse):

- ✅ Fix #1: Etymology tuple comparison
- ✅ Fix #2: Homonym double-numbering

**Should Fix** (improves reliability):

- ⚠️ Fix #3: German gloss pre-filtering

**Nice to Have** (improves observability):

- ℹ️ Fix #4: Pattern usage logging

**Total Effort**: ~30 minutes for critical fixes
