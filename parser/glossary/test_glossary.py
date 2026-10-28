"""Focused regressions for the source's structural and citation edge cases."""

import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from xml.sax.saxutils import escape
from zipfile import ZipFile

from .docx import Text, join
from .examples import parse_example, refs_at_start, split_examples
from .parse import REPO, parse_volumes, senses, write_glossary
from .roundtrip import audit


def rich(*parts):
    return join([Text(text, (italic,) * len(text), (False,) * len(text)) for text, italic in parts], "")


class ExamplesTest(unittest.TestCase):
    def test_inconsistent_translation_italics_do_not_hide_an_earlier_example(self):
        for first, translation in ((rich(("maqballe ‘sie stimmten zu’; 23/16 [MT]; ", True)), "sie stimmten zu"),
                                   (rich(("maqballe ‘S", True), ("ie stimmten zu’; ", False), ("23/16 [MT]; ", True)), "Sie stimmten zu")):
            value = join([first, rich(("aḥuno maqballe ", True), ("‘his brother agreed’; 24/97", False))], "")
            examples = [parse_example(p, n, str(i)) for i, (n, p) in enumerate(split_examples(value))]
            self.assertEqual([e["translation"] for e in examples], [translation, "his brother agreed"])

    def test_unformatted_and_inverted_unquoted_translations(self):
        cases = [rich(("U Sargey lo kmaqbal ʕal u+ʕantar does not allow people to offend him", False)),
                 rich(("U Sargey lo kmaqbal ʕal u+ʕantar ", False), ("does not allow people to offend him", True))]
        for value in cases:
            example = parse_example(value, None, "x")
            self.assertEqual(example["turoyo"], "U Sargey lo kmaqbal ʕal u+ʕantar")
            self.assertEqual(example["translation"], "does not allow people to offend him")
        example = parse_example(rich(("Šriṭo i fanerayḏi. My sweater was undone. (Ilyas p.c.)", True)), None, "x")
        self.assertEqual(example["translation"], "My sweater was undone.")

    def test_unquoted_numbers_and_turoyo_suffixes(self):
        value = rich(("qaḏili bu+ḥappәs (Iyas p.c.) ~ I spent 10 months in prison", False))
        self.assertEqual(parse_example(value, None, "x")["translation"], "I spent 10 months in prison")
        value = rich(("i=naqla d-obáʕ-way-no qoyamno ", True), ("‘ich wollte aufstehen’; LB 69;", False))
        self.assertEqual(parse_example(value, None, "x")["translation"], "ich wollte aufstehen")

    def test_unformatted_direct_speech_and_english_passage(self):
        value = rich(("Oṣman-Aġa:\n7. Hiye komar, ‘Lo eli maqṭeli!’\nQaḏila at+tәšʕo+yarḥe.\n"
                      "He swears, he says, ‘No, it was not I who had him killed!’ Nine months passed.", False))
        examples = split_examples(value)
        self.assertEqual(len(examples), 1)
        example = parse_example(examples[0][1], None, "x")
        self.assertIn("‘Lo eli maqṭeli!’", example["turoyo"])
        self.assertTrue(example["translation"].startswith("He swears, he says"))
        self.assertIsNone(parse_example(rich(("məlle ‘Yabo, kalí’.", False)), None, "x")["translation"])

    def test_possessives_and_adjacent_nested_closing_marks(self):
        value = rich(("moṣele ", True), ("‘But Silo marked his cousins’ houses’; 36/105 [MT];", False))
        examples = split_examples(value)
        self.assertEqual(len(examples), 1)
        self.assertEqual(parse_example(examples[0][1], None, "x")["translation"], "But Silo marked his cousins’ houses")
        value = rich(("awnǝ́q ", True), ("ʻer sagt: “säuge deinen Kleinen”", False), ("ʼ; 662; prs 126/1;", True))
        self.assertEqual(len(split_examples(value)), 1)
        self.assertEqual(parse_example(value, None, "x")["translation"], "er sagt: “säuge deinen Kleinen”")

    def test_citation_paragraph_and_new_source_or_verse_prefix(self):
        for prefix in ("29. Məḷḷe", "HD 205. Ilyas. Məḷḷe"):
            value = rich(("1) səmle ", True), ("‘he made it’; 24/46;\n", False),
                         (prefix + "\n", False), ("The man spoke.\n", False))
            examples = [parse_example(p, n, str(i)) for i, (n, p) in enumerate(split_examples(value))]
            self.assertEqual(len(examples), 2)
            self.assertEqual(examples[1]["turoyo"], prefix)
            self.assertEqual(examples[1]["translation"], "The man spoke.")
            self.assertEqual(examples[1]["sense"], "1")
        refs, _ = refs_at_start("LuF I.6-7; p.c. Ido Talay; [LTN];")
        self.assertEqual([r["kind"] for r in refs], ["luf", "other", "other"])
        self.assertEqual(refs_at_start("it is black"), ([], 0))

    def test_parenthetical_translation_and_editorial_notes(self):
        value = rich(("Koḥoṣno ḥasi bu Sargey. (I rely upon Sergey)", False))
        example = parse_example(value, None, "x")
        self.assertEqual(example["turoyo"], "Koḥoṣno ḥasi bu Sargey.")
        self.assertEqual(example["translation"], "I rely upon Sergey")
        for text in ("I do not see the reason to introduce new root ṣlw", "İlyas knows of no infectum"):
            self.assertIsNone(parse_example(rich((text, True)), None, "x")["translation"])
        value = rich(("ḥiko = damned by God, worthy of destruction, cursed: Kəmmo: “Kəšša ḥiko”", False))
        example = parse_example(value, None, "x")
        self.assertEqual(example["translation"], "damned by God, worthy of destruction, cursed")
        self.assertIn("Kəmmo", example["note"])

    def test_implicit_first_sense_and_bracketed_numbered_example(self):
        self.assertEqual(senses("fragen; 2) sich erkundigen;"),
                         [{"n": "1", "gloss": "fragen;"}, {"n": "2", "gloss": "sich erkundigen;"}])
        self.assertEqual(senses("(Detrans.) 2) sich erkundigen;"),
                         [{"n": "2", "gloss": "(Detrans.) sich erkundigen;"}])
        self.assertEqual([s["n"] for s in senses("čīk/mičək\n2) schleichen; 3) entbrennen;")], ["2", "3"])
        self.assertEqual(split_examples(rich(("2)[səmle] ‘he made it’", False)))[0][0], "2")

    def test_italic_quote_with_roman_translation_and_trailing_references(self):
        for citation in ("23/16 [MT]", "24/97 [LTN]", "[ML]", "(Ilyas p.c.)",
                         "JL 19.6.19", "LB 212", "731", "jl 17.6.10", "lj 175"):
            with self.subTest(citation=citation):
                value = rich(("2) maqballe ‘", True), ("sie stimmten zu", False),
                             (f"’; {citation}; fṣiḥ ġálabe ‘", True),
                             ("er freute sich", False), ("’; 24/97; aḥuno maqballe ", True),
                             ("‘his brother agreed’; 26/245", False))
                examples = [parse_example(p, n, str(i)) for i, (n, p) in enumerate(split_examples(value))]
                self.assertEqual([e["translation"] for e in examples], ["sie stimmten zu", "er freute sich", "his brother agreed"])
                self.assertEqual([e["sense"] for e in examples], ["2", "2", "2"])
                self.assertEqual(examples[1]["turoyo"], "fṣiḥ ġálabe")

    def test_numbers_in_translation_timestamps_and_notes_are_not_senses(self):
        value = rich(("2) mṭole ", True), ("‘he married her (cf. 3) above)’ (209 FG 15: 04)\n", False),
                     ("mṭeli i+Meri ", True), ("‘I married Mary’ (Ilyas p.c.)", False))
        examples = [parse_example(p, n, str(i)) for i, (n, p) in enumerate(split_examples(value))]
        self.assertEqual([e["sense"] for e in examples], ["2", "2"])
        self.assertEqual(examples[0]["translation"], "he married her (cf. 3) above)")

    def test_unquoted_translation_paragraph_belongs_to_previous_example(self):
        value = rich(("Lu Sargey čīk bu+baḥar.\n", True),
                     ("He plunged into the sea. (Ilyas p.c.)\n", False),
                     ("aḥuno maqballe ", True), ("‘his brother agreed’; 24/97;\np.c. ST;", False))
        examples = [parse_example(p, n, str(i)) for i, (n, p) in enumerate(split_examples(value))]
        self.assertEqual(len(examples), 2)
        self.assertEqual(examples[0]["translation"], "He plunged into the sea.")
        self.assertEqual(len(examples[1]["refs"]), 2)

    def test_sense_marker_is_not_a_citation(self):
        value = rich(("1) səmle ", True), ("ʻer machteʼ; ", False),
                     ("24/46; 2) səmme ", True), ("ʻsie machtenʼ; prs 143/1;", False))
        examples = [parse_example(p, n, str(i)) for i, (n, p) in enumerate(split_examples(value))]
        self.assertEqual([e["sense"] for e in examples], ["1", "2"])
        self.assertEqual(examples[0]["refs"][0]["textId"], "R024")
        self.assertIsNone(examples[1]["refs"][0]["textId"])
        self.assertEqual("".join(e["raw"] for e in examples).replace(" ", ""), value.text.replace(" ", ""))

    def test_nested_translation_quotes(self):
        value = rich(("mitawḏəʕ ", True), ("‘It becomes evident (lit. ‘gets made known’) that it is old’ 24/46;", False))
        example = parse_example(value, None, "x")
        self.assertEqual(example["translation"], "It becomes evident (lit. ‘gets made known’) that it is old")
        self.assertEqual(example["refs"][0]["verse"], 46)

    def test_unquoted_translation_and_russian_note(self):
        value = rich(("səmle ", True), ("he made it ", False), ("(Ilyas p.c.) Пример отсутствует", True))
        example = parse_example(value, None, "x")
        self.assertEqual(example["translation"], "he made it")
        self.assertEqual(example["note"], "Пример отсутствует")

    def test_direct_speech_inside_translation(self):
        value = rich(("hbīṭ u=qašo ", True), ('ʻ“dort ist die Kerze”, sagte der Pfaffe und starb vor Entsetzenʼ; 126; prs 223/30;', False))
        examples = split_examples(value)
        self.assertEqual(len(examples), 1)
        example = parse_example(examples[0][1], None, "x")
        self.assertEqual(example["translation"], '“dort ist die Kerze”, sagte der Pfaffe und starb vor Entsetzen')
        self.assertEqual([r["kind"] for r in example["refs"]], ["grammar-page", "prs"])

    def test_prs_verse_list_does_not_become_ritter(self):
        refs, _ = refs_at_start("prs 43/21, 22; 24/46-48; 731; JL 19.6.19; [MT]")
        self.assertEqual([r["kind"] for r in refs], ["prs", "text", "grammar-page", "jl", "other"])
        self.assertEqual(refs[0]["raw"], "prs 43/21, 22")
        self.assertIsNone(refs[0]["verse"])
        self.assertEqual(refs[1]["verse"], 46)

    def test_sense_gaps_and_verbatim_punctuation(self):
        self.assertEqual(senses("1) machen; 3) besorgen (???);"),
                         [{"n": "1", "gloss": "machen;"}, {"n": "3", "gloss": "besorgen (???);"}])
        self.assertEqual([s["n"] for s in senses("1)to do; 2)to make;")], ["1", "2"])

    def test_roman_personal_communication_is_not_translation(self):
        value = rich(("səmle (", True), ("İlyas p.c)", False))
        example = parse_example(value, None, "x")
        self.assertIsNone(example["translation"])
        self.assertEqual(example["refs"][0]["kind"], "other")

    def test_equivalence_stays_a_note(self):
        value = rich(("mitәšno ", True), ("‘I do not go’ ", False), ("= hič lo+kuzzí", True))
        examples = split_examples(value)
        self.assertEqual(len(examples), 1)
        self.assertEqual(parse_example(examples[0][1], None, "x")["note"], "= hič lo+kuzzí")


class RoundtripTest(unittest.TestCase):
    def test_real_fields_footnotes_repeated_sections_and_tampering(self):
        def paragraph(text, italic=False, extra=""):
            return f'<w:p><w:r><w:rPr>{"<w:i/>" if italic else ""}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t>{extra}</w:r></w:p>'

        def table(text):
            return '<w:tbl><w:tr><w:tc>' + paragraph("Preterit") + '</w:tc><w:tc>' + paragraph(text) + '</w:tc></w:tr></w:tbl>'

        namespace = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
        body = (paragraph("h\u0323wy (< MEA ḥwy)") + paragraph("II: mḥawele/mḥawe ‘to appear’", True)
                + table("1) mḥawele ʻhe appearedʼ; 24/46; 2)")
                + paragraph("Detransitive") + paragraph("erschienen sein;")
                + table("mḥawyo ʻvisibleʼ; prs 143/1;")
                + paragraph("Action Noun") + paragraph("1) appearing; 2) appearance;")
                + '<w:tbl><w:tr><w:tc>' + paragraph("2) ḥwoyo ‘appearance’; 24/48;") + '</w:tc></w:tr></w:tbl>'
                + paragraph("ḥwy (another source section)") + paragraph("II: mḥawele/mḥawe", True)
                + paragraph("to appear;", extra='<w:footnoteReference w:id="1"/>')
                + paragraph("Idiomatic phrases") + table("mḥawe ʻhe appearsʼ; 24/47;"))
        # All temporary artifacts remain inside the task's ignored virtualenv.
        with TemporaryDirectory(dir=REPO / ".devkit/glossary-parser-venv") as temp:
            root = Path(temp)
            with ZipFile(root / "1.docx", "w") as doc:
                doc.writestr("word/document.xml", f'<w:document {namespace}><w:body>{body}</w:body></w:document>')
                doc.writestr("word/styles.xml", f'<w:styles {namespace}/>')
                doc.writestr("word/footnotes.xml", f'<w:footnotes {namespace}><w:footnote w:id="1">{paragraph("Русская заметка")}</w:footnote></w:footnotes>')
            parsed = parse_volumes(root)
            self.assertEqual(len(parsed.entries), 1)
            entry = parsed.entries[0]
            self.assertEqual(entry["id"], "ḥwy")
            self.assertEqual([s["id"] for s in entry["stems"]], ["ḥwy.II", "ḥwy.II~2"])
            self.assertEqual(entry["stems"][0]["forms"], "mḥawele/mḥawe")
            self.assertEqual(entry["stems"][0]["senses"][0]["gloss"], "‘to appear’")
            self.assertEqual(entry["stems"][0]["boxes"][-1]["label"], "Nomen actionis")
            self.assertEqual(entry["stems"][0]["boxes"][-1]["examples"][0]["sense"], "2")
            self.assertIn("Русская заметка", entry["stems"][1]["notes"])
            self.assertEqual(len(entry["idioms"]), 1)
            write_glossary(parsed, root / "out")
            self.assertEqual(audit(root, root / "out")["residue"], [])
            path = root / "out/entries/ḥwy.json"
            saved = json.loads(path.read_text())
            saved["stems"][0]["boxes"][0]["examples"][0]["raw"] += "LOSS"
            path.write_text(json.dumps(saved, ensure_ascii=False))
            self.assertTrue(audit(root, root / "out")["residue"])


class SourceExamplesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parsed = parse_volumes()
        cls.entries = {e["id"]: e for e in cls.parsed.entries}
        cls.boxes = {b["id"]: b for e in cls.parsed.entries for s in e["stems"] for b in s["boxes"]}

    def test_reported_three_example_passage(self):
        examples = self.boxes["qbl.III.t.preterit"]["examples"]
        for example, beginning in zip(examples[2:5],
                                      ["Der Arme beriet sich mit", "[Der König] freute sich", "Bruder! Ich <…> erkenne"]):
            self.assertTrue(example["translation"].startswith(beginning), example["translation"])
        self.assertEqual([r["raw"] for r in examples[2]["refs"]], ["23/16", "[MT]"])
        self.assertEqual([r["raw"] for r in examples[3]["refs"]], ["24/97", "[MT]"])
        self.assertEqual(len({x["sense"] for x in examples[2:5]}), 1)

    def test_no_embedded_translation_and_citation_before_another_example(self):
        fused = re.compile(r"[ʻ‘][^ʼ’]{3,}[ʼ’]\s*;?\s*(\d|JL|prs|PrS|LB|MM)")
        self.assertEqual([x["id"] for b in self.boxes.values() for x in b["examples"] if fused.search(x["turoyo"])], [])

    def test_unquoted_translation_and_source_numbering(self):
        examples = self.boxes["qbl.III.t.infectum"]["examples"]
        example = next(x for x in examples if x["turoyo"].startswith("U Sargey lo kmaqbal"))
        self.assertEqual(example["translation"], "does not allow people to offend him")
        examples = self.boxes["mṭy-2.I.t.preterit"]["examples"]
        self.assertTrue(all(x["sense"] in ("1", "2") for x in examples))
        self.assertNotIn("11", [s["n"] for s in self.entries["sym"]["stems"][0]["senses"]])
        self.assertEqual(self.entries["ʔḏʕ"]["stems"][0]["detransitiveSenses"], [])

    def test_bracket_after_stem_forms_is_not_a_meaning(self):
        stems = {s["id"]: s for e in self.parsed.entries for s in e["stems"]}
        self.assertEqual(stems["rʕy.I"]["forms"], "rʕele (alt. raʕi)/roʕe")
        self.assertEqual(stems["rʕy.I"]["sensesRaw"], "weiden; abweiden")
        self.assertEqual(stems["rkw.I"]["forms"], "raku/roku (rokaw Kfarze)")
        self.assertEqual(stems["rkw.I"]["senses"][0]["gloss"], "seine Stelle einnehmen;")
        self.assertEqual(stems["ḥyl.III"]["forms"], "maḥəlla/maḥilo (f.) = mqaḥamla/mqaḥmo")
        self.assertEqual(stems["ḥyl.III"]["senses"], [])
        self.assertEqual(stems["frʕ-2.II~2"]["forms"], "mfaradle/mfarad")
        self.assertTrue(stems["frʕ-2.II~2"]["sensesRaw"].startswith("(trans.) to crumble"))
        self.assertEqual([s["id"] for s in stems.values() if s["forms"].count("(") != s["forms"].count(")")], [])


if __name__ == "__main__":
    unittest.main()
