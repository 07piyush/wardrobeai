from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class ImageMetadata(Base):
    __tablename__ = "image_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    image_url = Column(String)
    clothing_type = Column(String)
    dominant_color = Column(JSON)  # Store RGB values
    tags = Column(JSON)  # Store tags as JSON array
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    bounding_box = Column(JSON)  # Store x, y, width, height
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_url": self.image_url,
            "clothing_type": self.clothing_type,
            "dominant_color": self.dominant_color,
            "tags": self.tags,
            "uploaded_at": self.uploaded_at.isoformat(),
            "bounding_box": self.bounding_box
        } 