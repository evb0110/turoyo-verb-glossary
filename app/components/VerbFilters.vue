<script setup lang="ts">
import type { Filters, SelectOption } from '~/types/types/search'

const modelValue = defineModel<Filters>('modelValue', { required: true })

const props = defineProps<{
  letters: SelectOption[]
  etymologies: SelectOption[]
  stems: SelectOption[]
}>()

const emits = defineEmits<{(e: 'reset'): void}>()

const filtersActive = computed(() => Boolean(modelValue.value.letter || modelValue.value.etymology || modelValue.value.stem))

function reset() {
  modelValue.value = { letter: null, etymology: null, stem: null }
  emits('reset')
}
</script>

<template>
  <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
    <div>
      <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Letter</label>
      <USelect
        v-model="modelValue.letter"
        :items="letters"
        placeholder="All letters"
        class="w-full"
        :disabled="letters.length <= 1"
      />
    </div>

    <div>
      <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Etymology</label>
      <USelect
        v-model="modelValue.etymology"
        :items="etymologies"
        placeholder="All etymologies"
        class="w-full"
        :disabled="etymologies.length <= 1"
      />
    </div>

    <div>
      <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Stem</label>
      <USelect
        v-model="modelValue.stem"
        :items="stems"
        placeholder="All stems"
        class="w-full"
        :disabled="stems.length <= 1"
      />
    </div>

    <div v-if="filtersActive" class="sm:col-span-3 flex justify-end pt-2">
      <UButton
        icon="i-heroicons-x-mark"
        color="gray"
        variant="soft"
        size="sm"
        @click="reset"
      >
        Clear all filters
      </UButton>
    </div>
  </div>
</template>


