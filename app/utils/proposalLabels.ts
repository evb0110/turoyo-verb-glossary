import type { TProposalKind } from '#shared/types/TProposalKind'

export const proposalLabels: Record<TProposalKind, string> = {
    'fix-text': 'Typos and wording',
    'fix-citation': 'Wrong text references',
    'move-example': 'Example under the wrong meaning or form',
    'fix-structure': 'Layout and numbering',
    'duplicate-entry': 'Duplicate entries',
    'question': 'Questions for the editors',
    'note': 'Notes for the editors',
    'new-sense': 'New meanings',
    'gloss-change': 'Changes to meanings',
    'add-example': 'New examples',
    'new-idiom': 'New idioms',
    'new-stem': 'New stems',
    'new-form': 'New forms',
    'new-root': 'New verbs',
}
