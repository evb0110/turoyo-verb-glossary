-- Drizzle-generated DDL plus legacy review conversion and atomic review functions.
-- Guard the whole migration so a later CLI migration is safe after runtime ensure.
DO $migration$
BEGIN
    PERFORM pg_advisory_xact_lock(624719, 6);
    IF to_regprocedure('public.glossary_review_schema_v6()') IS NOT NULL THEN RETURN; END IF;
CREATE TABLE "proposal_decision" (
    "proposal_id" text PRIMARY KEY NOT NULL,
    "id" text NOT NULL,
    "entry_id" text NOT NULL,
    "user_id" text,
    "user_name" text NOT NULL,
    "verdict" "proposal_verdict" NOT NULL,
    "edited" jsonb,
    "comment" text,
    "created_at" timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT "proposal_decision_id_unique" UNIQUE("id"),
    CONSTRAINT "proposal_decision_comment_check" CHECK ("proposal_decision"."comment" IS NULL OR length("proposal_decision"."comment") <= 5000),
    CONSTRAINT "proposal_decision_edit_check" CHECK ("proposal_decision"."edited" IS NULL OR ("proposal_decision"."verdict" = 'accept' AND jsonb_typeof("proposal_decision"."edited") = 'object' AND "proposal_decision"."edited" ? 'text' AND jsonb_typeof("proposal_decision"."edited"->'text') = 'string' AND length(btrim("proposal_decision"."edited"->>'text')) BETWEEN 1 AND 20000 AND octet_length("proposal_decision"."edited"::text) <= 200000))
);


CREATE TABLE "proposal_review_event" (
    "id" text PRIMARY KEY NOT NULL,
    "proposal_id" text NOT NULL,
    "entry_id" text NOT NULL,
    "user_id" text,
    "user_name" text NOT NULL,
    "verdict" "proposal_verdict",
    "edited" jsonb,
    "comment" text,
    "previous_review_id" text,
    "undone_review_id" text,
    "created_at" timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT "proposal_review_event_action_check" CHECK (("proposal_review_event"."verdict" IS NOT NULL AND "proposal_review_event"."undone_review_id" IS NULL) OR ("proposal_review_event"."verdict" IS NULL AND "proposal_review_event"."undone_review_id" IS NOT NULL AND "proposal_review_event"."edited" IS NULL)),
    CONSTRAINT "proposal_review_event_comment_check" CHECK ("proposal_review_event"."comment" IS NULL OR length("proposal_review_event"."comment") <= 5000),
    CONSTRAINT "proposal_review_event_edit_check" CHECK ("proposal_review_event"."edited" IS NULL OR ("proposal_review_event"."verdict" = 'accept' AND jsonb_typeof("proposal_review_event"."edited") = 'object' AND "proposal_review_event"."edited" ? 'text' AND jsonb_typeof("proposal_review_event"."edited"->'text') = 'string' AND length(btrim("proposal_review_event"."edited"->>'text')) BETWEEN 1 AND 20000 AND octet_length("proposal_review_event"."edited"::text) <= 200000))
);


INSERT INTO "proposal_review_event"
    (id, proposal_id, entry_id, user_id, user_name, verdict, comment, created_at, previous_review_id)
SELECT r.id, r.proposal_id, r.entry_id, r.user_id, u.name, r.verdict, r.comment, r.created_at,
    lag(r.id) OVER (PARTITION BY r.proposal_id ORDER BY r.created_at, r.id)
FROM "proposal_review" r JOIN "user" u ON u.id = r.user_id;


INSERT INTO "proposal_decision" (id, proposal_id, entry_id, user_id, user_name, verdict, comment, created_at)
SELECT DISTINCT ON (proposal_id) id, proposal_id, entry_id, user_id, user_name, verdict, comment, created_at
FROM "proposal_review_event" ORDER BY proposal_id, created_at DESC, id DESC;


DROP TABLE "proposal_review";

ALTER TABLE "account" ALTER COLUMN "access_token_expires_at" SET DATA TYPE timestamp with time zone USING "access_token_expires_at" AT TIME ZONE 'UTC';

ALTER TABLE "account" ALTER COLUMN "refresh_token_expires_at" SET DATA TYPE timestamp with time zone USING "refresh_token_expires_at" AT TIME ZONE 'UTC';

ALTER TABLE "account" ALTER COLUMN "created_at" SET DATA TYPE timestamp with time zone USING "created_at" AT TIME ZONE 'UTC';

ALTER TABLE "account" ALTER COLUMN "created_at" SET DEFAULT now();

ALTER TABLE "account" ALTER COLUMN "updated_at" SET DATA TYPE timestamp with time zone USING "updated_at" AT TIME ZONE 'UTC';

ALTER TABLE "session" ALTER COLUMN "expires_at" SET DATA TYPE timestamp with time zone USING "expires_at" AT TIME ZONE 'UTC';

ALTER TABLE "session" ALTER COLUMN "created_at" SET DATA TYPE timestamp with time zone USING "created_at" AT TIME ZONE 'UTC';

ALTER TABLE "session" ALTER COLUMN "created_at" SET DEFAULT now();

ALTER TABLE "session" ALTER COLUMN "updated_at" SET DATA TYPE timestamp with time zone USING "updated_at" AT TIME ZONE 'UTC';

ALTER TABLE "user" ALTER COLUMN "created_at" SET DATA TYPE timestamp with time zone USING "created_at" AT TIME ZONE 'UTC';

ALTER TABLE "user" ALTER COLUMN "created_at" SET DEFAULT now();

ALTER TABLE "user" ALTER COLUMN "updated_at" SET DATA TYPE timestamp with time zone USING "updated_at" AT TIME ZONE 'UTC';

ALTER TABLE "user" ALTER COLUMN "updated_at" SET DEFAULT now();

ALTER TABLE "user_activity_log" ALTER COLUMN "created_at" SET DATA TYPE timestamp with time zone USING "created_at" AT TIME ZONE 'UTC';

ALTER TABLE "user_activity_log" ALTER COLUMN "created_at" SET DEFAULT now();

ALTER TABLE "user_session_activity" ALTER COLUMN "created_at" SET DATA TYPE timestamp with time zone USING "created_at" AT TIME ZONE 'UTC';

ALTER TABLE "user_session_activity" ALTER COLUMN "created_at" SET DEFAULT now();

ALTER TABLE "user_session_activity" ALTER COLUMN "last_activity_at" SET DATA TYPE timestamp with time zone USING "last_activity_at" AT TIME ZONE 'UTC';

ALTER TABLE "user_session_activity" ALTER COLUMN "last_activity_at" SET DEFAULT now();

ALTER TABLE "verification" ALTER COLUMN "expires_at" SET DATA TYPE timestamp with time zone USING "expires_at" AT TIME ZONE 'UTC';

ALTER TABLE "verification" ALTER COLUMN "created_at" SET DATA TYPE timestamp with time zone USING "created_at" AT TIME ZONE 'UTC';

ALTER TABLE "verification" ALTER COLUMN "created_at" SET DEFAULT now();

ALTER TABLE "verification" ALTER COLUMN "updated_at" SET DATA TYPE timestamp with time zone USING "updated_at" AT TIME ZONE 'UTC';

ALTER TABLE "verification" ALTER COLUMN "updated_at" SET DEFAULT now();

ALTER TABLE "verbs" ALTER COLUMN "created_at" SET DATA TYPE timestamp with time zone USING "created_at" AT TIME ZONE 'UTC';

ALTER TABLE "verbs" ALTER COLUMN "created_at" SET DEFAULT now();

ALTER TABLE "verbs" ALTER COLUMN "updated_at" SET DATA TYPE timestamp with time zone USING "updated_at" AT TIME ZONE 'UTC';

ALTER TABLE "verbs" ALTER COLUMN "updated_at" SET DEFAULT now();

ALTER TABLE "proposal_decision" ADD CONSTRAINT "proposal_decision_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE set null ON UPDATE no action;

ALTER TABLE "proposal_review_event" ADD CONSTRAINT "proposal_review_event_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE set null ON UPDATE no action;

CREATE INDEX "proposal_decision_user_idx" ON "proposal_decision" USING btree ("user_id");

CREATE INDEX "proposal_review_event_proposal_created_idx" ON "proposal_review_event" USING btree ("proposal_id","created_at","id");

CREATE INDEX "proposal_review_event_user_idx" ON "proposal_review_event" USING btree ("user_id");

CREATE INDEX "account_user_idx" ON "account" USING btree ("user_id");

CREATE INDEX "account_provider_idx" ON "account" USING btree ("provider_id","account_id");

CREATE INDEX "session_user_idx" ON "session" USING btree ("user_id");

CREATE INDEX "activity_recent_idx" ON "user_activity_log" USING btree ("created_at");

CREATE INDEX "activity_user_recent_idx" ON "user_activity_log" USING btree ("user_id","created_at");

CREATE INDEX "activity_session_recent_idx" ON "user_activity_log" USING btree ("session_activity_id","created_at");

CREATE INDEX "activity_type_recent_idx" ON "user_activity_log" USING btree ("event_type","created_at");

CREATE INDEX "activity_host_recent_idx" ON "user_activity_log" USING btree ("host","created_at");

CREATE INDEX "session_activity_recent_idx" ON "user_session_activity" USING btree ("last_activity_at","created_at");

CREATE INDEX "session_activity_user_recent_idx" ON "user_session_activity" USING btree ("user_id","last_activity_at");

CREATE INDEX "verification_identifier_idx" ON "verification" USING btree ("identifier");

ALTER TABLE "user_activity_log" ADD CONSTRAINT "activity_status_check" CHECK ("user_activity_log"."status_code" BETWEEN 100 AND 599);

ALTER TABLE "user_activity_log" ADD CONSTRAINT "activity_result_count_check" CHECK ("user_activity_log"."result_count" IS NULL OR "user_activity_log"."result_count" >= 0);

ALTER TABLE "user_session_activity" ADD CONSTRAINT "session_activity_counters_check" CHECK ("user_session_activity"."total_requests" >= 0 AND "user_session_activity"."search_requests" >= 0 AND "user_session_activity"."stats_requests" >= 0);


-- Serialize each proposal independently. Each function is one Neon HTTP statement and transaction.
CREATE OR REPLACE FUNCTION public.save_proposal_decision(
    p_id text, p_proposal text, p_entry text, p_user text, p_name text,
    p_verdict public.proposal_verdict, p_comment text, p_edited jsonb
) RETURNS SETOF public.proposal_decision LANGUAGE plpgsql SET search_path = public AS $save$
DECLARE prior_id text; saved public.proposal_decision;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtextextended(p_proposal, 624719));
    SELECT id INTO prior_id FROM public.proposal_decision WHERE proposal_id = p_proposal;
    INSERT INTO public.proposal_review_event
        (id, proposal_id, entry_id, user_id, user_name, verdict, comment, edited, previous_review_id)
    VALUES (p_id, p_proposal, p_entry, p_user, p_name, p_verdict, p_comment, p_edited, prior_id);
    INSERT INTO public.proposal_decision
        (id, proposal_id, entry_id, user_id, user_name, verdict, comment, edited)
    VALUES (p_id, p_proposal, p_entry, p_user, p_name, p_verdict, p_comment, p_edited)
    ON CONFLICT (proposal_id) DO UPDATE SET
        id = EXCLUDED.id, entry_id = EXCLUDED.entry_id, user_id = EXCLUDED.user_id,
        user_name = EXCLUDED.user_name, verdict = EXCLUDED.verdict, comment = EXCLUDED.comment,
        edited = EXCLUDED.edited, created_at = EXCLUDED.created_at
    RETURNING * INTO saved;
    RETURN NEXT saved;
END $save$;


CREATE OR REPLACE FUNCTION public.undo_proposal_decision(
    p_event text, p_review text, p_proposal text, p_user text
) RETURNS boolean LANGUAGE plpgsql SET search_path = public AS $undo$
DECLARE active public.proposal_decision; prior_id text;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtextextended(p_proposal, 624719));
    SELECT * INTO active FROM public.proposal_decision WHERE proposal_id = p_proposal;
    IF active.id IS DISTINCT FROM p_review OR active.user_id IS DISTINCT FROM p_user THEN
        RETURN false;
    END IF;
    SELECT previous_review_id INTO prior_id FROM public.proposal_review_event WHERE id = active.id;
    INSERT INTO public.proposal_review_event
        (id, proposal_id, entry_id, user_id, user_name, undone_review_id, previous_review_id)
    VALUES (p_event, p_proposal, active.entry_id, p_user, active.user_name, p_review, prior_id);
    DELETE FROM public.proposal_decision WHERE proposal_id = p_proposal;
    IF prior_id IS NOT NULL THEN
        INSERT INTO public.proposal_decision
            (id, proposal_id, entry_id, user_id, user_name, verdict, comment, edited, created_at)
        SELECT id, proposal_id, entry_id, user_id, user_name, verdict, comment, edited, created_at
        FROM public.proposal_review_event WHERE id = prior_id;
    END IF;
    RETURN true;
END $undo$;


-- Created last, in the same migration transaction. The runtime ensure checks this version marker.
CREATE OR REPLACE FUNCTION public.glossary_review_schema_v6() RETURNS integer
LANGUAGE sql IMMUTABLE AS $version$ SELECT 6 $version$;

END $migration$;
