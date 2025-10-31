# Vercel Environment Variable Migration

## Required Changes on Vercel

The application now follows Nuxt 4 conventions for environment variables. All runtime config values are automatically overridden by `NUXT_` prefixed environment variables.

### Environment Variable Renames

| Old Variable Name      | New Variable Name           | Value on Production                       |
| ---------------------- | --------------------------- | ----------------------------------------- |
| `BETTER_AUTH_URL`      | `NUXT_PUBLIC_SITE_URL`      | `https://turoyo-verb-glossary.vercel.app` |
| `BETTER_AUTH_SECRET`   | `NUXT_BETTER_AUTH_SECRET`   | (keep existing value)                     |
| `GOOGLE_CLIENT_ID`     | `NUXT_GOOGLE_CLIENT_ID`     | (keep existing value)                     |
| `GOOGLE_CLIENT_SECRET` | `NUXT_GOOGLE_CLIENT_SECRET` | (keep existing value)                     |
| `DATABASE_URL`         | `NUXT_DATABASE_URL`         | (keep existing value)                     |

### How Nuxt Environment Variables Work

1. **Naming Convention:**
   - `NUXT_` prefix for private server-side config
   - `NUXT_PUBLIC_` prefix for values accessible on both server and client
   - Underscores map to nested keys (e.g., `NUXT_PUBLIC_SITE_URL` → `runtimeConfig.public.siteUrl`)

2. **Runtime Override:**
   - Values in `nuxt.config.ts` are defaults
   - Environment variables automatically override at runtime
   - No code changes needed when updating URLs between environments

3. **Security:**
   - `NUXT_PUBLIC_*` variables are exposed to the client bundle
   - `NUXT_*` variables (without PUBLIC) stay server-side only

### OAuth Callback URL

With `NUXT_PUBLIC_SITE_URL=https://turoyo-verb-glossary.vercel.app`, the Google OAuth callback URL will be:

```
https://turoyo-verb-glossary.vercel.app/api/auth/callback/google
```

This is automatically constructed by Better Auth using the `baseURL` configuration in `server/lib/auth.ts`.

### Local Development

Local `.env` file already updated with `NUXT_` prefixed variables. The default in `nuxt.config.ts` is set to the dev URL, so the `.env` file is optional for local development.

### Steps to Apply on Vercel

1. Go to Vercel project settings → Environment Variables
2. Delete old variables: `BETTER_AUTH_URL`, `BETTER_AUTH_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
3. Add new variables with `NUXT_` prefix as shown in the table above
4. Redeploy the application

### Verification

After deployment, verify:

1. OAuth login works correctly
2. Callback URL matches Google Cloud Console configuration
3. No console errors related to authentication
