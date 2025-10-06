// @ts-check
import withNuxt from './.nuxt/eslint.config.mjs'

export default withNuxt({
    rules: {
    // Vue-specific formatting
        'vue/html-indent': ['error', 4],
        'vue/max-attributes-per-line': ['error', {
            singleline: 3,
            multiline: 1
        }],
        'vue/first-attribute-linebreak': ['error', {
            singleline: 'ignore',
            multiline: 'below'
        }],
        'vue/html-closing-bracket-newline': ['error', {
            singleline: 'never',
            multiline: 'always',
            selfClosingTag: {
                singleline: 'never',
                multiline: 'always'
            }
        }],
        'vue/multi-word-component-names': 'off',
        'vue/no-v-html': 'off'
    }
})
