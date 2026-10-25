<template>
    <div :id="example.id" class="example">
        <div v-if="layer !== 'proposals'" class="example-text">
            <span v-if="numbered" class="sense-number">{{ example.sense || '—' }}</span>
            <div>
                <p class="turoyo">
                    {{ example.turoyo || example.raw }}
                </p>
                <p v-if="example.translation" class="translation">
                    {{ example.translation }}
                </p>
                <div class="example-refs">
                    <template v-for="(ref, n) in example.refs" :key="n">
                        <button
                            v-if="ref.textId && ref.verse !== null"
                            @click="open(ref.textId, ref.verse, ref.raw)"
                        >
                            {{ ref.raw }}
                        </button>
                        <span v-else>{{ ref.raw }}</span>
                    </template>
                    <span v-if="example.note" class="muted">{{ example.note }}</span>
                </div>
            </div>
        </div>
        <template v-if="layer !== 'glossary'">
            <ProposalCard
                v-for="proposal in proposals"
                :key="proposal.id"
                :proposal="proposal"
            />
        </template>
    </div>
</template>

<script setup lang="ts">
import type { IExample } from '#shared/types/IExample'
import type { IProposal } from '#shared/types/IProposal'

defineProps<{ example: IExample
    proposals: IProposal[]
    numbered?: boolean }>()
const { layer } = useGlossaryPreferences()
const { open } = useEvidence()
</script>

<style scoped>
.example {
    margin: 0.8rem 0;
}
.example-text {
    display: flex;
    gap: 1rem;
}
.sense-number {
    color: var(--muted);
    min-width: 1rem;
    font-family: var(--font-serif);
}
.translation {
    font-family: var(--font-serif);
    font-size: 1.08rem;
}
.example-refs {
    display: flex;
    flex-wrap: wrap;
    gap: 0.65rem;
    font-size: 0.7rem;
}
.example-refs button {
    color: var(--accent);
    text-decoration: underline;
}
</style>
