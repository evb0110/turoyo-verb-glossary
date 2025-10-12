<script setup lang="ts">
// Initialize auth session check on app load (only if not already loaded from SSR)
const { checkSession, sessionStatus } = useAuth()

// Only check session if not already authenticated from SSR
if (import.meta.client && sessionStatus.value !== 'authenticated') {
    checkSession()
}
</script>

<template>
    <UApp :ui="{ primary: 'teal', gray: 'slate' }">
        <NuxtLayout>
            <NuxtPage />
        </NuxtLayout>
    </UApp>
</template>
