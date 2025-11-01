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

const editMode = ref(false)
const editableVerb = ref<IVerb | null>(null)

const displayVerb = computed(() => {
    return editMode.value && editableVerb.value ? editableVerb.value : verb.value
})

const stems = computed(() => {
    return (displayVerb.value?.stems || []).filter(Boolean)
})

if (error.value) {
    throw createError({
        statusCode: 404,
        statusMessage: 'Verb not found',
    })
}

useHead({
    title: () => displayVerb.value?.root,
    meta: [
        {
            name: 'description',
            content: displayVerb.value?.etymology?.etymons?.[0]?.meaning || 'Detailed view of a Turoyo verb',
        },
    ],
})
</script>

<template>
    <div class="space-y-6 p-6">
        <div class="flex items-center justify-between">
            <UButton icon="i-heroicons-arrow-left-circle" :to="toBack" variant="ghost">
                Back to verb list
            </UButton>
            <UButton
                v-if="verb"
                icon="i-heroicons-pencil-square"
                :color="editMode ? 'warning' : 'primary'"
                @click="() => {
                    if (editMode) { editMode = false; editableVerb = null }
                    else { editMode = true; editableVerb = structuredClone(verb) }
                }"
            >
                {{ editMode ? 'Exit edit mode' : 'Edit' }}
            </UButton>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="space-y-6">
                <UCard>
                    <template #header>
                        <VerbHeader :verb="displayVerb!"/>
                    </template>

                    <VerbEtymology v-if="displayVerb?.etymology" :etymology="displayVerb?.etymology"/>
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

            <div v-if="editMode" class="lg:sticky lg:top-16 self-start">
                <UCard :ui="{ body: 'space-y-4' }">
                    <VerbInspector
                        :verb="verb!"
                        @applied="v => { editableVerb = v }"
                        @reset="() => { editableVerb = null }"
                    />
                </UCard>
            </div>
        </div>
    </div>
</template>
