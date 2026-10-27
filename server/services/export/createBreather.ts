// Long synchronous writing holds up every other request on a server instance. The returned function yields to
// the event loop once at least `sliceMs` have passed since it last did, and is cheap to call often.
export function createBreather(sliceMs = 40): () => Promise<void> {
    let since = performance.now()
    return async () => {
        if (performance.now() - since < sliceMs) return
        await new Promise(resolve => setImmediate(resolve))
        since = performance.now()
    }
}
