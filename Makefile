.PHONY: help parse migrate-sqlite migrate-postgres deploy-verbs test-verbs clean-db

help:
	@echo "Turoyo Verb Glossary - Database Management"
	@echo ""
	@echo "Common workflows:"
	@echo "  make deploy-verbs    - Full pipeline: parse DOCX + migrate to SQLite"
	@echo "  make parse           - Parse DOCX files to JSON"
	@echo "  make migrate-sqlite  - Migrate JSON to SQLite (after parsing)"
	@echo "  make migrate-postgres - Migrate SQLite to Postgres (future)"
	@echo "  make test-verbs      - Test verb API locally"
	@echo "  make clean-db        - Delete SQLite database"
	@echo ""
	@echo "Environment variables:"
	@echo "  VERB_DATABASE=sqlite|postgres  - Which database to use (default: sqlite)"
	@echo "  VERB_DATABASE_URL=postgresql://... - Postgres connection string"
	@echo ""

parse:
	@echo "Parsing DOCX files to JSON..."
	python3 parser/parse_docx_production.py
	@echo "✅ JSON files generated in .devkit/analysis/docx_v2_verbs/"

migrate-sqlite: parse
	@echo "Migrating JSON to SQLite..."
	python3 scripts/migrate_json_to_sqlite.py
	@echo "✅ SQLite database created at .data/db/verbs.db"

migrate-postgres: parse
	@echo "Migrating JSON to Postgres..."
	python3 scripts/migrate_sqlite_to_postgres.py
	@echo "✅ Postgres database updated"

deploy-verbs: migrate-sqlite
	@echo ""
	@echo "✅ Database ready for deployment!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Test locally:  make test-verbs"
	@echo "  2. Commit:        git add .data/db/verbs.db && git commit -m 'Update verb database'"
	@echo "  3. Deploy:        git push"
	@echo ""

test-verbs:
	@echo "Testing verb API..."
	@echo ""
	@echo "1. Testing getVerbByRoot (hyw 1):"
	@curl -s http://localhost:3456/api/verbs/hyw%201 | head -c 200 && echo "..."
	@echo ""
	@echo "2. Testing verb count:"
	@curl -s http://localhost:3456/api/stats/verbs | head -c 200 && echo "..."
	@echo ""
	@echo "✅ Test complete (if dev server is running)"

clean-db:
	@echo "Deleting SQLite database..."
	rm -f .data/db/verbs.db
	@echo "✅ Database deleted"
