import { sql } from 'drizzle-orm'
import { getDatabase } from '~~/server/db'

// Migration 0005, idempotent: production's connection string is a sensitive Vercel variable that
// cannot be pulled, so the deployed app creates the review table on first use.
const statements = [
    sql`DO $$ BEGIN CREATE TYPE "public"."proposal_verdict" AS ENUM('accept', 'reject', 'discuss'); EXCEPTION WHEN duplicate_object THEN NULL; END $$`,
    sql`CREATE TABLE IF NOT EXISTS "proposal_review" ("id" text PRIMARY KEY NOT NULL, "proposal_id" text NOT NULL, "entry_id" text NOT NULL, "user_id" text NOT NULL, "verdict" "proposal_verdict" NOT NULL, "comment" text, "created_at" timestamp with time zone DEFAULT now() NOT NULL)`,
    sql`DO $$ BEGIN ALTER TABLE "proposal_review" ADD CONSTRAINT "proposal_review_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action; EXCEPTION WHEN duplicate_object THEN NULL; END $$`,
    sql`CREATE INDEX IF NOT EXISTS "proposal_review_proposal_created_idx" ON "proposal_review" USING btree ("proposal_id","created_at")`,
    sql`CREATE INDEX IF NOT EXISTS "proposal_review_entry_idx" ON "proposal_review" USING btree ("entry_id")`,
]

let ready: Promise<void> | null = null

export function ensureProposalReviewTable(): Promise<void> {
    ready ||= (async () => {
        for (const statement of statements) await getDatabase().execute(statement)
    })().catch((error) => {
        ready = null
        throw error
    })
    return ready
}
