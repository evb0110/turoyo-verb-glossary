import { defineConfig } from 'drizzle-kit'

export default defineConfig({
    schema: './server/db/schema.ts',
    out: './drizzle',
    dialect: 'postgresql',
    dbCredentials: { url: process.env.NUXT_DATABASE_URL! },
})
