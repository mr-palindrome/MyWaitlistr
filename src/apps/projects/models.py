from uuid import uuid4
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    event
)
from sqlalchemy.orm import relationship

from src.config.db.postgres_management.pg_manager import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'), index=True)
    is_active = Column(Boolean, default=True)
    limit = Column(Integer, default=50)
    project_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    url = Column(String, index=True)

    api_key = relationship("APIKey", back_populates="project", cascade="all,delete", passive_deletes=True)
    owner = relationship("User", back_populates="projects")

@event.listens_for(Project, "before_insert")
def set_project_id(mapper, connection, target):
    if not target.project_id:
        target.project_id = str(uuid4())


# class OriginUrl(Base):
#     __tablename__ = "origin_urls"

#     id = Column(Integer, primary_key=True, index=True)
#     url = Column(URL, index=True)
#     project_id = Column(Integer, ForeignKey('projects.id'), index=True)

#     project = relationship("Project", back_populates="origin_urls")