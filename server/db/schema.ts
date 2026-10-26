import { sql } from 'drizzle-orm'
import { pgTable, text, timestamp, boolean, pgEnum, integer, jsonb, index, check } from 'drizzle-orm/pg-core'
import { activityEventTypes } from '../../shared/config/activityEventTypes'
import type { IProposalEdit } from '../../shared/types/IProposalEdit'

export const userRoleEnum = pgEnum('user_role', ['admin', 'user', 'pending', 'blocked'])
export const activityEventTypeEnum = pgEnum('activity_event_type', activityEventTypes)

export const user = pgTable('user', {
    id: text('id').primaryKey(),
    name: text('name').notNull(),
    email: text('email').notNull().unique(),
    emailVerified: boolean('email_verified').default(false).notNull(),
    image: text('image'),
    role: userRoleEnum('role').default('pending').notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
    updatedAt: timestamp('updated_at', { withTimezone: true })
        .defaultNow()
        .$onUpdate(() => new Date())
        .notNull(),
})

export const session = pgTable('session', {
    id: text('id').primaryKey(),
    expiresAt: timestamp('expires_at', { withTimezone: true }).notNull(),
    token: text('token').notNull().unique(),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
    updatedAt: timestamp('updated_at', { withTimezone: true })
        .$onUpdate(() => new Date())
        .notNull(),
    ipAddress: text('ip_address'),
    userAgent: text('user_agent'),
    userId: text('user_id')
        .notNull()
        .references(() => user.id, { onDelete: 'cascade' }),
}, table => [index('session_user_idx').on(table.userId)])

export const account = pgTable('account', {
    id: text('id').primaryKey(),
    accountId: text('account_id').notNull(),
    providerId: text('provider_id').notNull(),
    userId: text('user_id')
        .notNull()
        .references(() => user.id, { onDelete: 'cascade' }),
    accessToken: text('access_token'),
    refreshToken: text('refresh_token'),
    idToken: text('id_token'),
    accessTokenExpiresAt: timestamp('access_token_expires_at', { withTimezone: true }),
    refreshTokenExpiresAt: timestamp('refresh_token_expires_at', { withTimezone: true }),
    scope: text('scope'),
    password: text('password'),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
    updatedAt: timestamp('updated_at', { withTimezone: true })
        .$onUpdate(() => new Date())
        .notNull(),
}, table => [index('account_user_idx').on(table.userId), index('account_provider_idx').on(table.providerId, table.accountId)])

export const verification = pgTable('verification', {
    id: text('id').primaryKey(),
    identifier: text('identifier').notNull(),
    value: text('value').notNull(),
    expiresAt: timestamp('expires_at', { withTimezone: true }).notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
    updatedAt: timestamp('updated_at', { withTimezone: true })
        .defaultNow()
        .$onUpdate(() => new Date())
        .notNull(),
}, table => [index('verification_identifier_idx').on(table.identifier)])

export const userSessionActivity = pgTable('user_session_activity', {
    id: text('id').primaryKey(),
    sessionId: text('session_id')
        .notNull()
        .references(() => session.id, { onDelete: 'cascade' })
        .unique(),
    userId: text('user_id')
        .notNull()
        .references(() => user.id, { onDelete: 'cascade' }),
    ipAddress: text('ip_address'),
    userAgent: text('user_agent'),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
    lastActivityAt: timestamp('last_activity_at', { withTimezone: true }).defaultNow().notNull(),
    totalRequests: integer('total_requests').default(0).notNull(),
    searchRequests: integer('search_requests').default(0).notNull(),
    statsRequests: integer('stats_requests').default(0).notNull(),
    lastSearchQuery: text('last_search_query'),
    lastFilters: jsonb('last_filters').$type<Record<string, unknown> | null>(),
}, table => [
    index('session_activity_recent_idx').on(table.lastActivityAt, table.createdAt),
    index('session_activity_user_recent_idx').on(table.userId, table.lastActivityAt),
    check('session_activity_counters_check', sql`${table.totalRequests} >= 0 AND ${table.searchRequests} >= 0 AND ${table.statsRequests} >= 0`),
])

export const userActivityLog = pgTable('user_activity_log', {
    id: text('id').primaryKey(),
    host: text('host'),
    userId: text('user_id')
        .notNull()
        .references(() => user.id, { onDelete: 'cascade' }),
    sessionActivityId: text('session_activity_id')
        .references(() => userSessionActivity.id, { onDelete: 'cascade' }),
    eventType: activityEventTypeEnum('event_type').notNull(),
    path: text('path'),
    query: text('query'),
    filters: jsonb('filters').$type<Record<string, unknown> | null>(),
    resultCount: integer('result_count'),
    metadata: jsonb('metadata').$type<Record<string, unknown> | null>(),
    statusCode: integer('status_code').default(200).notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
}, table => [
    index('activity_recent_idx').on(table.createdAt),
    index('activity_user_recent_idx').on(table.userId, table.createdAt),
    index('activity_session_recent_idx').on(table.sessionActivityId, table.createdAt),
    index('activity_type_recent_idx').on(table.eventType, table.createdAt),
    index('activity_host_recent_idx').on(table.host, table.createdAt),
    check('activity_status_check', sql`${table.statusCode} BETWEEN 100 AND 599`),
    check('activity_result_count_check', sql`${table.resultCount} IS NULL OR ${table.resultCount} >= 0`),
])

// Retained for schema continuity. The site reads glossary assets, but future
// generated migrations must not interpret retiring the UI as dropping data.
export const verbs = pgTable('verbs', {
    root: text('root').primaryKey(),
    etymology: jsonb('etymology'),
    crossReference: text('cross_reference'),
    stems: jsonb('stems').notNull(),
    idioms: jsonb('idioms'),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().$onUpdate(() => new Date()).notNull(),
})

export const proposalVerdictEnum = pgEnum('proposal_verdict', ['accept', 'reject', 'discuss'])

// One row per proposal. The id is the active decision event, not a second identity.
export const proposalDecision = pgTable('proposal_decision', {
    proposalId: text('proposal_id').primaryKey(),
    id: text('id').notNull().unique(),
    entryId: text('entry_id').notNull(),
    userId: text('user_id').references(() => user.id, { onDelete: 'set null' }),
    userName: text('user_name').notNull(),
    verdict: proposalVerdictEnum('verdict').notNull(),
    edited: jsonb('edited').$type<IProposalEdit | null>(),
    comment: text('comment'),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
}, table => [
    index('proposal_decision_user_idx').on(table.userId),
    check('proposal_decision_comment_check', sql`${table.comment} IS NULL OR length(${table.comment}) <= 5000`),
    check('proposal_decision_edit_check', sql`${table.edited} IS NULL OR (${table.verdict} = 'accept' AND jsonb_typeof(${table.edited}) = 'object' AND ${table.edited} ? 'text' AND jsonb_typeof(${table.edited}->'text') = 'string' AND length(btrim(${table.edited}->>'text')) BETWEEN 1 AND 20000 AND octet_length(${table.edited}::text) <= 200000)`),
])

// Immutable decision snapshots and undo events. User deletion keeps the editorial record.
export const proposalReviewEvent = pgTable('proposal_review_event', {
    id: text('id').primaryKey(),
    proposalId: text('proposal_id').notNull(),
    entryId: text('entry_id').notNull(),
    userId: text('user_id').references(() => user.id, { onDelete: 'set null' }),
    userName: text('user_name').notNull(),
    verdict: proposalVerdictEnum('verdict'),
    edited: jsonb('edited').$type<IProposalEdit | null>(),
    comment: text('comment'),
    previousReviewId: text('previous_review_id'),
    undoneReviewId: text('undone_review_id'),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
}, table => [
    index('proposal_review_event_proposal_created_idx').on(table.proposalId, table.createdAt, table.id),
    index('proposal_review_event_user_idx').on(table.userId),
    check('proposal_review_event_action_check', sql`(${table.verdict} IS NOT NULL AND ${table.undoneReviewId} IS NULL) OR (${table.verdict} IS NULL AND ${table.undoneReviewId} IS NOT NULL AND ${table.edited} IS NULL)`),
    check('proposal_review_event_comment_check', sql`${table.comment} IS NULL OR length(${table.comment}) <= 5000`),
    check('proposal_review_event_edit_check', sql`${table.edited} IS NULL OR (${table.verdict} = 'accept' AND jsonb_typeof(${table.edited}) = 'object' AND ${table.edited} ? 'text' AND jsonb_typeof(${table.edited}->'text') = 'string' AND length(btrim(${table.edited}->>'text')) BETWEEN 1 AND 20000 AND octet_length(${table.edited}::text) <= 200000)`),
])
