const TUROYO_VOWELS = '(?:a|e|i|o|u|ə|ǝ|é|ī|á|í|ó|ú|ā|ē|ō|ū)'

const TUROYO_CONSONANTS = '(?:b|d|f|g|h|k|l|m|n|p|q|r|s|t|v|w|x|y|z|č|ġ|š|ž|ǧ|ʔ|ʕ|ḏ|ḥ|ḷ|ṣ|ṭ|ṯ|ḅ|ḍ|ḳ|ẓ)'

export function expandRegexShortcuts(pattern: string) {
    return pattern
        .replace(/\\v/gi, TUROYO_VOWELS)
        .replace(/\\c/gi, TUROYO_CONSONANTS)
}
