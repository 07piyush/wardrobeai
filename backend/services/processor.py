import cv2
import numpy as np
from sklearn.cluster import KMeans
from typing import Dict, List, Tuple, Optional
import os
import logging
from sqlalchemy.orm import Session

from models.image_metadata import ImageMetadata
from models.image_repository import ImageMetadataRepository

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        """Initialize the image processor"""
        # Initialize any required models or configurations
        pass
    
    def process_image(
        self, 
        image_path: str, 
        image_url: str,
        user_id: str,
        db_session: Optional[Session] = None
    ) -> Dict:
        """
        Process an image to extract clothing features and store in database.
        
        Args:
            image_path: Path to the image file
            image_url: URL of the uploaded image
            user_id: User ID who uploaded the image
            db_session: Database session for storing metadata
            
        Returns:
            Dict: Extracted image features
        """
        try:
            logger.info(f"Processing image: {image_path}")
            
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Could not read image: {image_path}")
                raise ValueError("Could not read image")
            
            # Convert to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Extract features
            features = {
                "dominant_color": self._get_dominant_color(image_rgb),
                "bounding_box": self._get_bounding_box(image_rgb),
                "clothing_type": self._predict_clothing_type(image_rgb),
                "tags": self._extract_tags(image_rgb),
                "image_url": image_url,
                "user_id": user_id
            }
            
            # Store metadata in database if session provided
            if db_session:
                self._store_metadata(features, db_session)
                logger.info(f"Stored metadata in database for {image_url}")
            
            return features
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
    def _store_metadata(self, features: Dict, db_session: Session) -> Optional[ImageMetadata]:
        """Store image metadata in database"""
        try:
            repository = ImageMetadataRepository(db_session)
            
            # Create metadata object
            metadata = ImageMetadata(
                user_id=features["user_id"],
                image_url=features["image_url"],
                clothing_type=features["clothing_type"],
                dominant_color=features["dominant_color"][0] if features["dominant_color"] else None,
                tags=features["tags"],
                bounding_box=features["bounding_box"]
            )
            
            # Save to database
            return repository.create(metadata)
            
        except Exception as e:
            logger.error(f"Error storing metadata: {e}")
            return None
    
    def _get_dominant_color(self, image: np.ndarray, k: int = 3) -> List[List[int]]:
        """Extract dominant colors using K-means clustering."""
        try:
            # Reshape image to be a list of pixels
            pixels = image.reshape(-1, 3)
            
            # Perform k-means clustering
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get the dominant colors
            colors = kmeans.cluster_centers_.astype(int)
            
            # Convert to RGB dictionaries for better readability
            result = []
            for color in colors:
                result.append({"r": int(color[0]), "g": int(color[1]), "b": int(color[2])})
                
            return result
            
        except Exception as e:
            logger.error(f"Error getting dominant color: {e}")
            return []
    
    def _get_bounding_box(self, image: np.ndarray) -> Dict:
        """Get bounding box coordinates of detected clothing using contour detection."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Apply thresholding
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return {"x": 0, "y": 0, "width": 0, "height": 0}
            
            # Get the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            return {
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h)
            }
            
        except Exception as e:
            logger.error(f"Error getting bounding box: {e}")
            return {"x": 0, "y": 0, "width": 0, "height": 0}
    
    def _predict_clothing_type(self, image: np.ndarray) -> str:
        """Predict clothing type based on image analysis."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Get image dimensions
            height, width = gray.shape
            
            # Calculate aspect ratio
            aspect_ratio = width / height
            
            # Simple rule-based classification based on aspect ratio and color distribution
            if aspect_ratio > 1.5:  # Likely a shirt or top
                return "shirt"
            elif aspect_ratio < 0.7:  # Likely pants or bottom
                return "pants"
            else:  # Could be a dress or full outfit
                return "full_body"
                
        except Exception as e:
            logger.error(f"Error predicting clothing type: {e}")
            return "unknown"
            
    def _extract_tags(self, image: np.ndarray) -> List[str]:
        """Extract tags from image based on color and basic features."""
        try:
            # Get dominant colors
            dominant_colors = self._get_dominant_color(image, k=1)
            
            # Extract tags based on color
            tags = []
            
            if not dominant_colors:
                return tags
                
            # Get the main color
            color = dominant_colors[0]
            r, g, b = color["r"], color["g"], color["b"]
            
            # Add color tags
            if r > 200 and g < 100 and b < 100:
                tags.append("red")
            elif r < 100 and g > 200 and b < 100:
                tags.append("green")
            elif r < 100 and g < 100 and b > 200:
                tags.append("blue")
            elif r > 200 and g > 200 and b < 100:
                tags.append("yellow")
            elif r > 200 and g < 100 and b > 200:
                tags.append("purple")
            elif r < 100 and g > 200 and b > 200:
                tags.append("cyan")
            elif r > 200 and g > 120 and b > 120:
                tags.append("pastel")
            elif r < 100 and g < 100 and b < 100:
                tags.append("black")
            elif r > 200 and g > 200 and b > 200:
                tags.append("white")
            
            # Other tags could be added based on texture, pattern detection, etc.
            # This is a simplified implementation
            
            return tags
            
        except Exception as e:
            logger.error(f"Error extracting tags: {e}")
            return [] 