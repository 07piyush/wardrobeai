#!/usr/bin/env python3
"""
Database setup script for PostgreSQL.
Creates the database and tables if they don't exist.
"""

import os
import sys
import logging
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Base, PostgresConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Set up the PostgreSQL database"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get database configuration
        config = PostgresConfig()
        conn_string = config.get_connection_string()
        
        logger.info(f"Setting up database: {conn_string}")
        
        # Create database if it doesn't exist
        engine = create_engine(conn_string)
        if not database_exists(engine.url):
            logger.info(f"Creating database: {config.database}")
            create_database(engine.url)
            logger.info(f"Database {config.database} created successfully")
        else:
            logger.info(f"Database {config.database} already exists")
            
        # Create tables
        logger.info("Creating tables...")
        Base.metadata.create_all(engine)
        logger.info("Tables created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        return False

if __name__ == "__main__":
    if setup_database():
        logger.info("Database setup completed successfully")
    else:
        logger.error("Database setup failed")
        sys.exit(1) 