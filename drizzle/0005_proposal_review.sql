-- Additive migration. The retired verbs table is intentionally left untouched.
CREATE TYPE "public"."proposal_verdict" AS ENUM('accept', 'reject', 'discuss');--> statement-breakpoint
CREATE TABLE "proposal_review" (
	"id" text PRIMARY KEY NOT NULL,
	"proposal_id" text NOT NULL,
	"entry_id" text NOT NULL,
	"user_id" text NOT NULL,
	"verdict" "proposal_verdict" NOT NULL,
	"comment" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "proposal_review" ADD CONSTRAINT "proposal_review_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "proposal_review_proposal_created_idx" ON "proposal_review" USING btree ("proposal_id","created_at");--> statement-breakpoint
CREATE INDEX "proposal_review_entry_idx" ON "proposal_review" USING btree ("entry_id");
