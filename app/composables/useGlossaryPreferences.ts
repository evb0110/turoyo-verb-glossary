export function useGlossaryPreferences() {
    const viewCookie = useCookie<'sense' | 'box'>('glossary-example-view', { sameSite: 'lax' })
    const layerCookie = useCookie<'glossary' | 'with' | 'proposals'>('glossary-layer', { sameSite: 'lax' })
    const view = useState<'sense' | 'box'>('glossary-view', () =>
        viewCookie.value === 'box' ? 'box' : 'sense'
    )
    const layer = useState<'glossary' | 'with' | 'proposals'>('glossary-layer-state', () =>
        layerCookie.value === 'glossary' || layerCookie.value === 'proposals'
            ? layerCookie.value
            : 'with'
    )
    watch(view, (value) => {
        viewCookie.value = value
    })
    watch(layer, (value) => {
        layerCookie.value = value
    })
    return {
        view,
        layer,
    }
}
