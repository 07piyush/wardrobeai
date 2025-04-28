from typing import List, Dict, Optional
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import logging
from sqlalchemy.orm import Session
import traceback

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
                logger.info(f"Getting wardrobe data for user {user_id}")
                repository = ImageMetadataRepository(db_session)
                wardrobe = repository.get_wardrobe(user_id)
                logger.info(f"Retrieved {len(wardrobe)} items from wardrobe")
            
            # Check if wardrobe is empty
            if not wardrobe:
                logger.warning(f"Wardrobe is empty for user {user_id}")
                return []
            
            # Convert wardrobe to DataFrame
            logger.info("Converting wardrobe to DataFrame")
            df = pd.DataFrame(wardrobe)
            logger.info(f"DataFrame shape: {df.shape}")
            logger.info(f"DataFrame columns: {df.columns.tolist()}")
            
            # Create feature vectors
            logger.info("Creating feature vectors")
            features = self._create_feature_vectors(df, weather, event_type)
            logger.info(f"Feature vectors shape: {features.shape if features is not None else 'None'}")
            
            # Calculate similarity scores
            logger.info("Calculating similarity scores")
            similarity_scores = self._calculate_similarity(features)
            logger.info(f"Similarity scores shape: {similarity_scores.shape if similarity_scores is not None else 'None'}")
            
            # Get top recommendations
            logger.info("Getting top recommendations")
            recommendations = self._get_top_recommendations(
                df, similarity_scores, top_n
            )
            logger.info(f"Generated {len(recommendations)} recommendations")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error recommending outfits: {str(e)}")
            logger.error(f"Full error traceback: {traceback.format_exc()}")
            return []
    
    def _create_feature_vectors(
        self,
        df: pd.DataFrame,
        weather: str,
        event_type: str
    ) -> np.ndarray:
        """Create feature vectors for similarity calculation."""
        try:
            # Log input data
            logger.info(f"Creating feature vectors with weather={weather}, event_type={event_type}")
            logger.info(f"DataFrame head: {df.head().to_dict()}")
            
            # Ensure tags are lists and add default tags
            df['tags'] = df['tags'].apply(lambda x: x if isinstance(x, list) and x else [])
            
            # Add default tags based on clothing type and event type
            df['default_tags'] = df.apply(
                lambda row: [
                    row['clothing_type'],  # Add clothing type as a tag
                    'versatile' if row['clothing_type'] == 'full_body' else 'separates',  # Add category tag
                    'light' if weather in ['sunny', 'warm'] else 'heavy',  # Add weather-based tag
                    event_type  # Add event type as a tag
                ],
                axis=1
            )
            
            # Combine original and default tags
            df['all_tags'] = df.apply(
                lambda row: list(set(row['tags'] + row['default_tags'])),
                axis=1
            )
            
            # Create feature text by combining all tags
            df['features'] = df.apply(
                lambda row: ' '.join([
                    str(tag).lower() for tag in row['all_tags']
                ]),
                axis=1
            )
            
            logger.info("Feature text examples:")
            logger.info(df['features'].head().tolist())
            
            # Create TF-IDF vectors
            vectors = self.vectorizer.fit_transform(df['features']).toarray()
            logger.info(f"Created TF-IDF vectors with shape: {vectors.shape}")
            return vectors
            
        except Exception as e:
            logger.error(f"Error creating feature vectors: {str(e)}")
            logger.error(f"Full error traceback: {traceback.format_exc()}")
            return np.array([])
    
    def _calculate_similarity(self, features: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between items."""
        try:
            if features.size == 0:
                logger.warning("Empty feature array, returning empty similarity matrix")
                return np.array([])
                
            similarity = cosine_similarity(features)
            logger.info(f"Calculated similarity matrix with shape: {similarity.shape}")
            return similarity
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            logger.error(f"Full error traceback: {traceback.format_exc()}")
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
                logger.warning("Empty similarity scores or DataFrame, returning no recommendations")
                return []
                
            # Get average similarity scores
            avg_scores = np.mean(similarity_scores, axis=1)
            logger.info(f"Average similarity scores: {avg_scores}")
            
            # Get indices of top N items
            n_items = min(top_n, len(df))
            top_indices = np.argsort(avg_scores)[-n_items:][::-1]
            logger.info(f"Selected top {n_items} indices: {top_indices}")
            
            # Create recommendations
            recommendations = []
            for idx in top_indices:
                item = df.iloc[idx]
                recommendation = {
                    "id": item.get('id'),
                    "clothing_type": item['clothing_type'],
                    "image_url": item['image_url'],
                    "dominant_color": item['dominant_color'],
                    "tags": item['tags'],
                    "similarity_score": float(avg_scores[idx])
                }
                recommendations.append(recommendation)
                logger.info(f"Added recommendation: {recommendation}")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting top recommendations: {str(e)}")
            logger.error(f"Full error traceback: {traceback.format_exc()}")
            return [] 