"""Small state machine for root → stem → senses/boxes → idioms."""

from collections import Counter
from dataclasses import dataclass, field
import json
from pathlib import Path
import re

from .docx import Text, read_volume
from .examples import parse_example, split_examples

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "source/glossary-docx/2026-10-21"
OUTPUT = REPO / "server/assets/glossary"
CONSONANTS = "ʔʕbčdfgġǧhḥklmnpqrsṣštṭṯvwxyzžḏḍẓḷṛ\u0300-\u036f"
ROOT_TOKEN = rf"[{CONSONANTS}{CONSONANTS.upper()}Хх][{CONSONANTS}х]{{1,7}}"
ROOT = re.compile(rf"^({ROOT_TOKEN}(?:\s*[\d¹²³⁴⁵⁶⁷⁸⁹]+)?)(?=\s*(?:\(|<|$|→|see\b|cf\.|[‘ʻ:,/]))")
ROMAN_ROOT = re.compile(rf"^({ROOT_TOKEN}\s+[IVX]+)(?=\s*(?:\(|:$))")
INLINE_ROOT = re.compile(rf"^([{CONSONANTS}]{{2,8}})(?:\s+(\d+))?\s+(I{{1,3}})\s+(.*)$")
STEM = re.compile(r"^\s*(I{1,3}’?(?: \(or II\?\))?|IV|Pa\.|Af\.|Q|Quadri\w*|Št\.|Šaf\.)(?:\s*:\s*|\.\s*|\s+)")
BARE_STEM = re.compile(r"^\s*(I{1,3}’?|IV|Pa\.|Af\.|Q|Št\.|Šaf\.)\s*:?\s*$")
IDIOMS = re.compile(r"^\s*(?:Idiomatic\s+ph[ra]+ses?|Idioms)\b", re.I)
DETRANS = re.compile(r"^\s*Detransitive\b", re.I)
DETRANS_GLOSS = re.compile(r"^\s*\(Detrans[^)]*\)\s*", re.I)


def is_editorial(text):
    """Positive editorial/citation cues, independent of the text's script."""
    return bool(re.match(
        r"^(?:[→←]|More examples\b|Не уверен\b|Употребляется\b|Значения\b|Занятно\b"
        r"|(?:SL|Shabo|Kfarze):|See(?:\s+also|\s+under)?\b|\[We\b|Two informants\b"
        r"|History of\b|Detr\.\s*Pret\.|[A-Z][a-z]+,\s*[‘ʻ]"
        r"|\S+(?:le|li)(?::|\s.+\bexamples\b)|(?:PrS|M·\s*t)\s+\d+/\d+"
        r"|\([^()]+[<>][^()]+\)$)", text.strip(), re.I))


def entry_id(root):
    return re.sub(r"\s+", "-", root.strip())


def slug(label):
    return re.sub(r"[^\w]+", "-", label.lower()).strip("-") or "unlabelled"


def canonical_label(raw):
    label = re.sub(r"\s+", " ", raw.strip())
    label = re.sub(r"^Detransitive\s+", "", label, flags=re.I)
    key = re.sub(r"[\s.\-–]+", "", label.lower())
    aliases = {
        "preterit": "Preterit", "preterite": "Preterit",
        "preterit1": "Preterit", "preterit2": "Preterit",
        "preteritintransitive": "Preterit Intransitive",
        "preterittransitive": "Preterit", "preteritetransitive": "Preterit",
        "preteritwa": "Preterit-wa", "kopreterit": "ko-Preterit", "kpreterit": "ko-Preterit",
        "infectum": "Infectum", "infeсtum": "Infectum", "infc": "Infectum",
        "infectumwa": "Infectum-wa", "infwa": "Infectum-wa",
        "imperativ": "Imperativ", "imperative": "Imperativ",
        "infinitiv": "Infinitiv", "infinitive": "Infinitiv",
        "partact": "Part act.", "activeparticiple": "Part act.",
        "partpass": "Part. Pass.", "passiveparticiple": "Part. Pass.",
        "pastparticiple": "Part. Pass.", "passparticiple": "Part. Pass.",
        "passptc": "Part. Pass.", "passpart": "Part. Pass.",
        "passivepart": "Part. Pass.", "pastpart": "Part. Pass.",
        "nomenactionis": "Nomen actionis", "actionnoun": "Nomen actionis", "nomenpatiens": "Nomen Patiens",
        "nomenagentis": "Nomen agentis",
    }
    if key in aliases:
        return aliases[key]
    if re.match(r"^Preterit Intran(?:s|is)itive", label, re.I):
        return "Preterit Intransitive"
    if re.match(r"^Infectum-wa\(", label, re.I):
        return "Infectum-wa"
    if re.fullmatch(r"Infectum\s*(?:\(\?+\)|[–-]\s*Transitive)", label, re.I):
        return "Infectum"
    # Editorial qualifications and combined form labels remain visible.
    if re.match(r"^(Preter|Infect|Imper|Infinit|Part\b|Participle|Nomen\b|ko-)", label, re.I):
        return label
    return None


SENSE_NUMBER = re.compile(r"(?<![\w/:.\-])(\d{1,2})(?:\)|\.(?!\d)|-(?!\d))(?=\s|[^\W\d_]|[‘ʻ\"(\[]|$)\s*")


def sense_markers(raw):
    """List numbers outside commentary and explicit references to senses."""
    protected, brackets = set(), []
    candidates = list(SENSE_NUMBER.finditer(raw))
    # A source qualifier can lack its own closing bracket before the next
    # list marker: '(der Regen; 5) laufen' or '(mit ruḥo 2) loose'.
    list_closes = {m.start() + len(m[1]) for m in candidates
                   if (re.search(r";\s*$", raw[:m.start()])
                       or re.search(r"\((?:mit|with)\s+[^()]+\s+$", raw[:m.start()], re.I))
                   and re.match(r"[^\W\d_]", raw[m.end():])}
    for i, char in enumerate(raw):
        # '(1) gloss, (2) gloss' is a source list, not commentary.
        list_open = (char == "(" and re.match(r"\d{1,2}\)", raw[i + 1:])
                     and (i == 0 or raw[i - 1].isspace() or raw[i - 1] in ";,"))
        if char in "([" and not list_open:
            brackets.append((char, i))
        elif char == ")" and i in list_closes:
            continue
        elif brackets and char == {"(": ")", "[": "]"}[brackets[-1][0]]:
            _, start = brackets.pop()
            protected.update(range(start, i + 1))
    markers = []
    for marker in candidates:
        i = marker.start()
        reference = re.search(r"\b(?:gloss(?:es)?|sense(?:s)?|meaning(?:s)?|see|cf\.)\s+"
                              r"(?:\d{1,2}\)\s*(?:and|,)\s*)*\(?$", raw[:i], re.I)
        if i not in protected and not reference:
            markers.append(marker)
    return markers


def senses(raw):
    markers = sense_markers(raw)
    if not markers:
        return [{"n": "1", "gloss": raw.strip()}] if raw.strip() else []
    result = []
    prefix = raw[:markers[0].start()].strip()
    # Several lists omit the literal '1)' but explicitly continue with '2)'.
    # Keep the first gloss as sense 1 rather than folding it into sense 2.
    if (prefix and markers[0][1] != "1" and not re.fullmatch(r"\S+/\S+", prefix)
            and re.search(r"[^\W\d_]", DETRANS_GLOSS.sub("", prefix))):
        result.append({"n": "1", "gloss": prefix})
        prefix = ""
    for i, marker in enumerate(markers):
        end = markers[i + 1].start() if i + 1 < len(markers) else len(raw)
        gloss = raw[marker.end():end].strip()
        # A qualification before 1), e.g. '(Detrans.)', applies to that gloss.
        if i == 0 and prefix:
            gloss = prefix + " " + gloss
        result.append({"n": marker[1], "gloss": gloss})
    return result


@dataclass
class Emission:
    volume: str
    unit: str
    entry: str
    paths: list[tuple]  # (JSON path tuple, optional start, optional end)


@dataclass
class Parsed:
    entries: list[dict] = field(default_factory=list)
    emissions: list[Emission] = field(default_factory=list)
    diagnostics: list[dict] = field(default_factory=list)


class Reader:
    def __init__(self):
        self.result = Parsed()
        self.by_id = {}
        self.entry = self.stem = self.box = None
        self.si = self.bi = None
        self.mode = "root"
        self.detransitive = False
        self.seen_table = False
        self.expect_detransitive_forms = False
        self.correspondence = False
        self.pending = []
        self.volume = ""

    def account(self, unit, *paths):
        self.result.emissions.append(Emission(self.volume, unit.key, self.entry["id"], list(paths)))

    def note(self, unit, stem=False):
        owner = self.stem if stem and self.stem else self.entry
        prefix = ("stems", self.si) if owner is self.stem else ()
        owner["notes"].append(unit.text.strip())
        self.account(unit, (prefix + ("notes", len(owner["notes"]) - 1), None, None))

    def start_entry(self, unit, root, order):
        # Normalize only the identifier of source-attested nonstandard heads.
        # Literal head/root text is retained, including capitals and Cyrillic х.
        normalized_root = (root[0].lower() + root[1:]).translate(str.maketrans("¹²³⁴⁵⁶⁷⁸⁹х", "123456789x"))
        normalized_root = re.sub(r"(?<=\D)(\d+)$", r" \1", normalized_root) if any(c in root for c in "¹²³⁴⁵⁶⁷⁸⁹") else normalized_root
        identifier = entry_id(normalized_root)
        repeated = identifier in self.by_id
        if repeated:
            self.entry = self.by_id[identifier]
            self.note(unit)
            self.result.diagnostics.append({"kind": "repeated-root", "root": root, "volume": self.volume, "unit": unit.key})
        else:
            homonym = re.search(r"(\d+)$", normalized_root)
            self.entry = {"id": identifier, "root": root, "homonym": int(homonym[1]) if homonym else None,
                          "head": unit.text.strip(), "crossRefs": [], "notes": [], "stems": [], "idioms": [],
                          "source": {"volume": self.volume, "order": order}}
            self.by_id[identifier] = self.entry
            self.result.entries.append(self.entry)
            self.account(unit, (("head",), None, None))
        self.stem = self.box = None
        self.mode, self.detransitive, self.seen_table = "root", False, False
        self.correspondence = False
        for volume, pending in self.pending:
            current_volume, self.volume = self.volume, volume
            self.note(pending)
            self.volume = current_volume
        self.pending.clear()

    def start_stem(self, unit, label, content_start, account=True):
        count = sum(s["stem"] == label for s in self.entry["stems"])
        identifier = f"{self.entry['id']}.{label}" + (f"~{count + 1}" if count else "")
        self.stem = {"id": identifier, "stem": label, "forms": "", "senses": [], "sensesRaw": "",
                     "detransitiveSenses": [], "detransitiveSensesRaw": None, "boxes": [], "notes": []}
        self.entry["stems"].append(self.stem)
        self.si = len(self.entry["stems"]) - 1
        self.box, self.mode, self.detransitive, self.seen_table = None, "stem", False, False
        self.correspondence = False
        if account:
            # Retain the literal heading, including its marker and punctuation.
            self.note(unit, stem=True)
        self.sense_sections = {"senses": (0, 0), "detransitiveSenses": (0, 0)}
        self.mixed_detransitive = False
        tail = unit.text[content_start:]
        inline_detransitive = re.match(r"\s*Detransitive\s+", tail, re.I)
        if inline_detransitive:
            self.detransitive = True
            content_start += inline_detransitive.end()
            tail = unit.text[content_start:]
        first = re.search(r"\S", tail)
        if not first:
            return
        start = content_start + first.start()
        # Base forms are the leading italic run(s); roman commentary/glosses
        # on the same line must not leak into forms.
        end = start
        if unit.italic and unit.italic[start]:
            text = unit.text
            while end < len(text) and text[end] != "\n":
                if end > start and re.match(r"(?:More examples\b|Не уверен\b|Употребляется\b)", text[end:]):
                    break
                if (text[end].isalpha() and not unit.italic[end]) or text[end] in "‘ʻ\"":
                    break
                if text[end] == "(":
                    # A bracket opened after the forms ('maḥəlla/maḥilo (f.) = mqaḥamla/mqaḥmo',
                    # 'rʕele (alt. raʕi)/roʕe') belongs to them up to its closing bracket on the
                    # same line, roman or not. Without one, or after 'forms:', it starts the rest.
                    close = text.find(")", end)
                    line_end = text.find("\n", end)
                    if close < 0 or (0 <= line_end < close) or text[start:end].rstrip().endswith(":"):
                        break
                    end = close
                end += 1
            # 'maḥəlla/maḥilo (f.) = mqaḥamla/mqaḥmo' equates two sets of forms; the second is roman.
            if text[start:end].rstrip().endswith("="):
                end = len(text) if text.find("\n", end) < 0 else text.find("\n", end)
        else:
            form = re.match(r"[^\s/]+\s*/\s*\S+(?:\s*//\s*[^\s/]+\s*/\s*\S+)*|[^\s/]+", unit.text[start:])
            token = form[0] if form else ""
            # A few headings are gloss-only ('II: breathe').
            if "/" in token or any(c in token for c in "əәǝāēīūʕʔḏḥṭṣšġǧ") or re.match(r"m\w+le\b", token):
                end = start + len(token)
                # Unformatted space-separated base forms are rare but explicit.
                second = re.match(r"\s+(m[^\W\d_]+)(?=\s|$)", unit.text[end:])
                if "/" not in token and second:
                    end += second.end()
        self.stem["forms"] = unit.text[start:end].strip()
        # 'mfaradle/mfarad: (trans.) to crumble': after a colon, the rest is the meaning, bracket or not.
        gloss_follows = self.stem["forms"].endswith(":")
        if gloss_follows:
            self.stem["forms"] = self.stem["forms"][:-1].rstrip()
        rest = unit.cut(end)
        # Some inserted headers put the stem marker after the slash forms.
        trailing_marker = re.match(rf"\s*{re.escape(label)}\s+", rest.text)
        if trailing_marker:
            rest = rest.cut(trailing_marker.end())
        if rest.text.strip():
            if is_editorial(rest.text):
                return  # Editorial requests remain in the literal heading note.
            lexical_parenthesis = re.match(r"\s*\(to\s+", rest.text)
            if not gloss_follows and not lexical_parenthesis and rest.text.lstrip().startswith(("(", "SL ", "Kfarze")):
                # Already retained verbatim as part of the heading note.
                return
            self.add_senses(rest, account=False)

    def append_sense_text(self, raw, detransitive):
        raw_key = "detransitiveSensesRaw" if detransitive else "sensesRaw"
        list_key = "detransitiveSenses" if detransitive else "senses"
        old = self.stem[raw_key] or ""
        start = len(old) + (1 if old else 0)
        self.stem[raw_key] = old + ("\n" if old else "") + raw
        section_start, sense_count = self.sense_sections[list_key]
        self.stem[list_key] = self.stem[list_key][:sense_count] + senses(self.stem[raw_key][section_start:])
        return (("stems", self.si, raw_key), start, start + len(raw))

    def add_senses(self, unit, account=True):
        raw = unit.text.strip()
        # Explicit editorial requests can follow a lexical list in the same
        # paragraph. Move that suffix with its own ordered coverage address.
        editorial = re.search(r"\s*-\s*(?:no examples\b|перенесена\b)", raw, re.I)
        gloss = raw[:editorial.start()].rstrip() if editorial else raw
        sections = [(0, self.detransitive)]
        for marker in sense_markers(gloss):
            detransitive = self.detransitive or bool(DETRANS_GLOSS.match(gloss[marker.end():]))
            if detransitive != sections[-1][1]:
                sections.append((marker.start(), detransitive))
        paths = []
        for i, (start, detransitive) in enumerate(sections):
            end = sections[i + 1][0] if i + 1 < len(sections) else len(gloss)
            fragment = gloss[start:end].strip()
            if fragment:
                paths.append(self.append_sense_text(fragment, detransitive))
                if detransitive and not self.detransitive:
                    self.mixed_detransitive = True
        if editorial:
            self.stem["notes"].append(raw[editorial.start():].strip())
            paths.append((("stems", self.si, "notes", len(self.stem["notes"]) - 1), None, None))
        if account:
            self.account(unit, *paths)

    def paragraph(self, unit, order):
        text = unit.text.strip()
        if not text:
            return
        detransitive_header = self.expect_detransitive_forms
        self.expect_detransitive_forms = False
        if unit.style == "Heading1":
            if self.entry:
                self.note(unit)
            else:
                self.pending.append((self.volume, unit))
            return
        match = ROMAN_ROOT.match(text) or ROOT.match(text)
        if match:
            self.start_entry(unit, match[1], order)
            embedded = re.compile(STEM.pattern, re.M).search(unit.text, len(match[1]))
            if embedded:
                self.start_stem(unit, embedded[1], embedded.end(), account=False)
            return
        if self.entry is None:
            self.pending.append((self.volume, unit))
            return
        match = STEM.match(unit.text) or BARE_STEM.match(unit.text)
        if match and not re.search(r"[:.]", match[0]) and unit.text[match.end():].strip():
            # The article in 'I kalo ...' and English 'I read ...' are prose.
            # Real colonless headings supply initial base forms or a quoted gloss.
            tail = unit.text[match.end():].lstrip()
            if not re.match(r"(?:\S+/\S+|m\w+(?:\s|$)|[‘ʻ\"])", tail):
                match = None
        if match:
            tail = unit.text[match.end():].strip()
            if (detransitive_header and self.stem and match[1] == self.stem["stem"]
                    and re.fullmatch(r"[^\s/]+/[^\s/]+", tail)):
                self.note(unit, stem=True)
                if not self.stem["forms"]:
                    self.stem["forms"] = tail
                return
            self.start_stem(unit, match[1], match.end())
            return
        # Two newly inserted entries have a stem embedded in their root line.
        inline = INLINE_ROOT.match(text)
        if inline and inline[1] not in self.by_id and inline[1] != self.entry["root"]:
            root = inline[1] + (" " + inline[2] if inline[2] else "")
            self.start_entry(unit, root, order)
            self.start_stem(unit, inline[3], unit.text.index(inline[4]), account=False)
            return
        if IDIOMS.match(text):
            self.note(unit)
            self.mode = "idiom"
            self.correspondence = False
            return
        if DETRANS.match(text):
            self.note(unit, stem=True)
            self.detransitive, self.mode, self.seen_table, self.box = True, "stem", False, None
            self.correspondence = False
            trailing = DETRANS.sub("", text).strip(" :")
            self.expect_detransitive_forms = not trailing
            if self.stem and self.mixed_detransitive:
                old = self.stem["detransitiveSensesRaw"] or ""
                self.sense_sections["detransitiveSenses"] = (
                    len(old) + (1 if old else 0), len(self.stem["detransitiveSenses"]))
                self.mixed_detransitive = False
            if self.stem and trailing and not trailing.startswith(("(", "III")) and "/" not in trailing:
                self.add_senses(Text(trailing), account=False)
            return
        label = canonical_label(text)
        if (self.mode == "idiom" and self.stem and label
                and not re.search(r"[\t\n‘ʻʼ’\"]", text)):
            self.mode = "stem"
            self.start_box(unit, label)
            return
        if self.mode == "idiom":
            self.idiom([unit])
            return
        if self.stem and self.seen_table and label:
            # An explicit heading can introduce a one-cell table, e.g. the
            # Action Noun section following ʔṣr's passive participles.
            self.start_box(unit, label)
            return
        if self.stem and (label or re.fullmatch(r"(?:In)?transitive", text, re.I)):
            self.note(unit, stem=True)
            return
        if not self.stem:
            # Unlabelled base-form lines (fyṭ, mǧq, qwy II) are still stems.
            if re.match(r"\S+/\s*\S+", text):
                tail_stem = re.search(r"\s(I{1,3})\s", text)
                self.start_stem(unit, tail_stem[1] if tail_stem else "I", len(unit.text) - len(unit.text.lstrip()))
                self.result.diagnostics.append({"kind": "implicit-stem", "root": self.entry["root"], "volume": self.volume, "unit": unit.key})
            else:
                self.note(unit)
            return
        if re.match(r"^-?\s*Dear\b", text):
            self.correspondence = True
        if self.correspondence or is_editorial(text):
            self.note(unit, stem=True)
            return
        detransitive_gloss = DETRANS_GLOSS.match(text)
        if (detransitive_gloss and not self.detransitive
                and (not self.seen_table or "?" not in detransitive_gloss[0])):
            self.detransitive = True
            self.seen_table, self.box = False, None
        if not self.seen_table and re.fullmatch(r"[^\s/]+/[^\s/]+", text):
            # A separate forms line is not a definition. The contract has no
            # Detransitive-forms field; retain it in notes without replacing
            # the ordinary forms. An otherwise empty stem can use these forms.
            if not self.stem["forms"]:
                self.stem["forms"] = text
            self.note(unit, stem=True)
            return
        if not self.seen_table:
            self.add_senses(unit)
        else:
            self.note(unit, stem=True)

    def example_cell(self, unit):
        paths = []
        inherited = self.box["examples"][-1]["sense"] if self.box["examples"] else None
        for sense, part in split_examples(unit, inherited):
            if not any(c.isalpha() for c in part.text) or re.fullmatch(r"\s*[A-Z]{1,3}\s*", part.text):
                self.stem["notes"].append(part.text.strip())
                paths.append((("stems", self.si, "notes", len(self.stem["notes"]) - 1), None, None))
                continue
            index = len(self.box["examples"])
            example = parse_example(part, sense, f"{self.box['id']}.{index + 1}")
            self.box["examples"].append(example)
            paths.append((("stems", self.si, "boxes", self.bi, "examples", index, "raw"), None, None))
        self.account(unit, *paths)

    def idiom(self, cells):
        index = len(self.entry["idioms"])
        raw, offsets = "", []
        for cell in cells:
            if not cell.text.strip():
                continue
            start = len(raw) + (1 if raw else 0)
            raw += ("\n" if raw else "") + cell.text.strip()
            offsets.append((cell, start, len(raw)))
        headword = re.match(r"[^‘ʻʼ’:\n]+", raw)
        self.entry["idioms"].append({"id": f"{self.entry['id']}.idiom.{index + 1}", "raw": raw,
                                     "headword": headword[0].strip() if headword and canonical_label(headword[0]) is None else None})
        for cell, start, end in offsets:
            self.account(cell, (("idioms", index, "raw"), start, end))

    def start_box(self, unit, label):
        raw_label = unit.text.strip()
        detransitive = self.detransitive or bool(DETRANS.match(raw_label))
        base = f"{self.stem['id']}.{'d' if detransitive else 't'}.{slug(label)}"
        count = sum(b["id"] == base or b["id"].startswith(base + "~") for b in self.stem["boxes"])
        identifier = base + (f"~{count + 1}" if count else "")
        self.box = {"id": identifier, "label": label, "rawLabel": raw_label,
                    "detransitive": detransitive, "examples": []}
        self.stem["boxes"].append(self.box)
        self.bi = len(self.stem["boxes"]) - 1
        self.account(unit, (("stems", self.si, "boxes", self.bi, "rawLabel"), None, None))

    def table(self, rows):
        self.expect_detransitive_forms = False
        self.correspondence = False
        for cells in rows:
            if not any(c.text.strip() for c in cells):
                continue
            # Physical OOXML rows can have several empty cells before the
            # heading. Keep the real cell/key, without merged-cell aliases.
            first = next(i for i, cell in enumerate(cells) if cell.text.strip())
            cells = cells[first:]
            if self.entry is None:
                self.pending.extend((self.volume, c) for c in cells if c.text.strip())
                continue
            if self.mode == "idiom":
                self.idiom(cells)
                continue
            if self.stem is None:
                for cell in cells:
                    if cell.text.strip():
                        self.note(cell)
                continue
            self.seen_table = True
            if len(cells) == 1:
                if self.box:
                    self.example_cell(cells[0])
                else:
                    self.note(cells[0], stem=True)
                continue
            label_cell, *example_cells = cells
            raw_label = label_cell.text.strip()
            label = canonical_label(raw_label)
            if label:
                self.start_box(label_cell, label)
            elif raw_label:
                # Working correspondence inserted into tables is editorial text.
                for cell in cells:
                    if cell.text.strip():
                        self.note(cell, stem=True)
                self.result.diagnostics.append({"kind": "unparsed-table-row", "root": self.entry["root"], "volume": self.volume, "unit": label_cell.key})
                continue
            if self.box:
                for cell in example_cells:
                    if cell.text.strip():
                        self.example_cell(cell)
            else:
                for cell in example_cells:
                    if cell.text.strip():
                        self.note(cell, stem=True)

    def finish(self):
        roots = {e["id"] for e in self.result.entries}
        aliases = {alias: root for root in sorted(roots) for alias in (root.replace("-", " "), root.replace("-", ""))}
        target_pattern = re.compile("(?:" + "|".join(re.escape(a) for a in sorted(aliases, key=len, reverse=True)) + r")(?![\w\u0300-\u036f])")
        for entry in self.result.entries:
            refs = []
            paragraphs = [entry["head"], *entry["notes"], *(n for s in entry["stems"] for n in s["notes"])]
            for paragraph in paragraphs:
                for match in re.finditer(r"(?:\bsee(?:\s+(?:also|under))?|also\s+sieh|\bsieh|\bcf\.|→)\s*([^;()]+)", paragraph, re.I):
                    target = match[1].strip()
                    found = target_pattern.match(target)
                    while found:
                        root = aliases[found[0]]
                        if root != entry["id"] and root not in refs:
                            refs.append(root)
                        separator = re.match(r"\s*(?:,|\band\b)\s*", target[found.end():], re.I)
                        found = target_pattern.match(target, found.end() + separator.end()) if separator else None
            entry["crossRefs"] = refs
        return self.result


def parse_volumes(source=SOURCE):
    reader = Reader()
    paths = sorted(Path(source).glob("*.docx"))
    if not paths:
        raise ValueError(f"No DOCX volumes in {source}")
    for path in paths:
        reader.volume = path.name
        # Each Word volume is independent: a leading orphan stem must not be
        # attached to the last root of the previous volume.
        reader.entry = reader.stem = reader.box = None
        blocks, annotations = read_volume(path, include_notes=True)
        used_notes = set()

        def attach_note(key):
            if key in used_notes:
                return
            used_notes.add(key)
            for block in annotations.get(key, []):
                units = [block] if isinstance(block, Text) else [c for row in block for c in row]
                for unit in units:
                    if unit.text.strip():
                        if reader.entry:
                            reader.note(unit, stem=True)
                        else:
                            reader.pending.append((reader.volume, unit))

        for order, block in enumerate(blocks, 1):
            if isinstance(block, Text):
                reader.paragraph(block, order)
            else:
                reader.table(block)
            units = [block] if isinstance(block, Text) else [c for row in block for c in row]
            for unit in units:
                for key in unit.references:
                    attach_note(key)
        for key in sorted(annotations.keys() - used_notes):
            attach_note(key)
    if reader.pending:
        raise ValueError("Source ends with unassigned material")
    return reader.finish()


def gloss_preview(entry):
    """The first sense; for an entry without senses, its cross-reference or the rest of its heading."""
    glosses = [sense["gloss"] for s in entry["stems"] for sense in (s["senses"] or s["detransitiveSenses"])]
    if glosses:
        return glosses[0]
    rest = re.sub(rf"^{re.escape(entry['root'])}(\s+\d+)?", "", entry["head"]).strip()
    if entry["crossRefs"] and re.match(r"(→|see\b|sieh\b)", rest):
        return "see " + ", ".join(ref.replace("-", " ") for ref in entry["crossRefs"])
    return rest


def index_record(entry):
    return {"id": entry["id"], "root": entry["root"], "homonym": entry["homonym"],
            "stems": [{"stem": s["stem"], "forms": s["forms"]} for s in entry["stems"]],
            "glossPreview": gloss_preview(entry),
            "exampleCount": sum(len(b["examples"]) for s in entry["stems"] for b in s["boxes"]),
            "volume": entry["source"]["volume"]}


def write_glossary(parsed, output=OUTPUT):
    output = Path(output)
    (output / "entries").mkdir(parents=True, exist_ok=True)
    identifiers = {e["id"] for e in parsed.entries}
    for stale in (output / "entries").glob("*.json"):
        if stale.stem not in identifiers:
            stale.unlink()
    for entry in parsed.entries:
        (output / "entries" / f"{entry['id']}.json").write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "index.json").write_text(json.dumps([index_record(e) for e in parsed.entries], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def summary(entries):
    stems = [s for e in entries for s in e["stems"]]
    boxes = [(s, b) for s in stems for b in s["boxes"]]
    examples = [x for _, b in boxes for x in b["examples"]]
    mismatches = []
    for stem, box in boxes:
        valid = {sense["n"] for sense in stem["detransitiveSenses" if box["detransitive"] else "senses"]}
        mismatches.extend(x["id"] for x in box["examples"] if x["sense"] is not None and x["sense"] not in valid)
    return {"entries": len(entries), "stems": len(stems),
            "senses": sum(len(s["senses"]) for s in stems),
            "detransitiveSenses": sum(len(s["detransitiveSenses"]) for s in stems),
            "boxes": len(boxes), "examples": len(examples),
            "examplesWithUnknownSense": len(mismatches),
            "examplesWithoutTranslation": sum(x["translation"] is None for x in examples),
            "refsByKind": dict(sorted(Counter(r["kind"] for x in examples for r in x["refs"]).items())),
            "unknownSenseExampleIds": mismatches}
