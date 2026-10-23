from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.connection import get_db
from app.database.models import Document, Summary, FlashcardDeck, Flashcard, Quiz, QuizAttempt, StudyActivity
router=APIRouter(tags=["progress"])
@router.get("/api/dashboard/stats")
def dashboard_stats(db:Session=Depends(get_db)):
    attempts=db.query(QuizAttempt).all()
    recent_docs=db.query(Document).order_by(Document.created_at.desc()).limit(5).all()
    recent_activities=db.query(StudyActivity).order_by(StudyActivity.created_at.desc()).limit(8).all()
    return {"documents":db.query(Document).count(),"summaries":db.query(Summary).count(),"flashcards":db.query(Flashcard).count(),"decks":db.query(FlashcardDeck).count(),"quizzes":db.query(Quiz).count(),"quiz_attempts":len(attempts),"average_score":round(sum(a.percentage for a in attempts)/len(attempts),1) if attempts else 0,"cards_known":db.query(Flashcard).filter_by(status="known").count(),"cards_to_practice":db.query(Flashcard).filter_by(status="practice").count(),"recent_documents":[{"id":d.id,"title":d.title,"subject":d.subject,"created_at":d.created_at.isoformat() if d.created_at else None} for d in recent_docs],"recent_activity":[{"id":a.id,"type":a.activity_type,"resource_id":a.resource_id,"detail":a.detail,"created_at":a.created_at.isoformat() if a.created_at else None} for a in recent_activities]}
@router.get("/api/progress")
def progress(db:Session=Depends(get_db)):
    attempts=db.query(QuizAttempt).order_by(QuizAttempt.created_at.asc()).all()
    activity=db.query(StudyActivity).order_by(StudyActivity.created_at.desc()).limit(50).all()
    return {"quiz_scores":[{"attempt_id":a.id,"quiz_id":a.quiz_id,"percentage":a.percentage,"created_at":a.created_at.isoformat() if a.created_at else None} for a in attempts],"activities":[{"type":a.activity_type,"detail":a.detail,"created_at":a.created_at.isoformat() if a.created_at else None} for a in activity],"totals":{"documents":db.query(Document).count(),"flashcards_reviewed":db.query(StudyActivity).filter_by(activity_type="flashcard_review").count(),"quiz_attempts":len(attempts),"cards_known":db.query(Flashcard).filter_by(status="known").count(),"cards_to_practice":db.query(Flashcard).filter_by(status="practice").count()}}
@router.get("/api/library")
def library(db:Session=Depends(get_db)):
    return {"documents":[{"id":d.id,"title":d.title,"subject":d.subject,"created_at":d.created_at.isoformat() if d.created_at else None} for d in db.query(Document).order_by(Document.created_at.desc()).all()],"summaries":[{"id":s.id,"document_id":s.document_id,"document_title":s.document.title,"length":s.length,"content":s.content,"created_at":s.created_at.isoformat() if s.created_at else None} for s in db.query(Summary).order_by(Summary.created_at.desc()).all()],"decks":[{"id":d.id,"document_id":d.document_id,"title":d.title,"card_count":len(d.cards),"created_at":d.created_at.isoformat() if d.created_at else None} for d in db.query(FlashcardDeck).order_by(FlashcardDeck.created_at.desc()).all()],"quizzes":[{"id":q.id,"document_id":q.document_id,"title":q.title,"question_count":len(q.questions),"created_at":q.created_at.isoformat() if q.created_at else None} for q in db.query(Quiz).order_by(Quiz.created_at.desc()).all()],"attempts":[{"id":a.id,"quiz_id":a.quiz_id,"quiz_title":a.quiz.title,"percentage":a.percentage,"created_at":a.created_at.isoformat() if a.created_at else None} for a in db.query(QuizAttempt).order_by(QuizAttempt.created_at.desc()).all()]}
