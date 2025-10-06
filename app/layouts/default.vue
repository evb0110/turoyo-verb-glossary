<template>
    <div class="min-h-screen bg-background text-foreground pb-6">
        <Navbar />

        <main class="pb-6">
            <UContainer class="max-w-5xl mx-auto">
                <slot/>
            </UContainer>
        </main>
    </div>
</template>
