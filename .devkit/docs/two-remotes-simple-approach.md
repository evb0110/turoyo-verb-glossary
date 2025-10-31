# Two-Remote Strategy: Private Data + Public Code (Vercel CLI Deployment)

**Date:** 2025-10-18
**Context:** Vercel deployment via CLI (not GitHub integration)

## The Simplified Approach

Since you deploy via `vercel` CLI rather than GitHub integration, this becomes **dramatically simpler**. You don't need submodules, S3, or complex build scripts. Just use **two Git remotes with careful .gitignore management**.

## Architecture

```
Local Folder (single .git repo)
├── .git/                          # One Git repo
│   ├── config                     # Contains multiple remotes
├── .claude/                       # PRIVATE (Claude config)
├── server/assets/verbs/*.json     # PRIVATE (1,518 verb files)
├── source/Turoyo_all_2024.html   # PRIVATE (source data)
├── parser/*.py                    # PUBLIC (parsing code)
├── app/, server/, etc.            # PUBLIC (Nuxt app code)
└── .gitignore                     # Controls what goes public

Git Remotes:
├── origin (private) → github.com/evb0110/turoyo-verb-glossary-private
└── public → github.com/evb0110/turoyo-verb-glossary

Vercel Deployment:
└── vercel deploy (from local folder with everything)
```

## How It Works

1. **Local repo contains everything** (data + code)
2. **Private remote** (`origin`) gets everything pushed
3. **Public remote** gets only code (data files ignored via .gitignore)
4. **Vercel CLI deploys** from local folder (which has everything)

## Implementation Steps

### Step 1: Create Public Repository

```bash
# On GitHub, create new public repo: turoyo-verb-glossary
# Don't initialize it (you'll push from existing repo)
```

### Step 2: Update Current Repo to Private

```bash
# Make current repo private on GitHub
# Settings > Danger Zone > Change repository visibility > Make private
```

### Step 3: Add Public Remote

```bash
# Add second remote for public code-only repo
git remote add public git@github.com:evb0110/turoyo-verb-glossary.git

# Verify remotes
git remote -v
# Should show:
# origin  git@github.com:evb0110/turoyo-verb-glossary-private.git (fetch)
# origin  git@github.com:evb0110/turoyo-verb-glossary-private.git (push)
# public  git@github.com:evb0110/turoyo-verb-glossary.git (fetch)
# public  git@github.com:evb0110/turoyo-verb-glossary.git (push)
```

### Step 4: Create Public .gitignore

```bash
# Create .gitignore-public (what to exclude from public repo)
cat > .gitignore-public << 'EOF'
# Inherit base .gitignore
# (Copy everything from .gitignore first)

# PRIVATE: Claude configuration
.claude/
CLAUDE.md

# PRIVATE: Verb data
server/assets/verbs/
source/Turoyo_all_2024.html

# PRIVATE: Old data files
data/*.json

# PRIVATE: Development/analysis docs
.devkit/

# PRIVATE: Environment
.env*
.vercel/
EOF
```

### Step 5: Setup Push Workflow

Create a script to push to public repo with filtered content:

```bash
# scripts/push-public.sh
#!/bin/bash
set -e

echo "Pushing to public repository (code only)..."

# Save current .gitignore
cp .gitignore .gitignore.backup

# Use public .gitignore
cp .gitignore-public .gitignore

# Remove private files from git index (not from disk)
git rm --cached -r .claude/ 2>/dev/null || true
git rm --cached -r server/assets/verbs/ 2>/dev/null || true
git rm --cached -r source/ 2>/dev/null || true
git rm --cached -r .devkit/ 2>/dev/null || true
git rm --cached .vercel/ 2>/dev/null || true

# Commit the public version
git add .gitignore
git commit -m "Public release: Code only (no private data)"

# Push to public remote
git push public main

# Restore original .gitignore
mv .gitignore.backup .gitignore
git add .gitignore
git commit -m "Restore private .gitignore"

echo "✓ Public repository updated"
```

**WAIT - This approach has a problem**: It creates extra commits and messes with history.

### Better Approach: Git Filter-Branch or Subtree Split

Actually, let me revise this...

## REVISED: Cleaner Two-Remote Strategy

### Option A: Manual Branch Management (Simplest)

```bash
# 1. Create a public branch that excludes private files
git checkout -b public-release

# 2. Update .gitignore to exclude private data
cat >> .gitignore << 'EOF'

# PRIVATE DATA (excluded from public branch)
.claude/
server/assets/verbs/
source/Turoyo_all_2024.html
.devkit/
EOF

# 3. Remove private files from this branch only
git rm -r --cached .claude/
git rm -r --cached server/assets/verbs/
git rm -r --cached source/
git rm -r --cached .devkit/

# 4. Commit
git commit -m "Public release branch: Code only"

# 5. Push to public remote
git remote add public git@github.com:evb0110/turoyo-verb-glossary.git
git push public public-release:main

# 6. Switch back to private main branch
git checkout main

# From now on:
# - Work on 'main' branch (has everything)
# - Periodically merge main into public-release (git merge -X theirs main)
# - Push public-release to public remote
```

**Problem**: This still requires branch management and merging.

### Option B: Git-Filter-Repo on Push (Most Automated)

Use `git-filter-repo` or `git filter-branch` to automatically strip private data when pushing to public remote.

```bash
# Install git-filter-repo
brew install git-filter-repo  # macOS

# Create script: scripts/sync-public.sh
#!/bin/bash
set -e

# Clone current repo to temp location
TEMP_DIR=$(mktemp -d)
git clone . "$TEMP_DIR"
cd "$TEMP_DIR"

# Remove private data
git filter-repo --path .claude --invert-paths --force
git filter-repo --path server/assets/verbs --invert-paths --force
git filter-repo --path source/Turoyo_all_2024.html --invert-paths --force
git filter-repo --path .devkit --invert-paths --force

# Push to public remote
git remote add public git@github.com:evb0110/turoyo-verb-glossary.git
git push --force public main

# Cleanup
cd -
rm -rf "$TEMP_DIR"

echo "✓ Public repository synced"
```

**Problem**: This rewrites history and requires force push.

### Option C: Simplest Approach (Recommended)

**Just use .gitignore and never commit private data to public repo.**

Here's the cleanest solution:

```bash
# 1. Add private data to .gitignore NOW (before it's committed to public)
echo "" >> .gitignore
echo "# Private data (not for public release)" >> .gitignore
echo ".claude/" >> .gitignore
echo "server/assets/verbs/" >> .gitignore
echo "source/Turoyo_all_2024.html" >> .gitignore
echo ".devkit/" >> .gitignore

# 2. Remove from git tracking (keeps files on disk)
git rm -r --cached .claude/
git rm -r --cached server/assets/verbs/
git rm -r --cached source/
git rm -r --cached .devkit/

# 3. Commit the removal
git commit -m "Remove private data from version control"

# 4. Add public remote
git remote add public git@github.com:evb0110/turoyo-verb-glossary.git

# 5. Push to public
git push public main

# Done! From now on:
# - Private data stays on disk but not in Git
# - Push to 'origin' for private backup (if needed)
# - Push to 'public' for open source
# - Vercel CLI deploys from local disk (has everything)
```

**WAIT**: But you want the private data in Git for version control and backup.

## FINAL SOLUTION: The Right Way

After thinking through all options, here's the **correct architecture**:

### Architecture

1. **Private repo (origin)**: Contains EVERYTHING (code + data) - your source of truth
2. **Public repo (public remote)**: Contains ONLY code - synced periodically
3. **Local working directory**: Has everything (deploys to Vercel)

### Setup

```bash
# Current state: You have a private repo with everything
# Goal: Create public repo with just code

# Step 1: Create empty public repo on GitHub
# github.com/evb0110/turoyo-verb-glossary (public)

# Step 2: Add public remote
git remote add public git@github.com:evb0110/turoyo-verb-glossary.git

# Step 3: Create public branch (one-time)
git checkout -b public

# Step 4: Create .gitignore for public branch
cat > .gitignore-public << 'EOF'
# Copy all from main .gitignore, then add:

# === PRIVATE DATA (excluded from public repo) ===
.claude/
server/assets/verbs/
source/Turoyo_all_2024.html
.devkit/
.env*
.vercel/
EOF

# Step 5: Remove private files from public branch
git rm -r .claude/
git rm -r server/assets/verbs/
git rm -r source/
git rm -r .devkit/
cp .gitignore-public .gitignore
git add .gitignore

# Step 6: Commit and push
git commit -m "Initial public release - code only"
git push public public:main

# Step 7: Return to main branch
git checkout main

# Step 8: Set up sync script for future updates
```

### Sync Script (scripts/sync-public.sh)

```bash
#!/bin/bash
set -e

echo "Syncing public repository..."

# Save current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Switch to public branch
git checkout public

# Merge changes from main, keeping public's file exclusions
git merge main -m "Sync from main" --no-edit || true

# Ensure private files stay removed
git rm -r .claude/ 2>/dev/null || true
git rm -r server/assets/verbs/ 2>/dev/null || true
git rm -r source/ 2>/dev/null || true
git rm -r .devkit/ 2>/dev/null || true

# Commit if there are changes
if [[ -n $(git status -s) ]]; then
    git commit -m "Sync: Remove private files"
fi

# Push to public remote
git push public public:main

# Return to original branch
git checkout "$CURRENT_BRANCH"

echo "✓ Public repository synced"
```

**PROBLEM**: This is getting complex again. Let me think of the absolute simplest approach...

## THE SIMPLEST SOLUTION (Final Answer)

Since Vercel deploys via CLI from your local machine, you don't need the private data in Git at all!

### Ultra-Simple Approach

1. **Add private files to .gitignore** (never commit them)
2. **Keep private files on disk only** (local + backup)
3. **Push everything to public GitHub** (just code)
4. **Deploy via Vercel CLI** (reads from local disk, has everything)

```bash
# 1. Add private data to .gitignore
cat >> .gitignore << 'EOF'

# Private data (not in version control)
.claude/
server/assets/verbs/
source/Turoyo_all_2024.html
.devkit/
EOF

# 2. Remove from Git (keeps on disk)
git rm -r --cached .claude/
git rm -r --cached server/assets/verbs/
git rm -r --cached source/
git rm -r --cached .devkit/

# 3. Commit
git commit -m "Remove private data from version control"

# 4. Push to GitHub (now public-ready)
git push origin main

# 5. Make repo public on GitHub
# Settings > Change visibility > Public

# 6. Deploy to Vercel (CLI reads from local disk)
vercel deploy

# 7. Backup private data separately (outside Git)
tar -czf ~/Backups/turoyo-verbs-$(date +%Y%m%d).tar.gz \
    .claude/ \
    server/assets/verbs/ \
    source/ \
    .devkit/
```

### Pros

- Simplest possible setup
- One repo, one remote, no branches
- Vercel CLI has everything it needs
- Public repo is immediately open-source ready

### Cons

- Private data not in version control
- Need separate backup strategy for data files

---

## BUT WAIT - Do you want data in version control?

If YES → Use the two-remote approach with public branch
If NO → Use the ultra-simple .gitignore approach

Let me create one final recommendation...
