from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from databases import Database
from pydantic import PostgresDsn

from src.config import settings


database_url = PostgresDsn.build(
    scheme="postgresql",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    path=f"{settings.DB_NAME}",
)

DATABASE_URL = str(database_url)
# SQLAlchemy specific code
engine = create_engine(
    DATABASE_URL,
    connect_args={"connect_timeout": 10},
    pool_size=10,          # Adjust the pool size as needed
    max_overflow=20,       # Adjust the overflow size as needed
    pool_timeout=30,       # Adjust the pool timeout as needed
    pool_recycle=1800,     # Adjust the recycle time as needed (in seconds)
    pool_pre_ping=True     # Enable pre-ping to check the connection health before using it
)
metadata = MetaData()
Base = declarative_base()

# Async database connection
database = Database(DATABASE_URL)

# Session maker for SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
