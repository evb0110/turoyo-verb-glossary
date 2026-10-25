<template>
    <div v-if="isPending" class="pending" role="status">
        <strong>Your account is waiting for approval.</strong>
        The project team will approve it soon; you will then see the glossary and the suggested changes.
    </div>
</template>

<script setup lang="ts">
const { isPending } = useAuth()
</script>

<style scoped>
.pending {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--rule);
    background: var(--panel);
    text-align: center;
}
</style>
