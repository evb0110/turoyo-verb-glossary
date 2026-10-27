<template>
    <span class="document-download small">
        <span v-if="label">{{ label }}:</span>
        <button
            v-for="format in formats"
            :key="format.value"
            type="button"
            class="btn-link"
            :disabled="!!pending"
            :aria-busy="pending === url(format.value)"
            @click="download(url(format.value))"
        >
            {{ format.label }}
        </button>
        <span v-if="slow" role="status" class="muted">Preparing the {{ pendingLabel }}…</span>
        <span v-if="parts && !stale" class="parts">
            {{ partsFormat }} in {{ parts.items.length }} parts:
            <button
                v-for="item in parts.items"
                :key="item.part"
                type="button"
                class="btn-link"
                :disabled="!!pending"
                @click="download(partUrl(item.part))"
            >
                {{ item.part }} ({{ item.label }}, {{ megabytes(item.bytes) }})
            </button>
        </span>
        <span v-if="parts && stale" role="alert" class="parts">
            The document changed while you were downloading its parts, for example because a decision was saved.
            <button
                type="button"
                class="btn-link"
                :disabled="!!pending"
                @click="download(parts.url)"
            >
                List the parts again
            </button>
        </span>
        <span v-if="error" role="alert" class="error">{{ error }}</span>
    </span>
</template>

<script setup lang="ts">
// "Word" and "PDF" downloads of an export. `href` is the export URL without its format.
const props = defineProps<{ href: string
    label?: string }>()
const formats = [
    {
        value: 'docx',
        label: 'Word',
    },
    {
        value: 'pdf',
        label: 'PDF',
    },
] as const
const {
    pending,
    slow,
    error,
    stale,
    parts,
    partUrl,
    download,
    reset,
} = useDocumentDownload()
function megabytes(bytes: number) {
    return `${(bytes / 1_000_000).toFixed(1)} MB`
}
function url(format: string) {
    return `${props.href}${props.href.includes('?') ? '&' : '?'}format=${format}`
}
const pendingLabel = computed(() => (pending.value.includes('format=pdf') ? 'PDF' : 'Word document'))
const partsFormat = computed(() => (parts.value?.url.includes('format=pdf') ? 'PDF' : 'Word'))
// Another scope (a different letter, filter or option) starts afresh; a late answer for the old one is ignored.
watch(() => props.href, reset)
onBeforeUnmount(reset)
</script>

<style scoped>
.document-download {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0 0.5rem;
  font-weight: 400;
}
.parts {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0 0.5rem;
}
</style>
