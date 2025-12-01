import { neon } from '@neondatabase/serverless'
import type { IVerb } from '#shared/types/IVerb'
import type { IVerbDatabase } from '../IVerbDatabase'

export class PostgresVerbDatabase implements IVerbDatabase {
    private sql: ReturnType<typeof neon>
    private schemaInitialized = false

    constructor(connectionString: string) {
        this.sql = neon(connectionString)
    }

    async ensureSchema(): Promise<void> {
        if (this.schemaInitialized) {
            return
        }

        await this.sql`
            CREATE TABLE IF NOT EXISTS verbs (
                root TEXT PRIMARY KEY,
                etymology JSONB,
                cross_reference TEXT,
                stems JSONB NOT NULL,
                idioms JSONB,
                created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW() NOT NULL
            )
        `

        await this.sql`
            CREATE INDEX IF NOT EXISTS idx_root ON verbs(root)
        `

        await this.sql`
            CREATE INDEX IF NOT EXISTS idx_etymology_gin ON verbs USING GIN(etymology)
        `

        this.schemaInitialized = true
    }

    async findByRoot(root: string): Promise<IVerb | null> {
        await this.ensureSchema()

        const rows = await this.sql`
            SELECT * FROM verbs WHERE root = ${root}
        ` as any[]

        return rows.length > 0 ? this.rowToVerb(rows[0]) : null
    }

    async findAll(): Promise<IVerb[]> {
        await this.ensureSchema()

        const rows = await this.sql`
            SELECT * FROM verbs ORDER BY root
        ` as any[]

        return rows.map(row => this.rowToVerb(row))
    }

    async searchByRoot(query: string): Promise<IVerb[]> {
        await this.ensureSchema()

        const rows = await this.sql`
            SELECT * FROM verbs
            WHERE root ILIKE ${'%' + query + '%'}
            ORDER BY root
        ` as any[]

        return rows.map(row => this.rowToVerb(row))
    }

    async getRoots(): Promise<string[]> {
        await this.ensureSchema()

        const rows = await this.sql`
            SELECT root FROM verbs ORDER BY root
        ` as any[]
        return rows.map((r: any) => r.root as string)
    }

    async count(): Promise<number> {
        await this.ensureSchema()

        const rows = await this.sql`
            SELECT COUNT(*) as count FROM verbs
        ` as any[]
        return Number(rows[0].count)
    }

    async upsertVerb(verb: IVerb): Promise<void> {
        await this.ensureSchema()

        await this.sql`
            INSERT INTO verbs (root, etymology, cross_reference, stems, idioms)
            VALUES (
                ${verb.root},
                ${verb.etymology ? JSON.stringify(verb.etymology) : null},
                ${verb.cross_reference},
                ${JSON.stringify(verb.stems)},
                ${verb.idioms ? JSON.stringify(verb.idioms) : null}
            )
            ON CONFLICT (root) DO UPDATE SET
                etymology = EXCLUDED.etymology,
                cross_reference = EXCLUDED.cross_reference,
                stems = EXCLUDED.stems,
                idioms = EXCLUDED.idioms,
                updated_at = NOW()
        `
    }

    async upsertMany(verbs: IVerb[]): Promise<void> {
        await this.ensureSchema()

        for (const verb of verbs) {
            await this.upsertVerb(verb)
        }
    }

    async deleteAll(): Promise<void> {
        await this.ensureSchema()

        await this.sql`DELETE FROM verbs`
    }

    async close(): Promise<void> {
    }

    private rowToVerb(row: any): IVerb {
        return {
            root: row.root,
            etymology: row.etymology,
            cross_reference: row.cross_reference,
            stems: row.stems,
            idioms: row.idioms,
        }
    }
}
