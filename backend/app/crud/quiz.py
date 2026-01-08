
from typing import List, Any
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.quiz import PlayedQuiz, UserSubscribed
from app.schemas.quiz import PlayedQuizCreate, PlayedQuizUpdate, UserSubscribedCreate

class CRUDPlayedQuiz(CRUDBase[PlayedQuiz, PlayedQuizCreate, PlayedQuizUpdate]):
    pass

class CRUDUserSubscribed(CRUDBase[UserSubscribed, UserSubscribedCreate, UserSubscribedCreate]):
    def get_subscriptions_by_user(self, db: Session, user_id: int) -> List[Any]:
        # Circular import might happen if we import model at top if not careful, 
        # but models are usually safe.
        # However Subscription model is in different file.
        from app.models.subscription import Subscription
        
        return db.query(self.model, Subscription).join(
            Subscription, self.model.subs_id == Subscription.id
        ).filter(self.model.user_id == user_id).all()

quiz = CRUDPlayedQuiz(PlayedQuiz)
user_subscribed = CRUDUserSubscribed(UserSubscribed)
