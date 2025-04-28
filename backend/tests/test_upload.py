import argparse
import requests
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_upload(image_path):
    try:
        # Resolve and log the absolute path
        image_path = os.path.abspath(image_path)
        logger.info(f"Attempting to upload image from: {image_path}")
        
        # Check if file exists
        if not os.path.exists(image_path):
            logger.error(f"File not found: {image_path}")
            return
            
        with open(image_path, 'rb') as f:
            files = {
                'file': (os.path.basename(image_path), f, 'image/png')
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
    # 1. Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Upload an image to the server"
    )
    parser.add_argument(
        "-i", "--image",
        required=True,
        help="Path to the image file to upload"
    )
    args = parser.parse_args()  # parses sys.argv :contentReference[oaicite:2]{index=2}

    # 2. Call the upload function with the user-provided path
    test_upload(args.image)
