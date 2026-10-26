<template>
    <div :id="example.id" class="example">
        <div class="example-row">
            <p class="tur">
                {{ example.turoyo || example.raw }}
            </p>
            <p class="translation">
                {{ example.translation }}
            </p>
            <p class="refs small">
                <template v-for="(ref, n) in example.refs" :key="n">
                    <NuxtLink
                        v-if="ref.textId && ref.verse !== null"
                        class="ref"
                        :to="verseHref(ref.textId, ref.verse)"
                    >
                        <span v-text="ref.raw"></span>
                    </NuxtLink>
                    <span v-else class="ref" v-text="ref.raw"></span>
                </template>
            </p>
        </div>
        <p v-if="example.note" class="note small muted">
            {{ example.note }}
        </p>
        <ProposalCard
            v-for="proposal in proposals"
            :key="proposal.id"
            :proposal="proposal"
            :entry="entry"
        />
    </div>
</template>

<script setup lang="ts">
import { verseHref } from '~/utils/verseHref'
import type { IEntry } from '#shared/types/IEntry'
import type { IExample } from '#shared/types/IExample'
import type { IProposal } from '#shared/types/IProposal'

defineProps<{ example: IExample
    proposals: IProposal[]
    entry: IEntry | null }>()
</script>

<style scoped>
.example {
  padding: 0.3rem 0;
  border-top: 1px solid var(--rule);
}
.example-row {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr) 8rem;
  gap: 0 1.5rem;
  align-items: baseline;
}
.translation {
  font-size: 0.9375rem;
}
.refs {
  color: var(--muted);
}
.ref + .ref::before {
  display: inline-block;
  margin-right: 0.3em;
  color: var(--muted);
  content: ";";
}
.note {
  margin-top: 0.15rem;
}
@media (max-width: 1100px) {
  .example-row {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  }
  .refs {
    grid-column: 2;
  }
}
@media (max-width: 760px) {
  .example-row {
    grid-template-columns: minmax(0, 1fr);
  }
  .refs {
    grid-column: 1;
  }
}
</style>
