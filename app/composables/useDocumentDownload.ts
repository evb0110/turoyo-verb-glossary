import type { IExportPart } from '~/types/IExportPart'

// The file name from Content-Disposition, preferring the UTF-8 form (filename*=UTF-8''…).
function fileName(header: string | null, fallback: string) {
    const encoded = /filename\*=UTF-8''([^;]+)/iu.exec(header || '')?.[1]
    if (encoded) return decodeURIComponent(encoded)
    return /filename="([^"]+)"/iu.exec(header || '')?.[1] || fallback
}

// Fetches a Word or PDF export and saves it, so the control can be disabled and say "Preparing…" while a
// large document is made. A document that comes in parts answers 300 with its revision and parts; a part of
// a revision that has since changed (a decision was saved meanwhile) answers 409, and the parts are listed anew.
// reset() starts afresh for another scope: the request in flight is cancelled and any late answer to it ignored.
export function useDocumentDownload() {
    const pending = ref('')
    const slow = ref(false)
    const error = ref('')
    const stale = ref(false)
    const parts = ref<{ url: string
        revision: string
        items: IExportPart[] } | null>(null)
    let request = 0
    let controller: AbortController | null = null
    function partUrl(part: number) {
        return parts.value ? `${parts.value.url}&part=${part}&rev=${encodeURIComponent(parts.value.revision)}` : ''
    }
    function reset() {
        request++
        controller?.abort()
        controller = null
        pending.value = ''
        slow.value = false
        error.value = ''
        stale.value = false
        parts.value = null
    }
    async function download(url: string) {
        if (pending.value) return
        const current = ++request
        const own = new AbortController()
        controller = own
        pending.value = url
        error.value = ''
        stale.value = false
        const timer = setTimeout(() => {
            if (current === request) slow.value = true
        }, 400)
        try {
            const response = await fetch(url, {
                credentials: 'same-origin',
                signal: own.signal,
            })
            if (current !== request) return
            if (response.status === 300) {
                const listed = await response.json() as { revision: string
                    parts: IExportPart[] }
                if (current !== request) return
                parts.value = {
                    url,
                    revision: listed.revision,
                    items: listed.parts,
                }
                return
            }
            if (response.status === 409) {
                stale.value = true
                return
            }
            if (!response.ok) throw new Error(String(response.status))
            const blob = await response.blob()
            if (current !== request) return
            const href = URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = href
            link.download = fileName(response.headers.get('content-disposition'), 'turoyo-export')
            document.body.append(link)
            link.click()
            link.remove()
            setTimeout(() => URL.revokeObjectURL(href), 60_000)
        }
        catch {
            if (current === request) error.value = 'The document could not be made. Please try again.'
        }
        finally {
            clearTimeout(timer)
            if (current === request) {
                pending.value = ''
                slow.value = false
                controller = null
            }
        }
    }
    return {
        pending,
        slow,
        error,
        stale,
        parts,
        partUrl,
        download,
        reset,
    }
}
