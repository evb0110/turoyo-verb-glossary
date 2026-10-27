// One part of an export too large for a single download, as the server lists them.
export interface IExportPart {
    part: number
    label: string
    bytes: number
}
