from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.api import deps
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/sync-user", response_model=schemas.User)
def sync_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate
) -> Any:
    """
    Step 2 in Flow: Sync user data from external services.
    Updates if exists (by email or username), creates otherwise.
    Ensures a Messenger profile exists for future Telegram/Discord linking.
    """
    user = None
    if user_in.email:
        user = crud.user.get_by_email(db, email=user_in.email)
    
    if not user:
        user = crud.user.get_by_username(db, username=user_in.username)
    
    if user:
        # Update existing user
        update_data = user_in.dict(exclude_unset=True)
        user = crud.user.update(db, db_obj=user, obj_in=update_data)
        logger.info(f"Updated user: {user.username}")
    else:
        # Create new user
        user = crud.user.create(db, obj_in=user_in)
        logger.info(f"Created new user: {user.username}")
    
    return user

@router.post("/sync-subscription", response_model=schemas.Subscription)
def sync_subscription(
    *,
    db: Session = Depends(deps.get_db),
    subscription_in: schemas.SubscriptionCreate
) -> Any:
    """
    Step 1 in Flow: Sync subscription data from external services.
    Updates if exists (by name), creates otherwise.
    """
    subscription = crud.subscription.get_by_name(db, name=subscription_in.name)
    
    if subscription:
        # Update existing subscription
        update_data = subscription_in.dict(exclude_unset=True)
        subscription = crud.subscription.update(db, db_obj=subscription, obj_in=update_data)
        logger.info(f"Updated subscription: {subscription.name}")
    else:
        # Create new subscription
        subscription = crud.subscription.create(db, obj_in=subscription_in)
        logger.info(f"Created new subscription: {subscription.name}")
    
    return subscription

@router.get("/subscriptions", response_model=List[schemas.Subscription])
def list_subscriptions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    List subscriptions for external services to reference.
    """
    return crud.subscription.get_multi(db, skip=skip, limit=limit)

@router.post("/record-quiz", response_model=schemas.PlayedQuiz)
def record_quiz(
    *,
    db: Session = Depends(deps.get_db),
    quiz_in: schemas.WebhookQuizCreate
) -> Any:
    """
    Record a played quiz result for a user by username and subscription name.
    """
    # Lookup user
    user = crud.user.get_by_username(db, username=quiz_in.username)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{quiz_in.username}' not found")
    
    # Lookup subscription
    subscription = crud.subscription.get_by_name(db, name=quiz_in.subs)
    if not subscription:
        raise HTTPException(status_code=404, detail=f"Subscription '{quiz_in.subs}' not found")
            
    # Prepare internal create object
    internal_quiz_in = schemas.PlayedQuizCreate(
        user_id=user.id,
        subs_id=subscription.id,
        score=quiz_in.score,
        time=quiz_in.time
    )
    
    quiz = crud.quiz.create(db, obj_in=internal_quiz_in)
    logger.info(f"Recorded quiz for user {user.username}, subscription {subscription.name}, score: {quiz_in.score}")
    return quiz

@router.post("/link-user-subscription", response_model=schemas.UserSubscribed)
def link_user_subscription(
    *,
    db: Session = Depends(deps.get_db),
    link_in: schemas.WebhookUserSubscribedCreate
) -> Any:
    """
    Step 3 in Flow: Link a user to a subscription by username and subscription name.
    Expects names to exist already via previous sync steps.
    """
    # Lookup user
    user = crud.user.get_by_username(db, username=link_in.username)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{link_in.username}' not found. Ensure User Sync was called.")
    
    # Lookup subscription
    subscription = crud.subscription.get_by_name(db, name=link_in.subs)
    if not subscription:
        raise HTTPException(status_code=404, detail=f"Subscription '{link_in.subs}' not found. Ensure Subscription Sync was called.")
        
    # Check if this link already exists to avoid duplicates
    existing_link = db.query(models.UserSubscribed).filter(
        models.UserSubscribed.user_id == user.id,
        models.UserSubscribed.subs_id == subscription.id
    ).first()
    
    if existing_link:
        # Update existing link dates if provided
        if link_in.start_date:
            existing_link.start_date = link_in.start_date
        if link_in.end_date:
            existing_link.end_date = link_in.end_date
        db.add(existing_link)
    else:
        # Create internal link object
        internal_link_in = schemas.UserSubscribedCreate(
            user_id=user.id,
            subs_id=subscription.id,
            start_date=link_in.start_date,
            end_date=link_in.end_date
        )
        existing_link = crud.user_subscribed.create(db, obj_in=internal_link_in)
    
    # Also update the user's primary subscription_id and platform flags
    user.subscription_id = subscription.id
    if subscription.platform == models.enums.PlatformType.QUIZARD:
        user.quizard = True
    elif subscription.platform == models.enums.PlatformType.WORDLY:
        user.wordly = True
    elif subscription.platform == models.enums.PlatformType.ARCADERUSH:
        user.arcaderush = True
    db.add(user)
    db.commit()
    db.refresh(existing_link)
    
    logger.info(f"Linked user {user.username} to subscription {subscription.name}")
    return existing_link

@router.post("/check-user")
def check_user(
    *,
    db: Session = Depends(deps.get_db),
    check_in: schemas.UserCheck
) -> Any:
    """
    Check if a username exists and return their platform registration status.
    """
    user = crud.user.get_by_username(db, username=check_in.username)
    if not user:
        return {"exists": False}
    
    return {
        "exists": True,
        "username": user.username,
        "platforms": {
            "quizard": user.quizard,
            "wordly": user.wordly,
            "arcaderush": user.arcaderush
        }
    }

@router.post("/register-platform", response_model=schemas.User)
def register_platform(
    *,
    db: Session = Depends(deps.get_db),
    update_in: schemas.UserPlatformUpdate
) -> Any:
    """
    Register an existing user to a specific platform.
    """
    user = crud.user.get_by_username(db, username=update_in.username)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{update_in.username}' not found")

    platform = update_in.platform.lower()
    if platform == "quizard":
        user.quizard = True
    elif platform == "wordly":
        user.wordly = True
    elif platform == "arcaderush":
        user.arcaderush = True
    else:
        raise HTTPException(status_code=400, detail=f"Invalid platform '{platform}'. Must be one of: quizard, wordly, arcaderush")
    
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Registered user {user.username} to platform {platform}")
    return user
