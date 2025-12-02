<script lang="ts" setup>
import { useContainerWide } from '~/composables/useContainerWide'
import { deepClone } from '~/utils/deepClone'
import type { IVerb } from '#shared/types/IVerb'

const route = useRoute()
const clientPathHeader = useClientPathHeader()

const toBack = computed(() => {
    return {
        path: '/',
        query: route.query,
    }
})

const {
    data: verb,
    error,
} = await useFetch(() => `/api/verb/${route.params.root}`, { headers: clientPathHeader.value })

const editMode = ref(false)
const editableVerb = ref<IVerb | null>(null)
const containerWide = useContainerWide()

const displayVerb = computed(() => {
    return editMode.value && editableVerb.value ? editableVerb.value : verb.value
})

const stems = computed(() => {
    return (displayVerb.value?.stems || []).filter(Boolean)
})

watch(editMode, (v) => {
    containerWide.value = v
})

onBeforeUnmount(() => {
    containerWide.value = false
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
                    else { editMode = true; editableVerb = deepClone(verb as any) as any }
                }"
            >
                {{ editMode ? 'Exit edit mode' : 'Edit' }}
            </UButton>
        </div>

        <div class="space-y-6">
            <div class="space-y-6 border-b border-gray-200 dark:border-gray-700 pb-6">
                <VerbHeader :verb="displayVerb!"/>

                <div v-if="editMode" class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div class="md:col-span-1 flex items-center gap-3">
                            <label class="text-sm font-medium">Uncertain</label>
                            <USwitch v-model="(editableVerb as any).uncertain"/>
                        </div>
                        <div class="md:col-span-2">
                            <label class="block text-sm font-medium mb-1">Cross reference</label>
                            <UInput v-model="(editableVerb as any).cross_reference" placeholder="Type a root"/>
                        </div>
                    </div>
                </div>

                <template v-if="!editMode">
                    <VerbEtymology v-if="displayVerb?.etymology" :etymology="displayVerb?.etymology"/>
                </template>
                <template v-else>
                    <EtymologyEditor v-model:etymology="(editableVerb as any).etymology"/>
                </template>
            </div>

            <div class="space-y-4">
                <div class="flex items-center justify-between">
                    <h2 class="text-xl font-semibold" v-if="false">
                        Stems
                    </h2>
                    <UButton
                        v-if="editMode"
                        size="xs"
                        icon="i-heroicons-plus"
                        @click="() => (editableVerb as any).stems.push({ stem: 'I', forms: [], conjugations: {} })"
                    >
                        Add stem
                    </UButton>
                </div>

                <div class="space-y-4">
                    <template v-if="!editMode">
                        <VerbStemCard
                            v-for="stem in stems"
                            :key="stem.stem"
                            :stem="stem"
                        />
                    </template>
                    <template v-else>
                        <StemEditor
                            v-for="(s, sIdx) in (editableVerb as any).stems"
                            :key="sIdx + '-' + s.stem"
                            v-model:stem="(editableVerb as any).stems[sIdx]"
                            @remove="() => (editableVerb as any).stems.splice(sIdx, 1)"
                            @move-up="() => {
                                if (sIdx > 0) {
                                    const arr = (editableVerb as any).stems
                                    const it = arr.splice(sIdx, 1)[0]
                                    arr.splice(sIdx - 1, 0, it)
                                }
                            }"
                            @move-down="() => {
                                const arr = (editableVerb as any).stems
                                if (sIdx < arr.length - 1) {
                                    const it = arr.splice(sIdx, 1)[0]
                                    arr.splice(sIdx + 1, 0, it)
                                }
                            }"
                        />
                    </template>
                </div>
            </div>

            <div
                v-if="displayVerb?.idioms && displayVerb.idioms.length > 0"
                class="space-y-4 border-t border-gray-200 dark:border-gray-700 pt-6"
            >
                <h2 class="text-xl font-semibold">
                    Idiomatic Phrases
                </h2>
                <div class="space-y-3">
                    <div
                        v-for="(idiom, idx) in displayVerb.idioms"
                        :key="idx"
                        class="text-sm leading-relaxed border-l-2 border-gray-200 dark:border-gray-700 pl-3"
                    >
                        {{ idiom }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
