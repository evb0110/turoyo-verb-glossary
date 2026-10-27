// A stretch of text with one style. `link` names the id of a heading in the same document;
// the writers drop the link when that heading is not in the document.
export interface IDocRun {
    text: string
    italic?: boolean
    bold?: boolean
    link?: string
}
