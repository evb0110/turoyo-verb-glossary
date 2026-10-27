import type { IDocRun } from '~~/server/types/export/IDocRun'

// Word's Heading 1–4 and the PDF outline. `id` is the target of internal links and bookmarks.
export interface IDocHeading {
    type: 'heading'
    level: 1 | 2 | 3 | 4
    id: string
    runs: IDocRun[]
}
