CREATE TYPE "public"."user_role" AS ENUM('admin', 'user', 'pending', 'blocked');--> statement-breakpoint
ALTER TABLE "user" ADD COLUMN "role" "user_role" DEFAULT 'pending' NOT NULL;--> statement-breakpoint
UPDATE "user" SET "role" = 'admin' WHERE "email" = '7149553@gmail.com';