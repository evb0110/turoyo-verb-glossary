<script setup lang="ts">
// Initialize auth session check on app load
const { checkSession } = useAuth()
checkSession()
</script>

<template>
    <UApp :ui="{ primary: 'teal', gray: 'slate' }">
        <NuxtLayout>
            <NuxtPage />
        </NuxtLayout>
    </UApp>
</template>
