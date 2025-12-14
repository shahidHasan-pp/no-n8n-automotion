from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import subscription as subscription_crud
from app.schemas.subscription import Subscription, SubscriptionCreate, SubscriptionUpdate

router = APIRouter()

# User Subscriptions
@router.post("/", response_model=Subscription)
def create_subscription(sub_in: SubscriptionCreate, db: Session = Depends(deps.get_db)) -> Any:
    return subscription_crud.create(db, obj_in=sub_in)

@router.get("/{sub_id}", response_model=Subscription)
def read_subscription(sub_id: int, db: Session = Depends(deps.get_db)) -> Any:
    sub = subscription_crud.get(db, id=sub_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub

@router.get("/", response_model=List[Subscription])
def read_subscriptions(db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100) -> Any:
    return subscription_crud.get_multi(db, skip=skip, limit=limit)
