
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
    from app.models.user import User as UserModel
    from app.models.messenger import Message as MessageModel
    from app.models.quiz import UserSubscribed as UserSubscribedModel
    from sqlalchemy import exists, func
    
    query = db.query(UserModel)
    
    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (UserModel.username.like(search_pattern)) |
            (UserModel.email.like(search_pattern)) |
            (UserModel.full_name.like(search_pattern))
        )
    
    # Apply subscription filter
    if has_subscription is not None:
        if has_subscription:
            query = query.filter(UserModel.subscription_id.isnot(None))
        else:
            query = query.filter(UserModel.subscription_id.is_(None))
    
    # Apply messages filter
    if has_messages is not None:
        if has_messages:
            # Users who have at least one message
            query = query.filter(
                exists().where(MessageModel.user_id == UserModel.id)
            )
        else:
            # Users with no messages
            query = query.filter(
                ~exists().where(MessageModel.user_id == UserModel.id)
            )
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    
    # Add subscription count to each user
    for user in users:
        count = db.query(func.count(UserSubscribedModel.id)).filter(
            UserSubscribedModel.user_id == user.id
        ).scalar()
        user.active_subscriptions_count = count or 0
    
    return users

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
