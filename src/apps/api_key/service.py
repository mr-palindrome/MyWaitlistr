from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .models import APIKey
from src.apps.projects.models import Project
from .schemas.api_key_schema import APIKeySchema


def get_project_api_keys(db: Session, project_id: int):
    """
    Get all API keys by project id from the database.

    Args:
        db (Session): The database session.
        project_id (int): The id of the project.

    Returns:
        APIKey: The API key object.
    """
    return db.query(APIKey).filter(APIKey.project_id == project_id)

def verify_project_api_key(db: Session, pk: int, project_id: int):
    """
    Verify the API key by project id and key.

    Args:
        db (Session): The database session.
        project_id (int): The id of the project.
        pk (int): The API key id.

    Returns:
        APIKey: The API key object.
    """
    return db.query(APIKey).filter(APIKey.project_id == project_id, APIKey.id == pk).first()


def verify_api_key(db: Session, key: str):
    """
    Get the validity of the API key from the database.

    Args:
        db (Session): The database session.
        key (str): The API key.

    Returns:
        APIKey: The API key object.
    """
    
    return db.query(APIKey).filter(APIKey.key == key).first()


def create_api_key(db: Session, project_id: int, key: str, alias: Optional[str] = None):
    """
    Create an API key in the database.

    Args:
        db (Session): The database session.
        project_id (int): The id of the project.
        key (str): The API key.
        alias (str, optional): The alias of the API key. Defaults to None.

    Returns:
        APIKey: The API key object.
    """
    api_key = APIKey(project_id=project_id, key=key, alias=alias)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key

def update_api_key_alias(db: Session, api_key: APIKey, alias: str):
    """
    Update the alias of the API key in the database.

    Args:
        db (Session): The database session.
        api_key (APIKey): The API key object.
        alias (str): The alias of the API key.
    
    Returns:
        APIKey: The API key object.
    """
    api_key.alias = alias
    db.commit()
    db.refresh(api_key)
    return api_key

def delete_api_key(db: Session, api_key: APIKey):
    """
    Delete the API key from the database.

    Args:
        db (Session): The database session.
        api_key (APIKey): The API key object.
    """
    try:
        db.delete(api_key)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


def create_api_key_response_data(api_key: APIKey):
    """
    Create a response data for the API key.

    Args:
        api_key (APIKey): The API key object.

    Returns:
        APIKeySchema: The API key schema object.
    """
    return APIKeySchema(
        id=api_key.id,
        key=api_key.key,
        project_id=api_key.project_id,
        alias=api_key.alias,
        created_at=api_key.created_at.isoformat(),
    )