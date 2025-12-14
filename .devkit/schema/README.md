# Schema Validation - Summary

**Date:** 2025-12-14
**Reference:** [GitHub Issue #6](https://github.com/evb0110/turoyo-verb-glossary/issues/6)
**Schema:** `/schema/IEntry.ts` (UPDATED)

---

## Files in This Directory

| File                      | Description                                  |
| ------------------------- | -------------------------------------------- |
| **SCHEMA_REVISION_v2.md** | Final schema with clarifications applied     |
| SCHEMA_ANALYSIS.md        | Initial detailed analysis (superseded by v2) |
| PROPOSED_SCHEMA.md        | Initial proposal (superseded by v2)          |
| PROBLEMATIC_ENTRIES.md    | Specific entries that need attention         |
| CROSS_REFERENCES.md       | Cross-reference patterns                     |

---

## Key Decisions

### 1. Detransitive is Part of Stem, Not Separate Stem

**Decision:** Each stem (I, II, III) can have an optional `detransitive` array.

```typescript
interface IStem {
  stemNumber: TStemNumber; // 'I' | 'II' | 'III' only
  transitive: IRow[]; // Main conjugations
  detransitive?: IRow[]; // Optional detransitive part
}
```

**Parser must change:** Currently outputs "Detransitive" as separate stem - this is wrong.

### 2. Etymology Simplified

**Decision:** Keep etymology as plain text with extracted `provenance` for filtering.

```typescript
interface IEtymology {
  provenance?: string; // Arab, Syr, MEA, Kurd, etc.
  text: string; // Full etymology as-is
  notes?: string;
}
```

### 3. Notes at Every Level

**Principle:** Anything that doesn't fit structured fields goes to `notes`.

Every interface now has `notes?: string`:

- IExample
- IExamples
- IRow
- IMeaning
- IStem
- IEtymology
- IIdiom
- IEntry

### 4. TShape Expanded + Normalized

Added shapes found in data:

- `Preterit Transitive`
- `Nomen Actionis`
- `Nomen Patiens`
- `Nomen agentis`

Parser must normalize variants (Preterite→Preterit, etc.)

### 5. Idioms Restructured

```typescript
interface IIdiom {
  text: string;
  translation?: string;
  notes?: string;
}
```

### 6. Cross-References

Field exists: `IEntry.crossReference`. Parser needs to extract `→` patterns.

---

## Schema Updated

The schema file `/schema/IEntry.ts` has been updated to reflect these decisions.

---

## Parser Changes Required

1. **Detransitive handling** - Nest in parent stem, don't create separate stem
2. **Shape normalization** - Map variants to canonical forms
3. **Etymology simplification** - Extract provenance, keep text as-is
4. **Cross-reference extraction** - Find `→` patterns
5. **Notes population** - Put anything that doesn't fit in notes
