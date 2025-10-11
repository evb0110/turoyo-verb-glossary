/**
 * Type declarations for CSS Custom Highlight API
 * https://www.w3.org/TR/css-highlight-api-1/
 */

interface Highlight {
    add(range: AbstractRange): void
    delete(range: AbstractRange): boolean
    clear(): void
    has(range: AbstractRange): boolean
    readonly size: number
    forEach(callback: (range: AbstractRange, range2: AbstractRange, highlight: Highlight) => void): void
    [Symbol.iterator](): IterableIterator<AbstractRange>
}

interface HighlightConstructor {
    new (...initialRanges: AbstractRange[]): Highlight
    prototype: Highlight
}

interface CSSNamespace {
    highlights: Map<string, Highlight>
}

interface Window {
    Highlight: HighlightConstructor
}

declare const CSS: CSSNamespace
