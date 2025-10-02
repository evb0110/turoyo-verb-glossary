import { useDebounceFn } from '@vueuse/core'
import type { SearchState } from '~/types/search'

interface UseAsyncSearchOptions {
  minimumQueryLength?: number
  debounce?: number
}

export const useAsyncSearch = (
  state: SearchState,
  worker: ReturnType<typeof useSearchWorker>,
  options: UseAsyncSearchOptions = {}
) => {
  const results = ref<string[]>([])
  const searching = ref(false)
  const error = ref<Error | null>(null)

  const runSearch = useDebounceFn(async () => {
    if (!state.query || state.query.trim().length < (options.minimumQueryLength || 2)) {
      results.value = []
      return
    }

    try {
      searching.value = true
      results.value = await worker.search({ ...state })
    } catch (err) {
      error.value = err as Error
      console.error('Search failed', err)
    } finally {
      searching.value = false
    }
  }, options.debounce ?? 250)

  watch(() => ({ ...state }), runSearch, { deep: true })

  return {
    results,
    searching,
    error
  }
}
