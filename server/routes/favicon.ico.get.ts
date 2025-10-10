import { defineEventHandler, sendRedirect } from 'h3'

export default defineEventHandler((event) => {
    return sendRedirect(event, '/favicon.svg?v=2', 302)
})




