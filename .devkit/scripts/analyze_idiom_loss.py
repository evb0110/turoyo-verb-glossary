#!/usr/bin/env python3
"""
Analyze systematic data loss: scan all DOCX files to find verbs with
non-table content (idiomatic expressions, phrases) that the parser currently loses.
"""

import re
from pathlib import Path
from docx import Document
from collections import defaultdict

class IdiomLossAnalyzer:
    def __init__(self):
        self.turoyo_chars = r'ʔʕbčdfgġǧhḥklmnpqrsṣštṭvwxyzžḏṯẓāēīūə'
        self.root_pattern = re.compile(
            rf'^([{self.turoyo_chars}]+(?:\s+\d+)?(?:,\s*[{self.turoyo_chars}]+)*)\s*[<(]',
            re.UNICODE
        )
        self.stem_pattern = re.compile(r'^([IVX]+|Pa\.|Af\.|Št\.|Šaf\.):\s*', re.UNICODE)

        self.verbs_with_idioms = []
        self.total_idiom_paragraphs = 0
        self.verbs_analyzed = 0

    def is_root_paragraph(self, text):
        """Check if paragraph is a root definition"""
        return bool(self.root_pattern.match(text))

    def is_stem_header(self, text):
        """Check if paragraph is a stem header"""
        if not text.strip():
            return False
        if text.startswith('Detransitive'):
            return True
        return bool(self.stem_pattern.match(text))

    def is_table_related(self, para):
        """Check if paragraph is part of a table"""
        return para._element.getparent().tag.endswith('tbl')

    def is_idiom_paragraph(self, text):
        """
        Heuristic: likely an idiomatic expression if it contains Turoyo text
        followed by German translation or explanation
        """
        if not text.strip():
            return False

        # Skip if it's clearly a reference or note
        if text.startswith(('cf.', 'see', 'vgl.', 'SL ', 'VW ')):
            return False

        # Look for patterns like "obe/hule PHRASE" or "Turoyo text ʻGerman translationʼ"
        has_turoyo = bool(re.search(rf'[{self.turoyo_chars}]+', text, re.UNICODE))
        has_translation = bool(re.search(r'[ʻʼ"]', text))  # Quotation marks for translations

        return has_turoyo and (has_translation or '/' in text or len(text) > 30)

    def analyze_verb(self, root, paragraphs):
        """
        Analyze a single verb's paragraphs to find non-table content
        between root and first conjugation table
        """
        idiom_paras = []

        for para in paragraphs:
            text = para.text.strip()

            # Skip empty paragraphs
            if not text:
                continue

            # Skip if we hit a stem header (start of conjugation section)
            if self.is_stem_header(text):
                break

            # Skip if it's in a table
            if self.is_table_related(para):
                continue

            # Check if it's an idiomatic expression
            if self.is_idiom_paragraph(text):
                idiom_paras.append({
                    'text': text[:100] + '...' if len(text) > 100 else text,
                    'full_length': len(text)
                })

        return idiom_paras

    def analyze_docx(self, docx_path):
        """Analyze a single DOCX file for verbs with lost idioms"""
        print(f"\nAnalyzing {docx_path.name}...")
        doc = Document(docx_path)

        current_root = None
        current_verb_paras = []

        for para in doc.paragraphs:
            text = para.text.strip()

            if not text:
                continue

            # Check if this is a new root
            if self.is_root_paragraph(text):
                # Analyze previous verb if exists
                if current_root and current_verb_paras:
                    idioms = self.analyze_verb(current_root, current_verb_paras)
                    if idioms:
                        self.verbs_with_idioms.append({
                            'root': current_root,
                            'file': docx_path.name,
                            'idiom_count': len(idioms),
                            'examples': idioms[:3]  # First 3 examples
                        })
                        self.total_idiom_paragraphs += len(idioms)
                    self.verbs_analyzed += 1

                # Start new verb
                root_match = self.root_pattern.match(text)
                current_root = root_match.group(1) if root_match else text[:50]
                current_verb_paras = []
            else:
                # Accumulate paragraphs for current verb
                if current_root:
                    current_verb_paras.append(para)

        # Don't forget the last verb
        if current_root and current_verb_paras:
            idioms = self.analyze_verb(current_root, current_verb_paras)
            if idioms:
                self.verbs_with_idioms.append({
                    'root': current_root,
                    'file': docx_path.name,
                    'idiom_count': len(idioms),
                    'examples': idioms[:3]
                })
                self.total_idiom_paragraphs += len(idioms)
            self.verbs_analyzed += 1

    def analyze_all(self):
        """Analyze all DOCX files in the source directory"""
        source_dir = Path('.devkit/new-source-docx')
        docx_files = sorted(source_dir.glob('*.docx'))

        if not docx_files:
            print(f"ERROR: No DOCX files found in {source_dir}")
            return

        print(f"Found {len(docx_files)} DOCX files to analyze")

        for docx_path in docx_files:
            if docx_path.name.startswith('~'):  # Skip temp files
                continue
            self.analyze_docx(docx_path)

        self.print_report()

    def print_report(self):
        """Print comprehensive analysis report"""
        print("\n" + "="*80)
        print("SYSTEMATIC DATA LOSS ANALYSIS - IDIOMATIC EXPRESSIONS")
        print("="*80)

        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   Total verbs analyzed: {self.verbs_analyzed}")
        print(f"   Verbs with lost idioms: {len(self.verbs_with_idioms)}")
        print(f"   Total idiom paragraphs lost: {self.total_idiom_paragraphs}")

        if self.verbs_analyzed > 0:
            loss_rate = (len(self.verbs_with_idioms) / self.verbs_analyzed) * 100
            print(f"   Loss rate: {loss_rate:.1f}% of verbs affected")

        print(f"\n🔥 TOP 20 VERBS WITH MOST LOST IDIOMS:")
        sorted_verbs = sorted(self.verbs_with_idioms, key=lambda x: x['idiom_count'], reverse=True)

        for i, verb in enumerate(sorted_verbs[:20], 1):
            print(f"\n   {i}. {verb['root']} ({verb['file']})")
            print(f"      Lost idioms: {verb['idiom_count']}")
            print(f"      Examples:")
            for example in verb['examples']:
                print(f"        - {example['text']}")

        # Statistics by file
        print(f"\n📁 LOSS BY FILE:")
        by_file = defaultdict(lambda: {'count': 0, 'idioms': 0})
        for verb in self.verbs_with_idioms:
            by_file[verb['file']]['count'] += 1
            by_file[verb['file']]['idioms'] += verb['idiom_count']

        for file, stats in sorted(by_file.items()):
            print(f"   {file}: {stats['count']} verbs, {stats['idioms']} idiom paragraphs lost")

        print(f"\n💡 RECOMMENDATION:")
        if len(self.verbs_with_idioms) > 50:
            print(f"   ⚠️  CRITICAL: {len(self.verbs_with_idioms)} verbs have lost idioms.")
            print(f"   Parser MUST be updated to extract non-table content!")
        elif len(self.verbs_with_idioms) > 10:
            print(f"   ⚠️  SIGNIFICANT: {len(self.verbs_with_idioms)} verbs have lost idioms.")
            print(f"   Consider updating parser to preserve this data.")
        else:
            print(f"   ℹ️  Minor issue: Only {len(self.verbs_with_idioms)} verbs affected.")

if __name__ == '__main__':
    analyzer = IdiomLossAnalyzer()
    analyzer.analyze_all()
