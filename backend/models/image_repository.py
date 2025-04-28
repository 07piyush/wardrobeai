from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
import logging

from .repository import SQLAlchemyRepository
from .image_metadata import ImageMetadata

logger = logging.getLogger(__name__)

class ImageMetadataRepository(SQLAlchemyRepository[ImageMetadata]):
    """Repository for image metadata operations"""
    
    def __init__(self, db_session: Session):
        """Initialize image metadata repository"""
        super().__init__(db_session, ImageMetadata)
    
    def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[ImageMetadata]:
        """Get all images for a specific user"""
        try:
            return self.db.query(ImageMetadata).filter(
                ImageMetadata.user_id == user_id
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting images by user ID: {e}")
            return []
    
    def get_by_clothing_type(self, user_id: str, clothing_type: str) -> List[ImageMetadata]:
        """Get images by clothing type for a specific user"""
        try:
            return self.db.query(ImageMetadata).filter(
                and_(
                    ImageMetadata.user_id == user_id,
                    ImageMetadata.clothing_type == clothing_type
                )
            ).all()
        except Exception as e:
            logger.error(f"Error getting images by clothing type: {e}")
            return []
    
    def search_by_tags(self, user_id: str, tags: List[str]) -> List[ImageMetadata]:
        """Search images by tags (this is a simplified implementation)"""
        try:
            # This is a simplified implementation that returns all images
            # A more efficient implementation would use JSON containment operators
            # specific to PostgreSQL
            all_user_images = self.get_by_user_id(user_id)
            return [
                image for image in all_user_images 
                if any(tag in image.tags for tag in tags)
            ]
        except Exception as e:
            logger.error(f"Error searching images by tags: {e}")
            return []
    
    def get_wardrobe(self, user_id: str) -> List[Dict[str, Any]]:
        """Get the entire wardrobe for a user"""
        try:
            images = self.get_by_user_id(user_id)
            return [image.to_dict() for image in images]
        except Exception as e:
            logger.error(f"Error getting wardrobe: {e}")
            return [] 