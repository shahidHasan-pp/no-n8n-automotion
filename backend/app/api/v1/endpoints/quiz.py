
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import quiz as quiz_crud, user_subscribed as user_subscribed_crud
from app.schemas.quiz import PlayedQuiz, PlayedQuizCreate, UserSubscribed
from app.services.subscription_service import subscription_service

router = APIRouter()

class SubscribeRequest(BaseModel):
    username: str
    subscription_name: str

@router.post("/subscribe", response_model=UserSubscribed)
def subscribe_user(request: SubscribeRequest, db: Session = Depends(deps.get_db)) -> Any:
    return subscription_service.subscribe_user(db, request.username, request.subscription_name)

@router.get("/user/{user_id}/subscriptions")
def get_user_subscriptions(user_id: int, db: Session = Depends(deps.get_db)) -> Any:
    """Get all subscriptions for a specific user with full details"""
    results = user_subscribed_crud.get_subscriptions_by_user(db, user_id=user_id)
    
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

@router.post("/", response_model=PlayedQuiz)
def create_quiz(quiz_in: PlayedQuizCreate, db: Session = Depends(deps.get_db)) -> Any:
    return quiz_crud.create(db, obj_in=quiz_in)

@router.get("/{id}", response_model=PlayedQuiz)
def read_quiz(id: int, db: Session = Depends(deps.get_db)) -> Any:
    item = quiz_crud.get(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return item

@router.get("/", response_model=List[PlayedQuiz])
def read_quizzes(db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100) -> Any:
    return quiz_crud.get_multi(db, skip=skip, limit=limit)
