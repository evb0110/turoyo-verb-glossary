// Minimal RFC 6902-like patch generator for objects/arrays composed of primitives and objects.
// It emits add/replace/remove operations. Not fully compliant, but sufficient for PoC diffs.

type TJSONValue = null | boolean | number | string | TJSONArray | IJSONObject
interface IJSONObject { [key: string]: TJSONValue }
type TJSONArray = TJSONValue[]

export interface IJsonPatchOp {
    op: 'add' | 'replace' | 'remove'
    path: string
    value?: TJSONValue
}

function isObject(value: unknown): value is IJSONObject {
    return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function encodePathSegment(seg: string): string {
    return seg.replace(/~/g, '~0').replace(/\//g, '~1')
}

export function diffJson(original: TJSONValue, edited: TJSONValue, basePath = ''): IJsonPatchOp[] {
    const ops: IJsonPatchOp[] = []

    if (Array.isArray(original) && Array.isArray(edited)) {
        const max = Math.max(original.length, edited.length)
        for (let i = 0; i < max; i++) {
            const path = `${basePath}/${i}`
            if (i >= original.length) {
                ops.push({
                    op: 'add',
                    path,
                    value: edited[i] as TJSONValue,
                })
            }
            else if (i >= edited.length) {
                ops.push({
                    op: 'remove',
                    path,
                })
            }
            else {
                ops.push(...diffJson(original[i] as TJSONValue, edited[i] as TJSONValue, path))
            }
        }
        return ops
    }

    if (isObject(original) && isObject(edited)) {
        const keys = new Set([...Object.keys(original), ...Object.keys(edited)])
        for (const key of keys) {
            const path = `${basePath}/${encodePathSegment(key)}`
            if (!(key in edited)) {
                ops.push({
                    op: 'remove',
                    path,
                })
                continue
            }
            if (!(key in original)) {
                ops.push({
                    op: 'add',
                    path,
                    value: edited[key] as TJSONValue,
                })
                continue
            }
            ops.push(...diffJson(original[key] as TJSONValue, edited[key] as TJSONValue, path))
        }
        return ops
    }

    // Primitive change or type change
    if (JSON.stringify(original) !== JSON.stringify(edited)) {
        ops.push({
            op: 'replace',
            path: basePath || '/',
            value: edited,
        })
    }
    return ops
}
