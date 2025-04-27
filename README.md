# StyleDNA AI - Wardrobe POC

An AI-powered fashion image processor and outfit recommender system that helps users manage their wardrobe and get personalized outfit recommendations.

## Features

1. **Image Processing**
   - Automatic image optimization and resizing
   - Support for JPEG and PNG formats
   - Content-type validation
   - Secure file handling

2. **Storage System**
   - Firebase Storage integration
   - Automatic public URL generation
   - Organized file structure by user
   - Cleanup of temporary files

3. **Error Handling**
   - Comprehensive error catching
   - Detailed error messages
   - Input validation
   - File type verification

4. **Testing**
   - Integration tests with mock services
   - Firebase storage mocking
   - Sample image generation
   - Error scenario testing

## High-Level Architecture

The system consists of three main components:
1. **Image Processing Pipeline**: Handles image uploads, optimization, and clothing detection
2. **Storage System**: Manages image storage using Firebase Storage
3. **Recommendation Engine**: Provides outfit recommendations based on various factors

## Project Structure

```
wardrobePOC/
├── backend/
│   ├── api/
│   │   └── upload_image.py       # Image upload endpoint handlers
│   ├── models/
│   │   └── image_metadata.py     # Database models for image metadata
│   ├── services/
│   │   ├── processor.py          # Image processing service
│   │   ├── recommender.py        # Outfit recommendation service
│   │   └── storage.py            # Firebase storage service
│   ├── tests/
│   │   ├── test_integration.py   # Integration tests
│   │   └── firebase-credentials.json  # Firebase credentials (not committed)
│   └── main.py                   # FastAPI application entry point
└── requirements.txt              # Python dependencies
```

## Component Details

### 1. Backend Services

#### Main Application (`main.py`)
- FastAPI application setup and configuration
- Endpoint definitions for image upload and recommendations
- Dependency injection setup for services
- CORS configuration
- Comprehensive error handling and logging

#### Image Metadata Model (`models/image_metadata.py`)
- SQLAlchemy model for storing image metadata
- Fields:
  - `id`: Primary key
  - `user_id`: User identifier
  - `image_url`: Firebase Storage URL
  - `clothing_type`: Type of clothing
  - `dominant_color`: RGB color values
  - `tags`: Array of descriptive tags
  - `uploaded_at`: Timestamp
  - `bounding_box`: Clothing item location

#### Storage Service (`services/storage.py`)
- Handles Firebase Storage operations
- Features:
  - Image upload with optimization
  - Public URL generation
  - File deletion
  - Error handling

#### Image Processor (`services/processor.py`)
- Processes uploaded images
- Features:
  - Image optimization
  - Clothing detection
  - Color analysis
  - Metadata extraction

#### Outfit Recommender (`services/recommender.py`)
- Generates outfit recommendations
- Features:
  - Weather-based recommendations
  - Event-type matching
  - Color coordination
  - Style matching

### 2. Testing Infrastructure

#### Integration Tests (`tests/test_integration.py`)
- End-to-end testing of the application
- Test cases:
  1. Image upload and processing flow
  2. Image optimization
  3. Error handling
  4. Invalid file types
  5. Missing parameters
- Features:
  - Mock Firebase storage
  - Test database setup
  - Sample image generation
  - Cleanup procedures

## API Endpoints

### 1. Upload Image
```http
POST /upload-image
Content-Type: multipart/form-data
```
- Accepts image file (PNG, JPEG)
- Returns:
  - Temporary file path
  - Original filename
  - Firebase Storage URL

### 2. Get Recommendations
```http
GET /recommend
Query Parameters:
  - weather: string (required)
  - event_type: string (required)
```
- Returns array of recommended outfits with:
  - Clothing type
  - Image URL
  - Dominant color
  - Tags
  - Similarity score

## Setup and Testing

### Prerequisites
1. Python 3.13.3
2. Firebase project
3. Firebase credentials

### Installation

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure Firebase**:
- Place `firebase-credentials.json` in `backend/tests/`
- Ensure Firebase Storage is enabled

3. **Start the Server**:
```bash
cd backend
python main.py
```
Server will start at `http://localhost:8000`

### Running Tests

1. **Run All Tests**:
```bash
cd backend
pytest tests/test_integration.py -v
```

2. **Run Specific Test**:
```bash
pytest tests/test_integration.py::test_upload_and_process_image -v
```

### Manual Testing

1. **Image Upload Testing**:
```bash
curl -X POST http://localhost:8000/upload-image \
  -F "file=@/path/to/your/image.jpg"
```

2. **Recommendation Testing**:
```bash
curl "http://localhost:8000/recommend?weather=sunny&event_type=casual"
```

## Error Handling

The application implements comprehensive error handling for:
1. Invalid file uploads
2. Storage service failures
3. Processing errors
4. Database operations
5. Recommendation engine issues

Each error returns appropriate HTTP status codes and descriptive messages.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Technical Stack

- **Backend Framework**: FastAPI
- **Database**: SQLAlchemy with SQLite (for testing)
- **Storage**: Firebase Storage
- **Image Processing**: OpenCV, Pillow
- **Machine Learning**: scikit-learn
- **Testing**: pytest, pytest-asyncio
- **HTTP Client**: httpx

## Dependencies

```txt
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
opencv-python==4.11.0.86
boto3==1.38.1
SQLAlchemy==2.0.40
psycopg2-binary==2.9.10
python-dotenv==1.0.0
pandas==2.2.3
numpy==2.2.5
starlette==0.27.0
typing-extensions==4.13.2
scikit-learn==1.6.1
Pillow==10.2.0
firebase-admin==6.4.0
pytest==8.3.5
pytest-asyncio==0.23.5
httpx==0.27.0
```

## Development Status

### Completed Features
- ✅ Basic project structure and architecture
- ✅ Firebase Storage integration
- ✅ Image upload and validation
- ✅ Image optimization pipeline
- ✅ Integration tests
- ✅ Error handling
- ✅ Dependency injection setup

### In Progress
- 🔄 Outfit recommendation engine
- 🔄 User wardrobe management
- 🔄 Weather-based recommendations
- 🔄 Event-type matching

### Planned Features
- 📋 User authentication
- 📋 Advanced image analysis
- 📋 Style preference learning
- 📋 Seasonal wardrobe planning