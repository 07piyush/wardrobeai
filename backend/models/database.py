from abc import ABC, abstractmethod
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create SQLAlchemy Base
Base = declarative_base()

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
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = os.getenv("POSTGRES_PORT", "5432")
        self.user = os.getenv("POSTGRES_USER", "postgres")
        self.password = os.getenv("POSTGRES_PASSWORD", "postgres")
        self.database = os.getenv("POSTGRES_DB", "wardrobe")
        self.engine = self.create_engine()
        self.SessionLocal = self.create_session_factory()
    
    def get_connection_string(self) -> str:
        """Get PostgreSQL connection string"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def create_engine(self):
        """Create PostgreSQL engine"""
        return create_engine(
            self.get_connection_string(),
            echo=bool(os.getenv("SQL_ECHO", "False").lower() == "true")
        )
    
    def create_session_factory(self):
        """Create PostgreSQL session factory"""
        return sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

class DatabaseManager:
    """Database connection manager"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls, db_config: DatabaseConfig = None):
        """Get database manager singleton instance"""
        if cls._instance is None:
            if db_config is None:
                db_config = PostgresConfig()
            cls._instance = cls(db_config)
        return cls._instance
    
    def __init__(self, db_config: DatabaseConfig):
        """Initialize database manager"""
        self.db_config = db_config
        self.engine = db_config.engine
        self.SessionLocal = db_config.SessionLocal
    
    def create_tables(self):
        """Create all tables defined in models"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close() 