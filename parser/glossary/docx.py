"""Read document-order paragraphs and physical cells, including run formatting.

No python-docx merged-cell aliases: each physical OOXML cell is read once.
Text is NFC; tabs and line breaks are retained. Nothing is spell-corrected.
"""

from dataclasses import dataclass
from pathlib import Path
import unicodedata
from xml.etree import ElementTree as ET
from zipfile import ZipFile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


@dataclass
class Text:
    text: str
    italic: tuple[bool, ...] = ()
    bold: tuple[bool, ...] = ()
    style: str = ""
    key: str = ""
    references: tuple[tuple[str, str], ...] = ()

    def cut(self, start=0, end=None):
        return Text(self.text[start:end], self.italic[start:end], self.bold[start:end])


def join(parts, separator="\n"):
    text, italic, bold = [], [], []
    for i, part in enumerate(parts):
        if i:
            text.append(separator)
            italic.extend([False] * len(separator))
            bold.extend([False] * len(separator))
        text.append(part.text)
        italic.extend(part.italic)
        bold.extend(part.bold)
    return Text("".join(text), tuple(italic), tuple(bold), references=tuple(r for p in parts for r in p.references))


def plain(element):
    """Visible OOXML text, also used independently by the round-trip auditor."""
    special = {"tab": "\t", "br": "\n", "cr": "\n",
               "noBreakHyphen": "\u2011", "softHyphen": "\u00ad"}
    return "".join(node.text or "" if node.tag == W + "t"
                   else "" if node.tag == W + "tab" and node.get(W + "pos") is not None
                   else special.get(node.tag.removeprefix(W), "")
                   for node in element.iter())


def _on(properties, name, default=False):
    node = properties.find(W + name) if properties is not None else None
    return default if node is None else node.get(W + "val", "1") not in ("0", "false", "off")


def read_volume(path: Path, include_notes=False):
    with ZipFile(path) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        styles = ET.fromstring(archive.read("word/styles.xml"))
        note_parts = {kind: ET.fromstring(archive.read(f"word/{kind}.xml"))
                      for kind in ("footnotes", "endnotes", "comments") if f"word/{kind}.xml" in archive.namelist()}
    style_nodes = {s.get(W + "styleId"): s for s in styles.findall(W + "style")}

    def formatting(style_id, seen=()):
        if style_id not in style_nodes or style_id in seen:
            return False, False
        node = style_nodes[style_id]
        base = node.find(W + "basedOn")
        italic, bold = formatting(base.get(W + "val"), (*seen, style_id)) if base is not None else (False, False)
        return _on(node.find(W + "rPr"), "i", italic), _on(node.find(W + "rPr"), "b", bold)

    def paragraph(p):
        prop = p.find(W + "pPr/" + W + "pStyle")
        style = prop.get(W + "val", "") if prop is not None else ""
        default_i, default_b = formatting(style)
        chars = []
        for run in p.iter(W + "r"):
            props = run.find(W + "rPr")
            rstyle = props.find(W + "rStyle") if props is not None else None
            inherited_i, inherited_b = formatting(rstyle.get(W + "val")) if rstyle is not None else (default_i, default_b)
            italic, bold = _on(props, "i", inherited_i), _on(props, "b", inherited_b)
            for char in plain(run):
                if chars and unicodedata.combining(char):
                    chars[-1][0] += char
                else:
                    chars.append([char, italic, bold])
        text, italics, bolds = [], [], []
        for cluster, italic, bold in chars:
            cluster = unicodedata.normalize("NFC", cluster)
            text.append(cluster)
            italics.extend([italic] * len(cluster))
            bolds.extend([bold] * len(cluster))
        result = Text("".join(text), tuple(italics), tuple(bolds), style)
        result.references = tuple((kind, ref.get(W + "id"))
                                  for kind, tag in (("footnotes", "footnoteReference"), ("endnotes", "endnoteReference"), ("comments", "commentReference"))
                                  for ref in p.iter(W + tag))
        # Guard against text in an unfamiliar container being silently omitted.
        assert result.text == unicodedata.normalize("NFC", plain(p)), "Unrecognised run container"
        return result

    def blocks(container, prefix=""):
        result = []
        for block_index, node in enumerate(container):
            if node.tag == W + "p":
                value = paragraph(node)
                value.key = f"{prefix}p{block_index}"
                result.append(value)
            elif node.tag == W + "tbl":
                rows = []
                for row_index, row in enumerate(node.findall(W + "tr")):
                    cells = []
                    for cell_index, cell in enumerate(row.findall(W + "tc")):
                        value = join([paragraph(p) for p in cell.iter(W + "p")])
                        value.key = f"{prefix}t{block_index}.r{row_index}.c{cell_index}"
                        cells.append(value)
                    rows.append(cells)
                result.append(rows)
        return result

    body = blocks(document.find(W + "body"))
    annotations = {(kind, note.get(W + "id")): blocks(note, f"{kind}.{note.get(W + 'id')}.")
                   for kind, part in note_parts.items() for note in part}
    return (body, annotations) if include_notes else body
