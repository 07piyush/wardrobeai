#!/usr/bin/env python3
"""
Test script for the recommend API.
This script uploads sample images and tests the recommend API.
"""

import os
import requests
import argparse
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upload_image(api_url, image_path, user_id="test_user"):
    """Upload an image to the API"""
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return None
            
        # Upload image
        files = {'file': open(image_path, 'rb')}
        params = {'user_id': user_id}
        
        logger.info(f"Uploading image: {image_path}")
        response = requests.post(f"{api_url}/upload-image", files=files, params=params)
        
        if response.status_code != 200:
            logger.error(f"Upload failed with status code {response.status_code}: {response.text}")
            return None
            
        result = response.json()
        logger.info(f"Upload successful: {result['image_url']}")
        return result
        
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        return None

def get_recommendations(api_url, weather, event_type, user_id="test_user"):
    """Get outfit recommendations from the API"""
    try:
        # Get recommendations
        params = {
            'weather': weather,
            'event_type': event_type,
            'user_id': user_id
        }
        
        logger.info(f"Getting recommendations for weather={weather}, event_type={event_type}")
        response = requests.get(f"{api_url}/recommend", params=params)
        
        if response.status_code != 200:
            logger.error(f"Recommendation failed with status code {response.status_code}: {response.text}")
            return None
            
        result = response.json()
        logger.info(f"Received {len(result)} recommendations")
        return result
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return None

def get_wardrobe(api_url, user_id="test_user"):
    """Get user's wardrobe from the API"""
    try:
        logger.info(f"Getting wardrobe for user {user_id}")
        response = requests.get(f"{api_url}/wardrobe/{user_id}")
        
        if response.status_code != 200:
            logger.error(f"Get wardrobe failed with status code {response.status_code}: {response.text}")
            return None
            
        result = response.json()
        logger.info(f"Received {len(result)} wardrobe items")
        return result
        
    except Exception as e:
        logger.error(f"Error getting wardrobe: {e}")
        return None

def find_sample_images(sample_dir):
    """Find sample images in the given directory"""
    try:
        sample_images = []
        
        # Check if directory exists
        if not os.path.exists(sample_dir) or not os.path.isdir(sample_dir):
            logger.error(f"Sample directory not found: {sample_dir}")
            return sample_images
            
        # Find image files
        for file in os.listdir(sample_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                sample_images.append(os.path.join(sample_dir, file))
                
        logger.info(f"Found {len(sample_images)} sample images")
        return sample_images
        
    except Exception as e:
        logger.error(f"Error finding sample images: {e}")
        return []

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test the recommend API")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API URL")
    parser.add_argument("--sample-dir", default="tests/sample_images", help="Directory with sample images")
    parser.add_argument("--user-id", default="test_user", help="User ID")
    parser.add_argument("--weather", default="sunny", help="Weather condition")
    parser.add_argument("--event-type", default="casual", help="Event type")
    parser.add_argument("--upload-only", action="store_true", help="Only upload images, don't get recommendations")
    parser.add_argument("--recommend-only", action="store_true", help="Only get recommendations, don't upload images")
    args = parser.parse_args()
    
    # Create sample directory if it doesn't exist
    os.makedirs(args.sample_dir, exist_ok=True)
    
    # Check if sample images exist, if not create sample_images directory
    sample_images = find_sample_images(args.sample_dir)
    if not sample_images and not args.recommend_only:
        logger.warning(f"No sample images found in {args.sample_dir}.")
        logger.info("Please add some .jpg or .png images to this directory and run again.")
        return
    
    # Upload images
    if not args.recommend_only:
        for image_path in sample_images:
            result = upload_image(args.api_url, image_path, args.user_id)
            if result:
                logger.info(json.dumps(result, indent=2))
    
    # Get wardrobe
    if not args.upload_only:
        wardrobe = get_wardrobe(args.api_url, args.user_id)
        if wardrobe:
            logger.info("Wardrobe contents:")
            logger.info(json.dumps(wardrobe, indent=2))
    
    # Get recommendations
    if not args.upload_only:
        recommendations = get_recommendations(args.api_url, args.weather, args.event_type, args.user_id)
        if recommendations:
            logger.info("Recommendations:")
            logger.info(json.dumps(recommendations, indent=2))

if __name__ == "__main__":
    main() 