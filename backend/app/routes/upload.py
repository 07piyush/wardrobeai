from fastapi import APIRouter, UploadFile, HTTPException
import imghdr
import tempfile
import os
import logging
from ..services.storage import StorageService
from ..services.processor import ImageProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = ["image/jpeg", "image/png"]

@router.post("/upload-image")
async def upload_image(file: UploadFile):
    """
    Upload and process an image file
    """
    try:
        # Validate file type
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Read file content
        content = await file.read()
        
        # Validate actual content is an image
        if not imghdr.what(None, h=content):
            raise HTTPException(status_code=400, detail="Invalid content type")
            
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Process image
            processor = ImageProcessor()
            processed_image = processor.process_image(content)
            
            # Upload to storage
            storage = StorageService()
            url = storage.upload_file(temp_path, "test_user")
            
            if not url:
                raise HTTPException(status_code=500, detail="Failed to upload image to storage")
            
            return {"url": url}
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_path}: {e}")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}") 