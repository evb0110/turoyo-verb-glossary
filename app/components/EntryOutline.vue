<template>
    <nav v-if="items.length" class="entry-outline" aria-label="Entry outline">
        <div class="outline-jump">
            <label for="entry-jump">Jump to</label>
            <select
                id="entry-jump"
                :value="active"
                @change="jump(($event.target as HTMLSelectElement).value)"
            >
                <option v-for="item in items" :key="item.id" :value="item.id">
                    {{ item.depth ? '↳ ' : '' }}{{ item.label }}
                </option>
            </select>
        </div>
        <div class="outline-list">
            <p class="eyebrow">
                On this page
            </p>
            <a
                v-for="item in items"
                :key="item.id"
                :href="`#${encodeURIComponent(item.id)}`"
                :class="{ 'outline-sense': item.depth, 'active': active === item.id }"
                :aria-current="active === item.id ? 'location' : undefined"
                :title="item.label"
                @click.prevent="jump(item.id)"
            >{{ item.label }}</a>
        </div>
    </nav>
</template>

<script setup lang="ts">
import { useEventListener } from '@vueuse/core'

const props = defineProps<{ items: { id: string
    label: string
    depth?: number }[] }>()
const active = ref(props.items[0]?.id || '')
function update() {
    const offset = window.innerWidth <= 780 ? 185 : window.innerWidth < 1280 ? 150 : 115
    let current = props.items[0]?.id || ''
    for (const item of props.items) {
        const element = document.getElementById(item.id)
        if (element && element.getBoundingClientRect().top <= offset) current = item.id
    }
    active.value = current
}
function jump(id: string) {
    document.getElementById(id)?.scrollIntoView({
        behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
        block: 'start',
    })
    active.value = id
    history.replaceState(null, '', `#${encodeURIComponent(id)}`)
}
useEventListener('scroll', update, { passive: true })
useEventListener('resize', update)
watch(
    () => props.items,
    () => nextTick(update)
)
onMounted(update)
</script>

<style scoped>
.entry-outline {
    position: sticky;
    top: 68px;
    z-index: 15;
    background: var(--paper);
    padding: 0.6rem 0;
}
.outline-jump {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.75rem;
}
.outline-jump label {
    white-space: nowrap;
    color: var(--muted);
}
.outline-jump select {
    width: 100%;
}
.outline-list {
    display: none;
}
@media (min-width: 1280px) {
    .entry-outline {
        grid-column: 2;
        grid-row: 1;
        align-self: start;
        top: 90px;
        max-height: calc(100vh - 110px);
        overflow: auto;
        padding: 0 0 0 1rem;
        border-left: 1px solid var(--rule);
    }
    .outline-jump {
        display: none;
    }
    .outline-list {
        display: grid;
        gap: 0.2rem;
    }
    .outline-list p {
        margin-bottom: 0.5rem;
    }
    .outline-list a {
        display: block;
        font-size: 0.72rem;
        color: var(--muted);
        text-decoration: none;
        padding: 0.2rem 0.4rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .outline-list .outline-sense {
        padding-left: 1rem;
    }
    .outline-list a.active {
        color: var(--accent);
        background: var(--panel);
    }
}
@media (max-width: 780px) {
    .entry-outline {
        top: 100px;
    }
}
</style>
