<script lang="ts" setup>
const route = useRoute()

const toBack = computed(() => {
    return {
        path: '/',
        query: route.query,
    }
})

const {
    data: verb,
    error,
} = await useFetch(() => `/api/verb/${route.params.root}`)

const stems = computed(() => {
    return (verb.value?.stems || []).filter(Boolean)
})

if (error.value) {
    throw createError({
        statusCode: 404,
        statusMessage: 'Verb not found',
    })
}

useHead({
    title: () => verb.value?.root,
    meta: [
        {
            name: 'description',
            content: verb.value?.etymology?.etymons?.[0]?.meaning || 'Detailed view of a Turoyo verb',
        },
    ],
})
</script>

<template>
    <div class="space-y-6 p-6">
        <div class="flex justify-end">
            <UButton icon="i-heroicons-arrow-left-circle" :to="toBack" variant="ghost">
                Back to verb list
            </UButton>
        </div>

        <UCard>
            <template #header>
                <VerbHeader :verb="verb!"/>
            </template>

            <VerbEtymology v-if="verb?.etymology" :etymology="verb?.etymology"/>
        </UCard>

        <div class="space-y-4">
            <div class="flex items-center justify-between">
                <h2 class="text-xl font-semibold">
                    Stems
                </h2>
            </div>

            <div class="space-y-4">
                <VerbStemCard
                    v-for="stem in stems"
                    :key="stem.stem"
                    :stem="stem"
                />
            </div>
        </div>
    </div>
</template>
