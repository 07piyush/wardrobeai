from abc import ABC, abstractmethod
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging
import traceback

# Load environment variables
load_dotenv()

# Create SQLAlchemy Base
Base = declarative_base()

# Configure logger
logger = logging.getLogger(__name__)

class DatabaseConfig(ABC):
    """Abstract database configuration class"""
    
    @abstractmethod
    def get_connection_string(self) -> str:
        """Get database connection string"""
        pass
    
    @abstractmethod
    def create_engine(self):
        """Create database engine"""
        pass
    
    @abstractmethod
    def create_session_factory(self):
        """Create session factory"""
        pass

class PostgresConfig(DatabaseConfig):
    """PostgreSQL implementation of DatabaseConfig"""
    
    def __init__(self):
        """Initialize PostgreSQL configuration"""
        logger.info("Initializing PostgreSQL configuration")
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = os.getenv("POSTGRES_PORT", "5432")
        self.user = os.getenv("POSTGRES_USER", "postgres")
        self.password = os.getenv("POSTGRES_PASSWORD", "postgres")
        self.database = os.getenv("POSTGRES_DB", "wardrobe")
        logger.info(f"Database configuration: host={self.host}, port={self.port}, user={self.user}, database={self.database}")
        self.engine = self.create_engine()
        self.SessionLocal = self.create_session_factory()
        logger.info("PostgreSQL configuration initialized successfully")
    
    def get_connection_string(self) -> str:
        """Get PostgreSQL connection string"""
        conn_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        logger.info(f"Generated connection string: {conn_string.replace(self.password, '****')}")
        return conn_string
    
    def create_engine(self):
        """Create PostgreSQL engine"""
        logger.info("Creating database engine")
        engine = create_engine(
            self.get_connection_string(),
            echo=bool(os.getenv("SQL_ECHO", "False").lower() == "true")
        )
        logger.info("Database engine created successfully")
        return engine
    
    def create_session_factory(self):
        """Create PostgreSQL session factory"""
        logger.info("Creating session factory")
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info("Session factory created successfully")
        return session_factory

class DatabaseManager:
    """Database connection manager"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls, db_config: DatabaseConfig = None):
        """Get database manager singleton instance"""
        if cls._instance is None:
            logger.info("Creating new DatabaseManager instance")
            if db_config is None:
                db_config = PostgresConfig()
            cls._instance = cls(db_config)
            logger.info("DatabaseManager instance created successfully")
        return cls._instance
    
    def __init__(self, db_config: DatabaseConfig):
        """Initialize database manager"""
        logger.info("Initializing DatabaseManager")
        self.db_config = db_config
        self.engine = db_config.engine
        self.SessionLocal = db_config.SessionLocal
        logger.info("DatabaseManager initialized successfully")
    
    def create_tables(self):
        """Create all tables defined in models"""
        logger.info("Creating database tables")
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            logger.error(f"Full error traceback: {traceback.format_exc()}")
            raise
    
    def get_session(self):
        """Get database session"""
        logger.info("Getting new database session")
        db = self.SessionLocal()
        try:
            yield db
            logger.info("Database session yielded successfully")
        finally:
            logger.info("Closing database session")
            db.close()
            logger.info("Database session closed successfully") 