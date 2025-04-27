from typing import List, Dict
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class OutfitRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
    
    def recommend_outfits(
        self,
        wardrobe: List[Dict],
        weather: str,
        event_type: str,
        top_n: int = 3
    ) -> List[Dict]:
        """
        Recommend outfits based on wardrobe items, weather, and event type.
        """
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
    
    def _create_feature_vectors(
        self,
        df: pd.DataFrame,
        weather: str,
        event_type: str
    ) -> np.ndarray:
        """Create feature vectors for similarity calculation."""
        # Combine tags and metadata into text features
        df['features'] = df.apply(
            lambda row: ' '.join([
                row['clothing_type'],
                weather,
                event_type,
                *row['tags']
            ]),
            axis=1
        )
        
        # Create TF-IDF vectors
        return self.vectorizer.fit_transform(df['features']).toarray()
    
    def _calculate_similarity(self, features: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between items."""
        return cosine_similarity(features)
    
    def _get_top_recommendations(
        self,
        df: pd.DataFrame,
        similarity_scores: np.ndarray,
        top_n: int
    ) -> List[Dict]:
        """Get top N outfit recommendations."""
        # Get average similarity scores
        avg_scores = np.mean(similarity_scores, axis=1)
        
        # Get indices of top N items
        top_indices = np.argsort(avg_scores)[-top_n:][::-1]
        
        # Create recommendations
        recommendations = []
        for idx in top_indices:
            item = df.iloc[idx]
            recommendations.append({
                "clothing_type": item['clothing_type'],
                "image_url": item['image_url'],
                "dominant_color": item['dominant_color'],
                "tags": item['tags'],
                "similarity_score": float(avg_scores[idx])
            })
        
        return recommendations 