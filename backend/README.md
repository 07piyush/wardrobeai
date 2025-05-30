# StyleDNA AI Backend

AI-Powered Fashion Image Processor & Outfit Recommender

## Overview

This backend system handles image processing, storage, and outfit recommendations for the StyleDNA AI application.

## Features

1. **Image Processing** - Processes clothing images to extract features like dominant colors and clothing type
2. **Storage System** - Stores images in Firebase Storage and metadata in PostgreSQL
3. **Recommendation Engine** - Provides personalized outfit recommendations based on various factors

## Setup

### Prerequisites

1. Python 3.13.3
2. PostgreSQL
3. Firebase project with Storage enabled

### PostgreSQL Setup

You can set up PostgreSQL in two ways:

#### Option 1: Automated Setup (Recommended)
1. Run the setup script:
   ```powershell
   .\scripts\setup_postgres.ps1
   ```
   This will:
   - Start the PostgreSQL server if it's not running
   - Create the database and user
   - Display the credentials to use in your .env file

#### Option 2: Manual Setup
1. **Install PostgreSQL**:
   - Windows: Download and install from [PostgreSQL official website](https://www.postgresql.org/download/windows/)
   - Linux: `sudo apt-get install postgresql postgresql-contrib`
   - macOS: `brew install postgresql`

2. **Start PostgreSQL Service**:
   - Windows: PostgreSQL service should start automatically after installation
   - Linux: `sudo service postgresql start`
   - macOS: `brew services start postgresql`

3. **Create Database and User**:
   ```sql
   -- Connect to PostgreSQL
   psql -U postgres

   -- Create database
   CREATE DATABASE wardrobe;

   -- Create user (replace 'your_password' with a secure password)
   CREATE USER your_postgres_user WITH PASSWORD 'your_password';

   -- Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE wardrobe TO your_postgres_user;
   ```

4. **Verify Installation**:
   ```bash
   # Test connection
   psql -U your_postgres_user -d wardrobe -h localhost
   ```

5. **Troubleshooting**:
   - If you get a connection error, check if PostgreSQL is running
   - For Windows, check services.msc to ensure PostgreSQL service is running
   - For Linux/macOS, check service status with `sudo service postgresql status` or `brew services list`
   - If you can't connect, check pg_hba.conf for authentication settings

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables by creating a `.env` file in the backend directory:
```
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=wardrobe

# Application Settings
SQL_ECHO=False
DEBUG=False
```

3. Place your Firebase credentials in `backend/tests/firebase-credentials.json`

4. Set up the database:
```bash
python scripts/setup_db.py
```

5. Start the server:
```bash
python main.py
```
Server will start at `http://localhost:8000`

## Testing the Recommend API

### 1. Populate With Sample Images

To test the recommendation system, you need to upload some clothing images first. Place some images in the `tests/sample_images` directory, then run:

```bash
python test_recommend_api.py --upload-only
```

This will upload all images in the sample directory and store their metadata in the database.

### 2. Get Recommendations

Once you have uploaded some images, you can test the recommendation system:

```bash
python test_recommend_api.py --recommend-only --weather=sunny --event-type=casual
```

You can customize the weather and event type parameters to see different recommendations.

### 3. Complete Test

To upload images and get recommendations in one step:

```bash
python test_recommend_api.py --weather=rainy --event-type=formal
```

## API Endpoints

### 1. Upload Image
```http
POST /upload-image
Content-Type: multipart/form-data
Query Parameters:
  - user_id: string (optional, default: "test_user")
```

### 2. Get Recommendations
```http
GET /recommend
Query Parameters:
  - weather: string (required)
  - event_type: string (required)
  - user_id: string (optional, default: "test_user")
```

### 3. Get Wardrobe
```http
GET /wardrobe/{user_id}
```

## Running Tests

Run unit tests with:

```bash
pytest tests/test_recommender.py -v
```

Run integration tests with:

```bash
pytest tests/test_integration.py -v
```

## Project Structure

The backend follows a modular structure:

- `/api` - API endpoint handlers
- `/models` - Database models and repositories
- `/services` - Business logic services
- `/tests` - Unit and integration tests
- `/scripts` - Utility scripts 