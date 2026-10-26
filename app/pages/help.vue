<template>
    <article class="help">
        <h1>Help</h1>
        <p>
            The Turoyo Verb Glossary is a reference for the verbs of Ṭuroyo, the Neo-Aramaic language of Ṭur ʕAbdin.
            Entries keep the team’s roots, stems, forms, meanings and examples exactly as written. A machine has read
            the texts and proofread the glossary; its suggestions are shown beside the glossary for the editors to
            decide on. Decisions are saved for the team and never change the glossary text.
        </p>
        <nav class="contents small" aria-label="On this page">
            <a href="#glossary">Glossary and search</a>
            <a href="#entry">An entry</a>
            <a href="#suggestions">Suggestions and decisions</a>
            <a href="#review">Review</a>
            <a href="#texts">Texts</a>
            <a href="#contact">Contact</a>
        </nav>

        <section id="glossary">
            <h2>Glossary and search</h2>
            <p>
                <NuxtLink to="/glossary">Glossary</NuxtLink> lists every root with its stems and forms, its first
                meaning, its number of examples, and how many machine suggestions it has and how many of those are still
                undecided. Verbs that exist only as a suggestion are marked “Suggested new verb”. The letters at the top
                jump through the list.
            </p>
            <p>
                Typing in the search field searches roots, Turoyo forms, German and English meanings, glossary examples
                and the texts. Vowel marks, stress and joiners are optional; consonant diacritics count. Tick
                “Regular expression” for pattern searches. The search field in the page header does the same from any
                page.
            </p>
        </section>

        <section id="entry">
            <h2>An entry</h2>
            <p>
                An entry shows the root and its heading, then each stem with its forms. A small table under the stem
                heading counts the examples for each meaning and form; click a number to jump to those examples. Each
                meaning lists its examples by form: Turoyo on the left, the translation in the middle and the references
                on the right. A reference such as 24/51 opens the text at that verse. Detransitive meanings are numbered
                D1, D2 and so on; examples without a meaning number are listed as unnumbered.
            </p>
            <p>
                On a wide screen the column on the left lists the stems and meanings with the number of undecided
                suggestions in each, and lets you show all suggestions, only the undecided ones, or none. The arrows
                beside the root move to the previous and next root. “Back to …” at the top returns to the page you came
                from, at the same place.
            </p>
        </section>

        <section id="suggestions">
            <h2>Suggestions and decisions</h2>
            <p>
                Each suggestion sits next to what it would change: a new meaning under the meaning heading, a correction
                under its example, a new example among the examples of its form, and notes and questions about the whole
                verb at the end. Its first line gives the kind, the place it refers to and its status. Green marks
                additions, brown marks corrections and violet marks notes and questions; a dotted line marks a decided
                suggestion.
            </p>
            <p>
                For a correction, red struck-through words would be removed and green underlined words added. For an
                addition, the proposed Turoyo stands beside its translation. Translations made by the machine for
                this project are labelled “machine translation”. The cited verses link to the texts. <em>Why</em> shows
                the machine’s reason, <em>Passages</em> shows the cited verses in full, and <em>History</em> lists every
                decision on the suggestion.
            </p>
            <dl class="terms">
                <dt>Accept</dt>
                <dd>You agree with the suggestion as it stands.</dd>
                <dt>Edit and accept</dt>
                <dd>
                    Opens the proposed wording (and translation, where there is one) for editing. “Save and accept”
                    records your wording; the machine’s version is kept beside it.
                </dd>
                <dt>Reject</dt>
                <dd>You disagree. A comment can say why.</dd>
                <dt>Decide later</dt>
                <dd>Keeps it for discussion with the team.</dd>
                <dt>Noted, Dismiss, Discuss later</dt>
                <dd>The same choices for notes and questions, which do not change the glossary.</dd>
                <dt>Comment</dt>
                <dd>Opens a field; the comment is saved with the next decision you choose.</dd>
                <dt>Undo</dt>
                <dd>Takes back your own current decision and restores the one before it.</dd>
            </dl>
            <p>
                The button of the current decision is shown filled. Click another to change the decision. Every
                decision is saved with your name and the date, and earlier decisions stay in the history.
            </p>
        </section>

        <section id="review">
            <h2>Review</h2>
            <p>
                <NuxtLink to="/review">Review</NuxtLink> goes through suggestions one at a time. Choose a group from
                the list (on the left on a wide screen), such as “Most important first” or “Typos and wording”, and
                narrow it by verb or text reference if you wish. Each suggestion shows the glossary text as it is now
                beside the suggested change, followed by the reason and the cited passages. After a decision the next
                undecided suggestion opens, and “Undo” in the notice at the top takes the decision back. Previous and
                Next move without deciding. Your place in each group is remembered in this browser.
            </p>
            <table class="keys">
                <caption>Keyboard shortcuts on the review page</caption>
                <tbody>
                    <tr>
                        <th scope="row">
                            <kbd>A</kbd>
                        </th><td>Accept, or Noted</td>
                    </tr>
                    <tr>
                        <th scope="row">
                            <kbd>E</kbd>
                        </th><td>Edit and accept</td>
                    </tr>
                    <tr>
                        <th scope="row">
                            <kbd>R</kbd>
                        </th><td>Reject, or Dismiss</td>
                    </tr>
                    <tr>
                        <th scope="row">
                            <kbd>D</kbd>
                        </th><td>Decide later, or Discuss later</td>
                    </tr>
                    <tr>
                        <th scope="row">
                            <kbd>C</kbd>
                        </th><td>Open the comment field</td>
                    </tr>
                    <tr>
                        <th scope="row">
                            <kbd>U</kbd>
                        </th><td>Undo the last decision</td>
                    </tr>
                    <tr>
                        <th scope="row">
                            <kbd>J</kbd> or <kbd>→</kbd>
                        </th><td>Next suggestion</td>
                    </tr>
                    <tr>
                        <th scope="row">
                            <kbd>K</kbd> or <kbd>←</kbd>
                        </th><td>Previous suggestion</td>
                    </tr>
                </tbody>
            </table>
            <p>Shortcuts do nothing while you are typing in a field.</p>
        </section>

        <section id="texts">
            <h2>Texts</h2>
            <p>
                <NuxtLink to="/texts">Texts</NuxtLink> lists every text on one line, grouped by collection, with its
                speaker or place, length, translation and whether its verbs have been analysed. The filter searches
                all collections at once.
            </p>
            <p>
                A text shows each verse with the Turoyo beside its translation. A link to a verse opens the text at
                that verse and highlights it; the verse number links to the verse itself. Underlined verbs have been
                analysed: click one to see its root, stem, form and meaning in that passage, with a link to the
                glossary entry and, where the verse produced a suggestion, to that suggestion. Machine translations are
                labelled at the top of the text and above the translation column.
            </p>
            <p>
                <NuxtLink to="/research">Research notes</NuxtLink> collects the readers’ observations by research
                question, each linked to its verse and entry.
            </p>
        </section>

        <section id="contact">
            <h2>Contact</h2>
            <p>
                For an entry or a suggestion, write to the project lead through your usual project correspondence and
                include the root or the page link. For sign-in or account access, contact the site administrator.
            </p>
        </section>
    </article>
</template>

<script setup lang="ts">
useHead({ title: 'Help' })
</script>

<style scoped>
.help {
  display: grid;
  gap: 0.6rem;
  max-width: 48rem;
}
.contents {
  display: flex;
  flex-wrap: wrap;
  gap: 0 1rem;
}
section {
  display: grid;
  gap: 0.45rem;
  margin-top: 0.75rem;
}
h2 {
  padding-bottom: 0.15rem;
  border-bottom: 1px solid var(--rule);
}
.terms {
  display: grid;
  grid-template-columns: max-content minmax(0, 1fr);
  gap: 0.2rem 1rem;
  margin: 0;
}
.terms dt {
  font-weight: 600;
}
.terms dd {
  margin: 0;
}
.keys {
  border-collapse: collapse;
  font-size: 0.9375rem;
}
.keys caption {
  margin-bottom: 0.2rem;
  font-weight: 600;
  text-align: left;
}
.keys th,
.keys td {
  padding: 0.1rem 1rem 0.1rem 0;
  font-weight: 400;
  text-align: left;
}
@media (max-width: 760px) {
  .terms {
    grid-template-columns: minmax(0, 1fr);
  }
  .terms dd {
    margin-bottom: 0.3rem;
  }
}
</style>
