<template>
    <a
        v-if="back"
        :href="back"
        class="back-link"
        @click.prevent="router.back()"
    >← {{ backLabel(back) }}</a>
    <NuxtLink v-else-if="fallback" :to="fallback" class="back-link">← {{ fallbackLabel }}</NuxtLink>
</template>

<script setup lang="ts">
import { backLabel } from '~/utils/backLabel'

// Returns to the previous in-app page through the browser history, so it opens at the
// same scroll position. Without in-app history it offers the fallback page, if any.
defineProps<{ fallback?: string
    fallbackLabel?: string }>()
const router = useRouter()
const back = ref<string | null>(null)
onMounted(() => {
    const state = window.history.state as { back?: unknown } | null
    back.value = typeof state?.back === 'string' ? state.back : null
})
</script>
