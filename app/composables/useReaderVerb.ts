import type { IOccurrence } from '#shared/types/IOccurrence'

export function useReaderVerb() {
    const selected = useState<{ verb: IOccurrence
        token: string } | null>(
        'reader-verb',
        () => null
    )
    return { selected }
}
