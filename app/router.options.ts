import { START_LOCATION } from 'vue-router'
import type { RouterConfig } from '@nuxt/schema'
import type { RouteLocationNormalized } from 'vue-router'

function hashElement(hash: string) {
    if (!hash) return null
    try {
        return document.getElementById(decodeURIComponent(hash.slice(1)))
    }
    catch {
        return document.getElementById(hash.slice(1))
    }
}

// A reader link `/texts/:id?v=N` opens at verse N, placed a third of the way down.
function verseElement(to: RouteLocationNormalized) {
    const verse = Number(to.query.v)
    return to.path.startsWith('/texts/') && to.query.v !== undefined && Number.isSafeInteger(verse)
        ? document.getElementById(`verse-${verse}`)
        : null
}

// Nuxt's default scrolls to the top after the page has loaded, which overrode any
// verse scroll done in the page itself. This keeps the default for ordinary pages,
// restores the saved position on Back and Forward, and resolves verse and hash targets
// only once the new page is rendered.
export default {
    scrollBehavior(to, from, savedPosition) {
        if (to.path === from.path) {
            const element = to.hash !== from.hash ? hashElement(to.hash) : null
            return element
                ? {
                        el: element,
                        top: 12,
                    }
                : false
        }
        if (to.meta.scrollToTop === false) return false
        const position = () => {
            if (savedPosition) return savedPosition
            const verse = verseElement(to)
            if (verse) return {
                el: verse,
                top: Math.round(window.innerHeight / 3),
            }
            const element = hashElement(to.hash)
            return element
                ? {
                        el: element,
                        top: 12,
                    }
                : {
                        left: 0,
                        top: 0,
                    }
        }
        const nuxtApp = useNuxtApp()
        return new Promise((resolve) => {
            if (from === START_LOCATION) {
                resolve(position())
                return
            }
            nuxtApp.hooks.hookOnce('page:loading:end', () => {
                requestAnimationFrame(() => resolve(position()))
            })
        })
    },
} satisfies RouterConfig
