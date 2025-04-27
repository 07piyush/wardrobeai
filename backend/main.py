from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Dict
import tempfile
from PIL import Image
import os
from functools import lru_cache
import logging

from services.storage import StorageService
from services.processor import ImageProcessor
from services.recommender import OutfitRecommender

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    storage_service: StorageService = Depends(get_storage_service)
):
    """
    Upload and process a clothing image
    
    Args:
        file: The image file to upload
        storage_service: Injected storage service
        
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
            
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
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
            image_url = storage_service.upload_file(temp_path, "test_user")
            if not image_url:
                raise HTTPException(status_code=500, detail="Failed to upload image to storage")
            
            return {
                "message": "Image uploaded and processed successfully",
                "temp_path": temp_path,
                "filename": file.filename,
                "image_url": image_url
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
    weather: str = None,
    event_type: str = None,
    outfit_recommender: OutfitRecommender = Depends(get_outfit_recommender)
) -> List[Dict]:
    """
    Get outfit recommendations based on weather and event type
    
    Args:
        weather: Current weather condition
        event_type: Type of event/occasion
        outfit_recommender: Injected recommendation service
        
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
            
        # Mock wardrobe data for testing
        wardrobe = [
            {
                "clothing_type": "shirt",
                "image_url": "https://example.com/shirt.jpg",
                "dominant_color": {"r": 255, "g": 0, "b": 0},
                "tags": ["red", "casual", "cotton"]
            },
            {
                "clothing_type": "pants",
                "image_url": "https://example.com/pants.jpg",
                "dominant_color": {"r": 0, "g": 0, "b": 255},
                "tags": ["blue", "formal", "denim"]
            }
        ]
        
        # Get recommendations
        recommendations = outfit_recommender.recommend_outfits(
            wardrobe=wardrobe,
            weather=weather,
            event_type=event_type
        )
        
        return recommendations
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 