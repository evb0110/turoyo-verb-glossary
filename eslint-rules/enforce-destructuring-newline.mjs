export default {
    meta: {
        type: 'layout',
        docs: {
            description: 'Enforce each property on a new line in destructuring patterns with 2+ properties',
            category: 'Stylistic Issues',
            recommended: true,
        },
        fixable: 'whitespace',
        messages: { expectNewline: 'Property {{ name }} must be on a new line' },
    },
    create(context) {
        return {
            ObjectPattern(node) {
                if (node.properties.length < 2) {
                    return
                }

                const sourceCode = context.sourceCode

                for (let i = 0; i < node.properties.length - 1; i++) {
                    const current = node.properties[i]
                    const next = node.properties[i + 1]

                    const currentLine = current.loc.end.line
                    const nextLine = next.loc.start.line

                    if (currentLine === nextLine) {
                        context.report({
                            node: next,
                            messageId: 'expectNewline',
                            data: { name: next.key?.name || next.type },
                            fix(fixer) {
                                const range = [current.range[1], next.range[0]]
                                const text = sourceCode.text.substring(range[0], range[1])

                                if (text.includes('\n')) {
                                    return null
                                }

                                return fixer.replaceTextRange(range, ',\n    ')
                            },
                        })
                    }
                }
            },
        }
    },
}
