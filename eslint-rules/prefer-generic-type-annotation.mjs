export default {
    meta: {
        type: 'suggestion',
        docs: {
            description: 'Enforce generic type syntax over return type annotations for composition API functions',
            category: 'Stylistic Issues',
            recommended: true,
        },
        fixable: null,
        messages: { useGenericSyntax: 'Use generic type syntax {{functionName}}<Type> instead of return type annotation. Example: {{functionName}}<SomeType>(() => {})' },
    },
    create(context) {
        const compositionFunctions = new Set(['computed', 'ref', 'watch', 'watchEffect', 'provide', 'inject'])

        return {
            CallExpression(node) {
                const calleeName = node.callee.type === 'Identifier' ? node.callee.name : null

                if (!calleeName || !compositionFunctions.has(calleeName)) {
                    return
                }

                const firstArg = node.arguments[0]
                if (!firstArg || firstArg.type !== 'ArrowFunctionExpression') {
                    return
                }

                if (firstArg.returnType) {
                    context.report({
                        node: firstArg.returnType,
                        messageId: 'useGenericSyntax',
                        data: { functionName: calleeName },
                    })
                }
            },
        }
    },
}
