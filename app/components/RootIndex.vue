<template>
    <div class="index-shell">
        <div class="index-heading">
            <span class="eyebrow">Root index</span>
            <span class="muted">{{ roots.length }}</span>
        </div>
        <label class="sr-only" for="root-filter">Filter roots</label>
        <input
            id="root-filter"
            v-model="filter"
            placeholder="Filter roots…"
            class="root-filter"
        />
        <div v-if="error" class="error">
            Root index unavailable.
        </div>
        <section v-if="proposedRoots.length" class="proposed-roots">
            <h2 class="eyebrow">
                Proposed new roots · {{ proposedRoots.length }}
            </h2>
            <NuxtLink
                v-for="root in proposedRoots"
                :key="root.id"
                :to="entryHref(root.id)"
                class="root-link"
                @click="emit('navigate')"
            >
                <span class="root-label">{{ root.root }}</span>
                <span class="root-preview">{{ root.glossPreview }}</span>
            </NuxtLink>
        </section>
        <div v-bind="containerProps" class="root-scroll">
            <div v-bind="wrapperProps">
                <NuxtLink
                    v-for="row in list"
                    :key="row.data.id"
                    :to="entryHref(row.data.id)"
                    class="root-link"
                    @click="emit('navigate')"
                >
                    <span class="root-label">{{ row.data.root }}</span>
                    <span class="root-preview">{{ row.data.glossPreview }}</span>
                </NuxtLink>
            </div>
            <p v-if="!roots.length && !proposedRoots.length" class="empty">
                No matching roots.
            </p>
        </div>
        <div class="index-footer">
            In the glossary’s own order
            <br/>
            {{ user?.name }}
            <button class="index-signout" @click="logout">
                Sign out
            </button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useVirtualList } from '@vueuse/core'
import { entryHref } from '#shared/utils/entryHref'
import { normalizeTuroyo } from '#shared/utils/normalizeTuroyo'

const emit = defineEmits<{ navigate: [] }>()
const {
    user,
    signOut,
} = useAuth()
async function logout() {
    await signOut()
    await navigateTo('/login')
}
const {
    data,
    error,
} = await useFetch('/api/glossary/roots')
const filter = ref('')
const matching = computed(() =>
    (data.value || []).filter(entry =>
        normalizeTuroyo(entry.root).includes(normalizeTuroyo(filter.value))
    )
)
const proposedRoots = computed(() => matching.value.filter(entry => entry.proposed))
const roots = computed(() => matching.value.filter(entry => !entry.proposed))
const {
    list,
    containerProps,
    wrapperProps,
} = useVirtualList(roots, {
    itemHeight: 53,
    overscan: 10,
})
</script>

<style scoped>
.index-shell {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 1.3rem 1rem 0;
}
.index-heading {
    display: flex;
    justify-content: space-between;
    font-size: 0.7rem;
    align-items: center;
}
.root-filter {
    width: 100%;
    margin: 0.9rem 0;
    font-size: 0.8rem;
    background: var(--paper);
}
.root-scroll {
    flex: 1;
    overflow: auto;
    scrollbar-width: thin;
}
.proposed-roots {
    border-bottom: 1px solid var(--rule);
    margin-bottom: 0.5rem;
    max-height: 25%;
    overflow: auto;
    flex-shrink: 0;
}
.proposed-roots h2 {
    font-family: var(--font-sans);
    font-size: 0.6rem;
    padding: 0.2rem 0.5rem;
}
.root-link {
    height: 53px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 0 0.55rem;
    border-bottom: 1px solid color-mix(in srgb, var(--rule) 50%, transparent);
    text-decoration: none;
}
.root-link:hover,
.router-link-active {
    background: var(--paper);
}
.root-label {
    font-family: var(--font-serif);
    font-size: 1.25rem;
    line-height: 1.3;
    color: var(--ink);
}
.root-preview {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 0.65rem;
    color: var(--muted);
}
.index-signout {
    display: block;
    color: var(--accent);
    margin-top: 0.4rem;
    text-decoration: underline;
}
.index-footer {
    border-top: 1px solid var(--rule);
    padding: 0.8rem 0.5rem;
    color: var(--muted);
    font-size: 0.65rem;
}
</style>
