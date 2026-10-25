<template>
    <article class="help-page stack">
        <header class="page-heading">
            <h1>Help with the glossary</h1>
            <p>
                Use the glossary to look up verbs and help the team check suggested
                changes.
            </p>
        </header>
        <section class="stack">
            <h2>What is this glossary?</h2>
            <p>
                The Turoyo Verb Glossary is a reference for the verbs of Ṭuroyo, the
                Neo-Aramaic language of Ṭur ʕAbdin and its communities. Entries preserve
                the team’s roots, stems, forms, meanings and examples.
            </p>
        </section>
        <section class="stack">
            <h2>What did the machine do?</h2>
            <p>
                The machine read the texts and proofread the glossary. It suggested
                corrections to wording, references and the arrangement of examples, and
                raised questions for the editors. It can also suggest new meanings,
                examples, idioms and verbs.
            </p>
            <p>
                A suggestion is something for an editor to check. It may be wrong. The
                glossary’s original text is always preserved.
            </p>
        </section>
        <section class="stack">
            <h2>How to review a suggestion</h2>
            <ol>
                <li>
                    Open <NuxtLink to="/review">Review</NuxtLink> and choose a group, such
                    as “Typos and wording”.
                </li>
                <li>
                    Read “In the glossary now”, then “Suggested change”. Red,
                    struck-through words would be removed. Green, underlined words would
                    be added.
                </li>
                <li>
                    Read why the machine suggested it. Compare the Turoyo and translation
                    under “From the texts”.
                </li>
                <li>Choose a decision. You can add a comment first.</li>
            </ol>
            <figure>
                <img
                    src="/images/review-guide.png"
                    alt="Review card with glossary text, a suggested correction and three decision buttons"
                    width="390"
                    height="844"
                    loading="lazy"
                />
                <figcaption class="caption">
                    A suggestion on a phone. The decision buttons stay at the bottom while
                    you read.
                </figcaption>
            </figure>
        </section>
        <section class="stack">
            <h2>What the decisions mean</h2>
            <p><strong>Accept:</strong> you agree with the suggested change.</p>
            <p><strong>Reject:</strong> you disagree. A comment can explain why.</p>
            <p>
                <strong>Decide later:</strong> save it for discussion with the team.
            </p>
            <p>
                For questions, choose <strong>Noted</strong>,
                <strong>Dismiss</strong> or <strong>Discuss later</strong>.
            </p>
            <p>
                After a decision, the next undecided suggestion opens. Use
                <strong>Undo</strong> to take back your last decision, or Previous to
                revisit it. Skip moves on without recording a decision. Your position is
                remembered on this browser.
            </p>
            <p>
                Decisions are saved with your name and the date. They do not change the
                glossary text. Every earlier decision remains in the history unless its
                author uses Undo.
            </p>
        </section>
        <section class="stack">
            <h2>How to look up a verb</h2>
            <p>
                Use the search on the home page or open
                <NuxtLink to="/glossary">Glossary</NuxtLink>. Enter a root, a Turoyo
                form, or a meaning in German or English. Special transcription marks are
                optional. You can also browse roots by letter.
            </p>
            <p>
                On an entry, read the meanings and examples under each stem. Turn “Show
                machine suggestions” on or off. Tap a coloured suggestion note to read
                and review it. The table of examples is available below each stem
                heading.
            </p>
        </section>
        <section class="stack">
            <h2>Reading the texts</h2>
            <p>
                Open <NuxtLink to="/texts">Texts</NuxtLink> to choose a collection and
                text. Tap any underlined verb to see its root, stem and meaning in that
                passage. Use “Open glossary entry” to continue reading about the verb.
            </p>
            <p>
                References beside glossary examples open the passage with nearby verses.
                Some texts have no translation, and some verbs have not been analysed
                yet.
            </p>
        </section>
        <section class="stack">
            <h2>About this work</h2>
            <p>
                The glossary is grounded in examples from the text collections. Original
                wording, references and working notes are kept as the team wrote them.
                Detransitive meanings are marked D; examples without a meaning number
                remain unnumbered.
            </p>
            <p>
                Machine suggestions keep their reasons and source passages. Green notes
                mark additions, brown notes mark corrections, and violet notes mark
                questions. Approved editors can record decisions; administrators manage
                account access.
            </p>
            <NuxtLink to="/research">Research notes and questions from the texts →</NuxtLink>
        </section>
        <section class="stack">
            <h2>Who to contact</h2>
            <p>
                For help with an entry or a suggestion, contact the project lead through
                your usual project correspondence. Include the verb root or copy the
                page link. For sign-in or account access, contact the site
                administrator.
            </p>
        </section>
        <NuxtLink to="/review" class="primary">Start reviewing →</NuxtLink>
    </article>
</template>

<script setup lang="ts">
useHead({ title: 'Help' })
</script>

<style scoped>
.help-page {
  gap: 2rem;
}
.help-page section {
  gap: 0.9rem;
}
ol {
  list-style: decimal;
  padding-left: 1.5rem;
  margin: 0;
}
li {
  margin-bottom: 0.8rem;
}
figure {
  margin: 1rem 0;
}
img {
  width: min(100%, 390px);
  height: auto;
  border: 1px solid var(--rule);
  border-radius: 6px;
}
figcaption {
  margin-top: 0.7rem;
}
.help-page > .primary {
  justify-self: start;
}
</style>
