<template>
    <p v-if="isPending" class="pending" role="status">
        <strong>Your account is waiting for approval.</strong>
        The project team will approve it soon; you will then see the glossary and the suggested changes.
    </p>
</template>

<script setup lang="ts">
const { isPending } = useAuth()
</script>

<style scoped>
.pending {
  padding: 0.75rem 0;
}
</style>
