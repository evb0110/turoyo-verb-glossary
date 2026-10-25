import { requireApproved } from '~~/server/services/auth/requireApproved'

export default defineEventHandler(async (event) => {
    if (getRequestURL(event).pathname.startsWith('/api/glossary/')) await requireApproved(event)
})
