from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from .database import Base
from typing import Dict, List, Optional
import json

class ImageMetadata(Base):
    """SQLAlchemy model for image metadata"""
    
    __tablename__ = "image_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    image_url = Column(String, nullable=False)
    clothing_type = Column(String, nullable=False)
    dominant_color = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    bounding_box = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __init__(
        self,
        user_id: str,
        image_url: str,
        clothing_type: str,
        dominant_color: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        bounding_box: Optional[Dict] = None
    ):
        self.user_id = user_id
        self.image_url = image_url
        self.clothing_type = clothing_type
        self.dominant_color = dominant_color or {}
        self.tags = tags or []
        self.bounding_box = bounding_box or {}
    
    def to_dict(self) -> Dict:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_url": self.image_url,
            "clothing_type": self.clothing_type,
            "dominant_color": self.dominant_color,
            "tags": self.tags,
            "bounding_box": self.bounding_box,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ImageMetadata":
        """Create model from dictionary"""
        return cls(
            user_id=data.get("user_id"),
            image_url=data.get("image_url"),
            clothing_type=data.get("clothing_type"),
            dominant_color=data.get("dominant_color"),
            tags=data.get("tags"),
            bounding_box=data.get("bounding_box")
        ) 