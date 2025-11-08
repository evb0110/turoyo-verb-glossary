CREATE TYPE "public"."activity_event_type" AS ENUM('search_fulltext', 'search_roots', 'view_stats', 'view_verb');--> statement-breakpoint
CREATE TABLE "user_activity_log" (
	"id" text PRIMARY KEY NOT NULL,
	"user_id" text NOT NULL,
	"session_activity_id" text,
	"event_type" "activity_event_type" NOT NULL,
	"path" text,
	"query" text,
	"filters" jsonb,
	"result_count" integer,
	"metadata" jsonb,
	"status_code" integer DEFAULT 200 NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "user_session_activity" (
	"id" text PRIMARY KEY NOT NULL,
	"session_id" text NOT NULL,
	"user_id" text NOT NULL,
	"ip_address" text,
	"user_agent" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"last_activity_at" timestamp DEFAULT now() NOT NULL,
	"total_requests" integer DEFAULT 0 NOT NULL,
	"search_requests" integer DEFAULT 0 NOT NULL,
	"stats_requests" integer DEFAULT 0 NOT NULL,
	"last_search_query" text,
	"last_filters" jsonb,
	CONSTRAINT "user_session_activity_session_id_unique" UNIQUE("session_id")
);
--> statement-breakpoint
ALTER TABLE "user_activity_log" ADD CONSTRAINT "user_activity_log_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "user_activity_log" ADD CONSTRAINT "user_activity_log_session_activity_id_user_session_activity_id_fk" FOREIGN KEY ("session_activity_id") REFERENCES "public"."user_session_activity"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "user_session_activity" ADD CONSTRAINT "user_session_activity_session_id_session_id_fk" FOREIGN KEY ("session_id") REFERENCES "public"."session"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "user_session_activity" ADD CONSTRAINT "user_session_activity_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;