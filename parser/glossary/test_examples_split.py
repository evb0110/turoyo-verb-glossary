"""Regressions for source-backed example boundaries (EX01–EX09, EX14–EX22)."""

import unittest

from .examples import parse_example, refs_at_start, split_examples
from .test_glossary import rich


class CitationBoundariesTest(unittest.TestCase):
    def test_complete_recording_identifiers(self):
        for citation in ("2018_07_08_au_003_NE_1F; 27:29", "006_NE_GALA;17",
                         "‘2019_13_01_Malfono_Ishaq,16’", "NE_254;22:10",
                         "004_NE_ Ditin Hezar; 12:33", "‘tru_IL_conj_yzd’"):
            with self.subTest(citation=citation):
                value = rich(("səmle ", True), ("He made it. " + citation, False))
                example = parse_example(value, None, "x")
                self.assertEqual(example["translation"], "He made it.")
                self.assertEqual([r["raw"] for r in example["refs"]], [citation])

    def test_parenthesized_citations_and_unquoted_tails(self):
        for citation in ("(QM 2461)", "(XB 928)", "(94/1)", "(731; 78/115)",
                         "(Nisane 2018-07-08)", "(HD 85)", "(209 FG 12: 42)"):
            with self.subTest(citation=citation):
                for gloss in ("‘he made it’ ", "he made it "):
                    example = parse_example(rich(("səmle ", True), (gloss + citation, False)), None, "x")
                    self.assertTrue(example["refs"], example)
                    self.assertNotIn(citation, example["translation"])
                    self.assertIsNone(example["note"])
        example = parse_example(rich(("səmle.(İlyas p.c)", True)), None, "x")
        self.assertEqual(example["refs"][0]["raw"], "(İlyas p.c)")

    def test_text_lists_stop_before_the_next_text_number(self):
        refs, end = refs_at_start("97; 6/6, 6/9;")
        self.assertEqual([r["raw"] for r in refs], ["97", "6/6", "6/9"])
        self.assertEqual(end, len("97; 6/6, 6/9;"))
        refs, _ = refs_at_start("66/292, 363, 366, 67/19, 32, 73/18;")
        self.assertEqual([r["raw"] for r in refs], ["66/292, 363, 366", "67/19, 32", "73/18"])

    def test_personal_communication_does_not_consume_bilingual_prose(self):
        self.assertEqual(refs_at_start("Maţmacle biyya w mëdole l ruḥe He liked it p.c. Jan()")[0], [])
        self.assertEqual([r["raw"] for r in refs_at_start("p.c. Ido Talay; [LTN]")[0]],
                         ["p.c. Ido Talay", "[LTN]"])
        refs, _ = refs_at_start("(with 10 sheep) we left")
        self.assertEqual(refs, [])


class GlossBoundariesTest(unittest.TestCase):
    def test_unclosed_quotes_stop_at_citations(self):
        for gloss in ("‘So lief die Gazelle herum; 28/96;", "‘He said: “Take it out” LuF 296/36;",
                      "‘Scheich ‘Abdalmuṭṭalib nennt man mich’; 30/97"):
            example = parse_example(rich(("məlle ", True), (gloss, False)), None, "x")
            self.assertTrue(example["refs"], example)
            self.assertNotRegex(example["translation"], r"\d+/\d+")

    def test_possessive_before_parenthesis(self):
        example = parse_example(rich(("səmme ", True),
            ("‘They took their (the villagers’) beds and demolished their walls’ LB 329;", False)), None, "x")
        self.assertEqual(example["translation"], "They took their (the villagers’) beds and demolished their walls")
        self.assertEqual(example["refs"][0]["raw"], "LB 329")

    def test_italic_and_adjacent_or_doubled_gloss_quotes(self):
        for source, gloss in (("aṯe", "ʻwir bitten euch darumʼ LB 387;"),
                              ("məlle ", "‘All Yezidis back then worked’"),
                              ("mballe ", "‘’Sergey and Gule stole all our cattle. (İlyas pc.)"),
                              ("səmle ", "‘’do you see the way they poisoned us?’’ NE_254;2")):
            example = parse_example(rich((source, True), (gloss, source != "aṯe")), None, "x")
            self.assertEqual(example["turoyo"], source.strip())
            self.assertIsNotNone(example["translation"])

    def test_turoyo_direct_speech_is_not_a_gloss(self):
        for text in ('Mǝrla “zox tayli u ḥalwo” (163:8; 02. 26 Fox)',
                     'məlle: “Ya ḥurma! Ḥaṭino qumax, kobaʕno d ʕofatli”; 62/349.',
                     'Omar, ‘Yabo!’', 'Omar, ‘Ha?’',
                     'məlle: “Zoxu, kraxu qm aš šenawoṯani! 62/225;'):
            for italic in (False, True):
                example = parse_example(rich((text, italic)), None, "x")
                self.assertIsNone(example["translation"], example)

    def test_explicit_gloss_precedes_formatting_and_weak_english_cues(self):
        value = rich(("gəd-əzzino tamo ", True), ("tamo ‘I will build a village’; 36/146;", False))
        example = parse_example(value, None, "x")
        self.assertEqual(example["translation"], "I will build a village")
        value = rich(("rmalle all ste ", True), ("‘Then she says’ 24/46;", False))
        self.assertEqual(parse_example(value, None, "x")["turoyo"], "rmalle all ste")

    def test_internal_equals_sign_is_part_of_translation(self):
        value = rich(("səmle ", True), ("Naturally, this (=ʕafro) is needed. They smooth it (u=qṭoro).", False))
        self.assertEqual(parse_example(value, None, "x")["translation"],
                         "Naturally, this (=ʕafro) is needed. They smooth it (u=qṭoro).")

    def test_dialogue_and_alternative_quotes_are_one_translation(self):
        for gloss in ('“What do you have?” – He said: “I have milk” – “From where?” 75/316;',
                      '‘He was strategizing’, ‘He was watching them’ 24/46;',
                      '‘Father, how many days?’ ‘It lasted two days” Xori Caziz 2001 24b.'):
            example = parse_example(rich(("məlle ", True), (gloss, False)), None, "x")
            self.assertIsNone(example["note"], example)
            self.assertTrue(example["refs"])
            self.assertIn('”' if 'lasted' in gloss else '’' if 'strategizing' in gloss else '”', example["translation"])


class AnnotationBoundariesTest(unittest.TestCase):
    def test_complete_preference_note_is_retained(self):
        value = rich(("ʕyoṭo/teʕiṭo ", True), ("(Ilyas prefers ", False), ("ʕyoṭo", True),
                     (", but is ready to accept ", False), ("teʕiṭo", True), (" as a productive pattern)", False))
        example = parse_example(value, None, "x")
        self.assertIsNone(example["translation"])
        self.assertEqual(example["turoyo"], "ʕyoṭo/teʕiṭo")
        self.assertEqual(example["note"], value.text[len(example["turoyo"]):].strip())
        self.assertEqual(example["turoyo"] + ' ' + example["note"], example["raw"])

    def test_source_labels_and_attributions_are_not_glosses(self):
        for annotation in ("(CS)", "(Ilyas)", "(Nisane, Ilyas’ sister)",
                           "(Ilyas from Kfarze 13-07-2018)", "According to Ido Talay", "auch:",
                           "‘tru_IL_conj_yzd’", "Isḥaq Old houses:35"):
            example = parse_example(rich(("səmle ", True), (annotation, False)), None, "x")
            self.assertIsNone(example["translation"], example)
            self.assertTrue(example["note"] or example["refs"], example)

    def test_parenthetical_gloss_does_not_hide_main_translation(self):
        value = rich(("lo twəḷḷe ʕarz diḏe ", True), ("(", False),
                     ("lo məḷḷele mede ḥarbo, bas u+greʕo ġalabe nafəl qəm ruḥe ", True),
                     ("‘he was very much upset’) he did not insult him (p.c. Ilyas)", False))
        self.assertEqual(parse_example(value, None, "x")["translation"], "he did not insult him")
        value = rich(("nqīl hasyo dolabani ", True), ("(*nqīl hasyo ", True),
                     ("m= is obligatory!) Hasyo Dolabani died in 1969 (pc Ilyas 17/08/25)", False))
        self.assertEqual(parse_example(value, None, "x")["translation"], "Hasyo Dolabani died in 1969")

    def test_leading_citation_does_not_skip_remainder_of_roman_run(self):
        value = rich(("mgandarli adyawma tre+zlamat ", True),
                     ("(Ilyas p.c.) I killed two men today lit. I made them roll.", False))
        self.assertEqual(parse_example(value, None, "x")["translation"], "I killed two men today lit. I made them roll.")


class PassageBoundariesTest(unittest.TestCase):
    def examples(self, value):
        return [parse_example(p, n, str(i)) for i, (n, p) in enumerate(split_examples(value))]

    def test_cited_untranslated_forms_are_separate_examples(self):
        value = rich(("1) madmáx; 152; b-dukṯo naḏ̣əfto madmex-la ", True),
                     ("ʻbringt sie unter!ʼ; MM 98;", False))
        examples = self.examples(value)
        self.assertEqual(len(examples), 2)
        self.assertIsNone(examples[0]["translation"])
        self.assertEqual(examples[0]["refs"][0]["raw"], "152")
        self.assertEqual([e["sense"] for e in examples], ["1", "1"])
        self.assertEqual(examples[1]["turoyo"], "b-dukṯo naḏ̣əfto madmex-la")

    def test_quoted_source_and_source_after_russian_comment(self):
        for prefix in ('«awwə́l d-moṭe ', '“aḥuno, ŭno mazraqli” ',
                       'ПРИМЕР ОТСУТСТВУЕТ; haṯe i=kal-aṯxu '):
            value = rich(("səmle ", True), ("‘he made it’; 24/46; ", False),
                         (prefix, True), ("‘he did it’; 24/47;", False))
            examples = self.examples(value)
            self.assertEqual(len(examples), 2, examples)
            self.assertEqual(examples[1]["translation"], "he did it")
            if prefix.startswith('ПРИМЕР'):
                self.assertIn('ПРИМЕР', examples[0]["note"])
                self.assertTrue(examples[1]["turoyo"].startswith('haṯe'))
            self.assertEqual(''.join(e['raw'] for e in examples).replace(' ', ''), value.text.replace(' ', ''))

    def test_english_paragraphs_join_the_source_dialogue(self):
        for gloss in ('[The king] said, ‘Really, I wouldn’t expect it’.',
                      'He clasped it to his breast, that stone.'):
            value = rich(('Məḷḷe, ‘Yabo!’\nOmar, ‘Ha?’\n', False), (gloss, False))
            examples = self.examples(value)
            self.assertEqual(len(examples), 1, examples)
            self.assertEqual(examples[0]["translation"], gloss)
            self.assertIn('Omar, ‘Ha?’', examples[0]["turoyo"])

    def test_missing_quote_cannot_consume_a_later_example(self):
        value = rich(('məlle ', True), ('‘He said: “Go!” 24/46; ', False),
                     ('aḥuno səmle ', True), ('‘his brother made it’ 24/47;', False))
        examples = self.examples(value)
        self.assertEqual(len(examples), 2)
        self.assertEqual([r['raw'] for r in examples[0]['refs']], ['24/46'])


class BoundaryGuardsTest(unittest.TestCase):
    def test_source_name_inside_translation_is_not_a_citation(self):
        value = rich(('məlle ', True), ('‘Er sagte Onkel Shabo, sie hatte kein Haus’ 24/46;', False))
        example = parse_example(value, None, 'x')
        self.assertEqual(example['translation'], 'Er sagte Onkel Shabo, sie hatte kein Haus')
        self.assertEqual([r['raw'] for r in example['refs']], ['24/46'])
        value = rich(('məlle ', True), ('he did it (according to Shabo) yesterday (Ilyas p.c.)', False))
        self.assertEqual(parse_example(value, None, 'x')['translation'],
                         'he did it (according to Shabo) yesterday')

    def test_unclosed_gloss_does_not_cross_source_paragraph(self):
        value = rich(('ṭr-owe ', True), ('ʻmöge es sein! einverstanden!\n', False),
                     ('omər oṯe babəx ', True), ('ʻwenn dein Vater kommtʼ; 372;', False))
        examples = [parse_example(p, n, str(i)) for i, (n, p) in enumerate(split_examples(value))]
        self.assertEqual([e['translation'] for e in examples],
                         ['möge es sein! einverstanden!', 'wenn dein Vater kommt'])

    def test_page_after_mismatched_closing_quote(self):
        example = parse_example(rich(('səmle ', True), ('ʻhe made it” 184;', False)), None, 'x')
        self.assertEqual(example['translation'], 'he made it')
        self.assertEqual([r['raw'] for r in example['refs']], ['184'])

    def test_native_replies_and_english_metalinguistic_introductions(self):
        for speech in ('Haw ṭowe ʕal ʕəmran, bayiqina.', 'Elux maqṭelux!', 'Lo!',
                       'Ha, gnulux u+kosayḏi!'):
            value = rich(('omar, ', False), ('‘' + speech + '’', False))
            self.assertIsNone(parse_example(value, None, 'x')['translation'], speech)
        for gloss in ('Masʕəd said to Ṣabriyo: “You see it”',
                      'u=teḏ̣iro bedeutet: der, den man betrachtet'):
            value = rich(('səmle ', True), ('‘' + gloss + '’ 24/46;', False))
            self.assertEqual(parse_example(value, None, 'x')['translation'], gloss)

    def test_gloss_introduction_precedes_inner_quote(self):
        for gloss in ('he says, ‘That thing that you did not create’',
                      'lit. ‘my eyes became scarce’, i.e. I don’t see good'):
            example = parse_example(rich(('səmle ', True), (gloss + ' (Ilyas p.c.)', False)), None, 'x')
            self.assertEqual(example['translation'], gloss)

    def test_cyrillic_note_letters_are_not_recovered_passages(self):
        for note in ('Выпала вторая “m”', 'Это арабский dad, а не ḏ̣',
                     'Здесь последняя буква t', '-- MUST BE 2ND STEM!',
                     'the same example in 29/40 - Idiom???'):
            value = rich(('səmle ', True), ('‘he made it’; 24/46; ' + note, False))
            examples = split_examples(value)
            self.assertEqual(len(examples), 1, note)
            self.assertEqual(parse_example(examples[0][1], None, 'x')['note'], note)

    def test_untranslated_internal_parentheses_remain_source(self):
        value = rich(('qayəd (bi palləke du daftar) w ṭowe', True))
        example = parse_example(value, None, 'x')
        self.assertEqual(example['turoyo'], value.text)
        self.assertIsNone(example['note'])

    def test_source_timestamp_and_interlinear_appendix_stay_in_place(self):
        value = rich(('4) “Merəko, komakəm (3.51) tamhonike, komakəm tamhonike…” ', False),
                     ('it is black over there', False))
        self.assertEqual(len(split_examples(value)), 1)
        value = rich(('səmle ', True), ('‘he made it’ 24/46\n“Haka \tprs-accept.prs-2pl” (Autobiography of Nisane)', False))
        self.assertEqual(len(split_examples(value)), 1)

    def test_glued_equivalence_and_note_number(self):
        value = rich(('səmle ', True), ('he made it.= aṯe', False))
        self.assertEqual(parse_example(value, None, 'x')['note'], '= aṯe')
        value = rich(('2) səmle ', True), ('‘he made it’ 24/46; Смотри №3) выше\n', False),
                     ('səmme ', True), ('‘they made it’ 24/47;', False))
        self.assertEqual([n for n, p in split_examples(value)], ['2', '2'])

    def test_note_recovery_cannot_borrow_a_later_numbered_gloss(self):
        value = rich(('1) səmle ', True), ('‘he made it’; 24/46; ', False),
                     ('У Риттера арабский dad, а не ḏ̣ 2) áydarbo səmme ', True),
                     ('‘they made it’; 24/47;', False))
        examples = [parse_example(p, n, str(i)) for i, (n, p) in enumerate(split_examples(value))]
        self.assertEqual(len(examples), 2)
        self.assertEqual(examples[0]['note'], 'У Риттера арабский dad, а не ḏ̣')

    def test_native_quote_after_gloss_is_not_a_dialogue_continuation(self):
        value = rich(('səmle ', True), ('‘He made it.’\n\n', False),
                     ('‘mfark̇o’, i+maʕnayḏa yo: fayito, šafiʕo', True))
        example = parse_example(value, None, 'x')
        self.assertEqual(example['translation'], 'He made it.')
        self.assertIn('mfark̇o', example['note'])

    def test_english_inner_closer_and_native_cat_speech(self):
        value = rich(('səmle ', True), ('‘Finally, he says, ‘I am Joseph.’ (Story of Joseph, NE)', False))
        self.assertEqual(parse_example(value, None, 'x')['translation'], 'Finally, he says, ‘I am Joseph.’')
        value = rich(('44. Əmmo, ‘Răbane, may gməlyat hano?’.\nThe cat said, ‘Poor thing, whence?’', False))
        example = parse_example(value, None, 'x')
        self.assertTrue(example['translation'].startswith('The cat said'))


class CorpusSplitTest(unittest.TestCase):
    """Exercise the actual seven-volume DOCX/Reader seam, including run flags."""

    @classmethod
    def setUpClass(cls):
        from .parse import parse_volumes
        cls.entries = {e['id']: e for e in parse_volumes().entries}

    def examples(self, root, box):
        return [e for s in self.entries[root]['stems'] for b in s['boxes']
                if b['id'] == box for e in b['examples']]

    def example(self, identifier):
        return next(e for e in self.examples(identifier.split('.')[0], identifier.rsplit('.', 1)[0])
                    if e['id'] == identifier)

    def test_full_preference_note_and_internal_parenthetical_gloss(self):
        example = self.example('ʕyṭ.II.t.infinitive-action-noun.1')
        self.assertIsNone(example['translation'])
        self.assertEqual(example['turoyo'] + ' ' + example['note'], example['raw'])
        example = self.example('tny.II.t.preterit.4')
        self.assertEqual(example['translation'], 'he did not insult him')
        self.assertIn('‘he was very much upset’', example['turoyo'])

    def test_possessive_and_italic_english_suffix(self):
        for identifier in ('hdf.I.t.ko-preterit.1', 'nfq.III.t.ko-preterit.1', 'hdf.I~2.t.ko-preterit.1'):
            example = self.example(identifier)
            self.assertTrue(example['translation'].endswith('beds and demolished their walls'))
            self.assertEqual(example['refs'][0]['raw'], 'LB 329')
        example = self.example('šfr.II.t.preterit.1')
        self.assertTrue(example['translation'].endswith('came out finer.'))
        self.assertIn('(u=qṭoro)', example['translation'])
        self.assertEqual(example['refs'][0]['raw'], '2019_13_01_Malfono_İshaq;49')

    def test_recovered_passages_after_comments_and_citations(self):
        for root, box, source, gloss in (
                ('brx', 'brx.II.t.infectum', '«awwə́l', 'Sobald dieser Sohn'),
                ('flt', 'flt.III.t.infectum', 'hano latyo', 'das geht dich nichts an'),
                ('nhr', 'nhr.I.t.preterit-intransitive', 'nahər. qayəm', 'It was already daybreak.'),
                ('ḥwl', 'ḥwl.II.t.preterit', 'Ono bu qayṭo', 'In summer I married my wife.')):
            with self.subTest(root=root):
                example = next(e for e in self.examples(root, box) if e['turoyo'].startswith(source))
                self.assertTrue(example['translation'].startswith(gloss))
                self.assertTrue(example['refs'])

    def test_independently_cited_forms_and_bounded_personal_communication(self):
        examples = self.examples('dmx', 'dmx.III.t.imperativ')
        self.assertEqual([e['turoyo'] for e in examples[:2]], ['madmáx', 'b-dukṯo naḏ̣əfto madmex-la'])
        self.assertIsNone(examples[0]['translation'])
        self.assertEqual(examples[0]['refs'][0]['raw'], '152')
        examples = self.examples('ṭmʕ', 'ṭmʕ.III.t.preterit')
        self.assertEqual(examples[1]['translation'], 'He liked it and took it for himself')
        self.assertEqual(examples[1]['refs'][0]['raw'], 'p.c. Jan()')

    def test_native_speech_and_complete_english_paragraph(self):
        example = self.example('mty.I.t.imperativ.2')
        self.assertIsNone(example['translation'])
        example = self.example('slpx.I.d.infectum.1')
        self.assertTrue(example['translation'].startswith('They (two women) brought home'))
        self.assertIn('“Aǧ ǧewərkat', example['turoyo'])
        example = self.example('qḏ̣y.I.t.preterit-intransitive.5')
        self.assertIn('‘Elux maqṭelux!’', example['turoyo'])
        self.assertTrue(example['translation'].startswith('He swears, he says'))
        example = next(e for e in self.examples('nḥt-1', 'nḥt-1.III.t.imperativ')
                       if e['turoyo'].startswith('44. Əmmo'))
        self.assertTrue(example['translation'].startswith('The cat said'))

    def test_english_paragraph_joins_and_dialogue_glosses(self):
        self.assertEqual(len(self.examples('qbḏ', 'qbḏ.I.t.preterit')), 1)
        example = self.example('zwn.II.d.infinitiv.2')
        self.assertIn('From where?', example['translation'])
        self.assertIn('Now it is for sale.', example['translation'])
        self.assertEqual(example['refs'][0]['raw'], '75/316-317')
        self.assertIsNone(example['note'])

    def test_complete_recordings_wrappers_and_text_lists(self):
        example = self.example('blq-1.I.t.infectum.1')
        self.assertEqual(example['refs'][0]['raw'], '2018_07_08_au_003_NE_1F; 27:29')
        self.assertNotIn('2018_', example['translation'])
        example = self.example('ksd.I.t.infectum-wa.1')
        self.assertEqual(example['refs'][0]['raw'], '(QM 2461)')
        example = self.example('ḥṣd.I.t.infectum.1')
        self.assertEqual([r['raw'] for r in example['refs']], ['97', '6/6', '6/9'])
        example = self.example('qtl.II.t.infectum.2')
        self.assertEqual(example['refs'][0]['raw'], '(731; 78/115)')

    def test_english_openings_and_doubled_quotes(self):
        for identifier, opening in (
                ('gndr.I.d.preterit~2.2', 'I killed two men'),
                ('ḥys.III.t.preterit.8', 'A  snake passed'),
                ('yrw.III.t.preterit.2', 'Nisane, her grandmother'),
                ('dbr.II.t.infectum-wa.2', 'All Yezidis back then'),
                ('ybl.III.t.preterit.10', 'Sergey and Gule stole')):
            self.assertTrue(self.example(identifier)['translation'].startswith(opening), identifier)

    def test_ambiguous_appendices_and_russian_notes_keep_their_place(self):
        example = self.example('ḥwy-1.I.t.infectum.2')
        self.assertIn('prs-accept.prs-2pl', example['note'])
        self.assertEqual(len(self.examples('ḥwy-1', 'ḥwy-1.I.t.infectum')), 2)
        example = self.example('tḥsd-1.I.d.infectum.2')
        self.assertIn('this form deviates', example['note'])
        self.assertIn('I make Gule envious of Sergey.', example['note'])
        example = self.example('fḏ̣l.II.t.infectum.1')
        self.assertTrue(example['note'].endswith('dad, а не ḏ̣'))
        self.assertEqual(len(self.examples('fḏ̣l', 'fḏ̣l.II.t.infectum')), 2)

    def test_uncertain_comparison_and_internal_attribution_stay_intact(self):
        examples = self.examples('frk', 'frk.II.d.preterit')
        self.assertIn('mfarak̇ u+muklo = mbarbaz u+muklo', examples[-2]['note'])
        self.assertIn('Ilyas was unable to produce more examples.', examples[-2]['note'])
        self.assertTrue(examples[-1]['turoyo'].startswith('w bəṯr d-azzehən'))
        self.assertIsNone(examples[-1]['translation'])
        example = self.example('swʕ.I.t.infectum.2')
        self.assertTrue(example['translation'].endswith('‘get satiated with sleep’'))
        example = self.example('xrǧ.I.t.preterit.2')
        self.assertIn('(İlyas p.c)/ Ono xarǧo', example['turoyo'])
        self.assertEqual(example['refs'], [])
        examples = self.examples('lbk', 'lbk.III.d.infectum')
        self.assertIsNone(examples[0]['note'])
        self.assertTrue(examples[1]['raw'].startswith('According to Ido Talay'))

    def test_attribution_before_following_form_and_after_native_wrapper(self):
        examples = self.examples('ʕmr-1', 'ʕmr-1.I.t.infectum')
        self.assertEqual(examples[2]['refs'][0]['raw'], '- Shabo')
        self.assertTrue(examples[3]['turoyo'].startswith('way mo=kore'))
        examples = self.examples('wṣy', 'wṣy.III.d.part-pass')
        self.assertEqual(examples[2]['refs'][0]['raw'], '004_NE_DİTİN HEZAR.06:00')
        self.assertIsNone(examples[2]['note'])

    def test_source_names_and_nested_quotes_keep_complete_glosses(self):
        example = self.example('hyw-1.I.t.preterit-wa.1')
        self.assertIn('Onkel Shabo, sie hatte', example['translation'])
        example = self.example('ʔḏʕ.I.t.infectum-wa.4')
        self.assertIn('als sein Vater starb', example['translation'])
        self.assertIn('Deine Verlobte ist deine Base!', example['translation'])
