"""
Base CRUD operations module.

This module provides a generic CRUD (Create, Read, Update, Delete) class
that can be reused for any SQLAlchemy model. It uses Python generics (TypeVar)
to maintain type safety while being flexible.

The CRUDBase class is inherited by specific CRUD classes like CRUDUser.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)  # type: ignore
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD operations class.

    This class provides standard CRUD operations that work with any SQLAlchemy model.
    It uses Python generics to maintain type safety.

    Type Parameters:
        ModelType: The SQLAlchemy model class (e.g., User)
        CreateSchemaType: The Pydantic schema for creation (e.g., UserCreate)
        UpdateSchemaType: The Pydantic schema for updates (e.g., UserUpdate)

    Attributes:
        model: The SQLAlchemy model class this CRUD instance operates on

    Example:
        >>> user_crud = CRUDBase(User)
        >>> user = user_crud.get(db, id=1)
        >>> new_user = user_crud.create(db, obj_in=user_create_data)
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD object with a SQLAlchemy model.

        Args:
            model: The SQLAlchemy model class (e.g., User)
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Get a single record by ID.

        Args:
            db: Database session
            id: Primary key value of the record

        Returns:
            ModelType: The record if found
            None: If record doesn't exist

        Example:
            >>> user = crud.get(db, id=1)
            >>> if user:
            >>>     print(user.email)
        """

        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.

        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List[ModelType]: List of records (could be empty)

        Example:
            >>> users = crud.get_multi(db, skip=0, limit=10)  # First 10 users
            >>> users = crud.get_multi(db, skip=10, limit=10)  # Next 10 users
        """

        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record in the database.

        Args:
            db: Database session
            obj_in: Pydantic schema with data to create (e.g., UserCreate)

        Returns:
            ModelType: The created record with ID and timestamps populated

        Example:
            >>> user_in = UserCreate(email="test@example.com", password="secret")
            >>> user = crud.create(db, obj_in=user_in)
            >>> print(user.id)  # Auto-generated ID
        """

        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
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
            db: Database session
            db_obj: The existing record from database
            obj_in: Pydantic schema or dict with fields to update

        Returns:
            ModelType: The updated record

        Example:
            >>> user = crud.get(db, id=1)
            >>> user_update = UserUpdate(email="newemail@example.com")
            >>> updated_user = crud.update(db, db_obj=user, obj_in=user_update)
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        Delete a record from the database.

        Args:
            db: Database session
            id: Primary key of record to delete

        Returns:
            ModelType: The deleted record (before deletion)

        Example:
            >>> deleted_user = crud.remove(db, id=1)
            >>> print(f"Deleted user: {deleted_user.email}")
        """

        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()

        return obj
