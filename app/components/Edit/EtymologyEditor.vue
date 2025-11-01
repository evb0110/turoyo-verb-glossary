<script lang="ts" setup>
import type { IEtymology } from '#shared/types/IEtymology'

const model = defineModel<IEtymology>('etymology', { required: true })

function addEtymon() {
    if (!model.value) model.value = { etymons: [] }
    model.value.etymons.push({ source: '' })
}

function removeEtymon(idx: number) {
    if (!model.value?.etymons) return
    model.value.etymons.splice(idx, 1)
}

function move<T>(arr: T[], from: number, to: number) {
    if (from < 0 || from >= arr.length || to < 0 || to > arr.length) return
    const removed = arr.splice(from, 1)
    if (removed.length === 0) return
    arr.splice(to, 0, removed[0] as T)
}
</script>

<template>
    <div class="space-y-4">
        <div class="flex items-center gap-3">
            <label class="text-sm font-medium">Relationship</label>
            <URadioGroup
                v-model="model.relationship"
                :options="[
                    { value: undefined, label: 'None' },
                    { value: 'also', label: 'also' },
                    { value: 'or', label: 'or' },
                    { value: 'and', label: 'and' }
                ]"
            />
        </div>

        <div class="flex items-center justify-between">
            <h3 class="font-medium">
                Etymons
            </h3>
            <UButton size="xs" icon="i-heroicons-plus" @click="addEtymon">
                Add etymon
            </UButton>
        </div>

        <div class="space-y-4">
            <UCard v-for="(e, idx) in model.etymons || []" :key="idx">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                        <label class="block text-sm font-medium mb-1">Source</label>
                        <UInput v-model="e.source" placeholder="e.g., MEA, Arab."/>
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-1">Source root</label>
                        <UInput v-model="e.source_root"/>
                    </div>
                    <div class="md:col-span-2">
                        <label class="block text-sm font-medium mb-1">Meaning</label>
                        <UTextarea v-model="e.meaning"/>
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-1">Reference</label>
                        <UInput v-model="e.reference"/>
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-1">Notes</label>
                        <UInput v-model="e.notes"/>
                    </div>
                    <div class="md:col-span-2">
                        <label class="block text-sm font-medium mb-1">Raw</label>
                        <UTextarea v-model="e.raw"/>
                    </div>
                </div>
                <template #footer>
                    <div class="flex items-center justify-between">
                        <div class="flex gap-2">
                            <UButton
                                size="xs"
                                icon="i-heroicons-arrow-up"
                                :disabled="idx===0"
                                @click="move(model.etymons!, idx, idx-1)"
                            >
                                Up
                            </UButton>
                            <UButton
                                size="xs"
                                icon="i-heroicons-arrow-down"
                                :disabled="idx===(model.etymons!.length-1)"
                                @click="move(model.etymons!, idx, idx+1)"
                            >
                                Down
                            </UButton>
                        </div>
                        <UButton
                            size="xs"
                            color="error"
                            icon="i-heroicons-trash"
                            variant="soft"
                            @click="removeEtymon(idx)"
                        >
                            Delete
                        </UButton>
                    </div>
                </template>
            </UCard>
            <p v-if="!model?.etymons || model.etymons.length===0" class="text-sm text-muted">
                No etymons
            </p>
        </div>
    </div>
</template>
