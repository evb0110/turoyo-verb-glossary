# Etymology Fix: Multiple Etymons Migration Plan

## Executive Summary

**Problem**: Parser only captures FIRST etymon for verbs with multiple etymologies. Data for subsequent etymons is stored but not parsed correctly in the `meaning` field.

**Solution**: Transform existing JSON data to extract and properly structure all etymons (NO HTML re-parsing needed!).

**Impact**: 44 verbs affected (~3% of 1,432 total)

---

## I. PROBLEM ANALYSIS

### The Bug

Current data structure captures ONLY the first etymon:
```json
{
  "etymology": {
    "source": "Arab.",
    "source_root": "bdʔ",
    "reference": "Wehr 69",
    "meaning": "beginnen...; < Arab. bdʔ (II) cf. Wehr 69: voranstellen..."
  }
}
```

**The second etymon is hidden in the `meaning` field!**

### Affected Verbs

**44 verbs** with multiple etymons found using delimiters:
- `; <` (semicolon) - 38 verbs
- `; and <` - 4 verbs
- `; also <` - 3 verbs
- `; or <` - 1 verb
- `) <` (closing paren) - 1 verb

**Examples**:
- `bdy 1`: Arab. bdʔ + Arab. bdʔ (II) - same root, different stems
- `ʔḏy`: Arab. ʔḏy + Arab. ʔḏn - **DIFFERENT roots!**
- `ḥbš`: MEA ḥbš + MEA bḥš + MEA bḥš (Pa.) - **3 etymons!**
- `ṭbʕ`: Arab. ṭbʕ + Classical Syriac ṭbʕ - **cross-family!**

---

## II. NEW DATA STRUCTURE

### TypeScript Types

```typescript
interface Etymon {
  source: string           // "Arab.", "MA", "Classical Syriac", etc.
  source_root?: string     // "bdʔ", "ʔḏn", etc.
  reference?: string       // "Wehr 69", "SL 410-411", etc.
  meaning?: string         // Gloss/translation
  binyan?: string          // "(II)", "(Pa.)", etc.
  raw?: string             // Fallback for unparseable
}

interface Etymology {
  etymons: Etymon[]        // Array of all etymons
  relationship?: 'also' | 'or' | 'and'  // Relationship indicator

  // Deprecated - for backward compatibility
  source?: string
  source_root?: string
  reference?: string
  meaning?: string
}

interface Verb {
  root: string
  etymology: Etymology | null
  // ... rest unchanged
}
```

### Index Changes

```typescript
interface VerbIndexEntry {
  root: string
  etymology_sources: string[]  // Changed from singular!
  // ... rest unchanged
}
```

---

## III. MIGRATION STEPS

### Step 1: Test Transformation (✅ DONE)

```bash
python3 scripts/test-etymology-transform.py
```

All 5 test cases pass:
- `bdy 1`: ✅ 2 etymons (Arab. + Arab.)
- `ʔḏy`: ✅ 2 etymons (Arab. ʔḏy + Arab. ʔḏn)
- `ḥbš`: ✅ 3 etymons (MEA ḥbš + bḥš + bḥš)
- `nʕl`: ✅ 2 etymons (MEA + Arab.)
- `ṭbʕ`: ✅ 2 etymons (Arab. + Classical Syriac)

### Step 2: Backup Current Data

```bash
# Backup verb files
cp -r public/appdata/api/verbs public/appdata/api/verbs.backup.$(date +%Y%m%d)

# Backup indexes
cp public/appdata/api/index.json public/appdata/api/index.json.backup
cp public/appdata/api/search.json public/appdata/api/search.json.backup
cp public/appdata/api/statistics.json public/appdata/api/statistics.json.backup
```

### Step 3: Run Transformation

```bash
python3 scripts/transform-etymology.py
```

**Expected output**:
```
🔄 Transforming etymology data in public/appdata/api/verbs...
  ✓ bdy 1: multiple etymons found
  ✓ ʔḏy: multiple etymons found
  ... (44 total)

✅ Transformation complete!
   Total verbs: 1432
   Multi-etymon: 44
   Transformed: 1432
```

### Step 4: Update TypeScript Types

**File**: `app/composables/useVerbs.ts`

```typescript
// ADD new interfaces (lines 1-20)
export interface Etymon {
  source: string
  source_root?: string
  reference?: string
  meaning?: string
  binyan?: string
  raw?: string
}

// UPDATE Etymology interface
export interface Etymology {
  etymons: Etymon[]
  relationship?: 'also' | 'or' | 'and'

  // Deprecated (keep for compatibility)
  /** @deprecated Use etymons[0].source */
  source?: string
  /** @deprecated Use etymons[0].source_root */
  source_root?: string
  /** @deprecated Use etymons[0].reference */
  reference?: string
  /** @deprecated Use etymons[0].meaning */
  meaning?: string
}

// UPDATE VerbIndexEntry (line 40)
export interface VerbIndexEntry {
  root: string
  etymology_sources: string[]  // Changed from singular!
  // ... rest
}
```

### Step 5: Update Index Builder

**File**: `scripts/build-api.js`

```javascript
// Line 100-108: Update etymology_source to etymology_sources (array)
return {
  root: v.root,
  etymology_sources: v.etymology?.etymons?.map(e => e.source) || [],
  // ... rest
}

// Lines 179-186: Index ALL sources
if (v.etymology?.etymons) {
  for (const etymon of v.etymology.etymons) {
    const src = etymon.source
    if (!searchIndex.etymology_index[src]) {
      searchIndex.etymology_index[src] = []
    }
    if (!searchIndex.etymology_index[src].includes(v.root)) {
      searchIndex.etymology_index[src].push(v.root)
    }
  }
}

// Lines 210-212: Count ALL sources
for (const verb of allVerbs) {
  if (verb.etymology?.etymons) {
    for (const etymon of verb.etymology.etymons) {
      const src = etymon.source || 'Unknown'
      stats.by_etymology[src] = (stats.by_etymology[src] || 0) + 1
    }
  } else {
    stats.by_etymology['Unknown'] = (stats.by_etymology['Unknown'] || 0) + 1
  }
}
```

### Step 6: Rebuild Indexes

```bash
npm run build:api
```

### Step 7: Update UI Components

#### A. Verb Detail Page

**File**: `app/pages/verbs/[root].vue` (lines 38-61)

```vue
<div v-if="verb?.etymology?.etymons?.length" class="space-y-2">
  <h2 class="text-xs font-semibold uppercase tracking-wider text-muted">
    Etymology
  </h2>

  <div
    v-for="(etymon, idx) in verb.etymology.etymons"
    :key="idx"
    class="space-y-1 text-sm"
    :class="{ 'mt-2 pt-2 border-t border-gray-200 dark:border-gray-700': idx > 0 }"
  >
    <p v-if="etymon.source">
      <span class="font-medium">Source:</span>
      {{ etymon.source }}
      <span v-if="etymon.binyan" class="text-xs text-muted">{{ etymon.binyan }}</span>
    </p>
    <p v-if="etymon.source_root">
      <span class="font-medium">Root:</span> {{ etymon.source_root }}
    </p>
    <p v-if="etymon.reference">
      <span class="font-medium">Ref:</span> {{ etymon.reference }}
    </p>
    <p v-if="etymon.meaning" class="text-muted">
      {{ etymon.meaning }}
    </p>
  </div>

  <p v-if="verb.etymology.relationship" class="text-xs text-muted italic mt-2">
    Relationship: {{ verb.etymology.relationship }}
  </p>
</div>
```

#### B. Index Page Filters

**File**: `app/pages/index.vue`

```typescript
// Line 173-175: Update etymology counting
currentResults.forEach(v => {
  const sources = v.etymology_sources || ['Unknown']
  sources.forEach(source => {
    etymCounts.set(source, (etymCounts.get(source) || 0) + 1)
  })
})

// Line 305: Update filter logic
if (filters.value.etymology) {
  result = result.filter(v =>
    v.etymology_sources?.includes(filters.value.etymology) ||
    (!v.etymology_sources?.length && filters.value.etymology === 'Unknown')
  )
}
```

### Step 8: Validate Changes

```bash
# Check multi-etymon verbs are correctly displayed
open http://localhost:3000/verbs/bdy-1
open http://localhost:3000/verbs/ʔḏy
open http://localhost:3000/verbs/ḥbš

# Check etymology filter works
# Filter by "Arab." should show all verbs with Arab. in ANY etymon position
```

### Step 9: Deploy

```bash
# Test locally first
npm run dev

# Build for production
npm run build

# Deploy to Vercel/hosting
npm run deploy
```

---

## IV. VALIDATION CHECKLIST

- [ ] Backup complete
- [ ] Transformation test passes (all 5 cases)
- [ ] Run transformation script
- [ ] Verify 44 verbs have multiple etymons
- [ ] Update TypeScript types
- [ ] Update index builder
- [ ] Rebuild indexes
- [ ] Update UI components
- [ ] Test verb detail pages show all etymons
- [ ] Test etymology filter includes all sources
- [ ] Test search works across all etymons
- [ ] Visual regression check on 10 random verbs
- [ ] Deploy to staging
- [ ] Production deployment

---

## V. EXPECTED OUTCOMES

### Before
- 44 verbs with incomplete etymology data
- Only first etymon searchable/filterable
- Cross-linguistic data hidden

### After
- All etymons properly structured and accessible
- Search/filter works across ALL etymons
- Etymology sources increase from ~15 to ~20 unique values
- UI shows complete linguistic heritage for each verb

### Statistics Change

**Etymology counts** (before → after):
- Total sources: ~15 → ~20
- Arab. entries: ~800 → ~820
- MEA entries: ~400 → ~410
- New: Classical Syriac, Kurd., Turk., etc.

**Data completeness**: 97% → 100%

---

## VI. ROLLBACK PLAN

If issues occur:

```bash
# Restore verb files
rm -rf public/appdata/api/verbs
cp -r public/appdata/api/verbs.backup.YYYYMMDD public/appdata/api/verbs

# Restore indexes
cp public/appdata/api/index.json.backup public/appdata/api/index.json
cp public/appdata/api/search.json.backup public/appdata/api/search.json
cp public/appdata/api/statistics.json.backup public/appdata/api/statistics.json

# Revert code changes
git checkout app/composables/useVerbs.ts
git checkout app/pages/verbs/\[root\].vue
git checkout app/pages/index.vue
git checkout scripts/build-api.js

# Rebuild
npm run build:api
npm run build
```

---

## VII. TIMELINE

- **Backup & Transform**: 15 minutes
- **Code Updates**: 30 minutes
- **Testing**: 30 minutes
- **Deploy**: 15 minutes

**Total**: ~1.5 hours

---

## VIII. KEY INSIGHTS

1. **No HTML re-parsing needed** - all data already exists in JSON!
2. **Transformation preserves backward compatibility** - deprecated fields maintained
3. **Minimal UI changes** - just array iteration instead of single object
4. **Search enhancement** - users can now find verbs by ANY etymon source
5. **Linguistic accuracy** - proper representation of cross-linguistic borrowings

---

## IX. NEXT STEPS AFTER MIGRATION

1. Add etymology notes field for metathesis, uncertainty markers
2. Visual indicators for relationship types (also/or/and)
3. Export etymology data for linguistic research
4. Cross-reference verbs with shared etymons
5. Etymology timeline visualization

---

## Files Created

- `scripts/transform-etymology.py` - Main transformation script
- `scripts/test-etymology-transform.py` - Test suite
- `ETYMOLOGY_FIX_PLAN.md` - This migration plan

## Contact

For questions or issues during migration:
- Check `scripts/test-etymology-transform.py` for test cases
- Review transformation logic in `scripts/transform-etymology.py`
- See examples: bdy 1, ʔḏy, ḥbš, ṭbʕ
