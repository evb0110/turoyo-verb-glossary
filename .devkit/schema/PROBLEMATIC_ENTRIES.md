# Problematic Entries - Schema Mismatches

This document lists specific entries that don't fit cleanly into the proposed schema, requiring special handling.

---

## 1. Multiple Etymologies (24 entries)

These entries have 2+ etymologies connected by a relationship ("also" or "and").

### Examples:

**šyk** - 2 etymons, relationship='also'

```json
{
  "etymons": [
    { "notes": "see DJBA 1118 šwk 'to attach, connect',", "raw": "..." },
    { "raw": "metaphorically" }
  ],
  "relationship": "also"
}
```

**Issue:** Second etymon is just a note, not a full etymology.

---

**ʕry** - 2 etymons, relationship='and'

```json
{
  "etymons": [
    {
      "source": "MEA",
      "source_root": "ʕry",
      "reference": "SL 1138",
      "meaning": "to seize..."
    },
    { "raw": "< MEA ʕry (Af.) cf. SL 1138: to breakfast" }
  ]
}
```

**Issue:** Second etymon is raw text pointing to same source but different meaning.

---

**mrd** - 2 etymons, relationship='and'

```json
{
  "etymons": [
    {
      "source": "Arab.",
      "source_root": "mrd",
      "reference": "Lane 2705",
      "meaning": "to steep sth. in water"
    },
    {
      "source": "mash",
      "notes": "it with hand, so as to soften it; to soak in water"
    }
  ]
}
```

**Issue:** Second etymon is continuation of first (broken parsing).

---

### Complete list:

| Root  | Etymon Count | Relationship |
| ----- | ------------ | ------------ |
| šyk   | 2            | also         |
| lyd   | 2            | also         |
| ʕry   | 2            | and          |
| dġy   | 2            | also         |
| ltm   | 2            | also         |
| mrd   | 2            | and          |
| prqʕ  | 2            | also         |
| qrš 2 | 2            | also         |
| thth  | 2            | and          |
| frʕ 1 | 2            | also         |
| gdy   | 2            | also         |
| dyq 1 | 2            | also         |
| ḥwy 1 | 2            | also         |
| rwq 2 | 2            | also         |
| nǧr   | 2            | also         |
| ʕzy   | 2            | also         |
| qwm   | 2            | and          |
| bny 2 | 2            | also         |
| sry   | 2            | also         |
| ʕrk   | 2            | also         |
| ġby 1 | 2            | also         |
| ḥqq   | 2            | also         |
| ṭly 1 | 2            | also         |
| ṭrš   | 2            | also         |

---

## 2. Raw-Only Etymologies (105+ entries)

These entries have etymology text that couldn't be parsed into structured fields.

### Unknown etymologies:

| Root  | Etymology   |
| ----- | ----------- |
| nrnr  | unknown 800 |
| hrdl  | unknown 778 |
| kmč   | unknown 229 |
| brd 2 | unknown     |
| čnčr  | unknown 772 |
| vrvn  | unknown 793 |

### Complex unparsed etymologies:

| Root   | Raw Etymology                                                            |
| ------ | ------------------------------------------------------------------------ |
| mġl    | maġal 'Viehpferch auf dem Feld', cf. jl 16.6 < Kurd. meġel cf. Ku 518... |
| ʕtm    | cf. Kinderib ʕtm, Jastrow 2005: dunkel werden; Arab. Syr. ʕtm...         |
| šġl 1  | cf. Arab. šġl, Wehr 660-661: beschäftigen                                |
| blš 2  | cf. Kinderib blš II, Jastrow 2005 18: anfangen; Anat. blš II...          |
| nwhr 1 | cf. MEA SL 893 nhm, SL 892 nhg, JPA 343 nhq unknown                      |

---

## 3. Uncertain Entries (8 entries)

Flagged as uncertain in the data:

| Root | Notes     |
| ---- | --------- |
| tfq  | Uncertain |
| ḥyṣl | Uncertain |
| dbr  | Uncertain |
| mḥt  | Uncertain |
| šrbṭ | Uncertain |
| mqḏ  | Uncertain |
| tfk  | Uncertain |
| šrʕ  | Uncertain |

---

## 4. Unusual Conjugation Shapes

### Shapes with newlines (malformed):

| Root  | Shape                    |
| ----- | ------------------------ |
| hwy 2 | `Preterit\nIntransitive` |
| ṣly   | `Preterite\nTransitive`  |

### Variant spellings:

| Root  | Shape      | Should Be |
| ----- | ---------- | --------- |
| brm   | Infinitive | Infinitiv |
| brx   | Imperative | Imperativ |
| brx   | Infinitive | Infinitiv |
| ʕwǧ   | Imperative | Imperativ |
| fhm   | Imperative | Imperativ |
| qlʕ 2 | Infinitive | Infinitiv |
| plpx  | Preterite  | Preterit  |
| ḥṣr 1 | Preterite  | Preterit  |
| šlṭ   | Preterite  | Preterit  |
| gmbl  | Preterite  | Preterit  |

### Latin grammatical terms (add to schema):

| Root | Shape          |
| ---- | -------------- |
| ʕmḏ  | Nomen Actionis |
| ʕrṭ  | Nomen Actionis |
| hlx  | Nomen Actionis |
| twr  | Nomen Patiens  |
| ǧbr  | Nomen Patiens  |
| lwš  | Nomen Patiens  |
| snq  | Nomen Patiens  |

---

## 5. Complex Idioms

Idioms containing stem references, notes, or uncertainty markers:

### With stem references:

```
nkt: "III: mankatle/mankət (Hierher? Etymology?)"
qwy: "qwy II:"
tkrm: "tks (< tukkāsā SL 517)\n\nII: mtakasle/mtakas\n\nto prepare;"
```

### With notes:

```
kmč: "notes: A ftile du gelo bu rabәʕ mәd konәšfi..."
```

### With uncertainty (???):

```
nfq: "...zum Tode verurteilen???"
ṭrṣ: "wälzen ???"
wdʕ: "sich verabschieden; 2) see off (тот же корень???)"
tlf: "umkommen, fallen; 2) zerstören (trans.) ???"
mṭy 1: "ʕayno maṭyo/məṭyo 'sehen' ???..."
hyw 1: "obe/hule darbo 'allow, let go' (???)..."
tly: "tole/tlele i=ʕawḏ̣iye 'entgelten' ???..."
sym: "soyəm/səmle nuqṣaniye '...допускать ошибку???'"
ṣfy: "zu Ende sein...; 2) geraten (???)"
dlq: "Idiomatic phrases (???)"
```

---

## 6. Stem-Level Glosses (80 entries)

Entries where stems have label_raw field containing glosses, dialect notes, or other annotations:

### Dialect annotations:

| Root  | Stem | Label              |
| ----- | ---- | ------------------ |
| ngl 2 | II   | / mnagal (Kfarze)  |
| plpx  | II   | (Kfarze)           |
| lṣy 1 | I    | (Ilyas: laṣi/loṣe) |

### Free-text glosses:

| Root  | Stem         | Gloss                                         |
| ----- | ------------ | --------------------------------------------- |
| rqʕ   | III          | (to have (someone) sew or stitch (something)) |
| qbḏ   | I            | 'to grasp, clasp'                             |
| gvz   | Detransitive | To roll around, wallow                        |
| dfn   | Detransitive | begraben werden                               |
| qsd   | Detransitive | sich begeben                                  |
| dmr   | Detransitive | staunen                                       |
| hwy 3 | Detransitive | to get soaked in moisture                     |
| ġšm   | Detransitive | sich verändern                                |

### Labile verbs:

| Root | Stem | Label            |
| ---- | ---- | ---------------- |
| gvz  | II   | mәgavaz (labile) |

### Section headers (misparsed):

| Root  | Stem         | Label             |
| ----- | ------------ | ----------------- |
| flt   | Detransitive | Idiomatic Phrases |
| nsf   | I            | More examples     |
| mṭy 1 | Detransitive | Idiomatic phrases |

### Cross-references:

| Root | Stem         | Label       |
| ---- | ------------ | ----------- |
| ʕzz  | Detransitive | ʕžl → ʕǧl   |
| npʕ  | III          | See nfʕ III |

### Uncertainty:

| Root  | Stem | Label                                                               |
| ----- | ---- | ------------------------------------------------------------------- |
| šyl 2 | III  | Не уверен в правильности формы (Russian: "Not sure about the form") |
| ṣyd   | II   | (??? < denom. Turoyo ṣaydo...)                                      |

---

## 7. Entries Without Etymology (198 entries)

Sample of entries missing etymology entirely:

| Root  | Notes        |
| ----- | ------------ |
| dwy   | No etymology |
| ngl 2 | No etymology |
| dwlb  | No etymology |
| mǧq   | No etymology |
| rqʕ   | No etymology |
| ǧkǧk  | No etymology |
| hbṭ   | No etymology |
| ṭġmġ  | No etymology |
| zyr 2 | No etymology |
| tʕn   | No etymology |

**Note:** These may be native Turoyo words without known etymologies, or the etymology simply wasn't included in the source.

---

## Recommended Actions

### Parser Fixes Needed:

1. **Normalize shape names** - Remove newlines, standardize spelling
2. **Fix broken multi-etymon parsing** - mrd shows continuation as separate etymon
3. **Detect section headers in label_raw** - "Idiomatic Phrases" should not be a gloss
4. **Extract uncertainty markers** - "???" should go to notes field

### Schema Additions:

1. Add `'Detransitive'` to TStemNumber
2. Add `Nomen Actionis`, `Nomen Patiens`, `Nomen agentis` to TShape
3. Add `uncertain` field to IEntry
4. Add `gloss` and `dialectNotes` to IStem
5. Support etymology arrays with relationship

### Data Quality Issues:

1. Russian notes mixed with German/English
2. Cyrillic characters in otherwise Latin text
3. Inconsistent uncertainty marking (???, ?, parenthetical questions)
