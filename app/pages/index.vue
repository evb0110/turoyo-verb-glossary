<template>
    <div class="home-page">
        <header class="home-intro">
            <h1>Ṭuroyo verb glossary</h1>
            <p>A working reference for the glossary, corpus readings and editorial review.</p>
        </header>
        <SearchExplorer/>
        <section v-if="stats" class="run-section">
            <div class="run-heading">
                <h2>Reading the corpus</h2>
                <NuxtLink to="/texts">Explore texts ↗</NuxtLink>
            </div>
            <p class="muted">
                Agents compare each occurrence with the glossary. Every proposed change keeps its
                evidence and awaits an editor’s judgement.
            </p>
            <div class="run-numbers">
                <div>
                    <strong>{{ stats.entries.toLocaleString() }}</strong>
                    <span>glossary roots</span>
                </div>
                <div>
                    <strong>
                        {{ stats.read }}
                        <small>/ {{ stats.texts }}</small>
                    </strong>
                    <span>texts read</span>
                </div>
                <div>
                    <strong>{{ stats.proposals }}</strong>
                    <span>machine proposals</span>
                </div>
                <div>
                    <strong>{{ reviewed }}</strong>
                    <span>proposals reviewed</span>
                </div>
            </div>
            <progress
                :value="stats.read"
                :max="stats.texts || 1"
                :aria-label="`${stats.read} of ${stats.texts} texts read`"
            ></progress>
            <p class="reading-total muted">
                {{ stats.read }} read · {{ stats.partial }} partially read ·
                {{ stats.texts - stats.read - stats.partial }} unread
            </p>
            <div class="collection-progress">
                <div
                    v-for="item in stats.collections"
                    :key="item.collection"
                    class="collection-reading"
                >
                    <div>
                        <NuxtLink to="/texts">{{ item.collection }}</NuxtLink>
                        <span>{{ item.read }} read · {{ item.partial }} partial ·
                            {{ item.unread }} unread</span>
                    </div>
                    <progress
                        :value="item.read"
                        :max="item.total || 1"
                        :aria-label="`${item.collection}: ${item.read} read,
                        ${item.partial} partial, ${item.unread} unread`"
                    ></progress>
                </div>
            </div>
            <div class="kind-summary">
                <span v-for="(count, kind) in stats.kinds" :key="kind">
                    {{ kind.replaceAll('-', ' ') }}
                    <strong>{{ count }}</strong>
                </span>
            </div>
        </section>
        <p v-if="reviewError" class="error">
            {{ reviewError }}
        </p>
        <section class="recent-proposals rule-section">
            <div class="run-heading">
                <h2>Recently proposed</h2>
                <NuxtLink to="/review">Review queue ↗</NuxtLink>
            </div>
            <p class="muted recent-caption">
                Open proposals, highest priority first.
            </p>
            <NuxtLink
                v-for="proposal in recent"
                :key="proposal.id"
                :to="`/review?proposal=${encodeURIComponent(proposal.id)}`"
                class="recent-proposal"
            >
                <span class="pill">P{{ proposal.priority }}</span>
                <span><strong>{{ proposal.entryId.replaceAll('-', ' ') }}</strong> ·
                    {{ proposal.summary }}</span>
                <small>{{ proposal.kind.replaceAll('-', ' ') }}</small>
            </NuxtLink>
            <p v-if="!recent.length" class="empty">
                No open proposals yet.
            </p>
            <p v-if="proposalError" class="error">
                Proposals could not be loaded.
            </p>
        </section>
        <div class="home-links">
            <NuxtLink to="/review">
                <span class="eyebrow">Editorial work</span>
                <h3>Review the proposals ↗</h3>
                <p>Compare a suggestion with its evidence and record a decision.</p>
            </NuxtLink>
            <NuxtLink to="/research">
                <span class="eyebrow">Research notebook</span>
                <h3>Questions from the texts ↗</h3>
                <p>Trace recurring constructions and open linguistic questions.</p>
            </NuxtLink>
        </div>
    </div>
</template>

<script setup lang="ts">
const { data: stats } = await useFetch('/api/glossary/stats')
const {
    data: proposals,
    error: proposalError,
} = await useFetch('/api/glossary/proposals')
const {
    reviews,
    load,
    error: reviewError,
    status,
} = useProposalReviews()
await load()
const reviewed = computed(
    () =>
        new Set(
            reviews.value
                .filter(review =>
                    proposals.value?.some(proposal => proposal.id === review.proposalId)
                )
                .map(review => review.proposalId)
        ).size
)
const recent = computed(() =>
    (proposals.value || [])
        .filter(proposal => status(proposal.id) === 'open')
        .sort(
            (a, b) =>
                a.priority - b.priority
                || b.provenance.date.localeCompare(a.provenance.date)
                || a.id.localeCompare(b.id)
        )
        .slice(0, 6)
)
useHead({ title: 'Glossary' })
</script>

<style scoped>
.home-page {
    max-width: 960px;
    margin: auto;
}
.home-intro {
    padding: 1.5rem 0;
}
.home-intro h1 {
    font-size: clamp(2rem, 3vw, 2.8rem);
    margin: 0 0 0.7rem;
}
.home-intro em {
    color: var(--accent);
    font-weight: 400;
}
.home-intro p:last-child {
    color: var(--muted);
    line-height: 1.8;
    font-size: 0.9rem;
}
.run-section {
    border-top: 1px solid var(--rule);
    margin-top: 3rem;
    padding-top: 2rem;
}
.run-heading {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 1rem;
    margin-bottom: 0.7rem;
}
.run-heading a {
    font-size: 0.75rem;
    white-space: nowrap;
}
.run-section > p {
    font-size: 0.85rem;
    max-width: 44rem;
}
.run-numbers {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    margin: 2rem 0 1.2rem;
}
.run-numbers > div {
    border-left: 1px solid var(--rule);
    padding-left: 1rem;
}
.run-numbers > div:first-child {
    border: 0;
    padding-left: 0;
}
.run-numbers strong {
    font-family: var(--font-serif);
    font-size: 2.4rem;
    font-weight: 400;
    display: block;
    line-height: 1.2;
}
.run-numbers small {
    font-size: 1.2rem;
    color: var(--muted);
}
.run-numbers span {
    font-size: 0.67rem;
    color: var(--muted);
}
progress {
    width: 100%;
    height: 3px;
    accent-color: var(--accent);
    display: block;
}
.reading-total {
    font-size: 0.7rem;
    margin-top: 0.5rem;
}
.collection-progress {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr));
    gap: 1rem 1.5rem;
    margin-top: 1.5rem;
}
.collection-reading > div {
    display: grid;
    font-size: 0.7rem;
    margin-bottom: 0.4rem;
}
.collection-reading span {
    color: var(--muted);
    font-size: 0.65rem;
}
.recent-caption {
    font-size: 0.75rem;
}
.recent-proposal {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 0.6rem;
    padding: 0.8rem 0;
    border-bottom: 1px solid var(--rule);
    text-decoration: none;
    font-size: 0.8rem;
}
.recent-proposal small {
    color: var(--muted);
    margin-left: auto;
}
.kind-summary {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem 1rem;
    font-size: 0.65rem;
    color: var(--muted);
    margin-top: 1rem;
}
.kind-summary strong {
    color: var(--ink);
    margin-left: 0.3rem;
}
.home-links {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    border-top: 1px solid var(--rule);
    padding-top: 2rem;
    margin-top: 2rem;
}
.home-links a {
    text-decoration: none;
    color: var(--ink);
}
.home-links h3 {
    margin: 0.5rem 0;
}
.home-links p {
    color: var(--muted);
    font-size: 0.8rem;
}
@media (max-width: 600px) {
    .home-intro {
        padding-top: 1.8rem;
    }
    .run-numbers {
        grid-template-columns: 1fr 1fr;
        gap: 1.2rem;
    }
    .run-numbers > div:nth-child(3) {
        border: 0;
        padding-left: 0;
    }
    .home-links {
        grid-template-columns: 1fr;
    }
    .desktop-break {
        display: none;
    }
}
</style>
