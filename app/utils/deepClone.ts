export function deepClone<T>(value: T): T {
    return value == null ? value as unknown as T : JSON.parse(JSON.stringify(value)) as T
}
