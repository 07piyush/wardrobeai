from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Dict, Optional
import tempfile
from PIL import Image
import os
from functools import lru_cache
import logging
from sqlalchemy.orm import Session
import uuid
import traceback
import numpy as np

from services.storage import StorageService
from services.processor import ImageProcessor
from services.recommender import OutfitRecommender
from models.database import DatabaseManager, PostgresConfig
from models.image_repository import ImageMetadataRepository
from models.image_metadata import ImageMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
db_config = PostgresConfig()
db_manager = DatabaseManager.get_instance(db_config)
db_manager.create_tables()

app = FastAPI(
    title="StyleDNA AI",
    description="AI-Powered Fashion Image Processor & Outfit Recommender",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    """Get database session"""
    db = db_manager.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@lru_cache()
def get_storage_service():
    """Dependency for Firebase storage service"""
    try:
        return StorageService()
    except Exception as e:
        logger.error(f"Failed to initialize storage service: {e}")
        raise HTTPException(status_code=500, detail="Storage service initialization failed")

@lru_cache()
def get_image_processor():
    """Dependency for image processing service"""
    try:
        return ImageProcessor()
    except Exception as e:
        logger.error(f"Failed to initialize image processor: {e}")
        raise HTTPException(status_code=500, detail="Image processor initialization failed")

@lru_cache()
def get_outfit_recommender():
    """Dependency for outfit recommendation service"""
    try:
        return OutfitRecommender()
    except Exception as e:
        logger.error(f"Failed to initialize outfit recommender: {e}")
        raise HTTPException(status_code=500, detail="Outfit recommender initialization failed")

@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {"message": "Welcome to StyleDNA AI API"}

@app.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    user_id: str = Query("test_user", description="User ID"),
    storage_service: StorageService = Depends(get_storage_service),
    image_processor: ImageProcessor = Depends(get_image_processor),
    db: Session = Depends(get_db)
):
    """
    Upload and process a clothing image
    
    Args:
        file: The image file to upload
        user_id: User identifier for organizing files
        storage_service: Injected storage service
        image_processor: Injected image processor
        db: Database session
        
    Returns:
        dict: Upload results including image URL and metadata
    """
    try:
        # Validate file type first
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PNG and JPEG are supported"
            )
        
        # Validate content type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid content type. Only image files are supported"
            )
            
        # Create temporary file with a unique name
        filename = f"{uuid.uuid4()}_{file.filename}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{filename.split('.')[-1]}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Process image
            with Image.open(temp_path) as img:
                # Resize image
                img = img.resize((512, 512), Image.Resampling.LANCZOS)
                # Save processed image
                img.save(temp_path, quality=85, optimize=True)
            
            # Upload to Firebase Storage
            image_url = storage_service.upload_file(temp_path, user_id)
            if not image_url:
                raise HTTPException(status_code=500, detail="Failed to upload image to storage")
            
            # Process image and store metadata
            metadata = image_processor.process_image(
                image_path=temp_path,
                image_url=image_url,
                user_id=user_id,
                db_session=db
            )
            
            return {
                "message": "Image uploaded and processed successfully",
                "temp_path": temp_path,
                "filename": file.filename,
                "image_url": image_url,
                "metadata": metadata
            }
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_path}: {e}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/recommend")
async def recommend_outfit(
    weather: str = Query(None, description="Current weather condition"),
    event_type: str = Query(None, description="Type of event/occasion"),
    user_id: str = Query("test_user", description="User ID"),
    outfit_recommender: OutfitRecommender = Depends(get_outfit_recommender),
    db: Session = Depends(get_db)
) -> List[Dict]:
    """
    Get outfit recommendations based on weather and event type
    
    Args:
        weather: Current weather condition
        event_type: Type of event/occasion
        user_id: User identifier
        outfit_recommender: Injected recommendation service
        db: Database session
        
    Returns:
        List[Dict]: List of recommended outfits
    """
    try:
        # Validate input parameters
        if not weather or not event_type:
            missing_params = []
            if not weather:
                missing_params.append("weather")
            if not event_type:
                missing_params.append("event_type")
            raise HTTPException(
                status_code=400,
                detail=f"Missing required parameters: {', '.join(missing_params)}"
            )
            
        # Get wardrobe data from database
        logger.info(f"Getting wardrobe data for user {user_id}")
        repository = ImageMetadataRepository(db)
        wardrobe = repository.get_wardrobe(user_id)
        logger.info(f"Retrieved {len(wardrobe)} items from wardrobe")
        
        # Check if wardrobe is empty
        if not wardrobe:
            # For demonstration purposes, use a mock wardrobe
            logger.warning(f"No wardrobe found for user {user_id}, using mock data")
            wardrobe = [
                {
                    "id": 1,
                    "clothing_type": "shirt",
                    "image_url": "https://example.com/shirt.jpg",
                    "dominant_color": {"r": 255, "g": 0, "b": 0},
                    "tags": ["red", "casual", "cotton"]
                },
                {
                    "id": 2,
                    "clothing_type": "pants",
                    "image_url": "https://example.com/pants.jpg",
                    "dominant_color": {"r": 0, "g": 0, "b": 255},
                    "tags": ["blue", "formal", "denim"]
                }
            ]
        
        # Get recommendations
        logger.info("Getting recommendations")
        recommendations = outfit_recommender.recommend_outfits(
            user_id=user_id,
            weather=weather,
            event_type=event_type,
            db_session=db,
            wardrobe=wardrobe
        )
        logger.info(f"Generated {len(recommendations)} recommendations")
        
        # Convert numpy types to Python types
        processed_recommendations = []
        for rec in recommendations:
            processed_rec = {
                "id": int(rec["id"]) if isinstance(rec["id"], (np.int64, np.int32)) else rec["id"],
                "clothing_type": rec["clothing_type"],
                "image_url": rec["image_url"],
                "dominant_color": rec["dominant_color"],
                "tags": rec["tags"],
                "similarity_score": float(rec["similarity_score"])
            }
            processed_recommendations.append(processed_rec)
        
        return processed_recommendations
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        logger.error(f"Full error traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendations: {str(e)}"
        )

@app.get("/wardrobe/{user_id}")
async def get_wardrobe(
    user_id: str,
    db: Session = Depends(get_db)
) -> List[Dict]:
    """
    Get all clothing items for a user
    
    Args:
        user_id: User identifier
        db: Database session
        
    Returns:
        List[Dict]: List of clothing items
    """
    try:
        repository = ImageMetadataRepository(db)
        wardrobe = repository.get_wardrobe(user_id)
        return wardrobe
    
    except Exception as e:
        logger.error(f"Error getting wardrobe: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting wardrobe: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 