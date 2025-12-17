"""
Migration: Add soft delete to transactions table

Date: 2025-12-17
Description:
    Adds deleted_at column to transactions table to implement
    soft delete timestamp tracking. The `is_deleted` flag already exists
    in the database and will not be added here.

Changes:
    - Add deleted_at DATETIME column (nullable)

Notes:
    This migration follows the same approach used in 001_add_soft_delete_to_categories.py
    and avoids Alembic to keep migrations lightweight and repository-friendly.
"""
from app.db.session import engine
from sqlalchemy import text


def upgrade():
    """Apply migration: Add soft delete columns to transactions."""
    print("🔄 Running migration: Add soft delete to transactions...")
    with engine.connect() as conn:
        # Add deleted_at column only (is_deleted already present)
        conn.execute(text("""
            ALTER TABLE transactions
            ADD COLUMN deleted_at DATETIME
        """))
        print("  ✅ Added deleted_at column")

        conn.commit()

    print("✅ Migration completed successfully!")


def downgrade():
    """Rollback migration: Remove soft delete columns from transactions.

    SQLite does not support DROP COLUMN directly; a manual table recreate is required.
    See 001 migration for downgrade guidance.
    """
    print("🔄 Rolling back migration: Remove soft delete from transactions...")
    print("  ⚠️  SQLite doesn't support DROP COLUMN")
    print("  ⚠️  To rollback, you need to:")
    print("     1. Export data")
    print("     2. Drop table")
    print("     3. Recreate without is_deleted/deleted_at")
    print("     4. Import data")
    print("⚠️  Rollback not implemented for SQLite")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
