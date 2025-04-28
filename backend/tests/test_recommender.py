import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.recommender import OutfitRecommender
from services.processor import ImageProcessor
from models.database import Base
from models.image_metadata import ImageMetadata
from models.image_repository import ImageMetadataRepository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup test database
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)

@pytest.fixture
def sample_wardrobe_data():
    """Sample wardrobe data for testing"""
    return [
        {
            "user_id": "test_user",
            "image_url": "https://example.com/shirt1.jpg",
            "clothing_type": "shirt",
            "dominant_color": {"r": 255, "g": 0, "b": 0},
            "tags": ["red", "casual", "cotton"],
            "bounding_box": {"x": 10, "y": 10, "width": 100, "height": 100}
        },
        {
            "user_id": "test_user",
            "image_url": "https://example.com/pants1.jpg",
            "clothing_type": "pants",
            "dominant_color": {"r": 0, "g": 0, "b": 255},
            "tags": ["blue", "formal", "denim"],
            "bounding_box": {"x": 10, "y": 10, "width": 100, "height": 200}
        },
        {
            "user_id": "test_user",
            "image_url": "https://example.com/shirt2.jpg",
            "clothing_type": "shirt",
            "dominant_color": {"r": 0, "g": 255, "b": 0},
            "tags": ["green", "casual", "summer"],
            "bounding_box": {"x": 10, "y": 10, "width": 100, "height": 100}
        },
        {
            "user_id": "test_user",
            "image_url": "https://example.com/pants2.jpg",
            "clothing_type": "pants",
            "dominant_color": {"r": 50, "g": 50, "b": 50},
            "tags": ["black", "formal", "wool"],
            "bounding_box": {"x": 10, "y": 10, "width": 100, "height": 200}
        }
    ]

def populate_test_db(db_session, sample_data):
    """Populate test database with sample data"""
    repository = ImageMetadataRepository(db_session)
    
    for item_data in sample_data:
        item = ImageMetadata.from_dict(item_data)
        repository.create(item)
    
    return repository

def test_repository_get_wardrobe(db_session, sample_wardrobe_data):
    """Test getting wardrobe items from repository"""
    repository = populate_test_db(db_session, sample_wardrobe_data)
    
    # Get wardrobe
    wardrobe = repository.get_wardrobe("test_user")
    
    # Assertions
    assert len(wardrobe) == 4
    assert wardrobe[0]["clothing_type"] == "shirt"
    assert "red" in wardrobe[0]["tags"]

def test_recommender_with_empty_wardrobe(db_session):
    """Test recommender with empty wardrobe"""
    recommender = OutfitRecommender()
    
    recommendations = recommender.recommend_outfits(
        user_id="test_user",
        weather="sunny",
        event_type="casual",
        db_session=db_session
    )
    
    assert len(recommendations) == 0

def test_recommender_with_wardrobe(db_session, sample_wardrobe_data):
    """Test recommender with sample wardrobe"""
    # Populate database
    populate_test_db(db_session, sample_wardrobe_data)
    
    # Create recommender
    recommender = OutfitRecommender()
    
    # Get recommendations for casual event
    casual_recommendations = recommender.recommend_outfits(
        user_id="test_user",
        weather="sunny",
        event_type="casual",
        db_session=db_session
    )
    
    # Get recommendations for formal event
    formal_recommendations = recommender.recommend_outfits(
        user_id="test_user",
        weather="sunny",
        event_type="formal",
        db_session=db_session
    )
    
    # Assertions
    assert len(casual_recommendations) > 0
    assert len(formal_recommendations) > 0
    
    # Check if casual recommendations contain casual items
    casual_items = [item for item in casual_recommendations if "casual" in item["tags"]]
    assert len(casual_items) > 0
    
    # Check if formal recommendations contain formal items
    formal_items = [item for item in formal_recommendations if "formal" in item["tags"]]
    assert len(formal_items) > 0

def test_recommender_with_weather_and_event(db_session, sample_wardrobe_data):
    """Test recommender with specific weather and event type"""
    # Populate database
    populate_test_db(db_session, sample_wardrobe_data)
    
    # Create recommender
    recommender = OutfitRecommender()
    
    # Get recommendations for summer event
    summer_recommendations = recommender.recommend_outfits(
        user_id="test_user",
        weather="sunny",
        event_type="summer",
        db_session=db_session
    )
    
    # Assertions
    assert len(summer_recommendations) > 0
    
    # Check if summer recommendations prioritize summer items
    summer_items = [item for item in summer_recommendations if "summer" in item["tags"]]
    if summer_items:
        assert summer_items[0]["similarity_score"] > 0.5

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 