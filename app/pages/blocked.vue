<template>
    <main class="auth-page">
        <div class="auth-box">
            <h1>Access blocked</h1>
            <p>
                Your account has been blocked by the project team. If you think this is a mistake, please write
                to them.
            </p>
            <p v-if="user?.email" class="muted">
                Signed in as {{ user?.email }}
            </p>
            <button class="btn" @click="handleSignOut">
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
    display: grid;
    justify-items: start;
    gap: 0.75rem;
    max-width: 26rem;
}
</style>
