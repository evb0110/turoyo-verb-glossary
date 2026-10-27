// One download of a document, written and measured.
export interface IPlannedPart {
    part: number
    label: string // the first and last section in it, e.g. "ʔ – h"; empty for a document in one part
    fileName: string // with extension
    bytes: Buffer
}
