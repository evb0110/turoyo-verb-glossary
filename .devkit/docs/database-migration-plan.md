# Database Migration Plan: From Files to Database-First Architecture

## The Big Picture: From File-Based to Database-First

**What we're proposing:**

1. One-time migration: read all 1,696 JSON files, insert into database
2. Delete (or archive) the parser, source HTML, JSON files - they're done
3. Database becomes the single source of truth going forward
4. All edits happen directly in the database

**This is actually elegant because:**

- No complex "merge layer" needed
- No parser validation needed (you validate in the app)
- Editing becomes straightforward CRUD operations
- The data is already complete and correct from the parser's final run

---

## Core Decision: Database Schema Design

You have **two fundamental approaches** for storing deeply nested data like this:

### Approach A: Normalized Relational Tables

**The structure:**

- `verbs` table (root, uncertain, cross_reference)
- `etymologies` table (verb_id FK, relationship)
- `etymons` table (etymology_id FK, source, source_root, meaning, reference...)
- `stems` table (verb_id FK, stem_name, label_raw...)
- `forms` table (stem_id FK, form_text)
- `conjugations` table (stem_id FK, conjugation_type)
- `examples` table (conjugation_id FK, turoyo_text)
- `translations` table (example_id FK, translation_text)
- `references` table (example_id FK, reference_text)

**Pros:**

- Proper relational modeling
- Easy to query specific parts ("find all examples with this translation")
- Referential integrity enforced by database
- Can add indexes on any field for performance
- Standard SQL patterns for editing

**Cons:**

- Complex schema (9+ tables)
- Loading a single verb requires multiple JOIN queries
- More complex migration logic (need to handle foreign keys)
- Editing requires multiple table updates
- Order matters (forms, translations, references need ordering column)

### Approach B: JSON/JSONB Columns

**The structure:**

- `verbs` table with just a few columns:
  - `id` (primary key)
  - `root` (string, indexed)
  - `data` (JSONB column containing entire IVerb structure)
  - `uncertain` (boolean, pulled out for easy querying)
  - `created_at`, `updated_at`

**Pros:**

- Dead simple schema (one table!)
- Migration is trivial (read JSON file, insert into data column)
- Loading a verb is one SELECT query
- Editing is one UPDATE query
- Preserves exact structure from JSON files
- PostgreSQL JSONB supports indexing and querying nested fields

**Cons:**

- Querying nested data requires JSONB operators (less intuitive)
- No referential integrity within the JSON
- Can't enforce schema at database level
- Harder to add indexes on nested fields

### Hybrid Approach C: Best of Both Worlds

**The structure:**

- `verbs` table (root, uncertain, cross_reference, created_at, updated_at)
- `etymology_data` JSONB column on verbs table
- `stems` table (verb_id FK, stem_name, forms as JSONB, conjugations as JSONB)

**Rationale:**

- Top-level fields (root, uncertain) are queryable/indexable
- Etymology is self-contained, not queried often → JSONB is fine
- Stems benefit from being separate rows (can query "verbs with Stem III")
- But forms/conjugations/examples stay as JSONB (too deeply nested to normalize)

---

## Recommendation: Start with Approach B (Full JSONB)

**Why?**

1. **Simplest migration path** - You literally read each JSON file and insert it. Done in minutes.

2. **Editing is straightforward** - Update the JSONB column with the modified structure. Your TypeScript IVerb interface already defines the schema.

3. **Query needs are simple** - You mostly load individual verbs by root, or list all verbs. You're not doing complex joins across nested data.

4. **Can refactor later** - If you discover you need to query deeply nested data frequently, you can normalize specific parts later. But start simple.

5. **PostgreSQL JSONB is powerful** - You can still query nested fields:
   - "Find verbs with Arab. etymology": `WHERE data @> '{"etymology": {"etymons": [{"source": "Arab."}]}}'`
   - "Find verbs with Stem III": `WHERE data->'stems' @> '[{"stem": "III"}]'`

6. **Matches your current API** - Your API already returns full IVerb objects. No change needed.

---

## Migration Strategy: From Files to Database

### Pre-Migration Checklist

**Backup everything first:**

- Git commit current state (you have clean git status)
- Export all 1,696 JSON files to a tarball
- Document current verb count, stats (for validation)

**Validation baseline:**

- Run stats API, save output: `curl http://localhost:3456/api/stats > pre-migration-stats.json`
- Count verbs: `ls server/assets/verbs/*.json | wc -l` (should be 1,696)
- Pick 10 random verbs, save their full JSON for spot-checking after migration

### Migration Steps

**Step 1: Create database table**

- Add `verbs` table to Drizzle schema with JSONB column
- Run migration to create table

**Step 2: Write migration script**

- Read all files from `server/assets/verbs/`
- Parse each JSON file
- Insert into database: `{ root, data: <full JSON>, uncertain }`
- Handle errors gracefully (log which files failed)

**Step 3: Run migration**

- Execute script
- Watch for errors
- Should take seconds (1,696 small JSON objects)

**Step 4: Validate migration**

- Count rows: `SELECT COUNT(*) FROM verbs` → should be 1,696
- Spot-check 10 random verbs against saved JSON files
- Run stats calculation from database → compare to pre-migration stats
- Load 10 verb pages in UI → verify they look identical

**Step 5: Switch API layer**

- Change `getVerbByRoot()` repository function from reading file to database query
- Change `getAllVerbs()` to database query
- Update stats API to query database instead of files

**Step 6: Test thoroughly**

- Browse random verbs in UI
- Run search (roots and fulltext)
- Check stats page
- Verify dev and production builds work

**Step 7: Archive old data**

- Move `server/assets/verbs/` to `.devkit/archive/verbs-json-backup/`
- Move `parser/` to `.devkit/archive/parser-backup/`
- Move `source/Turoyo_all_2024.html` to `.devkit/archive/`
- Update README to reflect database-first architecture

---

## Handling the Deeply Nested Structure

**The beautiful thing about JSONB:** You don't need to change anything!

Your existing TypeScript interfaces (IVerb, IStem, IExample, etc.) perfectly describe the structure. When you:

- **Read from DB:** Drizzle returns the JSONB as a JavaScript object matching IVerb
- **Write to DB:** Pass your IVerb object, Drizzle serializes to JSONB
- **Edit a field:** Modify the IVerb object in memory, save back to database

**Example editing flow:**

1. User edits "meaning" field in etymon
2. Frontend updates local IVerb object
3. On save, send entire IVerb to API: `PATCH /api/verbs/[root]`
4. API updates database: `UPDATE verbs SET data = $1 WHERE root = $2`

**No complexity needed!**

---

## Editing Implementation Becomes Trivial

With database-first, the editing UI simplifies dramatically:

**For simple fields (root, uncertain):**

- User clicks edit → input appears
- User saves → sends updated IVerb to API
- API updates database

**For array fields (forms, translations):**

- User clicks "add" → push to array in memory
- User clicks "remove" → splice from array
- User saves → entire updated IVerb sent to API

**For nested structures (stems, examples):**

- Same pattern - just manipulate the IVerb object in memory
- Send entire updated object on save
- Database stores it atomically

**You're just editing a JavaScript object** - the database is a dumb storage bucket for that object.

---

## What About Search?

Currently you have two search types:

**Root search:** Already works perfectly with database - query the `root` column or JSONB `->>'root'` path.

**Full-text search:** This is the one consideration.

**Current approach:** You read all JSON files and search through them in memory.

**Database options:**

1. **Simple approach (keep current logic):** Query database for all verbs, run search logic in memory. Fine for 1,696 verbs.

2. **PostgreSQL full-text search:** Create a tsvector column, index it, use `ts_query`. More complex but very fast.

3. **Hybrid:** Keep full-text search as-is (runs in memory on the server) but load data from database instead of files.

**Recommendation:** Start with option 1 (or 3), migrate to option 2 later if performance becomes an issue. But with only 1,696 records, in-memory search is perfectly fine.

---

## API Layer Changes

**Minimal changes needed:**

**Before (current):**

```
Repository reads from: useStorage('assets:server').getItem('verbs/root.json')
```

**After (database):**

```
Repository queries: db.select().from(verbs).where(eq(verbs.root, root))
```

**Your API routes stay identical:**

- `/api/verb/[root]` - returns IVerb (from database instead of file)
- `/api/search/*` - queries database instead of reading files
- `/api/stats` - calculates from database instead of files

**Your components don't change at all** - they still receive IVerb objects.

---

## Component Changes (Almost None)

This is the beauty of your architecture - components are already decoupled from data source!

**Current flow:**

```
Component → API → Repository → File Storage → IVerb
```

**New flow:**

```
Component → API → Repository → Database → IVerb
```

**Components don't know or care** - they just consume IVerb objects.

---

## Handling Validation Without Parser

**You lose automated parser validation**, but you gain application-level validation:

**Required field validation:**

- Root cannot be empty
- Stem must have a name
- Example must have turoyo text

**Referential validation:**

- Cross-reference points to existing verb (query database)
- Etymology source is from known list (maintain a sources table or enum)

**Format validation:**

- Turoyo text uses valid Unicode characters
- References match expected format

**Implement validation in two places:**

1. **Client-side** - immediate feedback as user types
2. **Server-side** - enforce before database save

**No regression validation needed** - because you're not regenerating data from a parser. You're directly editing the canonical data.

---

## The Parser/Source HTML Question

**What do you do with them?**

**Option A: Archive and forget**

- Move to `.devkit/archive/`
- Keep for historical reference
- Never use again

**Option B: Delete entirely**

- Clean break, simplifies project
- Keep in git history if ever needed
- Free up disk space

**Option C: One-way export capability**

- Keep ability to export database back to JSON files
- Useful for backups, version control, sharing
- But parser never runs again

**Recommendation:** Option A or C. Don't delete history, but make it clear the database is now the source of truth.

---

## Backup & Rollback Strategy

**Before going live with migration:**

**Backup plan:**

- Git commit JSON files before migration
- Export database to SQL dump after migration
- Keep both for 30 days

**Rollback plan:**

- If migration fails validation → revert database, debug script, try again
- If migration succeeds but app breaks → fix app, data is safe in database
- If you decide database was a mistake (unlikely) → export back to JSON from database, restore file-based approach

**Ongoing backups:**

- Database backups (daily)
- Periodic exports to JSON format (for version control, if desired)

---

## Performance Considerations

**Current (file-based):**

- Loading one verb: read one JSON file (~1-600 lines)
- Loading all verbs: read 1,696 files (for search, stats)
- Stats calculation: parse all files, calculate in memory

**After (database):**

- Loading one verb: one SELECT query (indexed on root)
- Loading all verbs: one SELECT query returning 1,696 rows
- Stats calculation: could use SQL aggregations (much faster)

**Performance will improve** for bulk operations (search, stats).

**One query consideration:** Fetching all 1,696 verbs with full JSONB might be large. Optimize by:

- Only fetch fields you need for search results (root, first translation, etc.)
- Use pagination for browse views
- Cache stats calculations

But honestly, 1,696 records is tiny. Modern databases handle this effortlessly.

---

## Migration Risk Assessment

**Low risk:**

- Data is already clean and validated (from parser)
- 1,696 records is small (migration takes seconds)
- Easy to validate before switching over
- Can test locally before deploying

**Medium risk:**

- Need to ensure ALL 1,696 verbs migrate correctly
- Need to validate JSONB serialization preserves exact structure
- Need to update all API routes correctly

**High risk:**

- None really - worst case you revert and keep using files

**Mitigation:**

- Thorough validation after migration
- Keep JSON files as backup for 30 days
- Test in development before production
- Have rollback plan ready

---

## Step-by-Step Migration Timeline

**Day 1: Preparation**

- Add verbs table to Drizzle schema
- Write migration script (read files, insert into DB)
- Create validation script (compare file vs DB data)

**Day 2: Migration**

- Run migration script locally
- Validate all 1,696 verbs migrated correctly
- Spot-check 20 random verbs manually

**Day 3: API Switch**

- Update repository layer to query database
- Test all API endpoints locally
- Verify UI still works identically

**Day 4: Editing Implementation**

- Start adding edit controls to components
- Implement PATCH /api/verbs/[root] endpoint
- Test editing simple fields

**Day 5+: Expand Editing**

- Add editing for all field types
- Implement validation
- Polish UI/UX

---

## The Bottom Line

**Your instinct is right** - once you add editing, the parser becomes obsolete. Why maintain two systems (parser + database) when database alone suffices?

**The migration is actually straightforward:**

1. Create simple database table with JSONB column
2. Read 1,696 JSON files, insert into database (one script, runs in seconds)
3. Update repository layer to query database instead of files
4. Archive parser and JSON files
5. Build editing UI that manipulates IVerb objects

**The hard part isn't the migration** - it's building the editing UI for deeply nested structures. But at least you don't have the additional complexity of keeping files and database in sync.

**Biggest win:** Complete freedom to edit data directly without worrying about parser regeneration, validation systems, or file I/O.

---

## Next Steps

1. Review this plan and decide on schema approach (recommend JSONB)
2. Create database schema in Drizzle
3. Write and test migration script
4. Execute migration with validation
5. Switch API layer to database
6. Begin implementing editing UI
