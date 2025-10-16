<script setup lang="ts">
const { isPending } = useAuth()
</script>

<template>
    <div class="min-h-screen bg-background text-foreground pb-6">
        <Navbar/>
        <PendingUserBanner/>

        <main v-if="!isPending" class="pb-6">
            <UContainer class="max-w-5xl mx-auto">
                <slot></slot>
            </UContainer>
        </main>

        <GlobalSearchModal/>
    </div>
</template>
