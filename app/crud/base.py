"""
Base CRUD operations module.

This module provides a generic CRUD (Create, Read, Update, Delete) class
that supports any SQLAlchemy model. It leverages Python generics to ensure
type safety and code reusability across the application.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from datetime import datetime, timezone

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

# --- CORRECTION HERE: changed from .base_class to .base ---
from app.db.base import Base 

# Define generic type variables
ModelType = TypeVar("ModelType", bound=Base) # type: ignore
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD operations class.
    
    This class implements default methods for Create, Read, Update, and Delete
    operations. It can be extended or overridden by specific CRUD classes
    (e.g., CRUDUser, CRUDItem).

    Attributes:
        model: The SQLAlchemy model class associated with this CRUD instance.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize the CRUD object.

        Args:
            model: The SQLAlchemy model class to operate on.
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Retrieve a single record by its ID.
        
        It automatically checks if the model supports Soft Delete ('is_deleted')
        and filters out deleted records if applicable.

        Args:
            db: The database session.
            id: The primary key of the record.

        Returns:
            Optional[ModelType]: The found record, or None if not found or deleted.
        """
        query = db.query(self.model).filter(self.model.id == id)
        
        # Automatic Soft Delete Check
        if hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted == False)
            
        return query.first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Retrieve multiple records with pagination.

        Args:
            db: The database session.
            skip: The number of records to skip (offset).
            limit: The maximum number of records to return.

        Returns:
            List[ModelType]: A list of records.
        """
        query = db.query(self.model)
        
        # Simple Soft Delete filter for lists
        if hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted == False)

        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record in the database.

        Args:
            db: The database session.
            obj_in: The Pydantic schema containing the data to create.

        Returns:
            ModelType: The newly created and committed record.
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        
        db.add(db_obj)
        db.commit() 
        db.refresh(db_obj)
        
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record.

        Args:
            db: The database session.
            db_obj: The existing database object to update.
            obj_in: The Pydantic schema or dictionary containing update data.

        Returns:
            ModelType: The updated record.
        """
        obj_data = jsonable_encoder(db_obj)
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        # Auto-update timestamp
        if hasattr(db_obj, 'updated_at'):
             db_obj.updated_at = datetime.now(timezone.utc)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        Delete a record from the database.
        
        If the model supports Soft Delete, it marks it as deleted instead of removing.
        Otherwise, it performs a hard delete.

        Args:
            db: The database session.
            id: The primary key of the record.

        Returns:
            ModelType: The deleted (or marked deleted) record.
        """
        obj = db.get(self.model, id)
        
        if not obj:
            return None
        
        # Soft-delete path (audit)
        if hasattr(obj, "is_deleted"):
            obj.is_deleted = True
            obj.deleted_at = datetime.now(timezone.utc)
            db.add(obj)
            db.commit()
            db.refresh(obj)  # Safe: the object still exists, it was only marked

        # Hard-delete path (cleanup)
        else:
            db.delete(obj)
            db.commit()
            # IMPORTANT: we do not call db.refresh(obj) here.
            # The object was physically removed; calling refresh would raise an error.
            
        return obj