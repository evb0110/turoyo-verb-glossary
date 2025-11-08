import { pgTable, text, timestamp, boolean, pgEnum, integer, jsonb } from 'drizzle-orm/pg-core'
import { activityEventTypes } from '../../shared/config/activityEventTypes'

export const userRoleEnum = pgEnum('user_role', ['admin', 'user', 'pending', 'blocked'])
export const activityEventTypeEnum = pgEnum('activity_event_type', activityEventTypes)

export const user = pgTable('user', {
    id: text('id').primaryKey(),
    name: text('name').notNull(),
    email: text('email').notNull().unique(),
    emailVerified: boolean('email_verified').default(false).notNull(),
    image: text('image'),
    role: userRoleEnum('role').default('pending').notNull(),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at')
        .defaultNow()
        .$onUpdate(() => new Date())
        .notNull(),
})

export const session = pgTable('session', {
    id: text('id').primaryKey(),
    expiresAt: timestamp('expires_at').notNull(),
    token: text('token').notNull().unique(),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at')
        .$onUpdate(() => new Date())
        .notNull(),
    ipAddress: text('ip_address'),
    userAgent: text('user_agent'),
    userId: text('user_id')
        .notNull()
        .references(() => user.id, { onDelete: 'cascade' }),
})

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
    accessTokenExpiresAt: timestamp('access_token_expires_at'),
    refreshTokenExpiresAt: timestamp('refresh_token_expires_at'),
    scope: text('scope'),
    password: text('password'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at')
        .$onUpdate(() => new Date())
        .notNull(),
})

export const verification = pgTable('verification', {
    id: text('id').primaryKey(),
    identifier: text('identifier').notNull(),
    value: text('value').notNull(),
    expiresAt: timestamp('expires_at').notNull(),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at')
        .defaultNow()
        .$onUpdate(() => new Date())
        .notNull(),
})

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
    createdAt: timestamp('created_at').defaultNow().notNull(),
    lastActivityAt: timestamp('last_activity_at').defaultNow().notNull(),
    totalRequests: integer('total_requests').default(0).notNull(),
    searchRequests: integer('search_requests').default(0).notNull(),
    statsRequests: integer('stats_requests').default(0).notNull(),
    lastSearchQuery: text('last_search_query'),
    lastFilters: jsonb('last_filters').$type<Record<string, unknown> | null>(),
})

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
    createdAt: timestamp('created_at').defaultNow().notNull(),
})
