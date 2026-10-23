from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Document, Summary, StudyActivity
from app.services.ai_service import generate_summary, AIUnavailable
router=APIRouter(tags=["summaries"])
class SummaryRequest(BaseModel): length: str="Medium"
@router.post("/api/documents/{document_id}/summaries", status_code=201)
def create_summary(document_id:int, body:SummaryRequest, db:Session=Depends(get_db)):
    if body.length not in ("Short","Medium","Detailed"): raise HTTPException(422,"length must be Short, Medium, or Detailed")
    d=db.get(Document,document_id)
    if not d: raise HTTPException(404,"Document not found")
    try: content=generate_summary(d.extracted_text,body.length)
    except AIUnavailable as e: raise HTTPException(503,str(e))
    s=Summary(document_id=d.id,length=body.length,content=content); db.add(s); db.flush(); db.add(StudyActivity(activity_type="summary_generated",resource_id=s.id,detail=d.title)); db.commit(); db.refresh(s)
    return summary_out(s)
def summary_out(s): return {"id":s.id,"document_id":s.document_id,"length":s.length,"content":s.content,"created_at":s.created_at.isoformat() if s.created_at else None}
@router.get("/api/documents/{document_id}/summaries")
def list_summaries(document_id:int,db:Session=Depends(get_db)):
    if not db.get(Document,document_id): raise HTTPException(404,"Document not found")
    return [summary_out(s) for s in db.query(Summary).filter_by(document_id=document_id).order_by(Summary.created_at.desc()).all()]
@router.get("/api/summaries/{summary_id}")
def get_summary(summary_id:int,db:Session=Depends(get_db)):
    s=db.get(Summary,summary_id)
    if not s: raise HTTPException(404,"Summary not found")
    return summary_out(s)
@router.delete("/api/summaries/{summary_id}",status_code=204)
def delete_summary(summary_id:int,db:Session=Depends(get_db)):
    s=db.get(Summary,summary_id)
    if not s: raise HTTPException(404,"Summary not found")
    db.delete(s); db.commit()
