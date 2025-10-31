# Fixing Localhost Cookie Collision Across Multiple Dev Apps

## The Problem

When running multiple apps on different localhost ports (e.g., `localhost:3000`, `localhost:3100`), cookies set with `domain: 'localhost'` are shared across ALL ports, causing authentication conflicts and data leakage.

**Example Conflict:**

- App A on `localhost:3000` sets auth cookie with `domain: localhost`
- App B on `localhost:3100` receives the same cookie
- App B's auth breaks or uses wrong user session

## Why It Happens

**HTTP Cookie Behavior:**

- Cookies with `domain: 'localhost'` apply to ALL subdomains and ports
- Browsers ignore port numbers when matching cookie domains
- Both Nuxt and better-auth default to setting `domain: 'localhost'` in development

**Failed Solutions:**

- ❌ Setting `domain: undefined` or `domain: ''` - Libraries override this
- ❌ Using `.localhost` subdomains (e.g., `app.localhost`) - Google OAuth rejects these
- ❌ Using port-specific cookies - Port numbers are ignored by cookie domain matching

## The Solution: Use lvh.me

**lvh.me** is a magic DNS service that:

- ✅ Always resolves to `127.0.0.1` (including all subdomains)
- ✅ Uses real `.me` TLD (accepted by Google OAuth and other providers)
- ✅ Supports unlimited subdomains for cookie isolation
- ✅ Requires no `/etc/hosts` configuration
- ✅ Works with HTTP (no SSL required for local dev)

**Example URLs:**

- `http://app1.lvh.me:3000` → `127.0.0.1:3000` (cookies: `app1.lvh.me`)
- `http://app2.lvh.me:3100` → `127.0.0.1:3100` (cookies: `app2.lvh.me`)
- `http://api.lvh.me:8000` → `127.0.0.1:8000` (cookies: `api.lvh.me`)

**Alternatives:** `localtest.me`, `vcap.me`, `nip.io` (all work the same way)

## Implementation Guide

### 1. Nuxt 4 + better-auth (This Project)

**File: `nuxt.config.ts`**

```typescript
export default defineNuxtConfig({
  devServer: {
    port: 3100,
    host: "0.0.0.0", // Accept connections on all interfaces
  },

  hooks: {
    listen(server, { host, port }) {
      const devUrl = "http://mss-client.lvh.me:3100";
      console.log(`\n  ➜ Dev Client: \x1b[36m${devUrl}\x1b[0m`);
    },
  },

  runtimeConfig: {
    public: {
      siteUrl:
        process.env.NUXT_PUBLIC_SITE_URL ||
        (process.env.VERCEL_URL
          ? `https://${process.env.VERCEL_URL}`
          : "http://mss-client.lvh.me:3100"),
    },
  },
});
```

**File: `server/lib/auth.ts`**

```typescript
export const auth = betterAuth({
  baseURL: config.public.siteUrl, // Uses lvh.me in dev
  // ... rest of config
});
```

**Cookie Configuration:**

```typescript
// Remove explicit domain attribute - let browser use hostname
const deviceId = useCookie("device_id", {
  sameSite: "lax",
  maxAge: 60 * 60 * 24 * 180,
  // NO domain property - defaults to hostname only
});
```

**Backend CORS (Hono/Express):**

```typescript
const allowedOrigins = [
  "http://localhost:3100", // Keep for backwards compatibility
  "http://mss-client.lvh.me:3100", // New isolated domain
  "https://your-app.vercel.app", // Production
];
```

### 2. Next.js + NextAuth

**File: `next.config.js`**

```javascript
module.exports = {
  devIndicators: {
    buildActivity: true,
  },
  async rewrites() {
    return {
      beforeFiles: [
        {
          source: "/:path*",
          has: [{ type: "host", value: "app.lvh.me" }],
          destination: "/:path*",
        },
      ],
    };
  },
};
```

**File: `.env.local`**

```env
NEXTAUTH_URL=http://app.lvh.me:3000
```

**Run with:**

```bash
next dev -H 0.0.0.0 -p 3000
```

**Then access:** `http://app.lvh.me:3000`

### 3. Express/Hono Backend

**File: `src/index.ts`** (Bun)

```typescript
export default {
  port: 3000,
  hostname: "0.0.0.0", // Accept all interfaces
  async fetch(request: Request, server: any) {
    return app.fetch(request, server);
  },
};
```

**File: `server.js`** (Node.js)

```javascript
const express = require("express");
const app = express();

app.listen(3000, "0.0.0.0", () => {
  console.log("Backend: http://api.lvh.me:3000");
});
```

**CORS Configuration:**

```javascript
const cors = require("cors");

app.use(
  cors({
    origin: (origin, callback) => {
      const allowedOrigins = [
        "http://localhost:3000",
        "http://app.lvh.me:3000",
        "https://your-app.com",
      ];
      if (!origin || allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(new Error("Not allowed by CORS"));
      }
    },
    credentials: true,
  }),
);
```

### 4. Vite + React/Vue

**File: `vite.config.ts`**

```typescript
export default defineConfig({
  server: {
    port: 5173,
    host: "0.0.0.0",
    strictPort: true,
  },
});
```

**Access:** `http://app.lvh.me:5173`

### 5. Google OAuth Configuration

**Critical Step:** Update Authorized Redirect URIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Select your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs", **add**:
   ```
   http://mss-client.lvh.me:3100/api/auth/callback/google
   http://app.lvh.me:3000/api/auth/callback/google
   ```
4. Keep existing URIs (`localhost`, production)
5. Click **Save**

**Important:** Google OAuth requires:

- Real public TLD (`.com`, `.me`, `.org`) - ✅ `lvh.me` works
- NO `.local` domains - ❌ `app.localhost` is rejected
- NO IP addresses for OAuth (except `localhost`)

### 6. Other OAuth Providers

**GitHub OAuth:**

- Supports `lvh.me` subdomains
- Add to "Authorization callback URL": `http://app.lvh.me:3000/api/auth/callback/github`

**Auth0:**

- Add to "Allowed Callback URLs": `http://app.lvh.me:3000/callback`
- Add to "Allowed Logout URLs": `http://app.lvh.me:3000`

**Clerk:**

- Add to "Authorized redirect URLs" in Dashboard

## Testing Cookie Isolation

**Before Fix:**

```bash
# Chrome DevTools → Application → Cookies → localhost
Domain: localhost
Path: /
# ❌ Cookie visible on both localhost:3000 AND localhost:3100
```

**After Fix:**

```bash
# Chrome DevTools → Application → Cookies → app1.lvh.me
Domain: app1.lvh.me
Path: /
# ✅ Cookie ONLY visible on app1.lvh.me:3000, NOT on app2.lvh.me:3100
```

**Test Steps:**

1. Clear all cookies
2. Login at `http://app1.lvh.me:3000`
3. Check cookies in DevTools - should show `Domain: app1.lvh.me`
4. Open `http://app2.lvh.me:3100` - should NOT have app1's cookies
5. Verify localhost apps are isolated from lvh.me apps

## Troubleshooting

**Problem: "This site can't be reached"**

- **Solution:** Verify DNS: `ping app.lvh.me` should resolve to `127.0.0.1`
- **Cause:** DNS resolver issues - try `8.8.8.8` or restart network

**Problem: "ERR_SSL_PROTOCOL_ERROR"**

- **Solution:** Use `http://` not `https://` for local dev
- **Cause:** No SSL cert for local development

**Problem: Google OAuth "Invalid origin"**

- **Solution:** Ensure redirect URI exactly matches (check trailing slashes, ports)
- **Check:** Authorized redirect URI must be added in Google Console

**Problem: Cookies still showing "localhost"**

- **Solution:** Clear ALL cookies and restart both servers
- **Cause:** Old cookies persisting from previous configuration

**Problem: CORS errors**

- **Solution:** Add `app.lvh.me:PORT` to backend's allowed origins
- **Solution:** Ensure backend listens on `0.0.0.0`, not `127.0.0.1`

## Alternative Solutions

### Option A: Different Ports on Plain Localhost

**Pros:** Simple, no DNS changes
**Cons:** Cookies still collide - doesn't solve the problem

### Option B: /etc/hosts with Custom Domains

```bash
# /etc/hosts
127.0.0.1 app1.local.com
127.0.0.1 app2.local.com
```

**Pros:** Full control
**Cons:** Google OAuth may reject fake TLDs, requires manual setup

### Option C: Nginx Reverse Proxy

**Pros:** Production-like setup
**Cons:** Complex, overkill for simple cookie isolation

## Summary

**Best Practice for Multi-App Localhost Development:**

1. **Use `lvh.me` subdomains** for all apps
2. **Configure servers to listen on `0.0.0.0`** (not `127.0.0.1`)
3. **Update OAuth provider redirect URIs** to include `lvh.me` URLs
4. **Remove explicit cookie `domain` settings** - let browser use hostname
5. **Update CORS** to allow `lvh.me` origins
6. **Test cookie isolation** in DevTools

**Result:**

- ✅ Complete cookie isolation between apps
- ✅ Works with Google OAuth and other providers
- ✅ No `/etc/hosts` configuration needed
- ✅ Production-like domain structure in development
- ✅ Zero-configuration DNS

---

**Created:** 2025-01-19
**Project:** mss-client (Nuxt 4 + better-auth)
**Tested with:** Google OAuth, Nuxt 4, Hono backend, Bun runtime
