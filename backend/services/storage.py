import os
import firebase_admin
from firebase_admin import credentials, storage
import logging
from PIL import Image
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, test_mode=False):
        """Initialize Firebase Storage service
        
        Args:
            test_mode (bool): Whether to use mock credentials for testing
        """
        try:
            cred_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'firebase-credentials.json')
            logger.info(f"Loading Firebase credentials from: {cred_path}")
            
            if not os.path.exists(cred_path):
                logger.error(f"Firebase credentials file not found at: {cred_path}")
                raise FileNotFoundError(f"Firebase credentials not found at {cred_path}")
                
            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase app initialized successfully")
                
            bucket_name = "test-bucket" if test_mode else "wardrobeai-7bdf9.firebasestorage.app"
            logger.info(f"Connecting to Firebase Storage bucket: {bucket_name}")
            self.bucket = storage.bucket(bucket_name)
            logger.info("Firebase Storage initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Storage: {e}")
            raise

    def upload_file(self, file_path: str, user_id: str) -> str:
        """Upload a file to Firebase Storage
        
        Args:
            file_path (str): Path to the file to upload
            user_id (str): User identifier for organizing files
            
        Returns:
            str: Public URL of the uploaded file
        """
        try:
            logger.info(f"Starting file upload process for: {file_path}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
            
            # Optimize image before upload
            optimized_path = self._optimize_image(file_path)
            logger.info(f"Image optimized: {optimized_path}")
            
            # Generate a unique blob name
            filename = os.path.basename(optimized_path)
            blob_name = f"{user_id}/{filename}"
            logger.info(f"Generated blob name: {blob_name}")
            
            # Upload file
            blob = self.bucket.blob(blob_name)
            blob.upload_from_filename(optimized_path)
            logger.info("File uploaded successfully")
            
            # Make public
            blob.make_public()
            logger.info("File made public")
            
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return None
        finally:
            # Clean up optimized file
            if optimized_path and optimized_path != file_path:
                try:
                    os.unlink(optimized_path)
                    logger.info("Cleaned up optimized file")
                except Exception as e:
                    logger.warning(f"Failed to delete optimized file: {e}")

    def _optimize_image(self, file_path: str, max_size=(800, 800)) -> str:
        """Optimize image for storage
        
        Args:
            file_path (str): Path to the image file
            max_size (tuple): Maximum dimensions (width, height)
            
        Returns:
            str: Path to the optimized image
        """
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if larger than max_size
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save optimized image
                optimized_path = f"{file_path}_optimized.jpg"
                img.save(optimized_path, 'JPEG', quality=85, optimize=True)
                
                return optimized_path
        except Exception as e:
            logger.error(f"Failed to optimize image: {e}")
            return file_path

    def get_download_url(self, blob_name: str) -> str:
        """Get download URL for a file
        
        Args:
            blob_name (str): Name of the blob in storage
            
        Returns:
            str: Public URL of the file
        """
        try:
            blob = self.bucket.blob(blob_name)
            return blob.public_url
        except Exception as e:
            logger.error(f"Failed to get download URL: {e}")
            return None

    def delete_file(self, blob_name: str) -> bool:
        """Delete a file from storage
        
        Args:
            blob_name (str): Name of the blob to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False 