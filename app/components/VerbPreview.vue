<template>
    <div class="preview-content whitespace-normal break-words">
        <div v-if="hasEtymology" class="preview-etymology mb-3">
            <strong>Etymology:</strong> {{ etymologyText }}
        </div>

        <div v-for="stem in verb.stems" :key="stem.stem" class="preview-stem mb-4">
            <div class="preview-stem-header mb-2">
                <strong>Stem {{ stem.stem }}:</strong>
                <span class="turoyo-text">
                    {{ stem.forms.length > 0 ? stem.forms.join(', ') : '(no forms)' }}
                </span>
            </div>

            <div v-if="getStemGloss(stem)" class="preview-gloss mb-2 text-sm text-gray-700 dark:text-gray-300">
                {{ getStemGloss(stem) }}
            </div>

            <ul v-if="getStemExamples(stem).length > 0" class="preview-examples space-y-1 text-sm">
                <li v-for="(example, i) in getStemExamples(stem)" :key="i" class="ml-4">
                    <span class="turoyo-text">{{ example.turoyo }}</span>
                    <template v-if="example.translation">
                        <span> — {{ example.translation }}</span>
                    </template>
                    <span v-if="example.reference" class="preview-ref text-gray-600 dark:text-gray-400">
                        [{{ example.reference }}]
                    </span>
                </li>
            </ul>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { IVerb } from '~/types/IVerb'
import type { IStem } from '~/types/IStem'
import type { IExample } from '~/types/IExample'
import { truncateText } from '~/utils/truncateText'
import { tokenTextToString } from '~/utils/tokenTextToString'

interface ProcessedExample {
    turoyo: string
    translation: string
    reference: string
}

const props = withDefaults(
    defineProps<{
        verb: IVerb
        maxExamplesPerStem?: number
        maxExampleLength?: number
    }>(),
    {
        maxExamplesPerStem: 3,
        maxExampleLength: 150
    }
)

const hasEtymology = computed(() => {
    return props.verb.etymology?.etymons && props.verb.etymology.etymons.length > 0
})

const etymologyText = computed(() => {
    if (!props.verb.etymology?.etymons) return ''

    const etymonParts = props.verb.etymology.etymons.map((etymon) => {
        if (!etymon.source && etymon.raw) {
            return etymon.raw
        }

        const sourcePart = etymon.source_root
            ? `${etymon.source} ${etymon.source_root}`
            : etymon.source
        const meaningPart = etymon.meaning ? ` — ${etymon.meaning}` : ''
        return `< ${sourcePart}${meaningPart}`
    })

    return etymonParts.join('; ')
})

function getStemGloss(stem: IStem): string {
    if (!stem.label_gloss_tokens || stem.label_gloss_tokens.length === 0) {
        return ''
    }

    const glossText = tokenTextToString(stem.label_gloss_tokens)
        .replace(/^(I{1,3}|IV|Pa\.|Af\.|Detransitive):\s*/i, '')
        .trim()

    return glossText ? truncateText(glossText, 100) : ''
}

function collectExamples(conjugations: { [key: string]: IExample[] }, maxCount: number): IExample[] {
    const examples: IExample[] = []

    for (const exampleList of Object.values(conjugations)) {
        for (const example of exampleList) {
            if (examples.length >= maxCount) {
                return examples
            }

            if (example.turoyo && example.turoyo.trim()) {
                examples.push(example)
            }
        }
    }

    return examples
}

function getStemExamples(stem: IStem): ProcessedExample[] {
    const examples = collectExamples(stem.conjugations, props.maxExamplesPerStem)

    return examples.map(ex => ({
        turoyo: truncateText(ex.turoyo, props.maxExampleLength),
        translation: ex.translations[0]
            ? truncateText(ex.translations[0], props.maxExampleLength)
            : '',
        reference: ex.references[0] || ''
    }))
}
</script>
