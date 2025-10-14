<script setup lang="ts">
const { checkSession, sessionStatus } = useAuth()

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
