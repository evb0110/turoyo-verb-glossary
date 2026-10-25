<template>
    <p>Opening the glossary…</p>
</template>

<script setup lang="ts">
const route = useRoute()
await navigateTo(
    {
        path: '/glossary',
        query: route.query,
    },
    {
        redirectCode: 301,
        replace: true,
    }
)
</script>
