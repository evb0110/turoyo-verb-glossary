export const activityEventTypes = [
    'search_fulltext',
    'search_roots',
    'view_stats',
    'view_verb',
] as const

export type TActivityEventType = typeof activityEventTypes[number]
