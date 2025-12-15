
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import exists, func
from app.crud.base import CRUDBase
from app.models.user import User
from app.models.messenger import Message
from app.models.quiz import UserSubscribed
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
        has_subscription: Optional[bool] = None,
        has_messages: Optional[bool] = None
    ) -> List[User]:
        query = db.query(User)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (User.username.like(search_pattern)) |
                (User.email.like(search_pattern)) |
                (User.full_name.like(search_pattern))
            )
        
        if has_subscription is not None:
             if has_subscription:
                query = query.filter(User.subscription_id.isnot(None))
             else:
                query = query.filter(User.subscription_id.is_(None))
                
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
