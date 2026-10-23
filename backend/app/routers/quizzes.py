from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Document, Quiz, QuizQuestion, QuizAttempt, StudyActivity
from app.services.ai_service import generate_quiz, evaluate_short_answer, AIUnavailable
router=APIRouter(tags=["quizzes"])
class QuizRequest(BaseModel): count:int=Field(10,ge=1,le=30); difficulty:str="Medium"; question_type:str="multiple_choice"
class SubmitRequest(BaseModel): answers:dict[str,str]
def safe_quiz(q, include_answers=False):
    out={"id":q.id,"prompt":q.prompt,"question_type":q.question_type,"options":q.options,"topic":q.topic}
    if include_answers: out.update({"correct_answer":q.correct_answer,"explanation":q.explanation})
    return out
def quiz_out(q, answers=False): return {"id":q.id,"document_id":q.document_id,"title":q.title,"difficulty":q.difficulty,"created_at":q.created_at.isoformat() if q.created_at else None,"questions":[safe_quiz(x,answers) for x in q.questions]}
@router.post("/api/documents/{document_id}/quizzes",status_code=201)
def create_quiz(document_id:int,body:QuizRequest,db:Session=Depends(get_db)):
    if body.difficulty not in ("Easy","Medium","Hard"): raise HTTPException(422,"Invalid difficulty")
    if body.question_type not in ("multiple_choice","true_false","short_answer"): raise HTTPException(422,"Invalid question type")
    d=db.get(Document,document_id)
    if not d: raise HTTPException(404,"Document not found")
    try: questions=generate_quiz(d.extracted_text,body.count,body.difficulty,body.question_type)
    except AIUnavailable as e: raise HTTPException(503,str(e))
    q=Quiz(document_id=d.id,title=f"{d.title} practice quiz",difficulty=body.difficulty); db.add(q); db.flush()
    for item in questions: db.add(QuizQuestion(quiz_id=q.id,prompt=item["prompt"],question_type=item["question_type"],options=item["options"],correct_answer=item["correct_answer"],explanation=item["explanation"],topic=item["topic"]))
    db.add(StudyActivity(activity_type="quiz_generated",resource_id=q.id,detail=d.title)); db.commit(); db.refresh(q)
    return quiz_out(q)
@router.get("/api/quizzes/{quiz_id}")
def get_quiz(quiz_id:int,db:Session=Depends(get_db)):
    q=db.get(Quiz,quiz_id)
    if not q: raise HTTPException(404,"Quiz not found")
    return quiz_out(q,False)
@router.post("/api/quizzes/{quiz_id}/submit")
def submit_quiz(quiz_id:int,body:SubmitRequest,db:Session=Depends(get_db)):
    q=db.get(Quiz,quiz_id)
    if not q: raise HTTPException(404,"Quiz not found")
    if not q.questions: raise HTTPException(400,"Quiz has no questions")
    feedback={}; score=0.0
    for question in q.questions:
        answer=str(body.answers.get(str(question.id),""))
        if question.question_type=="short_answer":
            try:
                grade=evaluate_short_answer(question.prompt,question.correct_answer,answer) if answer.strip() else {"correct":False,"feedback":"No answer provided.","score":0}
                correct=grade["correct"]; points=grade["score"]
                feedback[str(question.id)]={"correct":correct,"correct_answer":question.correct_answer,"explanation":question.explanation,"feedback":grade["feedback"],"ai_estimated":True,"score":points}
            except AIUnavailable as e: raise HTTPException(503,str(e))
        else:
            correct=answer.strip().casefold()==question.correct_answer.strip().casefold(); points=1.0 if correct else 0.0
            feedback[str(question.id)]={"correct":correct,"correct_answer":question.correct_answer,"explanation":question.explanation,"feedback":"Correct" if correct else "Review this topic.","ai_estimated":False,"score":points}
        score+=points
    total=len(q.questions); pct=round(score/total*100,1)
    attempt=QuizAttempt(quiz_id=q.id,score=score,total=total,percentage=pct,answers=body.answers,feedback=feedback); db.add(attempt); db.add(StudyActivity(activity_type="quiz_attempt",resource_id=q.id,detail=f"{pct}%")); db.commit(); db.refresh(attempt)
    weak={}
    for question in q.questions:
        f=feedback[str(question.id)]
        if not f["correct"]: weak[question.topic]=weak.get(question.topic,0)+1
    return {"attempt_id":attempt.id,"quiz_id":q.id,"score":score,"total":total,"percentage":pct,"feedback":[{"question_id":int(k),**v} for k,v in feedback.items()],"weak_topics":[{"topic":k,"missed_questions":v} for k,v in weak.items()]}
@router.get("/api/quizzes/{quiz_id}/results")
def quiz_results(quiz_id:int,db:Session=Depends(get_db)):
    if not db.get(Quiz,quiz_id): raise HTTPException(404,"Quiz not found")
    return [{"id":a.id,"score":a.score,"total":a.total,"percentage":a.percentage,"created_at":a.created_at.isoformat() if a.created_at else None,"feedback":a.feedback} for a in db.query(QuizAttempt).filter_by(quiz_id=quiz_id).order_by(QuizAttempt.created_at.desc()).all()]
@router.get("/api/quiz-attempts")
def attempts(db:Session=Depends(get_db)):
    return [{"id":a.id,"quiz_id":a.quiz_id,"quiz_title":a.quiz.title,"score":a.score,"total":a.total,"percentage":a.percentage,"created_at":a.created_at.isoformat() if a.created_at else None} for a in db.query(QuizAttempt).order_by(QuizAttempt.created_at.desc()).limit(100).all()]
