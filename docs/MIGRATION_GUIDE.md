# Alembic Database Migration Guide

Developer 2 — Backend, Database & API Architect

---

## 1. Quick Commands

```bash
# Upgrade database to head revision
alembic upgrade head

# Downgrade database by 1 revision
alembic downgrade -1

# Generate a new migration script
alembic revision --autogenerate -m "description_of_changes"

# View current database revision
alembic current
```

---

## 2. Directory Structure

```
alembic/
├── env.py                # Environment configuration importing Base.metadata
├── script.py.mako        # Migration template
└── versions/
    └── 001_initial_schema.py  # Initial 5-table schema migration
```

---

## 3. Best Practices
1. Always test migrations in upgrade and downgrade directions:
   `alembic upgrade head && alembic downgrade base && alembic upgrade head`
2. Never perform manual DDL on production PostgreSQL tables.
