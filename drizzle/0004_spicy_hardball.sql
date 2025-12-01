CREATE TABLE "verbs" (
	"root" text PRIMARY KEY NOT NULL,
	"etymology" jsonb,
	"cross_reference" text,
	"stems" jsonb NOT NULL,
	"idioms" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
