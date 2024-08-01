from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship

from src.config.db.postgres_management.pg_manager import Base


class APIKey(Base):
    __tablename__ = "api_key"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, index=True)
    alias = Column(String, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), index=True)
    created_at = Column(DateTime, default=datetime.now)

    project = relationship("Project", back_populates="api_key")



# class OriginUrl(Base):
#     __tablename__ = "origin_urls"

#     id = Column(Integer, primary_key=True, index=True)
#     url = Column(URL, index=True)
#     project_id = Column(Integer, ForeignKey('projects.id'), index=True)

#     project = relationship("Project", back_populates="origin_urls")