// @ts-check
import withNuxt from './.nuxt/eslint.config.mjs'

export default withNuxt(
    {
        rules: {
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
            'vue/no-v-html': 'off',

            'no-restricted-imports': ['error', {
                patterns: [{
                    group: ['.*', '../*'],
                    message: 'Relative imports are not allowed. Use absolute imports with ~/ or ~~/ instead.'
                }]
            }],

            'import/no-anonymous-default-export': 'off',
            'import/max-dependencies': 'off',
            'import/no-default-export': 'off'
        }
    },
    {
        files: ['**/*.ts', '**/*.tsx'],
        ignores: ['*.config.ts', '*.config.mts', '*.config.mjs', 'eslint.config.mjs', 'nuxt.config.ts', 'server/db/schema.ts', '**/*.d.ts'],
        rules: {
            '@typescript-eslint/naming-convention': ['error',
                {
                    selector: 'typeAlias',
                    format: ['PascalCase'],
                    custom: {
                        regex: '^T[A-Z]',
                        match: true
                    }
                },
                {
                    selector: 'interface',
                    format: ['PascalCase'],
                    custom: {
                        regex: '^I[A-Z]',
                        match: true
                    }
                }
            ]
        }
    },
    {
        files: ['eslint.config.mjs', 'nuxt.config.ts', '*.config.{js,ts,mjs}', 'server/db/schema.ts'],
        rules: {
            'no-restricted-imports': 'off'
        }
    }
)
