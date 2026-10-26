// In-page anchor links replace the current history entry instead of adding one, so Back
// (and BackLink) leaves the page rather than stepping back through the anchors. Like native
// fragment navigation, the target then takes focus, so "Skip to content" keeps working.
function focusTarget(id: string) {
    const target = document.getElementById(id)
    if (!target) return
    if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1')
    target.focus({ preventScroll: true })
}
export default defineNuxtPlugin(() => {
    const router = useRouter()
    document.addEventListener('click', (event) => {
        if (event.defaultPrevented || event.button !== 0
            || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
        const link = (event.target as Element | null)?.closest('a[href^="#"]')
        const href = link?.getAttribute('href')
        if (!href || href === '#') return
        event.preventDefault()
        const hash = `#${decodeURIComponent(href.slice(1))}`
        const current = router.currentRoute.value
        if (current.hash === hash) {
            document.getElementById(hash.slice(1))?.scrollIntoView()
            focusTarget(hash.slice(1))
            return
        }
        router.replace({
            path: current.path,
            query: current.query,
            hash,
        }).then((failure) => {
            if (!failure) focusTarget(hash.slice(1))
        })
    })
})
