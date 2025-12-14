
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.api import deps
from app.crud import quiz as quiz_crud, user_subscribed as user_sub_crud
from app.crud import user as user_crud
from app.crud import subscription as subscription_crud
from app.schemas.quiz import Quiz, QuizCreate, QuizUpdate, UserSubscribed, UserSubscribedCreate

router = APIRouter()

class SubscribeRequest(BaseModel):
    username: str
    subscription_name: str

@router.post("/subscribe", response_model=UserSubscribed)
def subscribe_user(request: SubscribeRequest, db: Session = Depends(deps.get_db)) -> Any:
    # 1. Get User
    user = user_crud.get_by_username(db, username=request.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. Get Subscription
    sub = subscription_crud.get_by_name(db, name=request.subscription_name)
    if not sub:
        # Try by ID
        try:
            sub_id = int(request.subscription_name)
            sub = subscription_crud.get(db, id=sub_id)
        except ValueError:
            pass
            
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # 3. Calculate subscription period
    start_date = datetime.utcnow()
    
    # Calculate end_date based on subscription duration
    if sub.time == "MONTHLY":
        end_date = start_date + timedelta(days=30)
    elif sub.time == "YEARLY":
        end_date = start_date + timedelta(days=365)
    elif sub.time == "LIFETIME":
        end_date = start_date + timedelta(days=36500)  # 100 years
    else:
        end_date = start_date + timedelta(days=30)  # Default to monthly

    # 4. Create UserSubscribed with dates
    user_sub_in = UserSubscribedCreate(
        user_id=user.id, 
        subs_id=sub.id,
        start_date=start_date,
        end_date=end_date
    )
    user_sub = user_sub_crud.create(db, obj_in=user_sub_in)
    
    # 5. Update user's subscription_id field
    user.subscription_id = sub.id
    db.add(user)
    
    # 6. Increment Subscription Quantity
    sub.current_subs_quantity += 1
    db.add(sub)
    db.commit()
    db.refresh(sub)
    db.refresh(user)
    
    return user_sub

@router.get("/user/{user_id}/subscriptions")
def get_user_subscriptions(user_id: int, db: Session = Depends(deps.get_db)) -> Any:
    """Get all subscriptions for a specific user with full details"""
    from app.models.quiz import UserSubscribed as UserSubscribedModel
    from app.models.subscription import Subscription as SubscriptionModel
    
    # Query user_subscribed joined with subscriptions
    results = db.query(UserSubscribedModel, SubscriptionModel).join(
        SubscriptionModel, UserSubscribedModel.subs_id == SubscriptionModel.id
    ).filter(UserSubscribedModel.user_id == user_id).all()
    
    # Format response
    subscriptions = []
    for user_sub, sub in results:
        subscriptions.append({
            "id": sub.id,
            "name": sub.name,
            "type": sub.type,
            "time": sub.time,
            "offer": sub.offer,
            "prize": sub.prize,
            "amount": sub.amount,
            "link": sub.link,
            "start_date": user_sub.start_date,
            "end_date": user_sub.end_date,
            "subscribed_at": user_sub.created_at
        })
    
    return subscriptions

@router.post("/", response_model=Quiz)
def create_quiz(quiz_in: QuizCreate, db: Session = Depends(deps.get_db)) -> Any:
    return quiz_crud.quiz.create(db, obj_in=quiz_in)

@router.get("/{id}", response_model=Quiz)
def read_quiz(id: int, db: Session = Depends(deps.get_db)) -> Any:
    item = quiz_crud.quiz.get(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return item

@router.get("/", response_model=List[Quiz])
def read_quizzes(db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100) -> Any:
    return quiz_crud.quiz.get_multi(db, skip=skip, limit=limit)
