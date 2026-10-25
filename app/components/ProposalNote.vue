<template>
    <details
        class="suggestion-note"
        :class="`family-${proposalFamily(proposal.kind)}`"
        @toggle="open = ($event.target as HTMLDetailsElement).open"
    >
        <summary>
            {{ label
            }}<span v-if="status(proposal.id) !== 'open'"> · {{ decision }}</span>
        </summary>
        <ProposalCard v-if="open" :proposal="proposal" :entry="entry"/>
    </details>
</template>

<script setup lang="ts">
import type { IEntry } from '#shared/types/IEntry'
import type { IProposal } from '#shared/types/IProposal'
import { proposalFamily } from '#shared/utils/proposalFamily'

const props = defineProps<{ proposal: IProposal }>()
const entry = inject<ComputedRef<IEntry | null>>(
    'glossary-entry',
    computed(() => null)
)
const { status } = useProposalReviews()
const open = ref(false)
const label = computed(() =>
    props.proposal.kind === 'question'
        ? 'Question for the editors'
        : props.proposal.kind === 'note'
            ? 'Note for the editors'
            : props.proposal.kind === 'add-example'
                ? 'Suggested new example'
                : props.proposal.kind === 'new-sense'
                    ? 'Suggested new meaning'
                    : props.proposal.kind === 'new-idiom'
                        ? 'Suggested new idiom'
                        : props.proposal.kind === 'new-stem'
                            ? 'Suggested new stem'
                            : props.proposal.kind === 'new-root'
                                ? 'Suggested new verb'
                                : proposalFamily(props.proposal.kind) === 'addition'
                                    ? 'Suggested addition'
                                    : 'Suggested correction'
)
const decision = computed(() =>
    status(props.proposal.id) === 'accepted'
        ? 'Accepted'
        : status(props.proposal.id) === 'rejected'
            ? 'Rejected'
            : 'Decide later'
)
</script>

<style scoped>
.suggestion-note {
  --family: var(--correction);
  border-left: 3px solid var(--family);
  padding: 0.1rem 0.8rem;
  margin: 0.8rem 0;
  background: color-mix(in srgb, var(--family) 5%, var(--paper));
}
.family-addition {
  --family: var(--addition);
}
.family-note {
  --family: var(--note);
}
.suggestion-note > summary {
  color: var(--family);
  font-size: 0.889rem;
}
.suggestion-note[open] {
  padding-bottom: 1rem;
}
</style>
