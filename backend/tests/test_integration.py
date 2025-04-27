import os
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from PIL import Image
import numpy as np
from unittest.mock import patch, MagicMock
import firebase_admin
from firebase_admin import storage
import logging
import io
import json

# Import your application and models
from main import app, get_storage_service
from models.image_metadata import Base, ImageMetadata
from services.storage import StorageService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test client
client = TestClient(app)

# Database setup for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def test_db():
    """Create and clean up test database"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)
    try:
        os.remove("test.db")
    except Exception as e:
        logger.warning(f"Failed to remove test database: {e}")

@pytest.fixture(scope="function")
def db_session(test_db):
    """Provide a database session with transaction rollback"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def sample_image():
    """Create a small sample image for testing"""
    # Create a small sample image to minimize storage usage
    img = Image.new('RGB', (256, 256), color='red')
    # Save to bytes buffer first
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG', quality=100)  # Use high quality for original
    img_buffer.seek(0)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    temp_file.write(img_buffer.getvalue())
    temp_file.close()
    
    yield temp_file.name
    try:
        os.unlink(temp_file.name)
    except (OSError, PermissionError) as e:
        logger.warning(f"Could not delete temporary file {temp_file.name}: {e}")

@pytest.fixture
def mock_firebase():
    """Mock Firebase storage for successful operations"""
    with patch('firebase_admin.credentials.Certificate') as mock_cred, \
         patch('firebase_admin.initialize_app') as mock_init, \
         patch('firebase_admin.storage.bucket') as mock_bucket:
        
        # Mock bucket and blob
        mock_blob = MagicMock()
        mock_blob.public_url = "https://firebasestorage.googleapis.com/test-image.jpg"
        mock_bucket.return_value.blob.return_value = mock_blob
        
        # Create storage service in test mode
        storage_service = StorageService(test_mode=True)
        
        # Override the storage service
        app.dependency_overrides[get_storage_service] = lambda: storage_service
        
        yield {
            'cred': mock_cred,
            'init': mock_init,
            'bucket': mock_bucket,
            'blob': mock_blob,
            'storage_service': storage_service
        }
        
        # Clean up
        app.dependency_overrides.clear()

@pytest.fixture
def mock_firebase_error():
    """Mock Firebase storage for error scenarios"""
    with patch('firebase_admin.credentials.Certificate') as mock_cred, \
         patch('firebase_admin.initialize_app') as mock_init, \
         patch('firebase_admin.storage.bucket') as mock_bucket:
        
        # Mock bucket and blob with errors
        mock_blob = MagicMock()
        mock_blob.upload_from_filename.side_effect = Exception("Upload failed")
        mock_blob.make_public.side_effect = Exception("Make public failed")
        mock_blob.delete.side_effect = Exception("Delete failed")
        mock_blob.public_url = None
        mock_bucket.return_value.blob.return_value = mock_blob
        
        # Create storage service in test mode
        storage_service = StorageService(test_mode=True)
        
        # Override the storage service
        app.dependency_overrides[get_storage_service] = lambda: storage_service
        
        yield {
            'cred': mock_cred,
            'init': mock_init,
            'bucket': mock_bucket,
            'blob': mock_blob,
            'storage_service': storage_service
        }
        
        # Clean up
        app.dependency_overrides.clear()

def test_upload_and_process_image(sample_image, db_session, mock_firebase):
    """Test the complete flow from image upload to recommendation"""
    try:
        # 1. Upload image
        with open(sample_image, 'rb') as f:
            response = client.post(
                "/upload-image",
                files={"file": ("test.jpg", f, "image/jpeg")}
            )
        assert response.status_code == 200
        upload_data = response.json()
        
        # 2. Verify image processing
        assert "temp_path" in upload_data
        assert "filename" in upload_data
        assert "image_url" in upload_data
        
        # 3. Verify database storage
        # Create a test image metadata record
        test_metadata = ImageMetadata(
            user_id="test_user",
            image_url=upload_data["image_url"],
            clothing_type="shirt",
            dominant_color={"r": 255, "g": 0, "b": 0},
            tags=["red", "casual"],
            bounding_box={"x": 0, "y": 0, "width": 256, "height": 256}
        )
        db_session.add(test_metadata)
        db_session.commit()
        
        # Verify the record was created
        stored_metadata = db_session.query(ImageMetadata).first()
        assert stored_metadata is not None
        assert stored_metadata.user_id == "test_user"
        assert stored_metadata.clothing_type == "shirt"
        
        # 4. Verify Firebase storage
        mock_firebase['blob'].upload_from_filename.assert_called_once()
        mock_firebase['blob'].make_public.assert_called_once()
        
        # 5. Get recommendations
        response = client.get(
            "/recommend",
            params={
                "weather": "sunny",
                "event_type": "casual"
            }
        )
        assert response.status_code == 200
        recommendations = response.json()
        
        # 6. Validate recommendation format
        assert isinstance(recommendations, list)
        for rec in recommendations:
            assert "clothing_type" in rec
            assert "image_url" in rec
            assert "dominant_color" in rec
            assert "tags" in rec
            assert "similarity_score" in rec
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

def test_image_optimization(sample_image, mock_firebase):
    """Test that images are properly optimized before upload"""
    storage_service = StorageService()
    
    # Get original file size
    original_size = os.path.getsize(sample_image)
    
    # Upload and get optimized path
    optimized_path = storage_service._optimize_image(sample_image)
    
    try:
        # Verify optimization
        assert optimized_path != sample_image
        optimized_size = os.path.getsize(optimized_path)
        assert optimized_size < original_size
    finally:
        # Clean up
        try:
            if optimized_path and os.path.exists(optimized_path):
                os.unlink(optimized_path)
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not delete temporary file {optimized_path}: {e}")

def test_error_handling(mock_firebase_error):
    """Test error handling in storage service"""
    # Test with invalid file path
    response = client.post(
        "/upload-image",
        files={"file": ("test.jpg", b"invalid file content", "image/jpeg")}
    )
    assert response.status_code == 500
    
    # Test with invalid blob name
    result = mock_firebase_error['storage_service'].get_download_url("invalid/blob/name")
    assert result is None
    
    # Test delete with invalid blob name
    result = mock_firebase_error['storage_service'].delete_file("invalid/blob/name")
    assert result is False

def test_missing_parameters():
    """Test handling of missing parameters in recommendations"""
    # Test without weather parameter
    response = client.get("/recommend?event_type=casual")
    assert response.status_code == 400
    assert "weather" in response.json()["detail"].lower()
    
    # Test without event_type parameter
    response = client.get("/recommend?weather=sunny")
    assert response.status_code == 400
    assert "event_type" in response.json()["detail"].lower()

def test_invalid_file_types(mock_firebase):
    """Test handling of invalid file types"""
    # Test with non-image file
    response = client.post(
        "/upload-image",
        files={"file": ("test.txt", b"some text content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]
    
    # Test with invalid content type
    response = client.post(
        "/upload-image",
        files={"file": ("test.jpg", b"invalid content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Invalid content type" in response.json()["detail"] 