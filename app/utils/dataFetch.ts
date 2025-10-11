/**
 * Unified data fetching utility for SSR and client-side
 * Handles Vercel deployment specifics and fallback strategies
 */

/**
 * Read JSON data from public directory with SSR/client compatibility
 * @param path - Path to the JSON file (e.g., "appdata/api/verbs/root.json")
 * @returns Parsed JSON data
 */
export async function readPublicJson<T>(path: string): Promise<T> {
    const normalized = path.startsWith('/') ? path : `/${path}`

    // On server: use internal API (Nitro assets storage)
    if (import.meta.server) {
        const withoutLeading = normalized.slice(1)
        const apiRelative = withoutLeading.startsWith('appdata/api/')
            ? withoutLeading.slice('appdata/api/'.length)
            : withoutLeading
        const apiUrl = `/api/data/${apiRelative}`

        // On Vercel, prefer absolute fetch from the deployment origin to bypass any server route issues
        const vercelHost = process.env.VERCEL_URL
        if (vercelHost) {
            try {
                const absolute = `https://${vercelHost}${normalized}`
                return await $fetch<T>(absolute)
            }
            catch {
                // fall through to internal API
            }
        }

        try {
            return await $fetch<T>(apiUrl)
        }
        catch {
            // Fallback to static path if route is unavailable
            return await $fetch<T>(normalized)
        }
    }

    // On client: fetch directly from the CDN/static public path
    return await $fetch<T>(normalized)
}
