import Database from 'better-sqlite3'
import type { IVerb } from '#shared/types/IVerb'
import type { IVerbDatabase } from '../IVerbDatabase'

export class SqliteVerbDatabase implements IVerbDatabase {
    private db: Database.Database

    constructor(dbPath: string = '.data/db/verbs.db') {
        this.db = new Database(dbPath)
        this.db.pragma('journal_mode = WAL')
        this.initSchema()
    }

    private initSchema(): void {
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS verbs (
                root TEXT PRIMARY KEY,
                etymology TEXT,
                cross_reference TEXT,
                stems TEXT NOT NULL,
                uncertain INTEGER DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_root ON verbs(root);
            CREATE INDEX IF NOT EXISTS idx_root_search ON verbs(root COLLATE NOCASE);
        `)
    }

    async findByRoot(root: string): Promise<IVerb | null> {
        const row = this.db
            .prepare('SELECT * FROM verbs WHERE root = ?')
            .get(root) as any

        if (!row) {
            return null
        }

        return this.rowToVerb(row)
    }

    async findAll(): Promise<IVerb[]> {
        const rows = this.db
            .prepare('SELECT * FROM verbs ORDER BY root')
            .all() as any[]

        return rows.map(row => this.rowToVerb(row))
    }

    async searchByRoot(query: string): Promise<IVerb[]> {
        const rows = this.db
            .prepare(`
                SELECT * FROM verbs
                WHERE root LIKE ? COLLATE NOCASE
                ORDER BY root
            `)
            .all(`%${query}%`) as any[]

        return rows.map(row => this.rowToVerb(row))
    }

    async getRoots(): Promise<string[]> {
        const rows = this.db
            .prepare('SELECT root FROM verbs ORDER BY root')
            .all() as Array<{ root: string }>

        return rows.map(r => r.root)
    }

    async count(): Promise<number> {
        const result = this.db
            .prepare('SELECT COUNT(*) as count FROM verbs')
            .get() as { count: number }

        return result.count
    }

    async upsertVerb(verb: IVerb): Promise<void> {
        this.db
            .prepare(`
                INSERT OR REPLACE INTO verbs (root, etymology, cross_reference, stems, uncertain)
                VALUES (?, ?, ?, ?, ?)
            `)
            .run(
                verb.root,
                verb.etymology ? JSON.stringify(verb.etymology) : null,
                verb.cross_reference,
                JSON.stringify(verb.stems),
                verb.uncertain ? 1 : 0
            )
    }

    async upsertMany(verbs: IVerb[]): Promise<void> {
        const insert = this.db.prepare(`
            INSERT OR REPLACE INTO verbs (root, etymology, cross_reference, stems, uncertain)
            VALUES (?, ?, ?, ?, ?)
        `)

        const transaction = this.db.transaction((verbs: IVerb[]) => {
            for (const verb of verbs) {
                insert.run(
                    verb.root,
                    verb.etymology ? JSON.stringify(verb.etymology) : null,
                    verb.cross_reference,
                    JSON.stringify(verb.stems),
                    verb.uncertain ? 1 : 0
                )
            }
        })

        transaction(verbs)
    }

    async deleteAll(): Promise<void> {
        this.db.prepare('DELETE FROM verbs').run()
    }

    async close(): Promise<void> {
        this.db.close()
    }

    private rowToVerb(row: any): IVerb {
        return {
            root: row.root,
            etymology: row.etymology ? JSON.parse(row.etymology) : null,
            cross_reference: row.cross_reference,
            stems: JSON.parse(row.stems),
            uncertain: row.uncertain === 1,
        }
    }
}
