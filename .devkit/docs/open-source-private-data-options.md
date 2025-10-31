# Open Source Code with Private Data: Deployment Options

**Date:** 2025-10-18
**Project:** Turoyo Verb Glossary
**Current Data:** 1,518 verb JSON files, 8.1 MB total in `server/assets/verbs/`

## Executive Summary

This document analyzes options for open-sourcing the Turoyo Verb Glossary codebase while keeping the proprietary verb data (1,696+ verbs) private, yet accessible to the Vercel-deployed application.

## Current Architecture

- **Framework:** Nuxt 4 with SSR, Vercel preset
- **Data Storage:** JSON files in `server/assets/verbs/*.json`
- **Data Access:** Nitro's `useStorage('assets:server')` API
- **Deployment:** Vercel with automatic GitHub deployments
- **Data Size:** 8.1 MB (1,518 files)

## Requirements

1. Code must be publicly accessible (open source)
2. Verb data must remain private
3. Deployed Vercel app must access the data
4. Data should ideally be hosted on Vercel infrastructure
5. Solution should be maintainable and cost-effective

## Option Comparison Table

| Option                    | Cost (8MB data)             | Setup Complexity | Maintenance | Vercel Integration       | Security  |
| ------------------------- | --------------------------- | ---------------- | ----------- | ------------------------ | --------- |
| 1. Git Submodule          | Free                        | High             | Medium      | Excellent                | Excellent |
| 2. Vercel Blob            | ~$0.18/mo + $0.40/mo egress | Medium           | Low         | Excellent                | Good      |
| 3. Build-time S3 Download | AWS Free Tier               | High             | Medium      | Good                     | Excellent |
| 4. NuxtHub (Cloudflare)   | ~$0.12/mo                   | Low              | Low         | N/A (different platform) | Excellent |
| 5. Vercel KV/Postgres     | KV: ~$0.30/mo               | Medium           | Low         | Excellent                | Excellent |
| 6. Two-Repo Strategy      | Free                        | Low              | High        | Good                     | Excellent |

## Detailed Options Analysis

---

### Option 1: Git Submodule with Private Repository

**Description:** Create a private Git repository containing only the verb data, reference it as a submodule in the public repository.

**Implementation:**

```bash
# 1. Create private repo "turoyo-verb-data"
mkdir turoyo-verb-data
cd turoyo-verb-data
git init
cp -r ../turoyo-verb-glossary/server/assets/verbs .
git add . && git commit -m "Initial verb data"
# Push to private GitHub repo

# 2. In public repo, add as submodule
cd turoyo-verb-glossary
git submodule add https://github.com/yourusername/turoyo-verb-data.git server/assets/verbs

# 3. Configure Vercel
# Settings > Environment Variables:
# GITHUB_ACCESS_TOKEN = <Personal Access Token with repo scope>

# 4. Create custom install script
# vercel-install.sh:
#!/bin/bash
git config --global url."https://$GITHUB_ACCESS_TOKEN@github.com/".insteadOf "https://github.com/"
git submodule update --init --recursive
pnpm install

# 5. Configure Build Command in Vercel
# Settings > General > Build & Development Settings
# Install Command: bash vercel-install.sh
```

**Pros:**

- Free
- Data stays in Git (version control benefits)
- Excellent security (private repo + access token)
- Works seamlessly with existing `useStorage('assets:server')`
- No code changes required
- Standard Git workflow for data updates

**Cons:**

- High setup complexity (Vercel doesn't natively support private submodules)
- Requires GitHub Personal Access Token management
- Custom build script needed
- Build time increases (submodule clone on every deploy)
- Token rotation requires Vercel env var update

**Best For:** Projects that want Git version control for data and don't mind the setup complexity.

**Resources:**

- [Private Git Submodules with Vercel](https://timmyomahony.com/blog/private-git-submodule-with-vercel/)
- [GitHub: vercel-private-submodule](https://github.com/beeinger/vercel-private-submodule)

---

### Option 2: Vercel Blob Storage

**Description:** Store verb JSON files in Vercel Blob (S3-backed object storage) and fetch them at runtime.

**Implementation:**

```typescript
// 1. Install Vercel Blob SDK
pnpm add @vercel/blob

// 2. Upload data to Blob (one-time migration)
// scripts/migrate-to-blob.ts
import { put } from '@vercel/blob'
import fs from 'fs/promises'

const files = await fs.readdir('server/assets/verbs')
for (const file of files) {
  const content = await fs.readFile(`server/assets/verbs/${file}`)
  await put(`verbs/${file}`, content, { access: 'public' })
}

// 3. Update repository to fetch from Blob
// server/repositories/verbs/getVerbByRoot.ts
import { list } from '@vercel/blob'

export async function getVerbByRoot(root: string) {
  const { blobs } = await list({ prefix: `verbs/${root}.json` })
  if (blobs.length === 0) return null
  const response = await fetch(blobs[0].url)
  return response.json()
}
```

**Pros:**

- Low maintenance (managed service)
- Excellent Vercel integration (automatic env vars)
- Scalable (S3-backed, 99.999999999% reliability)
- Fast global CDN delivery
- Simple SDK

**Cons:**

- Costs money (though minimal for 8MB):
  - Storage: $0.023/GB-month = ~$0.18/month
  - Data transfer: $0.05/GB = ~$0.40/month (assuming 8GB/month egress)
  - Operations: Negligible for this use case
- **All blobs are publicly accessible** (no private access option)
- Requires code changes (migration from `useStorage` to Blob SDK)
- Data not in version control
- Vendor lock-in to Vercel

**Important Limitation:** Vercel Blob currently does NOT support private access. All blobs are publicly accessible via their URL. If your verb data must be truly private (not just obscured), this is not suitable.

**Best For:** Projects with small budgets willing to pay for simplicity, where data doesn't need to be truly private.

**Pricing Calculator:** For 8MB storage + 8GB/month transfer = ~$0.58/month

---

### Option 3: Build-Time Download from AWS S3

**Description:** Store verb data in a private AWS S3 bucket and download it during Vercel build process.

**Implementation:**

```javascript
// 1. Upload data to private S3 bucket
// Use AWS Console or CLI to create bucket and upload server/assets/verbs/*

// 2. Create IAM user with read-only policy
// Policy: s3:GetObject, s3:ListBucket on your bucket

// 3. Configure Vercel Environment Variables
// AWS_ACCESS_KEY_ID = <IAM user key>
// AWS_SECRET_ACCESS_KEY = <IAM user secret>
// AWS_REGION = us-east-1
// S3_VERB_BUCKET = turoyo-verb-data

// 4. Create build-time download script
// scripts/download-verbs.js
import {
  S3Client,
  ListObjectsV2Command,
  GetObjectCommand,
} from "@aws-sdk/client-s3";
import fs from "fs/promises";
import path from "path";

const client = new S3Client({ region: process.env.AWS_REGION });

async function downloadVerbs() {
  const { Contents } = await client.send(
    new ListObjectsV2Command({
      Bucket: process.env.S3_VERB_BUCKET,
      Prefix: "verbs/",
    }),
  );

  await fs.mkdir("server/assets/verbs", { recursive: true });

  for (const obj of Contents) {
    const { Body } = await client.send(
      new GetObjectCommand({
        Bucket: process.env.S3_VERB_BUCKET,
        Key: obj.Key,
      }),
    );
    const filename = path.basename(obj.Key);
    await fs.writeFile(`server/assets/verbs/${filename}`, Body);
  }
}

downloadVerbs();

// 5. Update package.json
// "scripts": { "prebuild": "node scripts/download-verbs.js" }
```

**Pros:**

- Free (AWS S3 Free Tier: 5GB storage, 20,000 GET requests/month)
- Excellent security (private S3 bucket)
- No code changes to data access layer
- Data in private cloud storage with versioning
- Works with existing `useStorage('assets:server')`
- Not locked to Vercel (portable to other platforms)

**Cons:**

- High setup complexity (AWS account, IAM, S3)
- Requires AWS credentials management
- Increases build time (S3 download on every deploy)
- Two platforms to manage (AWS + Vercel)
- Needs `@aws-sdk/client-s3` dependency

**Best For:** Projects that already use AWS infrastructure or want maximum portability.

**Cost:** Free for this use case (well under AWS Free Tier limits)

---

### Option 4: Migrate to NuxtHub (Cloudflare)

**Description:** Switch from Vercel to NuxtHub (Cloudflare Workers + R2) deployment.

**Implementation:**

```bash
# 1. Install NuxtHub
npx nuxthub init

# 2. Use Cloudflare R2 Blob storage
# NuxtHub automatically provisions R2 bucket

# 3. Update nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@nuxthub/core'],
  hub: {
    blob: true
  }
})

# 4. Upload verbs to R2 (similar to Vercel Blob approach)
# Use hubBlob() composable to access files

# 5. Deploy to Cloudflare via NuxtHub
npx nuxthub deploy
```

**Pros:**

- Cheaper than Vercel Blob:
  - R2 storage: $0.015/GB-month = ~$0.12/month
  - **Zero egress fees** (huge savings)
  - Free tier available
- No vendor markup (direct Cloudflare billing)
- Excellent Nuxt integration (official Nuxt team product)
- Faster edge deployment
- Built-in database, KV, and caching
- Keep control of your Cloudflare account

**Cons:**

- **Not Vercel** (requires platform migration)
- Different deployment workflow
- Requires code changes (migrate from Nitro storage to NuxtHub Blob)
- Learning curve for Cloudflare Workers
- Less mature than Vercel (NuxtHub is in beta)

**Best For:** Projects willing to switch platforms for cost savings and want to stay in the Nuxt ecosystem.

**Note:** This is a platform change, not compatible with staying on Vercel.

---

### Option 5: Vercel KV (Key-Value Store)

**Description:** Store verbs as JSON strings in Vercel KV (Redis-backed key-value store).

**Implementation:**

```typescript
// 1. Provision Vercel KV in dashboard
// Dashboard > Storage > Create KV Database

// 2. Migration script
// scripts/migrate-to-kv.ts
import { kv } from "@vercel/kv";
import fs from "fs/promises";

const files = await fs.readdir("server/assets/verbs");
for (const file of files) {
  const content = await fs.readFile(`server/assets/verbs/${file}`, "utf-8");
  const key = `verb:${file.replace(".json", "")}`;
  await kv.set(key, content);
}

// 3. Update repository
// server/repositories/verbs/getVerbByRoot.ts
import { kv } from "@vercel/kv";

export async function getVerbByRoot(root: string) {
  const data = await kv.get<string>(`verb:${root}`);
  return data ? JSON.parse(data) : null;
}
```

**Pros:**

- Fast (in-memory Redis, <1ms latency)
- Excellent Vercel integration
- Automatic connection strings
- Can store data privately (not publicly accessible like Blob)
- Works well for key-value access pattern

**Cons:**

- More expensive:
  - KV storage: ~$0.40/GB-month = ~$3.20/month for 8MB
  - Commands: $0.20 per 100,000 requests
- Requires code changes
- Not ideal for large JSON documents (Redis is for small values)
- Over-engineered for static data
- 8MB might hit KV limits (designed for smaller values)

**Alternative: Vercel Postgres**

- Could store verbs in PostgreSQL (json/jsonb columns)
- Similar pricing to KV (~$0.25/GB-month)
- Better for structured data
- Also over-engineered for static data

**Best For:** Projects that need fast, private key-value access and already use Vercel KV/Postgres for other data.

**Not Recommended:** KV/Postgres are designed for dynamic, frequently changing data. Static verb data doesn't benefit from these features.

---

### Option 6: Two-Repository Strategy

**Description:** Maintain separate public (code) and private (code + data) repositories with regular merging.

**Implementation:**

```bash
# 1. Create public repo (code only)
# Add server/assets/verbs/ to .gitignore

# 2. Keep existing private repo as source of truth (code + data)

# 3. Regular export workflow
# In private repo:
git checkout -b public-export
git rm -r server/assets/verbs/
git commit -m "Remove private data for public export"
git push public-repo public-export:main

# 4. Deploy from private repo to Vercel
# Vercel > Import Git Repository > Select private repo
# Private repos work fine on Vercel (just not open source)
```

**Pros:**

- Free
- Simple setup (just separate Git repos)
- No code changes required
- Deploy directly from private repo (Vercel supports private repos)
- Data stays in Git version control
- Full control over what gets published

**Cons:**

- High maintenance burden (manual sync between repos)
- Risk of accidentally committing private data to public repo
- Two repos to manage
- Merge conflicts if code evolves differently
- Public repo can become outdated

**Workflow Optimization:**

- Use scripts to automate public repo exports
- Keep public repo read-only (only accept PRs, merge to private first)
- Use pre-commit hooks to prevent data leaks

**Best For:** Projects with infrequent code updates where manual repo syncing is acceptable.

---

## Recommendations

### Recommended: Option 1 (Git Submodule)

**Rationale:**

- Free and most aligned with your requirements
- Data remains in version control (important for linguistic data)
- Works with existing code (no migration needed)
- Vercel-compatible (though requires setup)
- Standard Git workflow for data updates

**Setup Effort:** ~2-3 hours initially, minimal ongoing maintenance

**Implementation Plan:**

1. Create private `turoyo-verb-data` repository
2. Move `server/assets/verbs/` to that repo
3. Add as submodule to public repo
4. Create GitHub Personal Access Token
5. Configure Vercel environment variables
6. Create custom install script
7. Test deployment

---

### Alternative: Option 3 (S3 Download)

**When to Choose:**

- You already have AWS infrastructure
- You want maximum portability (not locked to Vercel)
- You plan to use the data in other projects/platforms

**Setup Effort:** ~3-4 hours initially, minimal ongoing maintenance

---

### Not Recommended for This Use Case

- **Option 2 (Vercel Blob):** All blobs are public, defeating the privacy requirement
- **Option 5 (KV/Postgres):** Over-engineered and expensive for static data
- **Option 6 (Two Repos):** High maintenance burden, error-prone

---

## Implementation Checklist (Git Submodule Approach)

- [ ] Create private GitHub repository `turoyo-verb-data`
- [ ] Copy `server/assets/verbs/` to private repo
- [ ] Add `.gitignore` to private repo (ignore Python cache, etc.)
- [ ] Commit and push private repo
- [ ] In public repo: `git rm -r server/assets/verbs/`
- [ ] In public repo: `git submodule add <private-repo-url> server/assets/verbs`
- [ ] Create GitHub Personal Access Token with `repo` scope
- [ ] Add to Vercel: Environment Variable `GITHUB_ACCESS_TOKEN`
- [ ] Create `vercel-install.sh` script
- [ ] Test build locally with `bash vercel-install.sh && pnpm run build`
- [ ] Configure Vercel Install Command: `bash vercel-install.sh`
- [ ] Deploy and verify build succeeds
- [ ] Test verb data accessibility in deployed app
- [ ] Document submodule update workflow for team
- [ ] Update `README.md` with submodule setup instructions
- [ ] Add private repo URL to `.gitmodules`

---

## Security Considerations

### Git Submodule

- Personal Access Token has full repo access (minimize scope if possible)
- Token stored in Vercel env vars (secure but visible to all team members with access)
- Consider using GitHub Apps for more granular permissions

### S3 Download

- IAM user should have read-only access to single bucket
- Rotate AWS credentials periodically
- Enable S3 bucket versioning for data recovery

### General

- Never commit credentials to Git (use environment variables)
- Use `.gitignore` to prevent accidental data leaks
- Audit Vercel project access (who can see environment variables)
- Consider using Vercel Teams for fine-grained access control

---

## Cost Projection (12 months)

| Option        | Monthly | Annually | Notes                    |
| ------------- | ------- | -------- | ------------------------ |
| Git Submodule | $0      | $0       | Free tier                |
| Vercel Blob   | $0.58   | $7       | Public access only       |
| S3 Download   | $0      | $0       | Within AWS free tier     |
| NuxtHub/R2    | $0.12   | $1.44    | Requires platform switch |
| Vercel KV     | $3.20   | $38.40   | Not recommended          |

---

## Migration Effort Estimate

| Option        | Setup Time | Code Changes                | Testing | Total                 |
| ------------- | ---------- | --------------------------- | ------- | --------------------- |
| Git Submodule | 2h         | None                        | 1h      | 3h                    |
| Vercel Blob   | 1h         | Medium (SDK integration)    | 2h      | 5h                    |
| S3 Download   | 3h         | None                        | 1h      | 4h                    |
| NuxtHub       | 2h         | Medium (platform migration) | 4h      | 10h                   |
| Vercel KV     | 1h         | Medium (SDK integration)    | 2h      | 5h                    |
| Two Repos     | 1h         | None                        | 1h      | 2h (but high ongoing) |

---

## Additional Resources

### Official Documentation

- [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables)
- [Vercel Blob Storage](https://vercel.com/docs/vercel-blob)
- [AWS S3 with Vercel](https://vercel.com/guides/how-can-i-use-aws-s3-with-vercel)
- [NuxtHub Documentation](https://hub.nuxt.com/docs)

### Community Guides

- [Private Git Submodules with Vercel](https://timmyomahony.com/blog/private-git-submodule-with-vercel/)
- [How to Deploy Private Submodules to Vercel](https://medium.com/@ingamaholwana/how-to-set-up-vercel-to-clone-your-private-git-repo-submodules-when-installing-building-your-app-d452c3d52fbb)
- [Open Sourcing a Private Project](https://www.ombulabs.com/blog/open-source/open-sourcing-a-private-project.html)

---

## Next Steps

1. Review this document and choose your preferred option
2. If choosing Git Submodule (recommended):
   - Follow the implementation checklist above
   - Test thoroughly in Vercel preview deployment
   - Document the setup for future maintainers
3. If choosing S3 Download:
   - Set up AWS account and S3 bucket
   - Create IAM user with restricted permissions
   - Implement download script and test locally
4. Update project documentation with chosen approach
5. Consider adding CI/CD checks to prevent accidental data commits

---

**Document Version:** 1.0
**Last Updated:** 2025-10-18
**Author:** Claude (Anthropic)
