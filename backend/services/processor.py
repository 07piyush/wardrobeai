import cv2
import numpy as np
from sklearn.cluster import KMeans
from typing import Dict, List, Tuple
import os

class ImageProcessor:
    def __init__(self):
        # Initialize any required models or configurations
        pass
    
    def process_image(self, image_path: str) -> Dict:
        """Process an image to extract clothing features."""
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not read image")
        
        # Convert to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Extract features
        features = {
            "dominant_color": self._get_dominant_color(image_rgb),
            "bounding_box": self._get_bounding_box(image_rgb),
            "clothing_type": self._predict_clothing_type(image_rgb)
        }
        
        return features
    
    def _get_dominant_color(self, image: np.ndarray, k: int = 3) -> List[int]:
        """Extract dominant colors using K-means clustering."""
        # Reshape image to be a list of pixels
        pixels = image.reshape(-1, 3)
        
        # Perform k-means clustering
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(pixels)
        
        # Get the dominant colors
        colors = kmeans.cluster_centers_.astype(int)
        return colors.tolist()
    
    def _get_bounding_box(self, image: np.ndarray) -> Dict:
        """Get bounding box coordinates of detected clothing using contour detection."""
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
            "x": x,
            "y": y,
            "width": w,
            "height": h
        }
    
    def _predict_clothing_type(self, image: np.ndarray) -> str:
        """Predict clothing type based on image analysis."""
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