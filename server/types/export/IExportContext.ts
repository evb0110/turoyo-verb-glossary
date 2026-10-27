// What every export states about itself: when it was made and from which glossary snapshot.
export interface IExportContext {
    generated: Date
    snapshot: string // the dated folder of the glossary Word volumes, e.g. "2026-10-21"
}
