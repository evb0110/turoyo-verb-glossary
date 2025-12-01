# Issue #3c: Missing Cross-References Analysis

**User Report:** "šġl 2 and šġl 3 were created but cross-references are missing"

**Date:** 2025-11-15

---

## Executive Summary

**ISSUE CONFIRMED:** The parser is currently **rejecting cross-reference entries** entirely, preventing them from being created in the JSON output. The cross-reference detection logic at line 115 of `parse_docx_production.py` is **case-sensitive** and only matches uppercase `See`, but the DOCX uses lowercase `see`.

**Impact:**

- **4 cross-reference stub entries** are missing from the database (šġl 2, šġl 3, žġl 1, žġl 2)
- **29 forward references** (→ pattern) are being partially parsed but losing reference information
- **48 "see also" references** in etymologies are being stored in etymology text but not as structured cross-references

---

## Current State

### 1. Missing Verbs

**Expected but not found:**

```
šġl 2  'sprechen, erzählen' see ǧġl1
šġl 3  'beschäftigen, ablenken' see ǧġl2
žġl 1 'sprechen, erzählen' see ǧġl1
žġl 2 'beschäftigen, ablenken' see ǧġl2
```

**Currently exist (empty stubs):**

```json
// server/assets/verbs/šġl 2.json
{
  "root": "šġl 2",
  "etymology": null,
  "cross_reference": null,
  "stems": [],
  "idioms": null,
  "uncertain": false
}
```

**Note:** The files exist but have no content (no cross-reference, no translation, no stems).

### 2. DOCX Source Data

**Paragraph 109 (file: 6. š,t,ṭ,ṯ.docx):**

```
šġl 2  'sprechen, erzählen' see ǧġl1
```

**Run formatting:**

- Run 0-8: Non-italic (root, number, translation)
- Run 9: Italic " "
- Run 10: Italic "see "
- Run 11-12: Non-italic "ǧġl1"

**Paragraph 110 (file: 6. š,t,ṭ,ṯ.docx):**

```
šġl 3  'beschäftigen, ablenken' see ǧġl2
```

**Run formatting:** Same pattern as above.

### 3. Target Verbs (Referenced Entries)

**Paragraph 1341 (file: 2. d, f, g, ġ, ǧ.docx):**

```
ǧġl1 (< Arab. coll.  šġl (VIII): cf. Az., Dr., VW 227: reden, sprechen; fragen; Has., Talay 2002 82;)  → šġl2, žġl1
```

**Paragraph 1353 (file: 2. d, f, g, ġ, ǧ.docx):**

```
ǧġl2 (< Arab. šġl (IV) cf. Wehr 661: beschäftigen;) see also šġl3, žġl2
```

**Observation:** The **forward references** (→ symbol and "see also") are in the etymology paragraph but are **not being parsed as cross-references**.

---

## Root Cause Analysis

### Parser Detection Logic (Line 115)

**File:** `parser/parse_docx_production.py`

```python
def is_root_paragraph(self, para, next_para=None):
    # ...
    has_root = re.match(rf'^({turoyo_with_combining}{{2,12}})(?:\s+\d+)?(?:\s|\(|<|$)', text)
    is_cross_ref = bool(re.search(r'→|See\s+[ʔʕbčdfgġǧhḥklmnpqrsṣštṭvwxyzžḏṯẓāēīūə]', text))

    if not has_root or is_cross_ref:
        return False  # REJECT paragraph as root
```

**Problem:** `is_cross_ref` regex is **case-sensitive**:

- Matches: `See ǧġl1` (uppercase S)
- Does NOT match: `see ǧġl1` (lowercase s)

**Result:** Paragraphs with lowercase `see` are **accepted as roots** but then fail to extract cross-reference data.

### Test Results

```
Text: šġl 2  'sprechen, erzählen' see ǧġl1
  has_root: šġl
  is_cross_ref: False  ← BUG: Should be True
  Would be detected as root: True
  is_cross_ref (case-insensitive): True  ← Correct detection
```

---

## Cross-Reference Patterns in DOCX

### Pattern 1: Cross-Reference Stubs (4 entries)

**Format:** `ROOT NUMBER 'translation' see TARGET`

**Examples:**

```
šġl 2  'sprechen, erzählen' see ǧġl1
šġl 3  'beschäftigen, ablenken' see ǧġl2
žġl 1 'sprechen, erzählen' see ǧġl1
žġl 2 'beschäftigen, ablenken' see ǧġl2
```

**Current behavior:** Parser accepts as root, creates empty verb entry with no cross-reference.

**Expected behavior:** Parser should:

1. Detect `see TARGET` pattern
2. Extract translation ('sprechen, erzählen')
3. Store cross-reference target (ǧġl1)
4. Mark as cross-reference entry

### Pattern 2: Forward References (29 entries)

**Format:** `ROOT (etymology)  → TARGET1, TARGET2`

**Examples:**

```
ǧġl1 (< Arab. coll.  šġl (VIII): ...)  → šġl2, žġl1
ʔkl → ʔxl
```

**Current behavior:** → symbol and targets are stored as part of etymology text, but not as structured cross-references.

**Expected behavior:** Parser should:

1. Extract → TARGET pattern from etymology
2. Store in `cross_reference` field
3. Remove from etymology text (or keep both)

### Pattern 3: "See Also" References (48 entries)

**Format:** `ROOT (etymology) see also TARGET1, TARGET2`

**Examples:**

```
ǧġl2 (< Arab. šġl (IV) ...) see also šġl3, žġl2
ʕḏb (< Arab. ...) see also ʕzb
```

**Current behavior:** "see also TARGET" is stored as part of etymology text.

**Expected behavior:** Could extract as secondary cross-references or keep in etymology.

---

## Schema Analysis

### Current IVerb Interface

**File:** `/Users/evb/WebstormProjects/turoyo-verb-glossary/shared/types/IVerb.ts`

```typescript
export interface IVerb {
  root: string;
  etymology: IEtymology | null;
  cross_reference: string | null; // ✅ Field exists
  stems: IStem[];
  uncertain: boolean;
  idioms?: string[] | null;

  lemma_header_raw?: string;
  lemma_header_tokens?: Array<{
    italic: boolean;
    text: string;
  }>;
}
```

**Analysis:**

- ✅ `cross_reference` field already exists
- ❌ Only supports **single target** (string)
- ⚠️ Cannot store multiple targets (e.g., "→ šġl2, žġl1")
- ⚠️ No distinction between "see" (redirect) and "see also" (related)

### Frontend Support

**File:** `/Users/evb/WebstormProjects/turoyo-verb-glossary/app/components/VerbHeader.vue`

```vue
<UBadge v-if="verb.cross_reference" variant="soft">
    Cross-reference
</UBadge>

<div v-if="verb.cross_reference" class="rounded-lg border px-4 py-3 text-sm">
    See related entry
    <NuxtLink
        :to="{
            name: 'verbs-root',
            params: { root: rootToSlug(verb.cross_reference) }
        }"
        class="font-medium"
    >
        {{ verb.cross_reference }}
    </NuxtLink>
</div>
```

**Analysis:**

- ✅ UI already displays cross-references
- ✅ Creates clickable link to target verb
- ❌ Only supports single target (cannot display multiple)
- ⚠️ No special handling for cross-reference stubs (verbs with no stems)

---

## Proposed Solutions

### Option A: Minimal Fix (Cross-Reference Stubs Only)

**Scope:** Fix only the 4 stub entries (šġl 2, šġl 3, žġl 1, žġl 2)

**Parser changes:**

1. Fix case-sensitivity bug in `is_cross_ref` regex (line 115)
2. Add cross-reference extraction in `extract_root_and_etymology()`
3. Extract translation from stub entries

**Code changes:**

```python
# Line 115: Fix case-sensitivity
is_cross_ref = bool(re.search(r'→|see\s+[ʔʕbčdfgġǧhḥklmnpqrsṣštṭvwxyzžḏṯẓāēīūə]', text, re.IGNORECASE))

# New function: extract_cross_reference()
def extract_cross_reference(self, text):
    """Extract cross-reference target from stub entries"""
    # Pattern: 'translation' see TARGET
    match = re.search(r"['']\s*see\s+([ʔʕbčdfgġǧhḥklmnpqrsṣštṭvwxyzžḏṯẓāēīūə]+\s*\d*)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None
```

**Pros:**

- ✅ Minimal code changes
- ✅ Fixes user-reported issue
- ✅ No schema changes needed

**Cons:**

- ❌ Ignores 29 forward references (→ pattern)
- ❌ Ignores 48 "see also" references
- ⚠️ Partial solution

### Option B: Comprehensive Fix (All Cross-References)

**Scope:** Parse all 3 patterns (stub, forward, see also)

**Parser changes:**

1. Fix case-sensitivity bug
2. Extract cross-references from stub entries
3. Extract forward references (→) from etymology
4. Optionally extract "see also" references

**Schema changes:**

```typescript
export interface IVerb {
  root: string;
  etymology: IEtymology | null;
  cross_reference: string | string[] | null; // Support multiple targets
  cross_reference_type?: "redirect" | "forward" | "related"; // Optional type
  // ... rest unchanged
}
```

**Frontend changes:**

- Update `VerbHeader.vue` to display multiple cross-references
- Add different styling for redirect vs. related

**Pros:**

- ✅ Comprehensive solution
- ✅ Preserves all cross-reference data
- ✅ Better data structure

**Cons:**

- ❌ Requires schema migration
- ❌ Frontend changes needed
- ⚠️ More complex implementation

### Option C: Hybrid (Stub Redirect + Etymology Preservation)

**Scope:** Fix stub entries fully, preserve → and "see also" in etymology text

**Parser changes:**

1. Fix case-sensitivity bug
2. Extract cross-references from stub entries
3. Leave forward/see-also references in etymology text (current behavior)

**Pros:**

- ✅ Fixes user-reported issue
- ✅ No schema changes
- ✅ Simple implementation
- ✅ Preserves data in readable form

**Cons:**

- ⚠️ Forward references not machine-readable

---

## Recommended Solution: Option C (Hybrid)

**Rationale:**

- **User priority:** Fix the 4 missing stub entries
- **Data preservation:** Keep → and "see also" in etymology (human-readable)
- **Minimal risk:** No breaking changes to schema/frontend
- **Future-proof:** Can upgrade to Option B later if needed

**Implementation steps:**

1. **Fix parser regex (line 115):**

   ```python
   is_cross_ref = bool(re.search(r'→|see\s+[ʔʕbčdfgġǧhḥklmnpqrsṣštṭvwxyzžḏṯẓāēīūə]', text, re.IGNORECASE))
   ```

2. **Add cross-reference extraction:**

   ```python
   def extract_cross_reference(self, text):
       """Extract cross-reference target from stub entries"""
       # Pattern: 'translation' see TARGET
       match = re.search(r"[''ʻʼ]\s*see\s+([ʔʕbčdfgġǧhḥklmnpqrsṣštṭvwxyzžḏṯẓāēīūə]+\s*\d*)", text, re.IGNORECASE)
       if match:
           return match.group(1).strip()
       return None
   ```

3. **Update extract_root_and_etymology():**

   ```python
   def extract_root_and_etymology(self, text, next_para_text=None):
       text = text.strip()
       root_match = re.match(r'^([ʔʕbčdfgġǧhḥklmnpqrsṣštṭvwxyzžḏṯẓāēīūə\u0300-\u036F]{2,12}(?:\s+\d+)?)(?:\s|\(|<|$)', text)
       if not root_match:
           return None, None, None

       root = root_match.group(1).strip()

       # Check for cross-reference stub
       cross_ref = self.extract_cross_reference(text)

       # Parse etymology (if not a cross-reference stub)
       etymology = None if cross_ref else self.parse_etymology_full(text, next_para_text)

       return root, etymology, cross_ref
   ```

4. **Update verb creation logic:**

   ```python
   root, etymology, cross_ref = self.extract_root_and_etymology(para.text, next_para_text)
   if root:
       current_verb = {
           'root': root,
           'etymology': etymology,
           'cross_reference': cross_ref,  # Now populated
           'stems': [],
           'idioms': None,
           'uncertain': '???' in para.text
       }
   ```

5. **Test and validate:**

   ```bash
   python3 parser/parse_docx_production.py
   python3 .devkit/scripts/comprehensive_validation.py .devkit/analysis/docx_v2_verbs
   ```

6. **Deploy:**
   ```bash
   cp .devkit/analysis/docx_v2_verbs/*.json server/assets/verbs/
   ```

---

## Expected Results

**Before fix:**

```json
{
  "root": "šġl 2",
  "etymology": null,
  "cross_reference": null,
  "stems": [],
  "idioms": null,
  "uncertain": false
}
```

**After fix:**

```json
{
  "root": "šġl 2",
  "etymology": null,
  "cross_reference": "ǧġl1",
  "stems": [],
  "idioms": null,
  "uncertain": false
}
```

**UI display:**

```
šġl 2
[Cross-reference badge]

See related entry ǧġl1
    (clickable link)
```

---

## Testing Checklist

- [ ] šġl 2 has `cross_reference: "ǧġl1"`
- [ ] šġl 3 has `cross_reference: "ǧġl2"`
- [ ] žġl 1 has `cross_reference: "ǧġl1"`
- [ ] žġl 2 has `cross_reference: "ǧġl2"`
- [ ] UI shows "Cross-reference" badge
- [ ] UI shows clickable link to target verb
- [ ] Clicking link navigates to correct verb
- [ ] Total verb count unchanged (1460 verbs)
- [ ] No other verbs affected (regression test)

---

## Future Enhancements

**If Option B is implemented later:**

1. **Schema update:**

   ```typescript
   cross_reference: string | string[] | null
   cross_reference_type?: 'redirect' | 'forward' | 'related'
   ```

2. **Extract forward references:**
   - Parse "→ TARGET1, TARGET2" from etymology
   - Store as array in cross_reference field

3. **Frontend enhancement:**
   - Display multiple cross-references
   - Different styling for redirect vs. related

4. **Search integration:**
   - Allow searching by cross-reference
   - Show bidirectional links (backlinks)

---

## Files to Modify

1. **Parser:** `parser/parse_docx_production.py`
   - Line 115: Fix case-sensitivity
   - Add `extract_cross_reference()` method
   - Update `extract_root_and_etymology()` return signature
   - Update verb creation logic

2. **No frontend changes needed** (already supports cross_reference field)

3. **No schema changes needed** (field already exists)

---

## Validation

After implementation, run:

```bash
# Check specific verbs
jq '.cross_reference' server/assets/verbs/šġl\ 2.json
jq '.cross_reference' server/assets/verbs/šġl\ 3.json
jq '.cross_reference' server/assets/verbs/žġl\ 1.json
jq '.cross_reference' server/assets/verbs/žġl\ 2.json

# Count verbs with cross-references
find server/assets/verbs -name "*.json" -exec jq -r '.cross_reference // empty' {} \; | wc -l

# Verify UI displays correctly
curl http://localhost:3456/api/verb/šġl%202
```
