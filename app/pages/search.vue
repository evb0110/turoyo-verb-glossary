<template>
    <div>
        <header class="page-heading">
            <p class="eyebrow">
                Glossary & corpus
            </p>
            <h1>Search</h1>
        </header>
        <SearchExplorer :initial="String(route.query.q || '')" autofocus/>
    </div>
</template>

<script setup lang="ts">
const route = useRoute()
useHead({ title: 'Search' })
</script>
