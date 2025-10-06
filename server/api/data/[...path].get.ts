export default defineEventHandler(async (event) => {
    const segments = event.context.params?.path

    if (!segments || (Array.isArray(segments) && segments.length === 0)) {
        throw createError({ statusCode: 400, statusMessage: 'Missing data path' })
    }

    const parts = Array.isArray(segments) ? segments : [segments]
    const relativePath = parts.map(s => decodeURIComponent(s)).join('/')

    if (relativePath.includes('..')) {
        throw createError({ statusCode: 400, statusMessage: 'Invalid path' })
    }

    // Prefer Nitro assets storage (works on serverless platforms)
    const storage = useStorage('assets:public')
    const key = `/appdata/api/${relativePath}`
    let raw = await storage.getItemRaw(key)
    if (!raw) {
        const alt = key.startsWith('/') ? key.slice(1) : key
        raw = await storage.getItemRaw(alt)
    }

    if (!raw) {
    // Dev fallback: filesystem, and finally absolute fetch from the same host (Vercel static CDN)
        try {
            const { join } = await import('node:path')
            const { promises: fsp } = await import('node:fs')
            const filePath = join(process.cwd(), 'public', 'appdata', 'api', relativePath)
            const ext = relativePath.split('.').pop()
            if (ext === 'json') {
                setHeader(event, 'content-type', 'application/json; charset=utf-8')
                return await fsp.readFile(filePath, 'utf-8')
            }
            return await fsp.readFile(filePath)
        }
        catch {
            try {
                const proto = getRequestHeader(event, 'x-forwarded-proto') || 'https'
                const host = getRequestHeader(event, 'x-forwarded-host') || getRequestHeader(event, 'host')
                if (!host) throw new Error('no-host')
                const url = `${proto}://${host}/appdata/api/${relativePath}`
                const ext = relativePath.split('.').pop()
                const response = await $fetch(url, { responseType: ext === 'json' ? 'text' : 'arrayBuffer' })
                if (ext === 'json') {
                    setHeader(event, 'content-type', 'application/json; charset=utf-8')
                    return response as string
                }
                return new Uint8Array(response as ArrayBuffer)
            }
            catch {
                throw createError({ statusCode: 404, statusMessage: 'Data file not found' })
            }
        }
    }

    const ext = relativePath.split('.').pop()
    if (ext === 'json') {
        setHeader(event, 'content-type', 'application/json; charset=utf-8')
        // Ensure JSON responses are returned as text, not raw bytes
        return (raw as Buffer).toString('utf-8')
    }

    return raw
})
