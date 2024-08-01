from .models import Project
from src.apps.auth.models import User
from typing import Annotated, Optional
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from src.apps.projects.schemas.response_schema import ProjectResponseSchema


def get_project_by_name(db: Session, name: str, owner_id: int):
    """
    Get a project by name from the database.

    Args:
        db (Session): The database session.
        name (str): The name of the project.

    Returns:
        Project: The project object.
    """
    return db.query(Project).filter(Project.name == name, Project.owner_id == owner_id).first()


def get_project_by_id(db: Session, project_id: int, owner_id: int):
    """
    Get a project by id from the database.

    Args:
        db (Session): The database session.
        project_id (int): The id of the project.

    Returns:
        Project: The project object.
    """
    return db.query(Project).filter(Project.id == project_id, Project.owner_id == owner_id).first()


def get_project_by_project_id(db: Session, project_id: str, owner_id: int):
    """
    Get a project by id from the database.

    Args:
        db (Session): The database session.
        project_id (int): The id of the project.

    Returns:
        Project: The project object.
    """
    return db.query(Project).filter(Project.project_id == project_id, Project.owner_id == owner_id).first()


def get_all_projects(db: Session, owner_id: int):
    """
    Get all projects from the database.

    Args:
        db (Session): The database session.

    Returns:
        List[Project]: The list of project objects.
    """
    return db.query(Project).filter(Project.owner_id == owner_id).order_by("created_at").all()


def create_project(db: Session, project: Project, ower_id: int):
    """
    Create a new project in the database.

    Args:
        db (Session): The database session.
        project (Project): The project object.

    Returns:
        Project: The project object.
    """
    _project = Project(**project.dict(), owner_id=ower_id)
    db.add(_project)
    db.commit()
    db.refresh(_project)
    return _project


def update_project(db: Session, project: Project):
    """
    Update a project in the database.

    Args:
        db (Session): The database session.
        project (Project): The project object.

    Returns:
        Project: The updated project object.
    """
    existing_project = get_project_by_id(db, project.id, project.owner_id)
    if existing_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    for attr, value in vars(project).items():
        setattr(existing_project, attr, value)

    db.commit()
    db.refresh(project)
    return project

def update_project_by_project_id(db: Session, existing_project: Project, project: Project):
    """
    Update a project in the database.

    Args:
        db (Session): The database session.
        project (Project): The project object.

    Returns:
        Project: The updated project object.
    """
    for attr, value in vars(project).items():
        setattr(existing_project, attr, value)

    db.commit()
    db.refresh(existing_project)
    return existing_project


def create_project_response_data(project: Project):
    return ProjectResponseSchema(
        id=project.id,
        project_id=str(project.project_id),  # Convert UUID to string
        limit=project.limit,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat() if project.updated_at else None,
        name=project.name,
        url=project.url,
        description=project.description,
    ).dict()