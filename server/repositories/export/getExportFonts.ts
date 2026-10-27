import { cachedAsset } from '~~/server/repositories/glossary/cachedAsset'
import type { IExportFonts } from '~~/server/types/export/IExportFonts'

// The site's Gentium Plus files, bundled as server assets (nuxt.config.ts: nitro.serverAssets "fonts").
export const getExportFonts = cachedAsset(async (): Promise<IExportFonts> => {
    const storage = useStorage('assets:fonts')
    const [regular, italic] = await Promise.all([
        storage.getItemRaw<Uint8Array>('GentiumPlus-Regular.ttf'),
        storage.getItemRaw<Uint8Array>('GentiumPlus-Italic.ttf'),
    ])
    if (!regular || !italic) throw new Error('The Gentium Plus fonts are missing from the server assets.')
    return {
        regular,
        italic,
    }
})
