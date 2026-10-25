<template>
    <span>
        <template v-for="(part, i) in parts" :key="i">
            <mark v-if="part.match">{{ part.text }}</mark>
            <template v-else>{{ part.text }}</template>
        </template>
    </span>
</template>

<script setup lang="ts">
const props = defineProps<{ text: string
    ranges: [number, number][] }>()
const parts = computed(() => {
    const out: { text: string
        match: boolean }[] = []
    let cursor = 0
    for (const [start, end] of props.ranges) {
        out.push(
            {
                text: props.text.slice(cursor, start),
                match: false,
            },
            {
                text: props.text.slice(start, end),
                match: true,
            }
        )
        cursor = end
    }
    out.push({
        text: props.text.slice(cursor),
        match: false,
    })
    return out
})
</script>
