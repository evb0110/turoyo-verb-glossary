<script setup lang="ts">
const isOpen = defineModel<boolean>('open', {
    required: true,
})
</script>

<template>
    <UModal v-model:open="isOpen" :ui="{ content: 'sm:max-w-2xl' }" title="Regex Search Help">
        <template #body>
            <div class="space-y-4">
                <div>
                    <h4 class="font-medium text-sm mb-2">
                        Turoyo-Specific Shortcuts
                    </h4>
                    <div class="space-y-2 text-sm">
                        <div class="flex gap-3">
                            <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">\c</code>
                            <span class="text-gray-600 dark:text-gray-400">
                                Matches any Turoyo consonant (b, d, f, g, h, k, l, m, n, p, q, r, s,
                                t, v, w, x, y, z, č, ġ, š, ž, ǧ, ʔ, ʕ, ḏ, ḥ, ṣ, ṭ, etc.)
                            </span>
                        </div>
                        <div class="flex gap-3">
                            <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">\v</code>
                            <span class="text-gray-600 dark:text-gray-400">
                                Matches any Turoyo vowel (a, e, i, o, u, ə, ǝ, é, ī, á, etc.)
                            </span>
                        </div>
                    </div>
                </div>

                <div>
                    <h4 class="font-medium text-sm mb-2">
                        Standard Regex Syntax
                    </h4>
                    <div class="grid grid-cols-2 gap-2 text-sm">
                        <div class="flex gap-2">
                            <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">^</code>
                            <span class="text-gray-600 dark:text-gray-400">Start of string</span>
                        </div>
                        <div class="flex gap-2">
                            <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">$</code>
                            <span class="text-gray-600 dark:text-gray-400">End of string</span>
                        </div>
                        <div class="flex gap-2">
                            <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">.</code>
                            <span class="text-gray-600 dark:text-gray-400">Any character</span>
                        </div>
                        <div class="flex gap-2">
                            <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">*</code>
                            <span class="text-gray-600 dark:text-gray-400">0 or more times</span>
                        </div>
                        <div class="flex gap-2">
                            <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">+</code>
                            <span class="text-gray-600 dark:text-gray-400">1 or more times</span>
                        </div>
                        <div class="flex gap-2">
                            <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">?</code>
                            <span class="text-gray-600 dark:text-gray-400">0 or 1 time</span>
                        </div>
                        <div class="flex gap-2">
                            <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">[abc]</code>
                            <span class="text-gray-600 dark:text-gray-400">Any of a, b, or c</span>
                        </div>
                        <div class="flex gap-2">
                            <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">|</code>
                            <span class="text-gray-600 dark:text-gray-400">OR operator</span>
                        </div>
                    </div>
                </div>

                <div>
                    <h4 class="font-medium text-sm mb-2">
                        Examples
                    </h4>
                    <div class="space-y-2 text-sm">
                        <div class="bg-gray-50 dark:bg-gray-900 p-3 rounded">
                            <code class="font-mono text-primary">b\vd</code>
                            <p class="text-gray-600 dark:text-gray-400 mt-1">
                                Finds: b + vowel + d (e.g., "bdl", "bdy")
                            </p>
                        </div>
                        <div class="bg-gray-50 dark:bg-gray-900 p-3 rounded">
                            <code class="font-mono text-primary">\c\c\c</code>
                            <p class="text-gray-600 dark:text-gray-400 mt-1">
                                Finds: Any sequence of 3 consonants
                            </p>
                        </div>
                        <div class="bg-gray-50 dark:bg-gray-900 p-3 rounded">
                            <code class="font-mono text-primary">^\c\c\c$</code>
                            <p class="text-gray-600 dark:text-gray-400 mt-1">
                                Finds: Roots that are exactly 3 consonants
                            </p>
                        </div>
                        <div class="bg-gray-50 dark:bg-gray-900 p-3 rounded">
                            <code class="font-mono text-primary">^ʕ</code>
                            <p class="text-gray-600 dark:text-gray-400 mt-1">
                                Finds: Roots starting with ʕ
                            </p>
                        </div>
                        <div class="bg-gray-50 dark:bg-gray-900 p-3 rounded">
                            <code class="font-mono text-primary">le$</code>
                            <p class="text-gray-600 dark:text-gray-400 mt-1">
                                Finds: Forms ending with "le"
                            </p>
                        </div>
                        <div class="bg-gray-50 dark:bg-gray-900 p-3 rounded">
                            <code class="font-mono text-primary">^m\c\v</code>
                            <p class="text-gray-600 dark:text-gray-400 mt-1">
                                Finds: Forms starting with m + consonant + vowel
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </template>
    </UModal>
</template>
