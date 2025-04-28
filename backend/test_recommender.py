#!/usr/bin/env python3
"""Test script for the recommender service"""

import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.recommender import OutfitRecommender
from models.database import PostgresConfig, DatabaseManager
from models.image_repository import ImageMetadataRepository

def test_recommender():
    """Test the recommender service"""
    try:
        # Initialize database
        logger.info("Initializing database")
        db_config = PostgresConfig()
        db_manager = DatabaseManager.get_instance(db_config)
        
        # Get database session
        logger.info("Getting database session")
        db = db_manager.SessionLocal()
        
        # Get wardrobe data
        logger.info("Getting wardrobe data")
        repository = ImageMetadataRepository(db)
        wardrobe = repository.get_wardrobe("test_user")
        logger.info(f"Retrieved {len(wardrobe)} items from wardrobe")
        
        # Initialize recommender
        logger.info("Initializing recommender")
        recommender = OutfitRecommender()
        
        # Get recommendations
        logger.info("Getting recommendations")
        recommendations = recommender.recommend_outfits(
            user_id="test_user",
            weather="sunny",
            event_type="casual",
            db_session=db,
            wardrobe=wardrobe
        )
        
        # Print recommendations
        logger.info("Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"\nRecommendation {i}:")
            logger.info(f"Clothing Type: {rec['clothing_type']}")
            logger.info(f"Image URL: {rec['image_url']}")
            logger.info(f"Tags: {rec['tags']}")
            logger.info(f"Similarity Score: {rec['similarity_score']}")
        
    except Exception as e:
        logger.error(f"Error testing recommender: {str(e)}")
        logger.error(f"Full error traceback: {traceback.format_exc()}")
    finally:
        db.close()

if __name__ == "__main__":
    test_recommender() 