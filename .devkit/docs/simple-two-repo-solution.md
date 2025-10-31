# Simple Two-Repo Solution for Vercel CLI Deployment

**Date:** 2025-10-18
**Key Insight:** Vercel CLI deploys from local disk, not from Git

## The Simple Truth

Since you deploy via `vercel` CLI (not GitHub integration), the deployed app reads from your **local disk**, not from Git. This makes the solution much simpler than all the submodule/S3/blob approaches.

## Recommended Solution

### One Repo, Two Remotes

**Local folder:**

- Has everything (code + data)
- Deploy from here via `vercel` CLI

**Private remote** (`origin`):

- Tracks everything (code + data + .claude/)
- Your source of truth with full history

**Public remote** (`public`):

- Tracks only code (data excluded via `.gitignore`)
- Open source repository

## Implementation

### Option 1: Separate Branch for Public (Simplest)

```bash
# 1. Your main branch stays private (has everything)
git checkout main

# 2. Create public-only branch
git checkout -b public

# 3. Remove private data from this branch
git rm -r .claude/
git rm -r server/assets/verbs/
git rm -r source/
git rm -r .devkit/

# Add them to .gitignore on this branch
cat >> .gitignore << 'EOF'

# Private data (excluded from public branch)
.claude/
server/assets/verbs/
source/
.devkit/
EOF

git add .gitignore
git commit -m "Public branch: exclude private data"

# 4. Add public remote and push
git remote add public git@github.com:evb0110/turoyo-verb-glossary.git
git push public public:main

# 5. Go back to main for daily work
git checkout main

# Your workflow:
# - Work on 'main' branch (has everything)
# - Push to origin (private repo)
# - Periodically sync to public branch and push
# - Deploy via: vercel (from main branch, has everything)
```

### Sync Public Branch (when ready to release)

```bash
#!/bin/bash
# scripts/sync-public.sh

# Save current branch
current=$(git branch --show-current)

# Switch to public branch
git checkout public

# Cherry-pick or merge specific commits from main
# (excluding any that touch private files)
git merge main --no-commit

# Remove private files if they snuck in
git reset HEAD .claude/ server/assets/verbs/ source/ .devkit/
git checkout -- .claude/ server/assets/verbs/ source/ .devkit/

# Commit and push
git commit -m "Sync from main"
git push public public:main

# Return to main
git checkout "$current"
```

### Option 2: Filter on Push (More Automated)

Use git's pathspec to push only specific files:

```bash
# This doesn't work directly, but you can script it:

# scripts/push-public-automated.sh
#!/bin/bash
set -e

TEMP=$(mktemp -d)
git clone --branch main . "$TEMP"
cd "$TEMP"

# Remove private files
rm -rf .claude/
rm -rf server/assets/verbs/
rm -rf source/
rm -rf .devkit/

# Update .gitignore
cat >> .gitignore << 'EOF'
.claude/
server/assets/verbs/
source/
.devkit/
EOF

# Commit
git add -A
git commit -m "Public release: code only" --allow-empty

# Push to public
git remote add public git@github.com:evb0110/turoyo-verb-glossary.git
git push --force public main

cd -
rm -rf "$TEMP"

echo "✓ Public repo updated"
```

## File Backup Strategy

Since the public repo won't have your data files, back them up separately:

```bash
# Automated backup script
# scripts/backup-private-data.sh
#!/bin/bash

BACKUP_DIR=~/Backups/turoyo-verbs
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p "$BACKUP_DIR"

tar -czf "$BACKUP_DIR/verbs-$DATE.tar.gz" \
    .claude/ \
    server/assets/verbs/ \
    source/ \
    .devkit/

echo "✓ Backup created: $BACKUP_DIR/verbs-$DATE.tar.gz"

# Keep only last 10 backups
ls -t "$BACKUP_DIR"/*.tar.gz | tail -n +11 | xargs rm -f 2>/dev/null || true
```

Run this weekly or before major changes.

## Deployment Workflow

```bash
# Daily development (on main branch with everything):
git add .
git commit -m "Your changes"
git push origin main

# Deploy to Vercel (from local disk with everything):
vercel deploy

# When ready to release code publicly:
./scripts/sync-public.sh

# Regular backups:
./scripts/backup-private-data.sh
```

## Summary: What Lives Where

| Location                | Code | Data | .claude | Deploy From  |
| ----------------------- | ---- | ---- | ------- | ------------ |
| Local disk (main)       | ✓    | ✓    | ✓       | ← Vercel CLI |
| Private remote (origin) | ✓    | ✓    | ✓       | Backup       |
| Public remote (public)  | ✓    | ✗    | ✗       | Open source  |
| Vercel (deployed)       | ✓    | ✓    | ✗       | Production   |
| Local backups           | ✗    | ✓    | ✓       | Safety net   |

## Pros & Cons

### Pros

- Free
- Data versioned in private Git repo
- Code open-sourced easily
- Vercel has everything it needs (local disk)
- No complex build scripts
- No Vercel configuration changes needed

### Cons

- Need to manage two remotes
- Manual sync to public branch
- Possible to accidentally push private data (mitigated by branch separation)

## Safety Checklist

- [ ] Private repo is set to private on GitHub
- [ ] Public branch never had private files committed
- [ ] Scripts are executable: `chmod +x scripts/*.sh`
- [ ] Test public branch locally before pushing
- [ ] Set up automated backups for private data
- [ ] Add pre-push hook to prevent accidents (optional)

## Pre-Push Safety Hook (Optional)

```bash
# .git/hooks/pre-push
#!/bin/bash

# Get the branch being pushed
branch=$(git rev-parse --abbrev-ref HEAD)

# If pushing public branch, verify no private files
if [[ "$branch" == "public" ]]; then
    if git ls-files | grep -E "^\.claude/|^server/assets/verbs/|^source/|^\.devkit/"; then
        echo "ERROR: Private files detected in public branch!"
        exit 1
    fi
fi
```

## Alternative: No Version Control for Data

If you don't need Git history for the data files (they're generated by parser anyway), the **absolute simplest** approach:

```bash
# Just add to .gitignore (both branches)
echo "server/assets/verbs/" >> .gitignore
echo ".claude/" >> .gitignore
echo "source/" >> .gitignore
echo ".devkit/" >> .gitignore

git rm -r --cached server/assets/verbs/ .claude/ source/ .devkit/
git commit -m "Remove generated/private data from Git"

# Now your one repo is public-ready
# Data lives on disk only
# Vercel CLI deploys from disk
# Back up data separately (not in Git)
```

This is even simpler but you lose version history for data files. Since they're parser-generated, this might be fine.

---

## My Recommendation

**Use Option 1 (Separate Branch)** because:

1. Data stays in version control (private branch)
2. Simple branch-based separation
3. Clear mental model
4. Easy to sync when needed
5. No risk of data loss

The workflow is:

- **main branch** = private, has everything, push to origin, deploy from here
- **public branch** = public, code only, push to public remote
- **Vercel** = deploys from local main branch via CLI

---

**Next Steps:**

1. Decide if you want data in Git or not
2. If yes: implement Option 1 (separate branch)
3. If no: use simple .gitignore approach
4. Test the workflow before making repo public
5. Set up automated backups
