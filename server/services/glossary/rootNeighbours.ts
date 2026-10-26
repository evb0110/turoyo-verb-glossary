import type { IEntryIndex } from '#shared/types/IEntryIndex'

// The roots before and after an entry in glossary order, for previous/next links.
export function rootNeighbours(roots: IEntryIndex[], id: string) {
    const position = roots.findIndex(root => root.id === id)
    const pick = (root: IEntryIndex | undefined) => (root
        ? {
                id: root.id,
                root: root.root,
            }
        : null)
    return {
        previous: position > 0 ? pick(roots[position - 1]) : null,
        next: position >= 0 ? pick(roots[position + 1]) : null,
    }
}
