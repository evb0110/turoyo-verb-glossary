<script setup lang="ts">
const { checkSession, sessionStatus } = useAuth()

if (import.meta.client && sessionStatus.value === 'idle') {
    checkSession()
}
</script>

<template>
    <UApp :ui="{ primary: 'teal', gray: 'slate' }">
        <NuxtLoadingIndicator/>
        <NuxtLayout>
            <NuxtPage/>
        </NuxtLayout>
    </UApp>
</template>
