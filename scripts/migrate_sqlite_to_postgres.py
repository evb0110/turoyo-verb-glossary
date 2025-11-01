#!/usr/bin/env python3
"""
Migrate verb data from SQLite to Neon Postgres.

This script is for future use when you're ready to migrate from SQLite to Postgres.

Prerequisites:
1. Install psycopg2: pip3 install psycopg2-binary
2. Set environment variable: export VERB_DATABASE_URL="postgresql://user:pass@host/db"

Usage:
    export VERB_DATABASE_URL="postgresql://..."
    python3 scripts/migrate_sqlite_to_postgres.py

This script is idempotent - safe to re-run multiple times.
"""

import sqlite3
import json
import os
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extras import Json
except ImportError:
    print('❌ Error: psycopg2 not installed')
    print('   Install with: pip3 install psycopg2-binary')
    exit(1)

def migrate_sqlite_to_postgres():
    db_url = os.getenv('VERB_DATABASE_URL')
    if not db_url:
        print('❌ Error: VERB_DATABASE_URL environment variable not set')
        print('   Example: export VERB_DATABASE_URL="postgresql://user:pass@host/db"')
        return 1

    sqlite_path = Path('.data/db/verbs.db')
    if not sqlite_path.exists():
        print(f'❌ Error: SQLite database not found: {sqlite_path}')
        print('   Please run migration first: python3 scripts/migrate_json_to_sqlite.py')
        return 1

    print()
    print('=' * 60)
    print('Migrating from SQLite to Postgres')
    print('=' * 60)
    print(f'Source:      {sqlite_path}')
    print(f'Destination: Neon Postgres')
    print()

    sqlite_conn = sqlite3.connect(str(sqlite_path))
    sqlite_cursor = sqlite_conn.cursor()

    sqlite_cursor.execute('SELECT COUNT(*) FROM verbs')
    total = sqlite_cursor.fetchone()[0]

    print(f'Total verbs to migrate: {total}')
    print()

    try:
        pg_conn = psycopg2.connect(db_url)
        pg_cursor = pg_conn.cursor()

        pg_cursor.execute('''
            CREATE TABLE IF NOT EXISTS verbs (
                root TEXT PRIMARY KEY,
                etymology JSONB,
                stems JSONB NOT NULL,
                idioms JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')

        pg_cursor.execute('CREATE INDEX IF NOT EXISTS idx_root ON verbs(root)')
        pg_cursor.execute('CREATE INDEX IF NOT EXISTS idx_etymology_gin ON verbs USING GIN(etymology)')

        pg_conn.commit()

        sqlite_cursor.execute('SELECT root, etymology, stems, idioms FROM verbs ORDER BY root')

        inserted = 0
        updated = 0
        errors = []

        for i, row in enumerate(sqlite_cursor, 1):
            root, etymology, stems, idioms = row

            try:
                pg_cursor.execute('SELECT root FROM verbs WHERE root = %s', (root,))
                exists = pg_cursor.fetchone() is not None

                pg_cursor.execute('''
                    INSERT INTO verbs (root, etymology, stems, idioms)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (root) DO UPDATE SET
                        etymology = EXCLUDED.etymology,
                        stems = EXCLUDED.stems,
                        idioms = EXCLUDED.idioms
                ''', (
                    root,
                    Json(json.loads(etymology)) if etymology else None,
                    Json(json.loads(stems)),
                    Json(json.loads(idioms)) if idioms else None,
                ))

                if exists:
                    updated += 1
                else:
                    inserted += 1

                if i % 100 == 0:
                    print(f'  Progress: {i}/{total} ({i*100//total}%) - {inserted} inserted, {updated} updated')
                    pg_conn.commit()

            except Exception as e:
                errors.append((root, str(e)))

        pg_conn.commit()

        pg_cursor.execute('SELECT COUNT(*) FROM verbs')
        final_count = pg_cursor.fetchone()[0]

        print()
        print('=' * 60)
        print('✅ Migration Complete!')
        print('=' * 60)
        print(f'Total verbs processed: {total}')
        print(f'New verbs inserted:    {inserted}')
        print(f'Existing verbs updated: {updated}')
        print(f'Errors:                {len(errors)}')
        print(f'Final database count:  {final_count}')
        print()

        if errors:
            print('❌ Errors encountered:')
            for root, error in errors[:10]:
                print(f'  - {root}: {error}')
            if len(errors) > 10:
                print(f'  ... and {len(errors) - 10} more errors')
            print()

        print('Next steps:')
        print('1. Update environment: VERB_DATABASE=postgres')
        print('2. Update Vercel dashboard with VERB_DATABASE_URL')
        print('3. Deploy: git push')
        print()

        pg_conn.close()

    except Exception as e:
        print(f'❌ Error connecting to Postgres: {e}')
        return 1

    finally:
        sqlite_conn.close()

    return 0 if len(errors) == 0 else 1

if __name__ == '__main__':
    exit(migrate_sqlite_to_postgres())
