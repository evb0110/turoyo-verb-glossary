import { VerbDatabaseFactory } from './VerbDatabaseFactory'
import type { IVerbDatabase } from './IVerbDatabase'

let verbDatabase: IVerbDatabase | null = null

export function getVerbDatabase(): IVerbDatabase {
    if (!verbDatabase) {
        verbDatabase = VerbDatabaseFactory.create()
    }
    return verbDatabase
}

export function setVerbDatabase(db: IVerbDatabase): void {
    verbDatabase = db
}

export async function closeVerbDatabase(): Promise<void> {
    if (verbDatabase) {
        await verbDatabase.close()
        verbDatabase = null
    }
}

export type { IVerbDatabase } from './IVerbDatabase'
export type { VerbDatabaseType } from './VerbDatabaseFactory'
