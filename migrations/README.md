# Database Migrations

This folder contains database schema migrations for the CashFlow API.

## Philosophy

We keep all database schema changes as migration files to:
- **Document evolution**: Show how the database schema evolved over time
- **Reproducibility**: Allow setup in new environments
- **Team coordination**: Everyone applies the same changes
- **Version control**: Track schema changes alongside code changes

## Structure

Each migration file follows the naming pattern:
```
{number}_{description}.py
```

Example: `001_add_soft_delete_to_categories.py`

## Running Migrations

### Apply a migration:
```bash
python migrations/001_add_soft_delete_to_categories.py
```

### Rollback a migration (if supported):
```bash
python migrations/001_add_soft_delete_to_categories.py downgrade
```

## Migration History

| # | File | Date | Description |
|---|------|------|-------------|
| 001 | `add_soft_delete_to_categories.py` | 2025-12-16 | Add soft delete to categories table |

## Best Practices

1. **Never modify existing migrations** - Create a new one instead
2. **Test migrations** - Always test on a backup database first
3. **Document changes** - Include rationale in migration docstring
4. **Sequential numbering** - Keep migrations in order
5. **Idempotent when possible** - Check if change already exists

## Future: Alembic Migration

For production environments, consider migrating to Alembic for:
- Automatic migration generation
- Better rollback support
- Migration history tracking
- Team collaboration features

To set up Alembic:
```bash
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Notes

- SQLite has limited `ALTER TABLE` support
- Some changes may require table recreation
- Always backup database before running migrations
- Test in development environment first
