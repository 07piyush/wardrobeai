# Database Configuration

This directory contains the database models and configuration for the wardrobe recommendation system.

## Architecture

We've implemented an abstraction layer for database operations using the following components:

1. **DatabaseConfig** - Abstract class for database configuration
   - **PostgresConfig** - PostgreSQL implementation

2. **Repository Pattern** - Abstract repository interface
   - **SQLAlchemyRepository** - SQLAlchemy implementation
   - **ImageMetadataRepository** - Specific repository for image metadata

3. **Database Models**
   - **ImageMetadata** - Model for clothing image metadata

## Setting Up PostgreSQL

1. Install PostgreSQL on your system (if not already installed)
2. Create a `.env` file in the backend directory with the following content:

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

3. Run the database setup script:

```bash
cd backend
python scripts/setup_db.py
```

## Repository Usage

The repository pattern provides a clean interface for database operations. Example usage:

```python
from models.image_repository import ImageMetadataRepository
from sqlalchemy.orm import Session

# Create repository with a database session
repository = ImageMetadataRepository(db_session)

# Get all images for a user
images = repository.get_by_user_id("user123")

# Get images by clothing type
shirts = repository.get_by_clothing_type("user123", "shirt")

# Search by tags
red_items = repository.search_by_tags("user123", ["red"])

# Get entire wardrobe
wardrobe = repository.get_wardrobe("user123")
```

## Adding New Database Models

1. Create a new model file in the `models` directory
2. Extend `Base` from `models.database`
3. Create a new repository implementation that extends `SQLAlchemyRepository`