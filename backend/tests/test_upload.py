import requests
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_upload():
    try:
        # Get the absolute path to the image
        image_path = os.path.abspath('D:/Developent/wardrobe/whitePant.png')
        logger.info(f"Attempting to upload image from: {image_path}")
        
        # Check if file exists
        if not os.path.exists(image_path):
            logger.error(f"File not found: {image_path}")
            return
            
        with open(image_path, 'rb') as f:
            files = {
                'file': ('whitePant.png', f, 'image/png')
            }
            logger.info("Sending POST request to /upload-image")
            response = requests.post('http://localhost:8000/upload-image', files=files)
            
            logger.info(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                logger.info("Upload successful!")
                logger.info(f"Response: {response.json()}")
            else:
                logger.error(f"Upload failed: {response.text}")
                
    except Exception as e:
        logger.error(f"Error during upload: {str(e)}")

if __name__ == "__main__":
    test_upload() 