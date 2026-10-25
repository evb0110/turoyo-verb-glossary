<template>
    <div :id="example.id" class="example">
        <p class="turoyo">
            {{ example.turoyo || example.raw }}
        </p>
        <p v-if="example.translation" class="translation serif">
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
        </div>
        <p v-if="example.note" class="caption">
            {{ example.note }}
        </p>
        <ProposalNote
            v-for="proposal in proposals"
            :key="proposal.id"
            :proposal="proposal"
        />
    </div>
</template>

<script setup lang="ts">
import type { IExample } from '#shared/types/IExample'
import type { IProposal } from '#shared/types/IProposal'

defineProps<{ example: IExample
    proposals: IProposal[] }>()
const { open } = useEvidence()
</script>

<style scoped>
.example {
  margin: 1.4rem 0;
}
.translation {
  font-size: 1.2rem;
  margin-top: 0.4rem;
}
.example-refs {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.889rem;
  color: var(--muted);
}
.example-refs button {
  color: var(--accent);
  text-decoration: underline;
  padding: 0.4rem;
  min-width: 48px;
}
</style>
