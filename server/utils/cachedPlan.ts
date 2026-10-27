import type { IExportPlan } from '~~/server/types/export/IExportPlan'

// Written documents are kept per server instance under a key that names their scope, format and data revision,
// so a manifest and the parts it lists are written once. At most ENTRIES plans (finished or still being written)
// and LIMIT bytes are kept, each plan counting its files plus OVERHEAD; the least recently used go first,
// including a plan that has just finished. A plan larger than LIMIT is served but not kept. Concurrent requests
// share one plan. Development plans afresh, as the data may be regenerated while the server runs.
const LIMIT = 64 * 1024 * 1024
const ENTRIES = 64
const OVERHEAD = 4096
const cache = new Map<string, Promise<IExportPlan>>()
const sizes = new Map<string, number>()

function prune() {
    let total = [...sizes.values()].reduce((sum, size) => sum + size, 0)
    for (const key of cache.keys()) {
        if (total <= LIMIT && cache.size <= ENTRIES) break
        total -= sizes.get(key) || 0
        sizes.delete(key)
        cache.delete(key)
    }
}

export function cachedPlan(key: string, make: () => Promise<IExportPlan>): Promise<IExportPlan> {
    if (import.meta.dev) return make()
    const hit = cache.get(key)
    if (hit) {
        cache.delete(key)
        cache.set(key, hit)
        return hit
    }
    // A plan is accounted for only while this promise is still the cached one: one evicted while it was being
    // written leaves no trace when it finishes.
    const value: Promise<IExportPlan> = make().then((plan) => {
        if (cache.get(key) === value) {
            const size = OVERHEAD + plan.parts.reduce((sum, part) => sum + part.bytes.length, 0)
            if (size > LIMIT) cache.delete(key)
            else {
                sizes.set(key, size)
                prune()
            }
        }
        return plan
    }, (error) => {
        if (cache.get(key) === value) {
            cache.delete(key)
            sizes.delete(key)
        }
        throw error
    })
    cache.set(key, value)
    prune()
    return value
}
