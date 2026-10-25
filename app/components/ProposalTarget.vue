<template>
    <section v-if="location || example || idiom" class="target">
        <p v-if="location" class="eyebrow">
            {{ location }}
        </p>
        <template v-if="example">
            <p class="turoyo serif">
                <span v-if="example.sense" class="muted">{{ example.sense }}</span>
                {{ example.turoyo || example.raw }}
            </p>
            <p v-if="example.translation" class="serif">
                {{ example.translation }}
            </p>
            <p class="refs muted">
                {{ example.refs.map(ref => ref.raw).join(' · ') }}
            </p>
        </template>
        <p v-else-if="idiom" class="serif">
            {{ idiom.raw }}
        </p>
    </section>
</template>

<script setup lang="ts">
import type { IEntry } from '#shared/types/IEntry'
import type { IProposal } from '#shared/types/IProposal'

const props = defineProps<{ entry: IEntry | null
    proposal: IProposal }>()

const stem = computed(() =>
    props.entry?.stems.find(
        item =>
            item.id === props.proposal.target.stemId
            || props.proposal.target.boxId?.startsWith(`${item.id}.`)
            || props.proposal.target.exampleId?.startsWith(`${item.id}.`)
    ) || null
)
const box = computed(() =>
    stem.value?.boxes.find(
        item =>
            item.id === props.proposal.target.boxId
            || props.proposal.target.exampleId?.startsWith(`${item.id}.`)
    ) || null
)
const example = computed(
    () => box.value?.examples.find(item => item.id === props.proposal.target.exampleId) || null
)
const idiom = computed(
    () => props.entry?.idioms.find(item => item.id === props.proposal.target.exampleId) || null
)
const location = computed(() => {
    const parts: string[] = []
    if (stem.value) parts.push(`Stem ${stem.value.stem}`)
    if (box.value) parts.push(`${box.value.detransitive ? 'Detransitive ' : ''}${box.value.label}`)
    if (idiom.value) parts.push('Idiomatic phrase')
    return parts.join(' · ')
})
</script>

<style scoped>
.target {
    margin: 0 0 1rem;
    padding: 0.8rem 1rem;
    border: 1px solid var(--rule);
    border-radius: 4px;
}
.turoyo {
    font-style: italic;
}
.turoyo .muted {
    font-style: normal;
    margin-right: 0.5rem;
}
.refs {
    font-size: 0.8rem;
}
</style>
