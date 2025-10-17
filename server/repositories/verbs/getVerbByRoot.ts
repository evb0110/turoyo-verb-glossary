import type { IVerb } from '#shared/types/IVerb'

export async function getVerbByRoot(root: string) {
    const storage = useStorage('assets:server')
    return storage.getItem<IVerb>(`verbs/${root}.json`)
}
