export function matchesRoutePattern(path: string, patterns: readonly string[]): boolean {
    return patterns.some(pattern => path === pattern || path.startsWith(`${pattern}/`))
}
