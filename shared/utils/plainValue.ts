// A proposal value as text. A few machine proposals carry a list or an object where the data contract has a
// string (e.g. before: { forms, sense_1 }): their parts are listed, a reference by its raw text.
export function plainValue(value: unknown): string {
    if (value === null || value === undefined) return ''
    if (typeof value === 'string') return value
    if (Array.isArray(value)) return value.map(plainValue).filter(Boolean).join('; ')
    if (typeof value === 'object') {
        if ('raw' in value && typeof value.raw === 'string') return value.raw
        return Object.entries(value).map(([key, item]) => `${key}: ${plainValue(item)}`).join('; ')
    }
    return String(value)
}
