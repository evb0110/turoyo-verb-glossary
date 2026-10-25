"""Prove coverage against saved JSON, independently extracting every source unit.

The reader supplies field addresses, not a cached source-text archive. The audit
reopens the DOCX and the emitted entry files, reconstructs every paragraph/cell
from those fields, and fails on missing, repeated, or unequal source units.
Only whitespace is ignored. Punctuation, sense markers and spelling must match.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import unicodedata
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from .parse import OUTPUT, SOURCE, index_record, parse_volumes

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def normalized(text):
    return re.sub(r"\s+", "", unicodedata.normalize("NFC", text))


def source_units(path):
    """Independent extraction: no formatting reader or example splitting."""
    def text(element):
        return "".join(n.text or "" if n.tag == W + "t"
                       else {W + "tab": "\t", W + "br": "\n", W + "cr": "\n",
                             W + "noBreakHyphen": "\u2011", W + "softHyphen": "\u00ad"}.get(n.tag, "")
                       for n in element.iter())

    with ZipFile(path) as archive:
        body = ET.fromstring(archive.read("word/document.xml")).find(W + "body")
        containers = [("", body)]
        for kind in ("footnotes", "endnotes", "comments"):
            name = f"word/{kind}.xml"
            if name in archive.namelist():
                containers.extend((f"{kind}.{note.get(W + 'id')}.", note) for note in ET.fromstring(archive.read(name)))
    for prefix, container in containers:
        for bi, element in enumerate(container):
            if element.tag == W + "p":
                yield f"{prefix}p{bi}", text(element)
            elif element.tag == W + "tbl":
                for ri, row in enumerate(element.findall(W + "tr")):
                    for ci, cell in enumerate(row.findall(W + "tc")):
                        yield f"{prefix}t{bi}.r{ri}.c{ci}", "\n".join(text(p) for p in cell.iter(W + "p"))


def field_value(entry, address):
    path, start, end = address
    value = entry
    for part in path:
        value = value[part]
    assert isinstance(value, str), f"Non-string coverage field: {path}"
    return value[start:end]


def keys(value, expected):
    assert set(value) == set(expected.split()), f"Contract keys differ: {set(value)}"


def audit(source=SOURCE, output=OUTPUT):
    parsed = parse_volumes(source)
    output = Path(output)
    entries = {e["id"]: json.loads((output / "entries" / f"{e['id']}.json").read_text(encoding="utf-8")) for e in parsed.entries}
    emissions = {}
    for emission in parsed.emissions:
        key = (emission.volume, emission.unit)
        assert key not in emissions, f"Repeated source attribution: {key}"
        emissions[key] = emission
    reports, residues = [], []
    for path in sorted(Path(source).glob("*.docx")):
        report = {"volume": path.name, "units": 0, "characters": 0, "covered": 0}
        for key, original in source_units(path):
            original = normalized(original)
            if not original:
                continue
            report["units"] += 1
            report["characters"] += len(original)
            emission = emissions.pop((path.name, key), None)
            emitted = "" if emission is None else normalized("".join(field_value(entries[emission.entry], p) for p in emission.paths))
            if original == emitted:
                report["covered"] += len(original)
            else:
                residues.append({"volume": path.name, "unit": key, "source": original, "emitted": emitted})
        report["coverage"] = round(100 * report["covered"] / report["characters"], 6)
        reports.append(report)
    assert not emissions, f"Emissions without source units: {list(emissions)[:10]}"
    # Also check identifiers, cross-references, index and the actual file set.
    identifiers = []
    for entry in entries.values():
        keys(entry, "id root homonym head crossRefs notes stems idioms source")
        keys(entry["source"], "volume order")
        identifiers.append(entry["id"])
        assert all(r in entries for r in entry["crossRefs"])
        for stem in entry["stems"]:
            keys(stem, "id stem forms senses sensesRaw detransitiveSenses detransitiveSensesRaw boxes notes")
            for sense in stem["senses"] + stem["detransitiveSenses"]:
                keys(sense, "n gloss")
            identifiers.append(stem["id"])
            for box in stem["boxes"]:
                keys(box, "id label rawLabel detransitive examples")
                identifiers.append(box["id"])
                for example in box["examples"]:
                    keys(example, "id sense turoyo translation refs note raw")
                    for field in ("turoyo", "translation", "note"):
                        assert example[field] is None or normalized(example[field]) in normalized(example["raw"]), f"Non-source {field}: {example['id']}"
                    identifiers.append(example["id"])
                    for ref in example["refs"]:
                        keys(ref, "raw kind textId verse")
                        assert ref["kind"] in ("text", "grammar-page", "prs", "jl", "lb", "mm", "luf", "other")
                        assert normalized(ref["raw"]) in normalized(example["raw"])
                        if ref["kind"] == "text":
                            number, verse = re.match(r"(\d+)/(\d+)", ref["raw"]).groups()
                            assert ref["textId"] == f"R{int(number):03d}" and ref["verse"] == int(verse)
                        if ref["kind"] == "prs":
                            assert ref["textId"] is None and ref["verse"] is None
        for idiom in entry["idioms"]:
            keys(idiom, "id raw headword")
            identifiers.append(idiom["id"])
    assert not [i for i, n in Counter(identifiers).items() if n > 1], "Duplicate IDs"
    assert {p.stem for p in (output / "entries").glob("*.json")} == set(entries), "Stale/missing entry files"
    assert json.loads((output / "index.json").read_text(encoding="utf-8")) == [index_record(e) for e in entries.values()], "Index differs from entries"
    return {"volumes": reports, "residue": residues}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--source", default=SOURCE)
    cli.add_argument("--output", default=OUTPUT)
    args = cli.parse_args()
    result = audit(args.source, args.output)
    for report in result["volumes"]:
        print(f"{report['volume']}: {report['covered']:,}/{report['characters']:,} characters ({report['coverage']:.6f}%), {report['units']:,} units")
    print("Residue:", json.dumps(result["residue"], ensure_ascii=False, indent=2))
    raise SystemExit(bool(result["residue"]))


if __name__ == "__main__":
    main()
