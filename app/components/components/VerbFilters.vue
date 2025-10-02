<script setup lang="ts">
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
  <UCard>
    <template #header>
      <div class="flex items-center justify-between">
        <h2 class="text-base font-semibold">Filters</h2>
        <UTooltip text="Reset all filters">
          <UButton
            v-if="filtersActive"
            icon="i-heroicons-arrow-path"
            color="gray"
            variant="ghost"
            size="sm"
            @click="reset"
          />
        </UTooltip>
      </div>
    </template>

    <div class="grid gap-4">
      <div>
        <label class="text-sm font-medium">Letter</label>
        <USelect v-model="modelValue.letter" :options="props.letters" option-attribute="label" />
      </div>
      <div>
        <label class="text-sm font-medium">Etymology</label>
        <USelect v-model="modelValue.etymology" :options="props.etymologies" option-attribute="label" />
      </div>
      <div>
        <label class="text-sm font-medium">Stem</label>
        <USelect v-model="modelValue.stem" :options="props.stems" option-attribute="label" />
      </div>
    </div>
  </UCard>
</template>
