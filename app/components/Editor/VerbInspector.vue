<!-- eslint-disable -->
<script lang="ts" setup>
import type { IExample } from '~/types/IExample'
import { deepClone } from '~/utils/deepClone'
import { diffJson } from '~/utils/jsonPatch'
import type { IStem } from '#shared/types/IStem'
import type { IVerb } from '#shared/types/IVerb'
import type { IEditableConjugationGroup } from '~/components/Editor/IEditableConjugationGroup'

const props = defineProps<{
    verb: IVerb
    knownRoots?: string[]
}>()

const emit = defineEmits<{
    (e: 'applied', value: IVerb): void
    (e: 'reset'): void
}>()

type EditableStem = Omit<IStem, 'conjugations'> & {
    groups: IEditableConjugationGroup[]
}

interface EditableVerbModel {
    root: string
    etymology: IVerb['etymology']
    cross_reference: IVerb['cross_reference']
    stems: EditableStem[]
    idioms?: string[] | null
}

function conjugationsToGroups(conjugations: Record<string, IExample[]> | undefined | null): IEditableConjugationGroup[] {
    if (!conjugations || typeof conjugations !== 'object') return []
    return Object.entries(conjugations).map(([name, examples]) => ({
        name,
        examples: Array.isArray(examples) ? examples : [],
    }))
}

function groupsToConjugations(groups: IEditableConjugationGroup[] | undefined | null): Record<string, IExample[]> {
    const result: Record<string, IExample[]> = {}
    if (!Array.isArray(groups)) return result
    for (const group of groups) {
        const key = (group?.name || '').trim()
        if (!key) continue
        result[key] = Array.isArray(group.examples) ? group.examples : []
    }
    return result
}

const activeTab = ref<'verb' | 'etymology' | 'stems'>('verb')

function toEditable(verb: IVerb): EditableVerbModel {
    return {
        root: verb.root,
        etymology: verb.etymology ? deepClone(verb.etymology) : { etymons: [] },
        cross_reference: verb.cross_reference ?? null,
        stems: (verb.stems || []).map(s => ({
            stem: s.stem,
            forms: deepClone(s.forms || []),
            label_raw: s.label_raw,
            label_gloss_tokens: deepClone(s.label_gloss_tokens || []),
            groups: conjugationsToGroups(s.conjugations),
        })),
        idioms: (verb as any).idioms ?? null,
    }
}

function fromEditable(model: EditableVerbModel): IVerb {
    const stems: IStem[] = model.stems.map(s => ({
        stem: s.stem,
        forms: Array.isArray(s.forms) ? s.forms : [],
        conjugations: groupsToConjugations(s.groups),
        label_raw: s.label_raw,
        label_gloss_tokens: s.label_gloss_tokens,
    }))
    return {
        root: model.root,
        etymology: deepClone(model.etymology),
        cross_reference: model.cross_reference ?? null,
        stems,
        ...(model as any).idioms != null ? { idioms: deepClone((model as any).idioms) } : {},
    } as IVerb
}

const original = computed(() => props.verb)
const draft = ref<EditableVerbModel>(toEditable(props.verb))
watch(() => props.verb, (v) => { draft.value = toEditable(v) })

const history = ref<EditableVerbModel[]>([])

function pushHistory() {
    const snapshot = deepClone(draft.value)
    history.value.push(snapshot)
    if (history.value.length > 20) history.value.shift()
}

function undo() {
    const prev = history.value.pop()
    if (prev) draft.value = prev
}

const hasHardErrors = computed(() => {
    // Hard validation: non-empty stem names and unique group names per stem
    for (const s of draft.value.stems) {
        if (!s.stem || !s.stem.trim()) return true
        const seen = new Set<string>()
        for (const g of s.groups) {
            const name = (g.name || '').trim()
            if (!name) return true
            if (seen.has(name)) return true
            seen.add(name)
        }
    }
    return false
})

function applyChanges() {
    if (hasHardErrors.value) return
    pushHistory()
    const edited = fromEditable(draft.value)
    emit('applied', edited)
}

function resetAll() {
    draft.value = toEditable(original.value)
    history.value = []
    emit('reset')
}

async function copyJson() {
    const edited = fromEditable(draft.value)
    await navigator.clipboard.writeText(JSON.stringify(edited, null, 2))
}

function download(filename: string, content: string, type = 'application/json') {
    const blob = new Blob([content], { type })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
}

function downloadJson() {
    const edited = fromEditable(draft.value)
    download(`${edited.root}.json`, JSON.stringify(edited, null, 2))
}

function downloadPatch() {
    const edited = fromEditable(draft.value)
    const patch = diffJson(original.value as any, edited as any, '')
    download(`${edited.root}.patch.json`, JSON.stringify(patch, null, 2))
}

// Simple helpers to edit arrays
const idiomModalOpen = ref(false)
const idiomText = ref('')

function addIdiom() {
    idiomText.value = ''
    idiomModalOpen.value = true
}

function confirmAddIdiom() {
    const v = idiomText.value.trim()
    if (!v) { idiomModalOpen.value = false; return }
    if (!draft.value.idioms) draft.value.idioms = []
    draft.value.idioms.push(v)
    idiomModalOpen.value = false
}

function removeIdiom(idx: number) {
    draft.value.idioms = (draft.value.idioms || []).filter((_, i) => i !== idx)
}

function addEtymon() {
    if (!draft.value.etymology) draft.value.etymology = { etymons: [] }
    draft.value.etymology.etymons.push({ source: '' } as any)
}

function removeEtymon(idx: number) {
    if (!draft.value.etymology?.etymons) return
    draft.value.etymology.etymons.splice(idx, 1)
}

function move<T>(arr: T[], from: number, to: number) {
    if (from < 0 || from >= arr.length || to < 0 || to > arr.length) return
    const removed = arr.splice(from, 1)
    if (removed.length === 0) return
    const item = removed[0] as T
    arr.splice(to, 0, item as T)
}

function addStem() {
    draft.value.stems.push({
        stem: 'I',
        forms: [],
        label_raw: '',
        label_gloss_tokens: [],
        groups: [],
    })
}

function removeStem(idx: number) {
    draft.value.stems.splice(idx, 1)
}

function addGroup(s: EditableStem) {
    s.groups.push({
        name: 'Preterit',
        examples: [],
    })
}

function removeGroup(s: EditableStem, gIdx: number) {
    s.groups.splice(gIdx, 1)
}

function addExample(g: IEditableConjugationGroup) {
    g.examples.push({
        turoyo: '',
        translations: [],
        references: [],
    } as IExample)
}

function removeExample(g: IEditableConjugationGroup, eIdx: number) {
    g.examples.splice(eIdx, 1)
}
</script>

<template>
    <div class="space-y-4">
        <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold">
                Inspector
            </h2>
            <div class="flex gap-2">
                <UButton color="primary" :disabled="hasHardErrors" @click="applyChanges">
                    Apply
                </UButton>
                <UButton variant="outline" @click="undo">
                    Undo
                </UButton>
                <UButton variant="ghost" @click="resetAll">
                    Reset
                </UButton>
                <UDropdown
                    :items="[[
                        { label: 'Copy JSON', click: copyJson },
                        { label: 'Download JSON', click: downloadJson },
                        { label: 'Download Patch', click: downloadPatch }
                    ]]"
                >
                    <UButton icon="i-heroicons-ellipsis-horizontal" variant="ghost"/>
                </UDropdown>
            </div>
        </div>

        <div class="flex gap-2">
            <UButton :variant="activeTab==='verb' ? 'solid':'soft'" size="sm" @click="activeTab='verb'">
                Verb
            </UButton>
            <UButton :variant="activeTab==='etymology' ? 'solid':'soft'" size="sm" @click="activeTab='etymology'">
                Etymology
            </UButton>
            <UButton :variant="activeTab==='stems' ? 'solid':'soft'" size="sm" @click="activeTab='stems'">
                Stems
            </UButton>
        </div>

        <div v-if="activeTab==='verb'" class="space-y-4">
            <div>
                <label class="block text-sm font-medium mb-1">Root</label>
                <UInput v-model="draft.root" disabled/>
            </div>
            <div class="flex items-center gap-3">
                <label class="text-sm font-medium">Uncertain</label>
                <UToggle v-model="draft.etymology!.uncertain"/>
            </div>
            <div>
                <label class="block text-sm font-medium mb-1">Cross reference</label>
                <UInput v-model="draft.cross_reference" placeholder="Type a root"/>
            </div>
            <div>
                <div class="flex items-center justify-between">
                    <label class="block text-sm font-medium">Idioms</label>
                    <UButton size="xs" icon="i-heroicons-plus" @click="addIdiom">
                        Add
                    </UButton>
                </div>
                <div class="mt-2 space-y-2">
                    <div v-for="(idiom, idx) in draft.idioms || []" :key="idx" class="flex items-center gap-2">
                        <UInput v-model="(draft.idioms as any)[idx]"/>
                        <UButton
                            size="xs"
                            icon="i-heroicons-trash"
                            color="error"
                            variant="soft"
                            @click="removeIdiom(idx)"
                        />
                    </div>
                    <p v-if="!draft.idioms || draft.idioms.length===0" class="text-sm text-muted">
                        No idioms
                    </p>
                </div>
            </div>
        </div>

        <div v-else-if="activeTab==='etymology'" class="space-y-4">
            <div class="flex items-center gap-3">
                <label class="text-sm font-medium">Relationship</label>
                <URadioGroup
                    v-model="draft.etymology!.relationship"
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
                <UCard v-for="(e, idx) in draft.etymology?.etymons || []" :key="idx">
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
                        <div>
                            <label class="block text-sm font-medium mb-1">Stem</label>
                            <UInput v-model="(e as any).stem"/>
                        </div>
                    </div>
                    <template #footer>
                        <div class="flex items-center justify-between">
                            <div class="flex gap-2">
                                <UButton
                                    size="xs"
                                    icon="i-heroicons-arrow-up"
                                    :disabled="idx===0"
                                    @click="move(draft.etymology!.etymons!, idx, idx-1)"
                                >
                                    Up
                                </UButton>
                                <UButton
                                    size="xs"
                                    icon="i-heroicons-arrow-down"
                                    :disabled="idx===(draft.etymology!.etymons!.length-1)"
                                    @click="move(draft.etymology!.etymons!, idx, idx+1)"
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
                <p v-if="!draft.etymology?.etymons || draft.etymology.etymons.length===0" class="text-sm text-muted">
                    No etymons
                </p>
            </div>
        </div>

        <div v-else class="space-y-5">
            <div class="flex items-center justify-between">
                <h3 class="font-medium">
                    Stems
                </h3>
                <UButton size="xs" icon="i-heroicons-plus" @click="addStem">
                    Add stem
                </UButton>
            </div>
            <div class="space-y-4">
                <UCard v-for="(s, sIdx) in draft.stems" :key="sIdx" :ui="{ body: 'space-y-4' }">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div>
                            <label class="block text-sm font-medium mb-1">Stem label</label>
                            <UInput v-model="s.stem" placeholder="I, II, III, Pa., Af., Detransitive"/>
                        </div>
                        <div class="md:col-span-2">
                            <label class="block text-sm font-medium mb-1">Forms (comma-separated)</label>
                            <UInput v-model="(s as any)._formsText" :placeholder="s.forms?.join(', ')" @blur="s.forms = String((s as any)._formsText || '').split(',').map(x => x.trim()).filter(Boolean)"/>
                        </div>
                        <div class="md:col-span-3">
                            <label class="block text-sm font-medium mb-1">Label (raw)</label>
                            <UTextarea v-model="s.label_raw"/>
                        </div>
                    </div>

                    <div class="space-y-2">
                        <div class="flex items-center justify-between">
                            <h4 class="font-medium">
                                Conjugation groups
                            </h4>
                            <UButton size="xs" icon="i-heroicons-plus" @click="addGroup(s)">
                                Add group
                            </UButton>
                        </div>

                        <div class="space-y-3">
                            <UCard v-for="(g, gIdx) in s.groups" :key="gIdx">
                                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                                    <div>
                                        <label class="block text-sm font-medium mb-1">Group name</label>
                                        <UInput v-model="g.name" placeholder="Preterit, Infectum, Imperativ, ..."/>
                                    </div>
                                </div>

                                <template #footer>
                                    <div class="flex items-center justify-between">
                                        <div class="flex gap-2">
                                            <UButton
                                                size="xs"
                                                icon="i-heroicons-arrow-up"
                                                :disabled="gIdx===0"
                                                @click="move(s.groups, gIdx, gIdx-1)"
                                            >
                                                Up
                                            </UButton>
                                            <UButton
                                                size="xs"
                                                icon="i-heroicons-arrow-down"
                                                :disabled="gIdx===(s.groups.length-1)"
                                                @click="move(s.groups, gIdx, gIdx+1)"
                                            >
                                                Down
                                            </UButton>
                                        </div>
                                        <UButton
                                            size="xs"
                                            color="error"
                                            icon="i-heroicons-trash"
                                            variant="soft"
                                            @click="removeGroup(s, gIdx)"
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
                                        <UButton size="xs" icon="i-heroicons-plus" @click="addExample(g)">
                                            Add example
                                        </UButton>
                                    </div>
                                    <div class="space-y-3">
                                        <div v-for="(ex, eIdx) in g.examples" :key="eIdx" class="rounded border p-3 space-y-2">
                                            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                                <div>
                                                    <label class="block text-sm font-medium mb-1">Text</label>
                                                    <UTextarea v-model="(ex as any).text"/>
                                                </div>
                                                <div>
                                                    <label class="block text-sm font-medium mb-1">Turoyo</label>
                                                    <UTextarea v-model="ex.turoyo"/>
                                                </div>
                                            </div>
                                            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                                <div>
                                                    <label class="block text-sm font-medium mb-1">Translations (comma-separated)</label>
                                                    <UInput v-model="(ex as any)._translationsText" @blur="ex.translations = String((ex as any)._translationsText || '').split(',').map(x => x.trim()).filter(Boolean)"/>
                                                </div>
                                                <div>
                                                    <label class="block text-sm font-medium mb-1">References (comma-separated)</label>
                                                    <UInput v-model="(ex as any)._referencesText" @blur="ex.references = String((ex as any)._referencesText || '').split(',').map(x => x.trim()).filter(Boolean)"/>
                                                </div>
                                            </div>
                                            <div class="flex items-center justify-between">
                                                <div class="flex gap-2">
                                                    <UButton
                                                        size="xs"
                                                        icon="i-heroicons-arrow-up"
                                                        :disabled="eIdx===0"
                                                        @click="move(g.examples, eIdx, eIdx-1)"
                                                    >
                                                        Up
                                                    </UButton>
                                                    <UButton
                                                        size="xs"
                                                        icon="i-heroicons-arrow-down"
                                                        :disabled="eIdx===(g.examples.length-1)"
                                                        @click="move(g.examples, eIdx, eIdx+1)"
                                                    >
                                                        Down
                                                    </UButton>
                                                </div>
                                                <UButton
                                                    size="xs"
                                                    color="error"
                                                    icon="i-heroicons-trash"
                                                    variant="soft"
                                                    @click="removeExample(g, eIdx)"
                                                >
                                                    Delete
                                                </UButton>
                                            </div>
                                        </div>
                                        <p v-if="g.examples.length===0" class="text-sm text-muted">
                                            No examples
                                        </p>
                                    </div>
                                </div>
                            </UCard>
                            <p v-if="!s.groups || s.groups.length===0" class="text-sm text-muted">
                                No groups
                            </p>
                        </div>
                    </div>

                    <template #footer>
                        <div class="flex items-center justify-between">
                            <div class="flex gap-2">
                                <UButton
                                    size="xs"
                                    icon="i-heroicons-arrow-up"
                                    :disabled="sIdx===0"
                                    @click="move(draft.stems, sIdx, sIdx-1)"
                                >
                                    Up
                                </UButton>
                                <UButton
                                    size="xs"
                                    icon="i-heroicons-arrow-down"
                                    :disabled="sIdx===(draft.stems.length-1)"
                                    @click="move(draft.stems, sIdx, sIdx+1)"
                                >
                                    Down
                                </UButton>
                            </div>
                            <UButton
                                size="xs"
                                color="error"
                                icon="i-heroicons-trash"
                                variant="soft"
                                @click="removeStem(sIdx)"
                            >
                                Delete stem
                            </UButton>
                        </div>
                    </template>
                </UCard>
                <p v-if="draft.stems.length===0" class="text-sm text-muted">
                    No stems
                </p>
            </div>
        </div>

        <div v-if="hasHardErrors" class="rounded border border-red-300 bg-red-50 p-3 text-sm text-red-700">
            Please resolve errors: non-empty stem labels and unique, non-empty group names per stem.
        </div>

        <UModal v-model:open="idiomModalOpen" title="Add idiom" :ui="{ content: 'sm:max-w-md' }">
            <template #body>
                <div class="space-y-3">
                    <p class="text-sm text-muted">Enter idiom text</p>
                    <UTextarea v-model="idiomText" autofocus />
                </div>
            </template>
            <template #footer>
                <div class="flex justify-end gap-2">
                    <UButton variant="ghost" @click="idiomModalOpen = false">Cancel</UButton>
                    <UButton color="primary" @click="confirmAddIdiom">Add</UButton>
                </div>
            </template>
        </UModal>
    </div>
</template>
