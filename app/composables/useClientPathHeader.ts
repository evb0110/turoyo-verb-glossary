import { computed } from 'vue'

export const useClientPathHeader = () => {
    const route = useRoute()

    return computed(() => ({ 'x-client-path': route.fullPath || route.path || '/' }))
}
