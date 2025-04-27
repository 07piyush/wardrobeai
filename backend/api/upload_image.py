from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import os
import tempfile
from typing import Optional

router = APIRouter()

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    # Validate file type
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, JPEG, and PNG files are allowed.")
    
    # Validate file size
    file_size = 0
    for chunk in file.stream:
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")
    
    # Reset file stream
    await file.seek(0)
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
            # Save uploaded file to temp file
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Process image
        with Image.open(temp_path) as img:
            # Resize image
            img = img.resize((512, 512), Image.Resampling.LANCZOS)
            
            # Compress image
            img.save(temp_path, quality=85, optimize=True)
        
        return JSONResponse({
            "message": "Image uploaded and processed successfully",
            "temp_path": temp_path,
            "filename": file.filename
        })
    
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}") 