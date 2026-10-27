<template>
    <span class="status">
        <strong :class="`verdict-${review.verdict}`">{{ decisionWords(review, question) }}</strong>
        by {{ review.userName }},
        <time :datetime="review.createdAt">{{ formatDecisionDate(review.createdAt) }}</time>
    </span>
</template>

<script setup lang="ts">
import { decisionWords } from '~/utils/decisionWords'
import { formatDecisionDate } from '~/utils/formatDecisionDate'
import type { IProposalReview } from '#shared/types/IProposalReview'

defineProps<{ review: IProposalReview
    question: boolean }>()
</script>

<style scoped>
.status {
  font-size: 0.875rem;
}
.verdict-accept {
  color: var(--addition);
}
.verdict-reject {
  color: var(--deletion);
}
.verdict-discuss {
  color: var(--correction);
}
</style>
