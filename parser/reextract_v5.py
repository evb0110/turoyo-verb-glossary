#!/usr/bin/env python3
import re
import json
from pathlib import Path
from collections import defaultdict
from bs4 import BeautifulSoup

# Reuse parsing logic from v4 for tables and stems
from parser.extract_clean_v4 import CleanTuroyoParser

ALLOWED = 'ʔʕbčdfgġǧhḥklmnpqrsṣštṭwxyzžḏṯẓāēīūə'
# Match: <p class="western"><font...><span>ROOT</span> ...
ROOT_PATTERN = re.compile(
    rf'<p[^>]*class="western"[^>]*><font[^>]*><span[^>]*>(?:&shy;)?([{ALLOWED}]{{2,6}})(?:\s*\d+)?</span>',
    re.DOTALL
)

SRC_HTML = Path('source/Turoyo_all_2024.html')
OUT_JSON = Path('data/verbs_final_v5.json')

# Stem header marker to locate the start of the first stem block
STEM_HEADER = re.compile(r'<font size="4"[^>]*><b><span[^>]*>([IVX]+):\s*</span>', re.DOTALL)


def segment_entries(html: str):
    matches = list(ROOT_PATTERN.finditer(html))
    segments = []
    for i, m in enumerate(matches):
        root = m.group(1)
        start = m.start()
        end = matches[i+1].start() if i + 1 < len(matches) else len(html)
        frag = html[start:end]
        segments.append((root, frag))
    return segments


def extract_lemma_header_raw(fragment_html: str) -> str:
    """Return the raw HTML between the root header paragraph and the first stem header/table."""
    stem = STEM_HEADER.search(fragment_html)
    if stem:
        header_html = fragment_html[:stem.start()]
    else:
        table_m = re.search(r'<table', fragment_html)
        header_html = fragment_html[:table_m.start()] if table_m else fragment_html
    return header_html.strip()


def extract_stem_labels(fragment_html: str):
    """Return dict of roman stem -> raw HTML label area including the roman header, up to the stem table."""
    labels = {}
    headers = list(STEM_HEADER.finditer(fragment_html))
    for i, m in enumerate(headers):
        roman = m.group(1)
        start = m.start()
        end_region = headers[i+1].start() if i + 1 < len(headers) else len(fragment_html)
        region = fragment_html[start:end_region]
        table = re.search(r'<table', region)
        end = table.start() if table else len(region)
        label_html = region[:end].strip()
        labels[roman] = label_html
    return labels


def html_to_tokens(parser: CleanTuroyoParser, html: str):
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    pairs = parser.walk_and_extract(soup)
    tokens = []
    for is_italic, text in pairs:
        if text and text.strip():
            tokens.append({ 'italic': bool(is_italic), 'text': text })
    return tokens


def extract_gloss_html_from_label(label_html: str) -> str:
    """Within label_html that contains roman header + forms + optional gloss, remove the first italic/bold span with forms and return remaining as gloss HTML."""
    try:
        soup = BeautifulSoup(label_html, 'html.parser')
        # Remove the roman header span (contains roman numeral and colon)
        header_span = soup.find('span')
        # More robust: keep all, but focus on removing the first italic/bold forms block
        ib = soup.find('i')
        if ib and ib.find('b') and ib.find('span'):
            ib.decompose()
        # Remaining soup is gloss area (possibly empty)
        gloss_html = str(soup)
        return gloss_html
    except Exception:
        return ''


def main():
    html = SRC_HTML.read_text(encoding='utf-8')
    segments = segment_entries(html)

    parser = CleanTuroyoParser(str(SRC_HTML))

    verbs = []
    stats = defaultdict(int)

    for root, frag in segments:
        try:
            entry = parser.parse_entry(root, frag)
            entry['root'] = root

            # Verb header (verbatim + tokens)
            header_html = extract_lemma_header_raw(frag)
            entry['lemma_header_raw'] = header_html
            entry['lemma_header_tokens'] = html_to_tokens(parser, header_html)

            # Stem labels (verbatim + tokens), plus split gloss
            labels = extract_stem_labels(frag)
            for stem in entry.get('stems', []):
                roman = stem.get('stem') or stem.get('binyan')
                if roman:
                    stem['stem'] = roman
                if 'binyan' in stem:
                    del stem['binyan']
                if roman and roman in labels:
                    label_html = labels[roman]
                    stem['label_raw'] = label_html
                    # Only keep gloss tokens separate; do not duplicate forms here
                    gloss_html = extract_gloss_html_from_label(label_html)
                    stem['label_gloss_tokens'] = html_to_tokens(parser, gloss_html)

            verbs.append(entry)
            stats['ok'] += 1
        except Exception:
            stats['errors'] += 1

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({'verbs': verbs, 'metadata': {'total_verbs': len(verbs), 'source_file': str(SRC_HTML), 'parser_version': 'v5-structured-tokens-gloss-split'}}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✅ Wrote {len(verbs)} verbs → {OUT_JSON}")


if __name__ == '__main__':
    main()
