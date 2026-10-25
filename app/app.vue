<template>
    <UApp>
        <NuxtLoadingIndicator color="var(--accent)"/>
        <NuxtLayout><NuxtPage/></NuxtLayout>
    </UApp>
</template>

<script setup lang="ts">
const {
    checkSession,
    sessionStatus,
} = useAuth()
if (import.meta.client && sessionStatus.value === 'idle') checkSession()
</script>
