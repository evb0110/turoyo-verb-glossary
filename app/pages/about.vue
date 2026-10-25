<template>
    <article class="about">
        <header class="page-heading">
            <p class="eyebrow">
                About this work
            </p>
            <h1>
                A glossary grounded
                <br/>
                in the texts.
            </h1>
            <p>
                The Turoyo Verb Glossary is a reference for the verbs of Ṭuroyo, the
                Neo-Aramaic language of Ṭur ʕAbdin and its communities.
            </p>
        </header>
        <section>
            <h2>Read a verb, follow its evidence</h2>
            <p>
                Each entry preserves the glossary’s roots, stems, base forms and numbered
                senses. Examples can be read under their senses or in the order of the
                original glossary tables. Short references open the cited verse with three
                verses on either side.
            </p>
            <p>
                The sense-by-box matrix shows how many examples support each part of an
                entry. Dotted cells have three or fewer examples. Detransitive senses are
                marked D; unnumbered examples remain unnumbered.
            </p>
        </section>
        <section>
            <h2>How machine proposals are made</h2>
            <p>
                Agents read the corpus verb by verb and compare each occurrence with the
                glossary. They suggest senses, examples, idioms and forms, and flag
                citations, wording or structure that may need correction. Every proposal
                records its rationale, source verses, model, stage and date.
            </p>
            <p>
                Green marks additions, ochre marks corrections, and violet marks notes or
                questions. A proposal is evidence for an editor to examine. Its status
                records the latest review; acceptance does not silently rewrite the source
                glossary.
            </p>
        </section>
        <section>
            <h2>How to review</h2>
            <ol>
                <li>Read the proposal beside its target sense or example.</li>
                <li>
                    Expand its rationale and open the evidence verses. Check the text and
                    translation in context.
                </li>
                <li>
                    Choose Accept, Reject or Discuss. Add a comment when it helps explain
                    the decision.
                </li>
            </ol>
            <p>
                All approved users may review. Every decision remains in the history with
                its reviewer and time. In the queue, use j/k to move, a/r/d to record a
                verdict, and o to open the entry. Keyboard shortcuts pause while you type.
            </p>
        </section>
        <section>
            <h2>Texts & research notes</h2>
            <p>
                The text reader highlights analysed verbs and links each to its glossary
                sense. Dashed highlights distinguish added or proposed occurrences.
                Alignment flags identify passages whose Turoyo and translation need
                comparison. The research notebook collects observations tagged with
                questions such as RQ-experiencer.
            </p>
            <NuxtLink to="/review">Go to the review queue ↗</NuxtLink>
        </section>
    </article>
</template>

<script setup lang="ts">
useHead({ title: 'About' })
</script>

<style scoped>
.about {
    max-width: 780px;
}
section {
    margin: 2.5rem 0;
}
section p,
ol {
    margin-top: 1rem;
    font-family: var(--font-serif);
    font-size: 1.25rem;
    line-height: 1.8;
}
ol {
    list-style: decimal;
    padding-left: 1.5rem;
}
</style>
