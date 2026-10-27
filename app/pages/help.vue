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
            <a href="#downloads">Word and PDF</a>
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
                The column on the left says how many machine suggestions the entry has and how many are still
                undecided, and lets you show all of them, only the undecided ones, or none. On a wide screen it also
                lists the stems and meanings, with the number of undecided suggestions in each; a meaning marked
                “new” exists only as a suggestion. The arrows beside the root move to the previous and next root.
                “Back to …” at the top returns to the page you came from, at the same place.
            </p>
        </section>

        <section id="suggestions">
            <h2>Suggestions and decisions</h2>
            <p>
                Each suggestion sits next to what it would change: a new meaning under the meaning heading, a correction
                under its example, a new example among the examples of its form, and notes and questions about the whole
                verb at the end. Its first words say what accepting it does, such as “Add this example”, “Add meaning
                1b” or “Correct the translation”, followed by the machine’s description of the change where it has
                one. Notes and questions for the editors change nothing in the glossary. Green marks additions, brown
                corrections and violet notes and questions. “Important” marks the suggestions the machine ranks first,
                the ones in the review group “Most important first”.
            </p>
            <p>
                A suggested example is laid out like the examples above it: Turoyo, translation and the passage it
                comes from, which opens the text at that verse. In a correction, red struck-through words would be
                removed and green underlined words added. Translations made by the machine for this project are
                labelled “machine translation”.
            </p>
            <dl class="terms">
                <dt>Accept</dt>
                <dd>You agree with the suggestion as it stands.</dd>
                <dt>Edit</dt>
                <dd>
                    Opens the proposed wording (and translation, where there is one) for editing. “Accept with changes”
                    records your wording; the machine’s version is kept beside it.
                </dd>
                <dt>Reject</dt>
                <dd>You disagree. A comment can say why.</dd>
                <dt>Decide later</dt>
                <dd>Keeps it for discussion with the team.</dd>
                <dt>Noted, Dismiss, Discuss later</dt>
                <dd>The same choices for notes and questions, which do not change the glossary.</dd>
                <dt>Comment</dt>
                <dd>Opens a field; the comment is saved with the decision you choose next.</dd>
                <dt>Details</dt>
                <dd>
                    The machine’s reason and how sure it is, the passages it cites in full, and every decision so far.
                </dd>
                <dt>Change</dt>
                <dd>Shows the buttons again on a decided suggestion, so you can choose another decision.</dd>
                <dt>Undo</dt>
                <dd>Takes back your own current decision and restores the one before it.</dd>
            </dl>
            <p>
                A decided suggestion shows the decision, who made it and when, such as “Accepted by A. Editor, 27 Oct
                2026”, in place of the buttons, and its coloured line turns dotted. Every decision is saved with your
                name and the date, and earlier decisions stay in the history under Details.
            </p>
        </section>

        <section id="review">
            <h2>Review</h2>
            <p>
                <NuxtLink to="/review">Review</NuxtLink> goes through suggestions one at a time. Choose a group from
                the list (on the left on a wide screen), such as “Most important first” or “Typos and wording”, and
                narrow it by verb or text reference if you wish. Each suggestion says what accepting it does and shows
                the glossary text as it is now beside the suggested change, then the decision buttons, the machine’s
                reason and the passages it cites. After a decision the next undecided suggestion opens, and “Undo” in
                the notice at the top takes the decision back. Previous and Next move without deciding. Your place in
                each group is remembered in this browser.
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
                        </th><td>Edit, then accept with changes</td>
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

        <section id="downloads">
            <h2>Word and PDF</h2>
            <p>
                The pages offer Word and PDF downloads of what they show: an entry (with its machine suggestions and
                the team’s decisions, or the entry alone), the whole glossary, one of its seven volumes or one letter,
                a text, a whole collection, the research notes with the current question and root, and all current
                decisions (on the Review page, for the editors who apply them to the Word volumes). Suggestions and
                machine translations are labelled as such in the documents too.
            </p>
            <p>
                The documents are built for finding your way through them. In Word, letters, roots, stems and
                meanings use the Heading 1–4 styles, so the Navigation pane lists them, and the table of contents at
                the start links to each heading; Word offers to update it when the file opens, which adds the page
                numbers. In a PDF the bookmarks panel shows the same headings, and the table of contents has page
                numbers. The page header names the root or text on the page. “See also” references link to their root
                when it is in the same document.
            </p>
            <p>
                A large document takes a few seconds to prepare. One that would be too large for a single download,
                such as the whole glossary as PDF, comes in parts, which are listed beside the link. If a decision is
                saved while you download the parts of a decisions document, you are asked to list the parts again,
                so that the parts fit together. The texts are
                third-party editions, for use within the project only. Word documents are set in Gentium Plus; with
                the font installed (free from SIL) they look like the PDF, otherwise Word substitutes another font.
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
