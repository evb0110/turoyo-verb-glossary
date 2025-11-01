import type { IVerbDatabase } from './IVerbDatabase'
import { SqliteVerbDatabase } from './adapters/SqliteVerbDatabase'
import { PostgresVerbDatabase } from './adapters/PostgresVerbDatabase'

export type VerbDatabaseType = 'sqlite' | 'postgres'

export class VerbDatabaseFactory {
    static create(type?: VerbDatabaseType): IVerbDatabase {
        const dbType = type || (process.env.VERB_DATABASE as VerbDatabaseType) || 'sqlite'

        switch (dbType) {
            case 'sqlite': {
                const dbPath = process.env.VERB_DATABASE_PATH || '.data/db/verbs.db'
                return new SqliteVerbDatabase(dbPath)
            }

            case 'postgres': {
                const connectionString = process.env.VERB_DATABASE_URL
                if (!connectionString) {
                    throw new Error('VERB_DATABASE_URL environment variable required for postgres')
                }
                return new PostgresVerbDatabase(connectionString)
            }

            default:
                throw new Error(`Unknown database type: ${dbType}. Use 'sqlite' or 'postgres'`)
        }
    }
}
