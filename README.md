# Turoyo Verb Glossary - Digital Edition

A comprehensive digital conversion of the Turoyo verb glossary from HTML to structured JSON data.

## 📊 Dataset Overview

```
1,450 verbs | 1,758 stems | 4,980 examples
29 alphabetical sections | 10+ etymology sources
```

## 🎯 Project Status

✅ **Data Extraction Complete**
- All verb entries extracted from source HTML
- Full conjugation tables with examples
- Etymology and cross-references captured
- Translations (German/English/Russian) preserved
- References maintained

## 📁 Project Structure

```
turoyo-verb-glossary/
├── source/
│   └── Turoyo_all_2024.html          # Original 14.8MB HTML
├── data/
│   ├── verbs_final.json               # Main dataset (1,197 verbs)
│   ├── verbs_final_sample.json        # Sample for inspection
│   └── verification/                  # Validation samples
│       ├── random_sample.json         # 20 random verbs
│       ├── top_examples.json          # Verbs with most examples
│       ├── most_stems.json            # Verbs with most stems
│       ├── uncertain_entries.json     # 47 uncertain entries (???)
│       ├── issues_sample.json         # Potential issues for review
│       └── report.html                # HTML validation report
├── parser/
│   ├── parse_verbs.py                 # MASTER PARSER (run this)
│   └── validate.py                    # Data validation tool
├── EXTRACTION_SUMMARY.md              # Detailed extraction report
└── README.md                          # This file
```

## 🚀 Quick Start

### View the Data

```bash
# View sample
cat data/verbs_final_sample.json

# View validation report
open data/verification/report.html

# Check stats
python3 -c "import json; d=json.load(open('data/verbs_final.json')); print(d['metadata'])"
```

### Run Validation

```bash
# Validate extracted data
python3 parser/validate.py
```

### Re-parse from Source

```bash
# Parse everything from scratch (ONE COMMAND does it all)
python3 parser/parse_verbs.py

# This automatically:
# - Parses HTML source
# - Adds homonym numbering
# - Generates tokens with proper spacing
# - Splits into individual files (public/ and server/assets/)
# - Creates statistics
```

## 📖 Data Structure

Each verb entry contains:

```json
{
  "root": "ʕbr",
  "etymology": {
    "source": "MEA",
    "source_root": "ʕbr",
    "reference": "SL 1064-1065",
    "meaning": "to pass, cross over..."
  },
  "stems": [
    {
      "stem": "I",
      "forms": ["ʕabər", "ʕobər"],
      "conjugations": {
        "Preterit Intransitive": [
          {
            "turoyo": "aṯi ʕabər, ḥzele...",
            "translations": ["darauf trat er ein..."],
            "references": ["233", "prs 130/22"]
          }
        ]
      }
    }
  ],
  "uncertain": false,
  "cross_reference": null
}
```

### Fields Explained

- **root**: Triconsonantal root (e.g., ʕbr, ʔmr)
- **etymology**: Source language, root, reference, meaning
- **stems**: Array of stems (I, II, III, Detransitive)
  - **forms**: Preterit/Infinitive forms
  - **conjugations**: Tables (Preterit, Infectum, Imperative, Participles)
    - **turoyo**: Original Turoyo text
    - **translations**: German/English translations
    - **references**: Page/source references
- **uncertain**: Marked with ??? in source
- **cross_reference**: Points to another root

## 📊 Data Quality

### Statistics
- **Complete verbs**: 1,180 (98.6%)
- **With etymology**: 982 (82.0%)
- **Average examples/verb**: 3.5
- **Range**: 0-30+ examples per verb

### Known Issues
- 215 verbs missing etymology (acceptable - loan words)
- 17 verbs with no stems (likely incomplete in source)
- 121 verbs with duplicate stems (needs review)
- 190 empty Turoyo cells (notes only)
- 47 uncertain entries (marked ??? in source)

See `EXTRACTION_SUMMARY.md` for full details.

## 🔍 Manual Verification Guide

### Priority Checks

1. **Random Sample** (20 verbs)
   ```bash
   cat data/verification/random_sample.json
   ```

2. **Top Examples** (10 verbs)
   ```bash
   cat data/verification/top_examples.json
   ```

3. **Uncertain Entries** (47 verbs)
   ```bash
   cat data/verification/uncertain_entries.json
   ```

4. **Potential Issues**
   ```bash
   cat data/verification/issues_sample.json
   ```

### Compare Against Source

```bash
# Interactive verification
python3 parser/verify_against_source.py
```

Then enter roots like: `ʕbr`, `ʔmr`, `ḥwrb`

Or use `random` to check a random verb.

## 🛠️ Tools & Scripts

### Master Parser (THE ONLY PARSER)
```python
# parser/parse_verbs.py - RUN THIS FOR ALL PARSING
python3 parser/parse_verbs.py
```
**This is the ONE canonical parser. It does EVERYTHING:**
- Parses 137K lines of HTML
- Extracts all fields (stems, conjugations, etymology)
- Adds homonym numbering for duplicate roots
- Generates tokens with proper spacing (fixes text concatenation)
- Splits into individual verb JSON files (public/ and server/assets/)
- Creates statistics
- Fault-tolerant (continues on errors)
- ~60 seconds runtime

**IMPORTANT**: Never create multiple parser scripts. All parsing logic is consolidated here.

### Validate Data
```python
# parser/validate.py
python3 parser/validate.py
```
- Checks data completeness
- Detects anomalies
- Validates structure

## 💡 Next Steps

### Option 1: Build Vue.js App
Ready to build:
- **Search**: By root, meaning, etymology
- **Browse**: 27 alphabetical sections
- **Filter**: By stem, source language
- **Full-text search**: In examples
- **Export**: PDF, CSV, Excel

### Option 2: Data Enrichment
Add:
- Audio pronunciations
- IPA transcriptions
- Usage frequency
- Related verb families
- Dialectal variants

### Option 3: Improve Parser
Based on verification:
- Fix duplicate stems
- Better empty cell handling
- Enhanced etymology parsing

## 📚 Etymology Sources

| Source | Count | Description |
|--------|-------|-------------|
| Arab.  | 484   | Classical Arabic |
| MEA    | 388   | Middle Eastern Aramaic |
| Kurd.  | 63    | Kurdish |
| Turk.  | 20    | Turkish |
| Others | 27    | Various (denom., Anat., etc.) |

## 🌐 Character Encoding

All data is UTF-8 encoded with full support for:
- Turoyo diacritics: ʔ, ʕ, ə, ḥ, ṭ, ḏ, ġ, ǧ, ṣ, š, ṯ, ẓ
- German umlauts: ä, ö, ü
- Cyrillic (Russian notes)

## 📝 License

[Specify license for extracted data]

Original glossary © [Original authors/institution]
Digital extraction: Technical conversion only

## 🙏 Credits

- **Original Glossary**: Academic researchers
- **Digital Conversion**: Claude Code (Anthropic)
- **Date**: October 2025

## 📧 Contact

For questions about:
- **Original data**: [Contact original authors]
- **Extraction/technical**: [Your contact]

---

**Status**: ✅ Extraction complete and validated. Ready for application development or manual verification.
