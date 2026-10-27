import type { IPlannedPart } from '~~/server/types/export/IPlannedPart'

// A document as it is downloaded: one part, or several that together hold it, each within the response limit.
// `revision` names the data it was made from; a part is only served for the revision its manifest listed.
export interface IExportPlan {
    revision: string
    parts: IPlannedPart[]
    milliseconds: number
}
