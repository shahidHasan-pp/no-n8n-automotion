
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import user as user_crud
from app.models.enums import PlatformType
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter()

@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(deps.get_db), 
    skip: int = 0, 
    limit: int = 20,
    search: str = None,
    quizard: bool = None,
    wordly: bool = None,
    arcaderush: bool = None,
    has_subscription: bool = None,
    has_messages: bool = None
) -> Any:
    """
    Retrieve users with optional search and filters.
    """
    return user_crud.get_with_filters(
        db, 
        skip=skip, 
        limit=limit, 
        search=search, 
        quizard=quizard,
        wordly=wordly,
        arcaderush=arcaderush,
        has_subscription=has_subscription, 
        has_messages=has_messages
    )

@router.post("/", response_model=User)
def create_user(user_in: UserCreate, db: Session = Depends(deps.get_db)) -> Any:
    if user_in.email:
        user = user_crud.get_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(status_code=400, detail="The user with this email already exists in the system.")
    
    # Check username
    user = user_crud.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="The user with this username already exists.")

    user = user_crud.create(db, obj_in=user_in)
    return user

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(deps.get_db)) -> Any:
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(deps.get_db)) -> Any:
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = user_crud.update(db, db_obj=user, obj_in=user_in)
    return user
