from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from src.config.db.postgres_management.pg_manager import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    img_url = Column(String)

    projects = relationship("Project", back_populates="owner")


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, index=True)
    user_id = Column(Integer)
