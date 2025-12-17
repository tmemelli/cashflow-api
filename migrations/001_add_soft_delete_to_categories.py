"""
Migration: Add soft delete to categories table

Date: 2025-12-16
Description:
    Adds is_deleted and deleted_at columns to categories table to implement
    soft delete pattern. This allows categories to be marked as deleted
    without losing historical data or breaking transaction relationships.

Changes:
    - Add is_deleted BOOLEAN column (default: False)
    - Add deleted_at DATETIME column (nullable)

Rationale:
    Soft delete preserves:
    - Historical transaction data
    - Category relationships in transactions
    - Ability to restore accidentally deleted categories
    - Audit trail and compliance requirements
"""
from app.db.session import engine
from sqlalchemy import text


def upgrade():
    """Apply migration: Add soft delete columns to categories."""
    print("🔄 Running migration: Add soft delete to categories...")
    
    with engine.connect() as conn:
        # Add is_deleted column
        conn.execute(text("""
            ALTER TABLE categories 
            ADD COLUMN is_deleted BOOLEAN DEFAULT 0 NOT NULL
        """))
        print("  ✅ Added is_deleted column")
        
        # Add deleted_at column
        conn.execute(text("""
            ALTER TABLE categories 
            ADD COLUMN deleted_at DATETIME
        """))
        print("  ✅ Added deleted_at column")
        
        conn.commit()
    
    print("✅ Migration completed successfully!")


def downgrade():
    """Rollback migration: Remove soft delete columns from categories."""
    print("🔄 Rolling back migration: Remove soft delete from categories...")
    
    with engine.connect() as conn:
        # SQLite doesn't support DROP COLUMN easily
        # This would require recreating the table
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
