
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import user as user_crud
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter()

@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(deps.get_db), 
    skip: int = 0, 
    limit: int = 20,
    search: str = None,
    has_subscription: bool = None,
    has_messages: bool = None
) -> Any:
    """
    Retrieve users with optional search and filters.
    - search: Search by username, email, or full_name
    - has_subscription: Filter by subscription status (true/false)
    - has_messages: Filter by message context (true/false)
    """
    return user_crud.get_with_filters(
        db, 
        skip=skip, 
        limit=limit, 
        search=search, 
        has_subscription=has_subscription, 
        has_messages=has_messages
    )

@router.post("/", response_model=User)
def create_user(user_in: UserCreate, db: Session = Depends(deps.get_db)) -> Any:
    user = user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="The user with this email already exists in the system.")
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
