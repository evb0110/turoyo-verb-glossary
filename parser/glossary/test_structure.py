"""Real-source regressions for entry, stem and section boundaries."""

import unittest

from .parse import Reader, parse_volumes, senses
from .docx import Text


class SourceStructureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parsed = parse_volumes()
        cls.entries = {e["id"]: e for e in cls.parsed.entries}
        cls.stems = {s["id"]: s for e in cls.parsed.entries for s in e["stems"]}
        cls.boxes = {b["id"]: b for s in cls.stems.values() for b in s["boxes"]}

    def test_recovered_root_heads_and_ownership(self):
        roots = {"drx": ("drх", "I"), "fhr": ("fhr, fxr", "II"),
                 "frd": ("frd/frḏ", "I"), "gwlč": ("Gwlč", "I"),
                 "ǧlǧl": ("Ǧlǧl", "II"), "ǧrm": ("ǧrm:", "III"),
                 "nʕl-2": ("nʕl²", "II"), "nǧr": ("Nǧr", "I"),
                 "npš": ("npš:", "II"), "pxpx": ("Pxpx", "II"),
                 "qndr": ("Qndr", "I"), "rbn": ("Rbn", "II"),
                 "šyk-1": ("Šyk 1", "I"), "šyk-2": ("Šyk 2", "III")}
        for identifier, (head, stem) in roots.items():
            with self.subTest(entry=identifier):
                entry = self.entries[identifier]
                self.assertTrue(entry["head"].startswith(head))
                self.assertIn(identifier + "." + stem, self.stems)
        self.assertEqual(self.entries["nʕl-2"]["homonym"], 2)
        self.assertEqual(self.stems["rbn.II"]["forms"], "mrabanle mraban")
        self.assertEqual(self.stems["šyk-1.I"]["senses"], [{"n": "1", "gloss": "to tickle"}])
        self.assertEqual(self.entries["gwlč"]["crossRefs"], ["glvč"])

    def test_detransitive_forms_are_not_senses(self):
        identifiers = ("bny-1.I bny-2.I byn.II dmx.I dwṣ.I grwn.I grš.I nql.I "
                       "qrf-1.I qsd.II qṭʕ-1.I snq.I sqṭ.II zrʕ.I čyk.I ġmm1.II "
                       "ǧrḥ.I ʔṣr.III ḥly-2.II ḥyr-2.II").split()
        for identifier in identifiers:
            with self.subTest(stem=identifier):
                raw = self.stems[identifier]["detransitiveSensesRaw"] or ""
                self.assertNotRegex(raw, r"(?:^|\n)\S+/\S+(?:\n|$)")
        self.assertEqual(self.stems["ġmm1.II"]["forms"], "mġaməm/miġaməm")
        self.assertIn("bani/məbne", self.stems["bny-1.I"]["notes"])
        self.assertEqual(self.stems["bny-1.I"]["forms"], "bnele/bone")
        self.assertEqual(self.stems["dwṣ.I"]["detransitiveSenses"], [])
        self.assertEqual([s["n"] for s in self.stems["čyk.I"]["detransitiveSenses"]], ["2", "3", "4", "5"])

    def test_form_markers_alternatives_and_editorial_tails(self):
        self.assertEqual(self.stems["dkr.I"]["forms"], "dkәrle/dokar // ḏkәrle/ḏokar")
        self.assertFalse(self.stems["bḏl.I"]["forms"].startswith("I."))
        self.assertTrue(self.stems["qwy-II.III"]["sensesRaw"].startswith("to have"))
        for identifier, forms in (("ftq.I", "ftəqle/fotəq"), ("nsf.I", "nsəfle/nosəf"),
                                  ("šyl-2.III", "mašele/mašəl")):
            self.assertEqual(self.stems[identifier]["forms"], forms)
            self.assertNotRegex(self.stems[identifier]["sensesRaw"], "More examples|Не уверен|Употребляется")

    def test_parenthesized_and_cyrillic_glosses(self):
        self.assertEqual(self.stems["rqʕ.III"]["senses"],
                         [{"n": "1", "gloss": "(to have (someone) sew or stitch (something))"}])
        self.assertEqual(self.stems["gmbl.II"]["sensesRaw"], "вывалять (в грязи);  to dunk/bathe into mud")
        self.assertEqual(self.stems["gmbl.II"]["detransitiveSensesRaw"], "вываляться (в грязи);")
        for identifier in ("dbr.II", "ʔmr-1.III"):
            self.assertTrue(any(any("А" <= c <= "я" for c in n) for n in self.stems[identifier]["notes"]))

    def test_prose_does_not_create_stems(self):
        for identifier in ("kmč.I~2", "kmč.I~3", "kyw.I~2"):
            self.assertNotIn(identifier, self.stems)
        self.assertTrue(any(n.startswith("I kalo") for n in self.stems["kmč.I"]["notes"]))
        self.assertTrue(any(n.startswith("I read") for n in self.stems["kyw.III"]["notes"]))
        self.assertEqual(self.stems["qḥm.II"]["forms"], "")
        self.assertTrue(self.stems["qḥm.II"]["sensesRaw"].startswith("‘to love’"))

    def test_repeated_header_immediately_after_detransitive(self):
        self.assertNotIn("dyn-1.II~2", self.stems)
        stem = self.stems["dyn-1.II"]
        self.assertEqual(stem["detransitiveSenses"], [{"n": "1", "gloss": "to borrow (money)"}])
        self.assertIn("II: mdayən/midayən", stem["notes"])
        self.assertTrue(self.boxes["dyn-1.II.d.infectum"]["detransitive"])
        self.assertIn("hdd.II~2", self.stems.keys())
        self.assertIn("šbḥ.II~2", self.stems.keys())

    def test_explicit_late_detransitive_transition(self):
        self.assertEqual(self.stems["ʔdb.II"]["detransitiveSensesRaw"], "(Detrans.) artig werden, Zucht annehmen;")
        # This paragraph is already inside an unrelated Detransitive section.
        self.assertIn("(Detrans.?) Schrecken bekommen;", self.stems["hdm.I"]["notes"])

    def test_commentary_numbers_and_literal_source_numbering(self):
        for identifier, expected in (("dry.I", ["1", "2", "3", "4", "5"]),
                                     ("nqr-1.I", ["1", "2", "3"]), ("šyf.I", ["1", "2"]),
                                     ("ʕly.III", ["1", "2", "3"])):
            self.assertEqual([s["n"] for s in self.stems[identifier]["senses"]], expected)
        for identifier in ("kfr.I", "nqṣ.III", "qḏ̣y.I", "ḥkm.I~2", "ḥyk.I"):
            self.assertEqual([s["n"] for s in self.stems[identifier]["senses"]], ["1", "2"])
        self.assertEqual(self.stems["qḏ̣y.I"]["senses"][1]["gloss"], "")
        self.assertEqual([s["n"] for s in self.stems["krx.I"]["senses"]].count("5"), 2)
        self.assertEqual(self.stems["kmč.I"]["senses"][-1], {"n": "2", "gloss": ""})
        self.assertEqual([s["n"] for s in self.stems["sym.I"]["senses"]],
                         [str(n) for n in range(1, 16) if n != 11])

    def test_structural_labels_and_editorial_material_are_not_senses(self):
        for identifier in ("dlq.I", "gwl.I", "gwl.II", "kry-1.I", "qdḥ.II", "rkx.I"):
            self.assertNotRegex(self.stems[identifier]["sensesRaw"],
                                r"(?:^|\n)(?:Transitive|Intransitive|Preterit Intransitive)(?:\n|$)")
        for identifier, snippet in (("bčq.I", "PrS 32/31"), ("dlq.I", "Dear Jan"),
                                    ("kyw.III", "Dear Shabo"), ("npʕ.III", "See nfʕ III"),
                                    ("nqwr.I (or II?)", "M· t 48/25"), ("dry.I", "We probably"),
                                    ("ḥmy.III", "History of Bsorino"), ("ḥsd.III", "maḥsadli"),
                                    ("wlḏ.III", "Detr. Pret."), ("xyr.III", "Omar,"),
                                    ("ʕṣy.III", "ʕ > ḥ"), ("fhr.II", "Two informants")):
            stem = self.stems[identifier]
            self.assertNotIn(snippet, stem["sensesRaw"] + (stem["detransitiveSensesRaw"] or ""))
            self.assertTrue(any(snippet in n for n in stem["notes"]), (identifier, snippet))
        self.assertEqual(self.stems["dlq.I"]["senses"], [])

    def test_idiom_exit_and_local_glosses(self):
        stem = self.stems["qṭʕ-1.I"]
        self.assertIn("qṭʕ-1.I.d.nomen-actionis", self.boxes.keys())
        box = self.boxes["qṭʕ-1.I.d.infinitiv"]
        self.assertEqual(len(box["examples"]), 2)
        self.assertIn("1) cutting; 2) stumbling of speech;", stem["notes"])
        self.assertEqual(len(self.entries["qṭʕ-1"]["idioms"]), 4)
        self.assertTrue(box["detransitive"])  # No new diathesis is printed.

    def test_bare_stem_and_offset_heading_cells(self):
        self.assertEqual(self.stems["dfn.I"]["forms"], "")
        self.assertEqual(self.stems["dfn.I"]["detransitiveSensesRaw"], "begraben werden")
        self.assertEqual(len(self.boxes["dfn.I.d.infectum"]["examples"]), 1)
        self.assertEqual(len(self.boxes["qlḏ.III.t.imperativ"]["examples"]), 1)
        self.assertEqual(len(self.boxes["qlḏ.III.t.infinitiv"]["examples"]), 1)
        self.assertEqual(len(self.boxes["rhm.III.t.infectum"]["examples"]), 1)

    def test_mixed_diathesis_sense_keeps_its_number(self):
        stem = self.stems["rstq.I"]
        self.assertEqual([s["n"] for s in stem["senses"]], ["1"])
        self.assertEqual(stem["detransitiveSenses"],
                         [{"n": "2", "gloss": "(Detrans.) geraden Weges gehen;"},
                          {"n": "1", "gloss": "Go/come directly"}])
        self.assertFalse(self.boxes["rstq.I.t.preterit"]["detransitive"])
        self.assertTrue(self.boxes["rstq.I.d.preterit"]["detransitive"])

    def test_reference_lists_capitalization_and_stem_notes(self):
        expected = {"ǧġl1": ["šġl-2", "žġl-1"], "ǧġl2": ["šġl-3", "žġl-2"],
                    "nwhr-2": ["nwr", "nhr"], "str": ["sṭr", "ṣtr", "ṣṭr"],
                    "ḏ̣yr-2": ["frq"], "grs1": ["grš"], "mḥy-2": ["lḥy", "slg"], "npʕ": ["nfʕ"]}
        for identifier, refs in expected.items():
            self.assertEqual(self.entries[identifier]["crossRefs"], refs)

    def test_repeated_roots_and_existing_ids_remain_stable(self):
        repeated = [d["root"].lower() for d in self.parsed.diagnostics if d["kind"] == "repeated-root"]
        self.assertEqual(sorted(repeated), sorted("hdd hdf hdm ḥkm ḥṣy ḥyz ngl swy šbḥ tšhy zʕf pxpx".split()))
        self.assertTrue(self.entries["pxpx"]["head"].startswith("Pxpx"))
        self.assertTrue(any(n.startswith("pxpx (<") for n in self.entries["pxpx"]["notes"]))
        self.assertEqual([s["id"] for s in self.entries["pxpx"]["stems"]], ["pxpx.II", "pxpx.I"])
        self.assertEqual(self.entries["ġmm1"]["id"], "ġmm1")
        self.assertEqual(self.entries["qwy-II"]["root"], "qwy II")

    def test_source_irregularities_are_preserved(self):
        self.assertEqual([s["n"] for s in self.stems["nḥt-1.I"]["senses"]], list("1234567"))
        self.assertEqual([s["n"] for s in self.stems["xrǧ.I"]["senses"]], ["1", "2"])
        self.assertEqual([s["n"] for s in self.stems["dry.III"]["senses"]], ["1", "2"])
        self.assertEqual([s["n"] for s in self.stems["dwmr.I"]["detransitiveSenses"]], ["1"])
        self.assertEqual(self.stems["ʔdb.II"]["sensesRaw"], "to teach (by punushment)")
        self.assertEqual(self.entries["drx"]["root"], "drх")
        self.assertEqual(self.entries["nʕl-2"]["root"], "nʕl²")
        self.assertTrue(self.entries["hymn"]["idioms"][-1]["raw"].startswith("Infectum\t"))

    def test_other_explicit_detransitive_senses_follow_the_same_rule(self):
        for identifier, numbers in (("brz.II", ["2"]), ("dmdm.I", ["2"]), ("dyq-1.I", ["8"]),
                                    ("dywn.I", ["2"]), ("gwtr.I", ["2"]), ("ptpt.I", ["2"]),
                                    ("qyṣ.I", ["3", "4"]), ("qšʕ.I", ["3"]), ("qṣf.I", ["2"]),
                                    ("tʕmž.I", ["2"]), ("xlxl.I", ["2"]), ("xrbq.I", ["3"]),
                                    ("čqlb.I", ["2"]), ("šqšq.I", ["2"]), ("ǧlǧʕ.I", ["2"]),
                                    ("ḥrm-1.II", ["2"]), ("ḥwdl.I", ["2"]), ("ṣnṣl.I", ["2", "3"])):
            with self.subTest(stem=identifier):
                stem = self.stems[identifier]
                self.assertEqual([s["n"] for s in stem["detransitiveSenses"]], numbers)
                self.assertNotIn("(Detrans.)", stem["sensesRaw"])


class StructureRulesTest(unittest.TestCase):
    def test_comment_numbers_are_protected_but_parenthesized_lists_work(self):
        self.assertEqual(senses("1) rub (see 12); 2) warm [compare 3) above]"),
                         [{"n": "1", "gloss": "rub (see 12);"},
                          {"n": "2", "gloss": "warm [compare 3) above]"}])
        self.assertEqual([s["n"] for s in senses("(1)to spend, 2) to exhaust)")], ["1", "2"])

    def test_normalized_repeated_root_is_merged(self):
        reader = Reader()
        reader.start_entry(Text("rbn", key="p0"), "rbn", 1)
        reader.start_entry(Text("Rbn", key="p1"), "Rbn", 2)
        self.assertEqual(len(reader.result.entries), 1)
        self.assertEqual(reader.entry["notes"], ["Rbn"])
        self.assertEqual(reader.result.diagnostics[0]["kind"], "repeated-root")

    def test_a_citation_with_capitals_is_not_a_recovered_head(self):
        reader = Reader()
        reader.paragraph(Text("bčq", key="p0"), 1)
        reader.paragraph(Text("I: bčəqle/bočəq", key="p1"), 2)
        reader.paragraph(Text("PrS 32/31", key="p2"), 3)
        self.assertEqual([e["id"] for e in reader.result.entries], ["bčq"])
        self.assertIn("PrS 32/31", reader.stem["notes"])

    def test_gloss_dates_and_citation_decimals_are_not_sense_markers(self):
        self.assertEqual([s["n"] for s in senses("1) first; 3) second (JL 19.6.19; 12)")], ["1", "3"])


if __name__ == "__main__":
    unittest.main()
