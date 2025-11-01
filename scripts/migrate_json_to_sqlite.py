#!/usr/bin/env python3
"""
Migrate verb JSON files to SQLite database.

Workflow:
1. Parser generates JSON files: .devkit/analysis/docx_v2_verbs/*.json
2. Run this script to migrate JSON → SQLite
3. SQLite database ready for use: .data/db/verbs.db

Usage:
    python3 scripts/migrate_json_to_sqlite.py

This script is idempotent - safe to re-run multiple times.
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

def migrate_json_to_sqlite():
    json_dir = Path('.devkit/analysis/docx_v2_verbs')
    db_path = Path('.data/db/verbs.db')

    if not json_dir.exists():
        print(f'❌ Error: JSON directory not found: {json_dir}')
        print('   Please run the parser first: python3 parser/parse_docx_production.py')
        return 1

    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verbs (
            root TEXT PRIMARY KEY,
            etymology TEXT,
            cross_reference TEXT,
            stems TEXT NOT NULL,
            uncertain INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_root ON verbs(root)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_root_search ON verbs(root COLLATE NOCASE)')

    cursor.execute('PRAGMA journal_mode=WAL')

    json_files = list(json_dir.glob('*.json'))
    total = len(json_files)

    if total == 0:
        print(f'❌ Error: No JSON files found in {json_dir}')
        return 1

    print()
    print('=' * 60)
    print('Migrating JSON files to SQLite database')
    print('=' * 60)
    print(f'Source:      {json_dir}')
    print(f'Destination: {db_path}')
    print(f'Total files: {total}')
    print()

    inserted = 0
    updated = 0
    errors = []

    for i, json_file in enumerate(json_files, 1):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                verb = json.load(f)

            cursor.execute('SELECT root FROM verbs WHERE root = ?', (verb['root'],))
            exists = cursor.fetchone() is not None

            cursor.execute('''
                INSERT OR REPLACE INTO verbs (root, etymology, cross_reference, stems, uncertain)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                verb['root'],
                json.dumps(verb.get('etymology')) if verb.get('etymology') else None,
                verb.get('cross_reference'),
                json.dumps(verb['stems']),
                1 if verb.get('uncertain') else 0,
            ))

            if exists:
                updated += 1
            else:
                inserted += 1

            if i % 100 == 0:
                print(f'  Progress: {i}/{total} ({i*100//total}%) - {inserted} inserted, {updated} updated')
                conn.commit()

        except Exception as e:
            errors.append((json_file.name, str(e)))

    conn.commit()

    cursor.execute('SELECT COUNT(*) FROM verbs')
    final_count = cursor.fetchone()[0]

    conn.close()

    print()
    print('=' * 60)
    print('✅ Migration Complete!')
    print('=' * 60)
    print(f'Total files processed: {total}')
    print(f'New verbs inserted:    {inserted}')
    print(f'Existing verbs updated: {updated}')
    print(f'Errors:                {len(errors)}')
    print(f'Final database count:  {final_count}')
    print(f'Database size:         {db_path.stat().st_size / 1024 / 1024:.2f} MB')
    print(f'Database path:         {db_path}')
    print()

    if errors:
        print('❌ Errors encountered:')
        for filename, error in errors:
            print(f'  - {filename}: {error}')
        print()

    print('Next steps:')
    print('1. Test locally:  VERB_DATABASE=sqlite pnpm dev')
    print('2. Deploy:        git add .data/db/verbs.db && git push')
    print()

    return 0 if len(errors) == 0 else 1

if __name__ == '__main__':
    exit(migrate_json_to_sqlite())
