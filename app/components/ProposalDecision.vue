<template>
    <div class="decision" :class="{ docked: dock }">
        <div v-if="editing" class="edit-fields">
            <p class="small muted">
                Change the wording, then accept it. The machine’s version is kept for reference.
            </p>
            <template v-if="edit.headword !== undefined">
                <label :for="`edit-headword-${proposal.id}`">Idiom heading</label>
                <textarea
                    :id="`edit-headword-${proposal.id}`"
                    v-model="edit.headword"
                    rows="2"
                    maxlength="5000"
                ></textarea>
            </template>
            <label :for="`edit-text-${proposal.id}`">{{ editLabel }}</label>
            <textarea
                :id="`edit-text-${proposal.id}`"
                v-model="edit.text"
                :class="{ tur: turoyoWording }"
                rows="3"
                maxlength="20000"
            ></textarea>
            <template v-if="edit.translation !== undefined">
                <label :for="`edit-translation-${proposal.id}`">Translation</label>
                <textarea
                    :id="`edit-translation-${proposal.id}`"
                    v-model="edit.translation"
                    rows="2"
                    maxlength="20000"
                ></textarea>
            </template>
        </div>
        <div v-if="commentOpen" :id="`comment-area-${proposal.id}`" class="comment-field">
            <label :for="`comment-${proposal.id}`">Comment, saved with your decision</label>
            <textarea
                :id="`comment-${proposal.id}`"
                v-model="comment"
                rows="2"
                maxlength="5000"
            ></textarea>
        </div>
        <p v-if="saveError" role="alert" class="error small">
            {{ saveError }}
        </p>
        <div
            ref="bar"
            class="decision-bar"
            role="group"
            aria-label="Decision"
        >
            <template v-if="editing">
                <button
                    type="button"
                    class="btn btn-primary"
                    :disabled="saving || !edit.text.trim() || edit.headword === ''"
                    @click="submit('accept', true)"
                >
                    Accept with changes
                </button>
                <button
                    type="button"
                    class="btn"
                    :disabled="saving"
                    @click="editing = false"
                >
                    Cancel
                </button>
            </template>
            <ProposalStatus v-else-if="latest && !changing" :review="latest" :question="question"/>
            <template v-else>
                <button
                    type="button"
                    class="btn verdict verdict-accept"
                    :aria-pressed="current === 'accept'"
                    :disabled="saving"
                    @click="submit('accept')"
                >
                    {{ question ? "Noted" : "Accept" }}
                </button>
                <button
                    v-if="!question"
                    type="button"
                    class="btn verdict verdict-accept"
                    :aria-pressed="current === 'edited'"
                    :disabled="saving"
                    @click="startEditing"
                >
                    Edit
                </button>
                <button
                    type="button"
                    class="btn verdict verdict-reject"
                    :aria-pressed="current === 'reject'"
                    :disabled="saving"
                    @click="submit('reject')"
                >
                    {{ question ? "Dismiss" : "Reject" }}
                </button>
                <button
                    type="button"
                    class="btn verdict verdict-later"
                    :aria-pressed="current === 'discuss'"
                    :disabled="saving"
                    @click="submit('discuss')"
                >
                    {{ question ? "Discuss later" : "Decide later" }}
                </button>
            </template>
            <span class="links">
                <template v-if="latest && !changing && !editing">
                    <button
                        ref="changeButton"
                        type="button"
                        class="btn-link"
                        :disabled="saving"
                        @click="startChanging"
                    >
                        Change
                    </button>
                    <button
                        v-if="canUndo"
                        type="button"
                        class="btn-link"
                        :disabled="saving"
                        @click="undoLatest"
                    >
                        Undo
                    </button>
                </template>
                <button
                    v-else
                    type="button"
                    class="btn-link"
                    :aria-expanded="commentOpen"
                    :aria-controls="`comment-area-${proposal.id}`"
                    @click="toggleComment"
                >
                    {{ commentOpen ? "Hide comment" : "Comment" }}
                </button>
                <button
                    v-if="changing && !editing"
                    type="button"
                    class="btn-link"
                    @click="stopChanging"
                >
                    Keep the decision
                </button>
                <slot></slot>
            </span>
            <span class="sr-only" role="status">{{ saving ? "Saving decision…" : announcement }}</span>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useEventListener } from '@vueuse/core'
import { isEditableTarget } from '~/utils/isEditableTarget'
import type { IProposal } from '#shared/types/IProposal'
import type { IProposalEdit } from '#shared/types/IProposalEdit'
import type { IProposalReview } from '#shared/types/IProposalReview'
import type { TReviewVerdict } from '#shared/types/TReviewVerdict'
import { verdictLabel } from '#shared/utils/verdictLabel'

const props = withDefaults(
    defineProps<{ proposal: IProposal
        shortcuts?: boolean
        dock?: boolean }>(),
    {
        shortcuts: false,
        dock: false,
    }
)
const emit = defineEmits<{ reviewed: [review: IProposalReview]
    undone: [proposalId: string] }>()
const {
    decision,
    pending,
    review,
    undo,
} = useProposalReviews()
const { user } = useAuth()
const question = computed(() => ['question', 'note'].includes(props.proposal.kind))
const latest = computed(() => decision(props.proposal.id))
const current = computed(() => latest.value?.verdict === 'accept' && latest.value.edited
    ? 'edited'
    : latest.value?.verdict || null)
const saving = computed(() => pending.value.includes(props.proposal.id))
const canUndo = computed(() => !!latest.value && latest.value.userId === user.value?.id
    && !latest.value.id.startsWith('pending:'))
const comment = ref('')
const commentOpen = ref(false)
const saveError = ref('')
const announcement = ref('')
const editing = ref(false)
// A decided suggestion shows who decided what; "Change" brings the decision buttons back.
const changing = ref(false)
const bar = ref<HTMLElement | null>(null)
const changeButton = ref<HTMLButtonElement | null>(null)
const edit = ref<IProposalEdit>({ text: '' })
const turoyoWording = computed(() => ['add-example', 'new-form', 'new-idiom'].includes(props.proposal.kind))
const editLabel = computed(() => {
    if (turoyoWording.value) return 'Turoyo wording'
    if (['new-sense', 'gloss-change'].includes(props.proposal.kind)) return 'Meaning'
    if (props.proposal.kind === 'new-stem') return 'Stem forms'
    if (['move-example', 'duplicate-entry'].includes(props.proposal.kind)
        || (props.proposal.kind === 'fix-structure' && props.proposal.after === null)) return 'Instructions for the editor'
    return 'Proposed wording'
})
async function focusField(id: string) {
    await nextTick()
    const field = document.getElementById(id)
    field?.focus({ preventScroll: true })
    field?.scrollIntoView({ block: 'nearest' })
}
// Keeps keyboard focus in the bar when the button that had it is replaced.
async function keepFocus(target: () => HTMLElement | null | undefined) {
    const active = document.activeElement
    if (active && active !== document.body && !bar.value?.contains(active)) return
    await nextTick()
    target()?.focus({ preventScroll: true })
}
async function startChanging() {
    changing.value = true
    await keepFocus(() => bar.value?.querySelector<HTMLElement>('.verdict[aria-pressed="true"]')
        || bar.value?.querySelector<HTMLElement>('.verdict'))
}
async function stopChanging() {
    changing.value = false
    commentOpen.value = false
    // Keeping the decision abandons the comment, so a later change does not send it unseen.
    comment.value = ''
    await keepFocus(() => changeButton.value)
}
async function toggleComment() {
    commentOpen.value = !commentOpen.value
    if (commentOpen.value) {
        if (latest.value) changing.value = true
        await focusField(`comment-${props.proposal.id}`)
    }
}
// The initial wording follows the edit contract in docs/review-storage.md.
async function startEditing() {
    const proposal = props.proposal
    const initial: IProposalEdit = {
        text: proposal.after
            ?? String(proposal.data.turoyo ?? proposal.data.forms ?? proposal.data.gloss ?? proposal.summary),
    }
    if (turoyoWording.value || typeof proposal.data.translation === 'string')
        initial.translation = String(proposal.data.translation ?? '')
    if (proposal.kind === 'new-idiom' && typeof proposal.data.headword === 'string')
        initial.headword = proposal.data.headword
    edit.value = latest.value?.edited ? { ...latest.value.edited } : initial
    editing.value = true
    await focusField(`edit-text-${proposal.id}`)
}
async function submit(verdict: TReviewVerdict, withChanges = false) {
    saveError.value = ''
    const result = await review(
        props.proposal.id,
        props.proposal.entryId,
        verdict,
        comment.value,
        withChanges ? edit.value : null
    )
    if (result) {
        editing.value = false
        changing.value = false
        commentOpen.value = false
        comment.value = ''
        announcement.value = `Saved: ${verdictLabel(result.verdict, question.value, !!result.edited)}.`
        if (!props.shortcuts) await keepFocus(() => changeButton.value)
        emit('reviewed', result)
    }
    else saveError.value = 'Your decision was not saved. Please try again.'
}
async function undoLatest() {
    if (!latest.value) return
    saveError.value = ''
    const proposalId = latest.value.proposalId
    if (await undo(latest.value)) {
        announcement.value = 'Decision undone.'
        await keepFocus(() => changeButton.value || bar.value?.querySelector<HTMLElement>('.verdict'))
        emit('undone', proposalId)
    }
    else saveError.value = 'The decision could not be undone. It may have been changed by another editor; reload to see the latest decision.'
}
// Review-queue shortcuts. They are ignored while typing in a field or with a modifier key.
if (props.shortcuts)
    useEventListener('keydown', (event: KeyboardEvent) => {
        if (event.defaultPrevented || event.repeat || event.metaKey || event.ctrlKey || event.altKey
            || editing.value || saving.value || isEditableTarget(event.target)) return
        const actions: Record<string, () => unknown> = {
            a: () => submit('accept'),
            r: () => submit('reject'),
            d: () => submit('discuss'),
            c: () => toggleComment(),
            ...(question.value ? {} : { e: () => startEditing() }),
        }
        const action = actions[event.key.toLowerCase()]
        if (!action) return
        event.preventDefault()
        action()
    })
</script>

<style scoped>
.decision {
  display: grid;
  gap: 0.4rem;
}
.edit-fields,
.comment-field {
  display: grid;
  gap: 0.2rem;
  max-width: 60rem;
}
.edit-fields label,
.comment-field label {
  font-size: 0.875rem;
  font-weight: 600;
}
.decision-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
}
.links {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0 0.6rem;
  margin-left: 0.4rem;
}
.decision-bar .verdict-accept[aria-pressed="true"] {
  border-color: var(--addition);
  background: var(--addition);
  color: var(--bg);
}
.decision-bar .verdict-reject[aria-pressed="true"] {
  border-color: var(--deletion);
  background: var(--deletion);
  color: var(--bg);
}
.decision-bar .verdict-later[aria-pressed="true"] {
  border-color: var(--correction);
  background: var(--correction);
  color: var(--bg);
}
.decision-bar .btn[aria-pressed="true"]:hover:not(:disabled) {
  filter: brightness(1.1);
}
@media (max-width: 760px) {
  .docked .decision-bar {
    position: fixed;
    z-index: 20;
    right: 0;
    bottom: 0;
    left: 0;
    padding: 0.45rem 0.6rem calc(0.45rem + env(safe-area-inset-bottom));
    border-top: 1px solid var(--rule);
    background: var(--bg);
  }
}
</style>
