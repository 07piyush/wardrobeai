from typing import List, Dict, Optional
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import logging
from sqlalchemy.orm import Session

from models.image_repository import ImageMetadataRepository

logger = logging.getLogger(__name__)

class OutfitRecommender:
    def __init__(self):
        """Initialize the outfit recommender"""
        self.vectorizer = TfidfVectorizer()
    
    def recommend_outfits(
        self,
        user_id: str,
        weather: str,
        event_type: str,
        db_session: Session,
        wardrobe: Optional[List[Dict]] = None,
        top_n: int = 3
    ) -> List[Dict]:
        """
        Recommend outfits based on wardrobe items, weather, and event type.
        
        Args:
            user_id: User ID to recommend outfits for
            weather: Current weather condition
            event_type: Type of event/occasion
            db_session: Database session
            wardrobe: Optional pre-loaded wardrobe data
            top_n: Number of top recommendations to return
            
        Returns:
            List[Dict]: List of recommended outfits
        """
        try:
            # Get wardrobe data from database if not provided
            if wardrobe is None:
                repository = ImageMetadataRepository(db_session)
                wardrobe = repository.get_wardrobe(user_id)
            
            # Check if wardrobe is empty
            if not wardrobe:
                logger.warning(f"Wardrobe is empty for user {user_id}")
                return []
            
            # Convert wardrobe to DataFrame
            df = pd.DataFrame(wardrobe)
            
            # Create feature vectors
            features = self._create_feature_vectors(df, weather, event_type)
            
            # Calculate similarity scores
            similarity_scores = self._calculate_similarity(features)
            
            # Get top recommendations
            recommendations = self._get_top_recommendations(
                df, similarity_scores, top_n
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error recommending outfits: {e}")
            return []
    
    def _create_feature_vectors(
        self,
        df: pd.DataFrame,
        weather: str,
        event_type: str
    ) -> np.ndarray:
        """Create feature vectors for similarity calculation."""
        try:
            # Ensure tags are lists
            df['tags'] = df['tags'].apply(lambda x: x if isinstance(x, list) else [])
            
            # Combine tags and metadata into text features
            df['features'] = df.apply(
                lambda row: ' '.join([
                    str(row['clothing_type']),
                    weather,
                    event_type,
                    *[str(tag) for tag in row['tags']]
                ]),
                axis=1
            )
            
            # Create TF-IDF vectors
            return self.vectorizer.fit_transform(df['features']).toarray()
        except Exception as e:
            logger.error(f"Error creating feature vectors: {e}")
            return np.array([])
    
    def _calculate_similarity(self, features: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between items."""
        try:
            if features.size == 0:
                return np.array([])
            return cosine_similarity(features)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return np.array([])
    
    def _get_top_recommendations(
        self,
        df: pd.DataFrame,
        similarity_scores: np.ndarray,
        top_n: int
    ) -> List[Dict]:
        """Get top N outfit recommendations."""
        try:
            if similarity_scores.size == 0 or df.empty:
                return []
                
            # Get average similarity scores
            avg_scores = np.mean(similarity_scores, axis=1)
            
            # Get indices of top N items (or all if less than top_n)
            n_items = min(top_n, len(df))
            top_indices = np.argsort(avg_scores)[-n_items:][::-1]
            
            # Create recommendations
            recommendations = []
            for idx in top_indices:
                item = df.iloc[idx]
                recommendations.append({
                    "id": item.get('id'),
                    "clothing_type": item['clothing_type'],
                    "image_url": item['image_url'],
                    "dominant_color": item['dominant_color'],
                    "tags": item['tags'],
                    "similarity_score": float(avg_scores[idx])
                })
            
            return recommendations
        except Exception as e:
            logger.error(f"Error getting top recommendations: {e}")
            return [] 