<template>
    <p>Opening the help guide…</p>
</template>

<script setup lang="ts">
await navigateTo('/help', {
    redirectCode: 301,
    replace: true,
})
</script>
