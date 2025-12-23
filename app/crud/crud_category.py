"""
Category CRUD operations module.

This module provides database operations for Category model.
Includes methods for user categories and system default categories.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.crud.base import CRUDBase
from app.models.category import Category, CategoryType
from app.models.transaction import Transaction
from app.schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    """
    CRUD operations for Category model.
    
    Handles both system default categories and user-created categories.
    """
    
    def get_by_owner(self, db: Session, *, id: int, user_id: int) -> Optional[Category]:
        """
        Get a specific category ensuring it belongs to the user (or is default).
        Used for security isolation (returns None if user is not owner).
        """
        return (
            db.query(self.model)
            .filter(Category.id == id)
            .filter(
                (Category.user_id == user_id) | (Category.is_default == True)
            )
            .filter(Category.is_deleted == False)
            .first()
        )

    def get_by_user(
        self,
        db: Session,
        *,
        user_id: int,
        category_type: Optional[CategoryType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        """
        Get categories available to a user (system defaults + user's own).
        
        Args:
            db: Database session
            user_id: User ID
            category_type: Optional filter by type (income/expense)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Category objects (both default and user-created)
        """
        query = db.query(self.model).filter(
            and_(
                or_(
                    Category.is_default == True,  # System categories
                    Category.user_id == user_id    # User's categories
                ),
                Category.is_deleted == False  # Exclude deleted categories
            )
        )
        
        if category_type:
            query = query.filter(Category.type == category_type)
        
        return (
            query
            .order_by(Category.is_default.desc(), Category.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_defaults(
        self,
        db: Session,
        *,
        category_type: Optional[CategoryType] = None
    ) -> List[Category]:
        """
        Get system default categories.
        
        Args:
            db: Database session
            category_type: Optional filter by type
            
        Returns:
            List of default Category objects
        """
        query = db.query(self.model).filter(
            and_(
                Category.is_default == True,
                Category.is_deleted == False
            )
        )
        
        if category_type:
            query = query.filter(Category.type == category_type)
        
        return query.order_by(Category.name.asc()).all()
    
    def get_user_categories(
        self,
        db: Session,
        *,
        user_id: int,
        category_type: Optional[CategoryType] = None
    ) -> List[Category]:
        """
        Get only user-created categories (excludes defaults).
        
        Args:
            db: Database session
            user_id: User ID
            category_type: Optional filter by type
            
        Returns:
            List of user's Category objects
        """
        query = db.query(self.model).filter(
            and_(
                Category.user_id == user_id,
                Category.is_default == False,
                Category.is_deleted == False
            )
        )
        
        if category_type:
            query = query.filter(Category.type == category_type)
        
        return query.order_by(Category.name.asc()).all()
    
    def create_with_owner(
        self,
        db: Session,
        *,
        obj_in: CategoryCreate,
        user_id: int
    ) -> Category:
        """
        Create a user category (always non-default).
        
        If a deleted category with the same name and type exists for this user,
        it will be restored instead of creating a new one. This preserves
        historical transaction relationships.
        
        Args:
            db: Database session
            obj_in: Category creation data
            user_id: User ID
            
        Returns:
            Created or restored Category object
        """
        # Check if deleted category exists with same name and type
        deleted_category = db.query(self.model).filter(
            and_(
                Category.user_id == user_id,
                Category.name == obj_in.name,
                Category.type == obj_in.type,
                Category.is_deleted == True
            )
        ).first()
        
        # If deleted category exists, restore it
        if deleted_category:
            deleted_category.is_deleted = False
            deleted_category.deleted_at = None
            db.add(deleted_category)
            db.commit()
            db.refresh(deleted_category)
            return deleted_category
        
        # Otherwise, create new category
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(
            **obj_in_data,
            user_id=user_id,
            is_default=False  # User categories are never default
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_with_transaction_count(
        self,
        db: Session,
        *,
        user_id: int,
        category_id: int
    ) -> Optional[dict]:
        """
        Get category with count of associated transactions.
        
        Args:
            db: Database session
            user_id: User ID
            category_id: Category ID
            
        Returns:
            Dictionary with category and transaction_count or None
        """
        category = db.query(self.model).filter(
            and_(
                Category.id == category_id,
                or_(
                    Category.is_default == True,
                    Category.user_id == user_id
                )
            )
        ).first()
        
        if not category:
            return None
        
        transaction_count = (
            db.query(func.count(Transaction.id))
            .filter(
                and_(
                    Transaction.category_id == category_id,
                    Transaction.user_id == user_id,
                    Transaction.is_deleted == False
                )
            )
            .scalar()
        ) or 0
        
        return {
            "category": category,
            "transaction_count": transaction_count
        }
    
    def can_delete(
        self,
        db: Session,
        *,
        category_id: int,
        user_id: int
    ) -> tuple[bool, str]:
        """
        Check if category can be deleted.
        
        Args:
            db: Database session
            category_id: Category ID
            user_id: User ID
            
        Returns:
            Tuple (can_delete: bool, message: str)
        """
        # Check if category exists and user has permission
        category = db.query(self.model).filter(
            and_(
                Category.id == category_id,
                or_(
                    Category.is_default == True,
                    Category.user_id == user_id
                ),
                Category.is_deleted == False
            )
        ).first()
        
        if not category:
            return False, "Category not found"
        
        # Cannot delete default categories
        if category.is_default:
            return False, "Cannot delete system default category"
        
        # With soft delete, we allow deletion even with transactions
        # Transactions will keep their category_id, but the category will be hidden
        return True, "OK"
    
    def soft_delete(self, db: Session, *, id: int) -> Category:
        """
        Soft delete a category (mark as deleted).
        
        Args:
            db: Database session
            id: Category ID
            
        Returns:
            Soft deleted Category object
        """
        from datetime import datetime, timezone
        
        category = db.get(self.model, id)
        category.is_deleted = True
        category.deleted_at = datetime.now(timezone.utc)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category


# Create instance for use in endpoints
category = CRUDCategory(Category)
