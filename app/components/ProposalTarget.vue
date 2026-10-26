<template>
    <div class="target">
        <p v-if="context.location" class="small muted">
            {{ context.location }}
        </p>
        <template v-if="context.example">
            <p class="tur">
                {{ context.example.turoyo || context.example.raw }}
            </p>
            <p v-if="context.example.translation">
                {{ context.example.translation }}
            </p>
            <p v-if="context.example.refs.length" class="small muted">
                {{ context.example.refs.map((ref) => ref.raw).join(" · ") }}
            </p>
            <p v-if="context.example.note" class="small">
                {{ context.example.note }}
            </p>
        </template>
        <p v-else-if="context.idiom" class="serif">
            {{ context.idiom.raw }}
        </p>
        <p v-else-if="context.current" class="serif">
            {{ context.current }}
        </p>
        <template v-else-if="context.stem">
            <p class="tur">
                {{ context.stem.forms }}
            </p>
            <p class="serif">
                {{ context.stem.sensesRaw }}
            </p>
        </template>
        <p v-else-if="entry" class="serif">
            {{ entry.head }}
        </p>
        <p v-else class="muted">
            This verb is not in the glossary yet.
        </p>
    </div>
</template>

<script setup lang="ts">
import { proposalContext } from '~/utils/proposalContext'
import type { IEntry } from '#shared/types/IEntry'
import type { IProposal } from '#shared/types/IProposal'

const props = defineProps<{ entry: IEntry | null
    proposal: IProposal }>()
const context = computed(() => proposalContext(props.entry, props.proposal))
</script>

<style scoped>
.target {
  display: grid;
  gap: 0.15rem;
}
</style>
