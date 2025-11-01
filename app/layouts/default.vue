<script setup lang="ts">
const { isPending } = useAuth()
const containerWide = useContainerWide()
const containerClass = computed(() => (
    containerWide.value
        ? 'max-w-[1400px] mx-auto transition-all duration-300'
        : 'max-w-5xl mx-auto transition-all duration-300'
))
</script>

<template>
    <div class="min-h-screen bg-background text-foreground pb-6">
        <Navbar/>
        <PendingUserBanner/>

        <main v-if="!isPending" class="pb-6">
            <UContainer :class="containerClass">
                <slot></slot>
            </UContainer>
        </main>

        <GlobalSearchModal/>
    </div>
</template>
