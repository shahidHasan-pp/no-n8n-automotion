
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exists, func
from app.crud.base import CRUDBase
from app.models.user import User
from app.models.messenger import Message, Messenger
from app.models.quiz import UserSubscribed
from app.models.enums import PlatformType
from app.schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_with_filters(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None,
        quizard: Optional[bool] = None,
        wordly: Optional[bool] = None,
        arcaderush: Optional[bool] = None,
        has_subscription: Optional[bool] = None,
        has_messages: Optional[bool] = None
    ) -> List[User]:
        # Eagerly load messenger relationship
        query = db.query(User).options(
            joinedload(User.messenger)
        )
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (User.username.like(search_pattern)) |
                (User.email.like(search_pattern)) |
                (User.full_name.like(search_pattern))
            )
        
        if quizard is not None:
            if quizard:
                query = query.filter(User.quizard == True)
            else:
                query = query.filter((User.quizard == False) | (User.quizard.is_(None)))
        if wordly is not None:
            if wordly:
                query = query.filter(User.wordly == True)
            else:
                query = query.filter((User.wordly == False) | (User.wordly.is_(None)))
        if arcaderush is not None:
            if arcaderush:
                query = query.filter(User.arcaderush == True)
            else:
                query = query.filter((User.arcaderush == False) | (User.arcaderush.is_(None)))
        
        if has_subscription is not None:
            if has_subscription:
                query = query.filter(exists().where(UserSubscribed.user_id == User.id))
            else:
                query = query.filter(~exists().where(UserSubscribed.user_id == User.id))
                
        if has_messages is not None:
            if has_messages:
                query = query.filter(exists().where(Message.user_id == User.id))
            else:
                query = query.filter(~exists().where(Message.user_id == User.id))
                
        users = query.offset(skip).limit(limit).all()
        
        # Populate auxiliary fields
        for u in users:
            count = db.query(func.count(UserSubscribed.id)).filter(
                UserSubscribed.user_id == u.id
            ).scalar()
            u.active_subscriptions_count = count or 0
            
        return users

user = CRUDUser(User)
