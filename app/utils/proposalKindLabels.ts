import type { TProposalKind } from '#shared/types/TProposalKind'

// Singular labels for one suggestion; proposalLabels names the review groups.
export const proposalKindLabels: Record<TProposalKind, string> = {
    'fix-text': 'Fix wording',
    'fix-citation': 'Fix reference',
    'move-example': 'Move example',
    'fix-structure': 'Fix layout',
    'duplicate-entry': 'Duplicate entry',
    'question': 'Question',
    'note': 'Note',
    'new-sense': 'New meaning',
    'gloss-change': 'Change meaning',
    'add-example': 'New example',
    'new-idiom': 'New idiom',
    'new-stem': 'New stem',
    'new-form': 'New form',
    'new-root': 'New verb',
}
