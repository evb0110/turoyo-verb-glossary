<template>
    <div>
        <UModal
            v-if="open"
            v-model:open="open"
            title="Quick search"
        >
            <template #body>
                <div class="">
                    <UInput
                        ref="inputRef"
                        v-model="query"
                        icon="i-heroicons-magnifying-glass"
                        :placeholder="placeholder"
                        class="w-full"
                        @keydown.enter.prevent="submit"
                    />
                    <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                        <div>
                            Press Enter to search
                        </div>
                    </div>
                </div>
            </template>
        </UModal>
    </div>

    <UButton
        class="sr-only"
        aria-hidden="true"
        tabindex="-1"
        @click="open = true"
    />
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()

const open = ref(false)
const query = ref('')

const inputRef = ref()

const placeholder = computed(() => {
    return 'Search verbs…'
})

function onKeydown(e: KeyboardEvent) {
    const target = e.target as HTMLElement | null
    const tag = (target?.tagName || '').toLowerCase()
    const isEditable = target && (
        tag === 'input'
        || tag === 'textarea'
        || (target as HTMLElement).isContentEditable
    )
    if (isEditable) return

    const isMac = navigator.platform.toUpperCase().includes('MAC')
    const metaPressed = isMac ? e.metaKey : e.ctrlKey
    if (metaPressed && (e.key === 'k' || e.key === 'K')) {
        e.preventDefault()
        open.value = true
        nextTick(() => {
            const el = (inputRef.value as any)?.$el?.querySelector?.('input') || (inputRef.value as any)
            if (el && typeof el.focus === 'function') el.focus()
        })
    }
}

onMounted(() => {
    window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
    window.removeEventListener('keydown', onKeydown)
})

function submit() {
    const q = query.value.trim()
    if (!q || q.length < 2) return

    const currentQuery = route.query
    const type = (currentQuery.type as string) || 'roots'
    const regex = (currentQuery.regex as string) || 'on'
    const caseParam = (currentQuery.case as string) || 'off'

    open.value = false

    console.log({
        q,
        type,
        regex,
        case: caseParam
    })

    router.push({
        path: '/',
        query: {
            q,
            type,
            regex,
            case: caseParam
        }
    })
}
</script>

<style scoped>
</style>
