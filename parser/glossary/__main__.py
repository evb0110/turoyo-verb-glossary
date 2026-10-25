"""Regenerate with: python -m parser.glossary [--source DIR] [--output DIR]."""

import argparse
from collections import Counter
import json

from .parse import OUTPUT, SOURCE, parse_volumes, summary, write_glossary


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--source", default=SOURCE)
    cli.add_argument("--output", default=OUTPUT)
    args = cli.parse_args()
    parsed = parse_volumes(args.source)
    write_glossary(parsed, args.output)
    counts = summary(parsed.entries)
    counts.pop("unknownSenseExampleIds")
    print(json.dumps(counts, ensure_ascii=False, indent=2))
    print("Source diagnostics:", dict(Counter(d["kind"] for d in parsed.diagnostics)))


if __name__ == "__main__":
    main()
