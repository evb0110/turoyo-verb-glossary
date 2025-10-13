/**
 * Slug utilities for handling homonymous roots
 * Converts between root notation and URL-safe slugs
 * Example: "bdy 1" <-> "bdy-1"
 */

/**
 * Convert a root to a URL-safe slug
 * @param root - The root string (e.g., "bdy 1")
 * @returns URL-safe slug (e.g., "bdy-1")
 */
export const rootToSlug = (root: string): string => root.replace(/\s/g, '-')

/**
 * Convert a slug back to a root
 * @param slug - The URL slug (e.g., "bdy-1")
 * @returns Root string (e.g., "bdy 1")
 */
export const slugToRoot = (slug: string): string => slug.replace(/-/g, ' ')
