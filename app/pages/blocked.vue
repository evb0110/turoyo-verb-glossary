<template>
    <main class="auth-page">
        <div class="auth-box stack">
            <h1>Access blocked</h1>
            <p>
                Your account has been blocked by the project team. If you think this is a mistake, please write
                to them.
            </p>
            <p v-if="user?.email" class="muted">
                Signed in as {{ user?.email }}
            </p>
            <button class="quiet" @click="handleSignOut">
                Sign out
            </button>
        </div>
    </main>
</template>

<script setup lang="ts">
useHead({ title: 'Access blocked' })
const {
    signOut,
    user,
} = useAuth()

definePageMeta({ layout: false })

const handleSignOut = async () => {
    await signOut()
}
</script>

<style scoped>
.auth-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.5rem;
}
.auth-box {
    max-width: 30rem;
    gap: 1.2rem;
}
h1 {
    font-size: 2.2rem;
    line-height: 1.2;
}
</style>
