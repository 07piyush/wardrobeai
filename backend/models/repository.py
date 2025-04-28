from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any, Dict, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

# Generic type for database models
T = TypeVar('T')

class Repository(Generic[T], ABC):
    """Abstract repository interface for database operations"""
    
    @abstractmethod
    def create(self, data: Union[T, Dict[str, Any]]) -> Optional[T]:
        """Create a new record"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[T]:
        """Get a record by ID"""
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination"""
        pass
    
    @abstractmethod
    def update(self, id: Any, data: Dict[str, Any]) -> Optional[T]:
        """Update a record"""
        pass
    
    @abstractmethod
    def delete(self, id: Any) -> bool:
        """Delete a record"""
        pass

class SQLAlchemyRepository(Repository[T], Generic[T]):
    """SQLAlchemy implementation of Repository interface"""
    
    def __init__(self, db_session: Session, model_class: type):
        """Initialize SQLAlchemy repository"""
        self.db = db_session
        self.model_class = model_class
    
    def create(self, data: Union[T, Dict[str, Any]]) -> Optional[T]:
        """Create a new record"""
        try:
            if isinstance(data, dict):
                db_item = self.model_class(**data)
            else:
                db_item = data
                
            self.db.add(db_item)
            self.db.commit()
            self.db.refresh(db_item)
            return db_item
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model_class.__name__}: {e}")
            return None
    
    def get_by_id(self, id: Any) -> Optional[T]:
        """Get a record by ID"""
        try:
            return self.db.query(self.model_class).filter(self.model_class.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model_class.__name__} by ID: {e}")
            return None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination"""
        try:
            return self.db.query(self.model_class).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model_class.__name__}: {e}")
            return []
    
    def update(self, id: Any, data: Dict[str, Any]) -> Optional[T]:
        """Update a record"""
        try:
            item = self.get_by_id(id)
            if not item:
                return None
                
            for key, value in data.items():
                setattr(item, key, value)
                
            self.db.commit()
            self.db.refresh(item)
            return item
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model_class.__name__}: {e}")
            return None
    
    def delete(self, id: Any) -> bool:
        """Delete a record"""
        try:
            item = self.get_by_id(id)
            if not item:
                return False
                
            self.db.delete(item)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model_class.__name__}: {e}")
            return False 