<template>
    <section class="target stack">
        <h3>In the glossary now</h3>
        <p v-if="context.location" class="caption">
            {{ context.location }}
        </p>
        <template v-if="context.example">
            <p class="turoyo">
                {{ context.example.turoyo || context.example.raw }}
            </p>
            <p v-if="context.example.translation" class="serif translation">
                {{ context.example.translation }}
            </p>
            <p v-if="context.example.refs.length" class="caption">
                {{ context.example.refs.map((ref) => ref.raw).join(" · ") }}
            </p>
            <p v-if="context.example.note">
                {{ context.example.note }}
            </p>
        </template>
        <p v-else-if="context.idiom" class="serif">
            {{ context.idiom.raw }}
        </p>
        <p v-else-if="context.current" class="serif">
            {{ context.current }}
        </p>
        <p v-else-if="context.stem" class="serif">
            {{ context.stem.forms }}<br/>{{ context.stem.sensesRaw }}
        </p>
        <p v-else-if="entry" class="serif">
            {{ entry.head }}
        </p>
        <p v-else>
            This verb is not in the glossary yet.
        </p>
    </section>
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
  gap: 0.6rem;
  padding-bottom: 1.3rem;
  border-bottom: 1px solid var(--rule);
}
.translation {
  font-size: 1.2rem;
}
</style>
