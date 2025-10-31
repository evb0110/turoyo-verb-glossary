# Turoyo Verb Parser

## Production Parser (CURRENT)

**`parse_docx_production.py`** - Production DOCX parser

- **Source:** `.devkit/new-source-docx/*.docx` (7 DOCX files organized by letter)
- **Output:** `server/assets/verbs/*.json` (1,502 individual verb files)
- **Status:** ✅ PRODUCTION - Use this parser

### Usage

```bash
# Parse all DOCX files
python3 parser/parse_docx_production.py

# Output will be in:
# - .devkit/analysis/docx_v2_parsed.json (combined)
# - .devkit/analysis/docx_v2_verbs/*.json (individual files)

# Deploy to production:
rm server/assets/verbs/*.json
cp .devkit/analysis/docx_v2_verbs/*.json server/assets/verbs/
```

### Recent Fixes (2025-11-01)

1. **Missing 'v' bug** - Fixed character class missing 'v' in 7 locations
   - Recovered: gvz, lvlv, vyʕ, glvč, vrvn, vzl, ʕvǧq, ḥvz

2. **Homonym renumbering bug** - Parser now preserves DOCX numbering
   - Fixed: hwy 3 (was being renumbered to hwy 2 and lost)

3. **Stem header detection bug** - Accepts stem markers without formatting
   - Recovered: nfs, pšm, rqʕ, fyx, and 28 more verbs

### Quality Metrics

- **1,502 verbs** (+15 from previous version)
- **1,844 stems**
- **4,941 examples**
- **100% extraction rate** from DOCX source
- **187 DOCX-numbered homonyms preserved**
- **32 verbs recovered via contextual validation**

## Legacy HTML Parser (DEPRECATED)

**`parse_verbs.py`** - Old HTML-based parser

- **Source:** `source/Turoyo_all_2024.html` (single HTML file)
- **Status:** ⚠️ DEPRECATED - Do not use
- **Replaced by:** DOCX parser (better accuracy, formatting-based extraction)

This parser has been superseded by the DOCX parser which provides:

- Better etymology extraction (100% vs 99%)
- Format-based Turoyo detection (italic text)
- Preserved homonym numbering from source
- Contextual validation for incomplete formatting
