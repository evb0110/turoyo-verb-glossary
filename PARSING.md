# Parsing Pipeline (DOCX → JSON → App)

This document describes the **authoritative** way verb data is parsed from the DOCX sources and shipped to the Nuxt app. It replaces the old HTML-based pipeline.

If you need to touch the data, follow this file and **do not edit JSON by hand**.

---

## Single Source of Truth

- **Source DOCX files**: `.devkit/new-source-docx/*.docx`  
  (private, not committed; 7 files grouped by letters)
- **Production parser**: `.devkit/scripts/parse_docx_v2_fixed.py`
- **Parser output (combined)**: `.devkit/analysis/docx_v2_parsed.json`
- **Parser output (per-verb)**: `.devkit/analysis/docx_v2_verbs/*.json`
- **Runtime storage (Nitro assets)**: `server/assets/verbs/*.json`

All server API routes read from `server/assets/verbs` via Nitro storage (`useStorage('assets:server')`).

---

## End-to-End Pipeline

From DOCX to deployed JSON:

```text
.devkit/new-source-docx/*.docx
      │
      │  (1) parse_docx_v2_fixed.py
      ▼
.devkit/analysis/docx_v2_parsed.json
.devkit/analysis/docx_v2_verbs/*.json
      │
      │  (2) comprehensive_validation.py
      ▼
[validation reports under .devkit/analysis]
      │
      │  (3) copy into Nitro assets
      ▼
server/assets/verbs/*.json
      │
      │  (4) read in API
      ▼
Nuxt app (search + detail views)
```

### 1. Run the DOCX parser (v2, production)

From the repo root:

```bash
python3 .devkit/scripts/parse_docx_v2_fixed.py
```

This will:

- Read all `.devkit/new-source-docx/*.docx`
- Produce `.devkit/analysis/docx_v2_parsed.json`
- Produce `.devkit/analysis/docx_v2_verbs/*.json` (one file per root)

The v2 parser includes:

- Combining-diacritic fixes (ḏ̣, etc.)
- Homonym numbering
- Contextual root recovery
- Empty-Turoyo and null-etymology fixes

### 2. Run comprehensive validation

Always validate new parser output before deploying:

```bash
python3 .devkit/scripts/comprehensive_validation.py .devkit/analysis/docx_v2_verbs
```

This:

- Compares DOCX parser output against historic baselines
- Checks verb counts, stem counts, example counts
- Verifies etymology extraction completeness (see detailed reports in `.devkit/analysis`)

If validation flags new regressions, fix the parser and re-run; **do not “patch” JSON files**.

### 3. Deploy verb JSONs into Nitro assets

Once validation looks good:

```bash
# Backup current assets
cp -r server/assets/verbs server/assets/verbs.backup_$(date +%Y%m%d%H%M%S)

# Replace with fresh DOCX-based JSON
rm server/assets/verbs/*.json
cp .devkit/analysis/docx_v2_verbs/*.json server/assets/verbs/
```

These files are bundled by Nitro and used by:

- `/api/verb/:root`
- `/api/search/roots`
- `/api/search/fulltext`
- `/api/stats`

---

## Rules and Invariants

**Hard rules:**

- **Never edit JSON directly** in:
  - `server/assets/verbs/*.json`
  - `.devkit/analysis/docx_v2_verbs/*.json`
  - `.devkit/analysis/docx_v2_parsed.json`
- **Always fix the parser**, then regenerate + validate.
- **DOCX is authoritative**.

If you see a data problem:

1. Reproduce it by inspecting the DOCX source under `.devkit/new-source-docx`.
2. Fix the relevant logic in `.devkit/scripts/parse_docx_v2_fixed.py` (or a dedicated helper script if you are doing a temporary experiment).
3. Re-run the full pipeline:
   - `parse_docx_v2_fixed.py`
   - `comprehensive_validation.py`
   - Copy into `server/assets/verbs`.

---

## Where to Learn More

For deeper technical details and historical context:

- `.devkit/analysis/FINAL_PRODUCTION_SUMMARY.md`
- `.devkit/analysis/ETYMOLOGY_100_PERCENT.md`
- `.devkit/analysis/COMPLETE_SUCCESS_SUMMARY.md`
- `.devkit/analysis/PHASE2_CONTEXTUAL_VALIDATION.md`

For overall project guidelines and architecture, see:

- `.claude/CLAUDE.md`
