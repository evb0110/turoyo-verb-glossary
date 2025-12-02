<script lang="ts" setup>
import type { ITransformedStem } from '~/types/ITransformedStem'
import { segmentsToStructured } from '~/utils/segmentsToStructured'

defineProps<{
    stem: ITransformedStem
}>()
</script>

<template>
    <div v-if="stem.hasExamples" class="w-full overflow-x-auto">
        <table class="w-full border-collapse border border-gray-300 dark:border-gray-700">
            <tbody>
                <tr
                    v-for="group in stem.conjugationGroups"
                    :key="group.name"
                    class="border-b border-gray-300 dark:border-gray-700 last:border-b-0"
                >
                    <!-- Conjugation Group Name -->
                    <td
                        :class="[
                            'w-1/4 p-4 align-top border-r border-gray-300 dark:border-gray-700',
                            'bg-gray-50 dark:bg-gray-800 font-medium'
                        ]"
                    >
                        {{ group.name }}
                    </td>

                    <!-- Examples -->
                    <td class="p-4 align-top">
                        <div class="space-y-4">
                            <div
                                v-for="(example, index) in group.examples"
                                :key="`${group.name}-${index}`"
                                class="space-y-1"
                            >
                                <VerbExample :structured="segmentsToStructured(example)" :simple="true"/>
                            </div>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <p v-else class="text-sm text-muted">
        No examples available.
    </p>
</template>
