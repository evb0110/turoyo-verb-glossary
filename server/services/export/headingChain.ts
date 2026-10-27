import type { IDocHeading } from '~~/server/types/export/IDocHeading'
import type { TDocBlock } from '~~/server/types/export/TDocBlock'

// The headings in force after `blocks`, outermost first, starting from those in force before them.
export function headingChain(context: IDocHeading[], blocks: TDocBlock[]): IDocHeading[] {
    const chain = [...context]
    for (const block of blocks) {
        if (block.type !== 'heading') continue
        while (chain.length && chain.at(-1)!.level >= block.level) chain.pop()
        chain.push(block)
    }
    return chain
}
