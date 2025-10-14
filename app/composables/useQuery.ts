import { useRouteQuery } from '@vueuse/router'
import type { Ref } from 'vue'

export function useQuery(name: string): Ref<string | null>
export function useQuery(name: string, defaultValue: string): Ref<string>
export function useQuery(name: string, defaultValue: boolean, truthy?: string, falsy?: string): Ref<boolean>
export function useQuery(
    name: string,
    defaultValue?: string | boolean,
    truthy: string = 'on',
    falsy: string = 'off'
): Ref<string | boolean | null> {
    if (defaultValue === undefined) {
        return useRouteQuery<string | null>(name, null)
    }

    if (typeof defaultValue === 'string') {
        return useRouteQuery<string | null, string>(name, null, {
            transform: {
                get: val => val ?? defaultValue,
                set: val => val === defaultValue ? null : val
            }
        })
    }

    const defaultUrlValue = defaultValue ? truthy : falsy
    return useRouteQuery<string | null, boolean>(name, null, {
        transform: {
            get: (val) => {
                if (val === null || val === undefined) {
                    return defaultValue
                }
                return val === truthy
            },
            set: (val) => {
                const targetValue = val ? truthy : falsy
                return targetValue === defaultUrlValue ? null : targetValue
            }
        }
    })
}
