// @ts-check
import withNuxt from './.nuxt/eslint.config.mjs'
import enforceDestructuringNewline from './eslint-rules/enforce-destructuring-newline.mjs'
import preferGenericTypeAnnotation from './eslint-rules/prefer-generic-type-annotation.mjs'

export default withNuxt(
    {
        ignores: ['app/components/Editor/**', 'server/db/verbs/**'],
    },
    {
        plugins: {
            'custom-rules': {
                rules: {
                    'prefer-generic-type-annotation': preferGenericTypeAnnotation,
                    'enforce-destructuring-newline': enforceDestructuringNewline,
                },
            },
        },
        rules: {
            '@typescript-eslint/unified-signatures': 'off',
            'custom-rules/prefer-generic-type-annotation': 'error',
            'custom-rules/enforce-destructuring-newline': 'error',
            'vue/html-indent': ['error', 4],
            'vue/max-attributes-per-line': ['error', {
                singleline: 3,
                multiline: 1,
            }],
            'vue/first-attribute-linebreak': ['error', {
                singleline: 'ignore',
                multiline: 'below',
            }],
            'vue/html-closing-bracket-newline': ['error', {
                singleline: 'never',
                multiline: 'always',
                selfClosingTag: {
                    singleline: 'never',
                    multiline: 'always',
                },
            }],
            'vue/html-closing-bracket-spacing': ['error', {
                startTag: 'never',
                endTag: 'never',
                selfClosingTag: 'never',
            }],
            'vue/html-quotes': ['error', 'double'],
            'vue/html-self-closing': ['error', {
                html: {
                    void: 'always',
                    normal: 'never',
                    component: 'always',
                },
                svg: 'always',
                math: 'always',
            }],
            'vue/mustache-interpolation-spacing': ['error', 'always'],
            'vue/no-multi-spaces': 'error',
            'vue/no-spaces-around-equal-signs-in-attribute': 'error',
            'vue/attributes-order': ['error', {
                order: [
                    'DEFINITION',
                    'LIST_RENDERING',
                    'CONDITIONALS',
                    'RENDER_MODIFIERS',
                    'GLOBAL',
                    ['UNIQUE', 'SLOT'],
                    'TWO_WAY_BINDING',
                    'OTHER_DIRECTIVES',
                    'OTHER_ATTR',
                    'EVENTS',
                    'CONTENT',
                ],
            }],
            'vue/block-order': ['error', { order: ['script', 'template', 'style'] }],
            'vue/multi-word-component-names': 'off',
            'vue/no-v-html': 'off',

            'no-restricted-imports': ['error', {
                patterns: [{
                    group: ['.*', '../*'],
                    message: 'Relative imports are not allowed. Use absolute imports with ~/ or ~~/ instead.',
                }],
            }],

            'import/no-anonymous-default-export': 'off',
            'import/max-dependencies': 'off',
            'import/no-default-export': 'off',

            'import/order': ['error', {
                'groups': [
                    'builtin',
                    'external',
                    'internal',
                    ['parent', 'sibling'],
                    'index',
                    'object',
                    'type',
                ],
                'pathGroups': [
                    {
                        pattern: '~/**',
                        group: 'internal',
                        position: 'after',
                    },
                    {
                        pattern: '~~/**',
                        group: 'internal',
                        position: 'after',
                    },
                ],
                'pathGroupsExcludedImportTypes': ['builtin'],
                'newlines-between': 'never',
                'alphabetize': {
                    order: 'asc',
                    caseInsensitive: true,
                },
            }],

            '@stylistic/comma-dangle': ['error', {
                arrays: 'always-multiline',
                objects: 'always-multiline',
                imports: 'always-multiline',
                exports: 'always-multiline',
                functions: 'never',
            }],

            '@stylistic/object-curly-newline': ['error', {
                ObjectExpression: {
                    multiline: true,
                    minProperties: 2,
                },
                ObjectPattern: {
                    multiline: true,
                    minProperties: 2,
                },
                ImportDeclaration: 'never',
                ExportDeclaration: 'never',
            }],

            '@stylistic/object-property-newline': ['error', { allowAllPropertiesOnSameLine: false }],

            '@stylistic/max-len': ['error', {
                code: 120,
                tabWidth: 4,
                comments: 120,
                ignoreComments: false,
                ignoreStrings: true,
                ignoreTemplateLiterals: true,
                ignoreUrls: true,
                ignorePattern: '^\\s*(class=|:class=|v-|@|ref=|key=)',
            }],
        },
    },
    {
        files: ['**/*.ts', '**/*.tsx'],
        ignores: ['*.config.ts', '*.config.mts', '*.config.mjs', 'eslint.config.mjs', 'nuxt.config.ts', 'server/db/schema.ts', '**/*.d.ts'],
        rules: {
            '@typescript-eslint/array-type': ['error', {
                default: 'array-simple',
                readonly: 'array-simple',
            }],

            '@typescript-eslint/naming-convention': ['error',
                {
                    selector: 'typeAlias',
                    format: ['PascalCase'],
                    custom: {
                        regex: '^T[A-Z]',
                        match: true,
                    },
                },
                {
                    selector: 'interface',
                    format: ['PascalCase'],
                    custom: {
                        regex: '^I[A-Z]',
                        match: true,
                    },
                },
            ],
        },
    },
    {
        files: ['eslint.config.mjs', 'nuxt.config.ts', '*.config.{js,ts,mjs}', 'server/db/schema.ts'],
        rules: { 'no-restricted-imports': 'off' },
    },
    {
        files: ['**/*.vue'],
        rules: {
            '@stylistic/max-len': ['error', {
                code: 120,
                tabWidth: 4,
                comments: 120,
                ignoreComments: false,
                ignoreStrings: true,
                ignoreTemplateLiterals: true,
                ignoreUrls: true,
                ignorePattern: 'd="',
            }],
        },
    }
)
