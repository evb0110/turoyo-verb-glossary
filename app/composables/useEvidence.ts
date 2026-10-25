export function useEvidence() {
    const selected = useState<{ textId: string
        v: number
        cite: string } | null>('evidence', () => null)
    function open(textId: string, v: number, cite: string) {
        selected.value = {
            textId,
            v,
            cite,
        }
    }
    return {
        selected,
        open,
    }
}
