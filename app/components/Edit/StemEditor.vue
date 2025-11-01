<script lang="ts" setup>
import type { IStem } from '#shared/types/IStem'

const model = defineModel<IStem>('stem', { required: true })
const emit = defineEmits<{ (e: 'remove'): void
    (e: 'moveUp'): void
    (e: 'moveDown'): void }>()

function addGroup() {
    if (!model.value.conjugations) model.value.conjugations = {}
    const base = 'Preterit'
    let i = 0
    while (model.value.conjugations[base + (i ? ` ${i + 1}` : '')]) i++
    const name = base + (i ? ` ${i + 1}` : '')
    model.value.conjugations[name] = []
}

function removeGroup(name: string) {
    const {
        [name]: _,
        ...rest
    } = model.value.conjugations
    model.value.conjugations = rest
}

function renameGroup(oldName: string, newName: string) {
    const name = newName.trim()
    if (!name || name === oldName) return
    const data = model.value.conjugations[oldName]
    const {
        [oldName]: _,
        ...rest
    } = model.value.conjugations
    model.value.conjugations = {
        ...rest,
        [name]: data,
    }
}

function addExample(name: string) {
    model.value.conjugations[name] = [
        ...(model.value.conjugations[name] || []),
        {
            turoyo: '',
            translations: [],
            references: [],
        },
    ]
}

function removeExample(name: string, idx: number) {
    model.value.conjugations[name] = model.value.conjugations[name].filter((_, i) => i !== idx)
}

function moveExample(name: string, from: number, to: number) {
    const arr = model.value.conjugations[name]
    if (from < 0 || from >= arr.length || to < 0 || to > arr.length) return
    const item = arr.splice(from, 1)[0]
    arr.splice(to, 0, item)
}

function formsText(): string {
    return (model.value.forms || []).join(', ')
}

function updateForms(text: string) {
    model.value.forms = String(text || '')
        .split(',')
        .map(x => x.trim())
        .filter(Boolean)
}

function updateExampleTranslations(ex: { translations: string[] }, value: string) {
    ex.translations = String(value || '')
        .split(',')
        .map(x => x.trim())
        .filter(Boolean)
}

function updateExampleReferences(ex: { references: string[] }, value: string) {
    ex.references = String(value || '')
        .split(',')
        .map(x => x.trim())
        .filter(Boolean)
}
</script>

<template>
    <UCard :ui="{ body: 'space-y-4' }">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
                <label class="block text-sm font-medium mb-1">Stem label</label>
                <UInput v-model="model.stem" placeholder="I, II, III, Pa., Af., Detransitive"/>
            </div>
            <div class="md:col-span-2">
                <label class="block text-sm font-medium mb-1">Forms (comma-separated)</label>
                <UInput :model-value="formsText()" :placeholder="formsText()" @update:model-value="updateForms"/>
            </div>
            <div class="md:col-span-3">
                <label class="block text-sm font-medium mb-1">Label (raw)</label>
                <UTextarea v-model="model.label_raw"/>
            </div>
        </div>

        <div class="space-y-2">
            <div class="flex items-center justify-between">
                <h4 class="font-medium">
                    Conjugation groups
                </h4>
                <UButton size="xs" icon="i-heroicons-plus" @click="addGroup">
                    Add group
                </UButton>
            </div>

            <div class="space-y-3">
                <UCard v-for="(examples, name) in model.conjugations" :key="name">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div>
                            <label class="block text-sm font-medium mb-1">Group name</label>
                            <UInput
                                :model-value="name"
                                placeholder="Preterit, Infectum, Imperativ, ..."
                                @update:model-value="v => renameGroup(name as string, v)"
                            />
                        </div>
                    </div>

                    <template #footer>
                        <div class="flex items-center justify-between">
                            <div></div>
                            <UButton
                                size="xs"
                                color="error"
                                icon="i-heroicons-trash"
                                variant="soft"
                                @click="removeGroup(name as string)"
                            >
                                Delete group
                            </UButton>
                        </div>
                    </template>

                    <div class="space-y-2 mt-3">
                        <div class="flex items-center justify-between">
                            <h5 class="font-medium text-sm">
                                Examples
                            </h5>
                            <UButton size="xs" icon="i-heroicons-plus" @click="addExample(name as string)">
                                Add example
                            </UButton>
                        </div>
                        <div class="space-y-3">
                            <div
                                v-for="(ex, eIdx) in examples"
                                :key="eIdx"
                                class="rounded border p-3 space-y-2"
                            >
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    <div>
                                        <label class="block text-sm font-medium mb-1">Text</label>
                                        <UTextarea v-model="ex.text"/>
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium mb-1">Turoyo</label>
                                        <UTextarea v-model="ex.turoyo"/>
                                    </div>
                                </div>
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    <div>
                                        <label class="block text-sm font-medium mb-1">
                                            Translations (comma-separated)
                                        </label>
                                        <UInput
                                            :model-value="ex.translations?.join(', ')"
                                            @update:model-value="v => updateExampleTranslations(ex, v)"
                                        />
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium mb-1">
                                            References (comma-separated)
                                        </label>
                                        <UInput
                                            :model-value="ex.references?.join(', ')"
                                            @update:model-value="v => updateExampleReferences(ex, v)"
                                        />
                                    </div>
                                </div>
                                <div class="flex items-center justify-between">
                                    <div class="flex gap-2">
                                        <UButton
                                            size="xs"
                                            icon="i-heroicons-arrow-up"
                                            :disabled="eIdx===0"
                                            @click="moveExample(name as string, eIdx, eIdx-1)"
                                        >
                                            Up
                                        </UButton>
                                        <UButton
                                            size="xs"
                                            icon="i-heroicons-arrow-down"
                                            :disabled="eIdx===(examples.length-1)"
                                            @click="moveExample(name as string, eIdx, eIdx+1)"
                                        >
                                            Down
                                        </UButton>
                                    </div>
                                    <UButton
                                        size="xs"
                                        color="error"
                                        icon="i-heroicons-trash"
                                        variant="soft"
                                        @click="removeExample(name as string, eIdx)"
                                    >
                                        Delete
                                    </UButton>
                                </div>
                            </div>
                            <p v-if="examples.length===0" class="text-sm text-muted">
                                No examples
                            </p>
                        </div>
                    </div>
                </UCard>
                <p v-if="!model.conjugations || Object.keys(model.conjugations).length===0" class="text-sm text-muted">
                    No groups
                </p>
            </div>
        </div>

        <template #footer>
            <div class="flex items-center justify-between">
                <div class="flex gap-2">
                    <UButton size="xs" icon="i-heroicons-arrow-up" @click="emit('moveUp')">
                        Up
                    </UButton>
                    <UButton size="xs" icon="i-heroicons-arrow-down" @click="emit('moveDown')">
                        Down
                    </UButton>
                </div>
                <UButton
                    size="xs"
                    color="error"
                    icon="i-heroicons-trash"
                    variant="soft"
                    @click="emit('remove')"
                >
                    Delete stem
                </UButton>
            </div>
        </template>
    </UCard>
</template>
