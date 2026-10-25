export function plainProposalText(text: string) {
    return text
        .replace(/\bboxes\b/giu, 'forms')
        .replace(/\bbox\b/giu, 'form')
        .replace(/\bsenses\b/giu, 'meanings')
        .replace(/\bsense\b/giu, 'meaning')
        .replace(/\bagents?\b/giu, 'machine')
        .replace(/\boccurrences\b/giu, 'uses in the texts')
        .replace(/\boccurrence\b/giu, 'use in the text')
        .replace(/\bbinyan\b/giu, 'stem')
}
