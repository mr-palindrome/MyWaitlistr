import json
from typing import Annotated, Optional, List
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from .models import Project
from src.config.settings import BUCKET_NAME
from src.config.db.redis_management.redis_manager import get_redis
from src.apps.auth.models import User
from src.apps.projects.schemas.response_schema import ProjectResponseSchema
from src.apps.waitlist.schemas.waitlist_schema import WaitlistResponse
from src.apps.base.s3_helpers import upload_data_to_s3



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

EXTENSION_TYPES = {
    "csv": "text/csv",
    "json": "application/json",
    "xml": "application/xml",
}

def download_waitlist_csv(waitlist_data: List[WaitlistResponse]):
    """
    Download the waitlist data as a CSV file.

    Args:
        waitlist_data (List[WaitlistResponse]): The waitlist data.

    Returns:
        str: The CSV data.
    """
    csv_data = "email,date_added\n"
    for item in waitlist_data:
        csv_data += f"{item.email},{item.date_added}\n"
    return csv_data


def download_waitlist_json(waitlist_data: List[WaitlistResponse]):
    """
    Download the waitlist data as a JSON file.

    Args:
        waitlist_data (List[WaitlistResponse]): The waitlist data.

    Returns:
        str: The JSON data.
    """
    return json.dumps([item.dict() for item in waitlist_data], indent=4)

def download_waitlist_xml(waitlist_data: List[WaitlistResponse]):
    """
    Download the waitlist data as a XML file.

    Args:
        waitlist_data (List[WaitlistResponse]): The waitlist data.

    Returns:
        str: The XML data.
    """
    xml_data = '<?xml version="1.0" encoding="UTF-8"?>\n<waitlist>\n'
    for item in waitlist_data:
        xml_data += f"<item>\n<email>{item.email}</email>\n<date_added>{item.date_added}</date_added>\n</item>\n"
    xml_data += "</waitlist>\n"
    return xml_data

async def download_waitlist(waitlist_data: List[WaitlistResponse], extension_type: str, user_id:int, project_uuid: str, download_id: Optional[str] = None):
    """
    Download the waitlist data as a CSV file.

    Args:
        waitlist_data (List[WaitlistResponse]): The waitlist data.
        extension_type (str): The file extension type.
        user_id (int): The user id.
        project_uuid (str): The project UUID.

    Returns:
        str: The S3 link to the download file
    """
    
    if extension_type == "csv":
        dump_data = download_waitlist_csv(waitlist_data)
    elif extension_type == "json":
        dump_data = download_waitlist_json(waitlist_data)
    elif extension_type == "xml":
        dump_data = download_waitlist_xml(waitlist_data)

    file_name = f"{user_id}/{project_uuid}-waitlist.{extension_type}"

    download_url = upload_data_to_s3(dump_data, file_name, BUCKET_NAME, expiry=3600)

    if download_id:
        redis = await get_redis()
        await redis.set(download_id, download_url, ex=3600)

    return download_url
