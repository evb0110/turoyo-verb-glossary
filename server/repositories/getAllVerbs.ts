import type { IVerb } from '~/types/IVerb'

export async function getAllVerbs() {
    const storage = useStorage('assets:server')
    const keys = await storage.getKeys('verbs')
    return Promise.all(keys.map(key => storage.getItem<IVerb>(key)))
}
