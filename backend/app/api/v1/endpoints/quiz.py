
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import quiz as quiz_crud
from app.schemas.quiz import Quiz, QuizCreate, QuizUpdate

router = APIRouter()

@router.post("/", response_model=Quiz)
def create_quiz(quiz_in: QuizCreate, db: Session = Depends(deps.get_db)) -> Any:
    return quiz_crud.create(db, obj_in=quiz_in)

@router.get("/{id}", response_model=Quiz)
def read_quiz(id: int, db: Session = Depends(deps.get_db)) -> Any:
    item = quiz_crud.get(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return item

@router.get("/", response_model=List[Quiz])
def read_quizzes(db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100) -> Any:
    return quiz_crud.get_multi(db, skip=skip, limit=limit)
