export async function readGlossaryAsset<T>(key: string): Promise<T | null> {
    if (import.meta.dev) {
        const { readFile } = await import('node:fs/promises')
        const {
            resolve,
            sep,
        } = await import('node:path')
        const base = resolve(process.cwd(), process.env.NUXT_SITE_FIXTURE === '1' ? '.devkit/site-fixture' : 'server/assets/glossary')
        const file = resolve(base, key)
        if (file.startsWith(base + sep)) {
            try {
                return JSON.parse(await readFile(file, 'utf8')) as T
            }
            catch (error) {
                if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error
                return null
            }
        }
    }
    return await useStorage('assets:server').getItem<T>(`glossary:${key.replaceAll('/', ':')}`)
}
