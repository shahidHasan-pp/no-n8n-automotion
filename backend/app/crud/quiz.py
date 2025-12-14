
from app.crud.base import CRUDBase
from app.models.quiz import Quiz, UserSubscribed
from app.schemas.quiz import QuizCreate, QuizUpdate, UserSubscribedCreate

class CRUDQuiz(CRUDBase[Quiz, QuizCreate, QuizUpdate]):
    pass

class CRUDUserSubscribed(CRUDBase[UserSubscribed, UserSubscribedCreate, UserSubscribedCreate]): # Using Create schema for Update as simplified
    pass

quiz = CRUDQuiz(Quiz)
user_subscribed = CRUDUserSubscribed(UserSubscribed)
