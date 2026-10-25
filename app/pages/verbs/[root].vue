<template>
    <span class="muted">Opening entry…</span>
</template>

<script setup lang="ts">
const route = useRoute()
const id = String(route.params.root).normalize('NFC').replaceAll(' ', '-')
await navigateTo(
    {
        path: `/entry/${encodeURIComponent(id)}`,
        query: route.query,
        hash: route.hash,
    },
    {
        redirectCode: 301,
        replace: true,
    }
)
</script>
