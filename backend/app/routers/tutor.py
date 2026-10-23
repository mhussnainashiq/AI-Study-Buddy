from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Document, StudyActivity
from app.services.ai_service import explain_concept, answer_document_question, AIUnavailable
from app.services.retrieval_service import retrieve_relevant
router=APIRouter(prefix="/api/tutor",tags=["tutor"])
class TutorRequest(BaseModel):
    question:str=Field(min_length=1,max_length=4000)
    document_id:int|None=None
    mode:str="Beginner-Friendly"
    history:list[dict]=Field(default_factory=list)
@router.post("/ask")
def ask(body:TutorRequest,db:Session=Depends(get_db)):
    context=""
    if body.document_id:
        doc=db.get(Document,body.document_id)
        if not doc: raise HTTPException(404,"Document not found")
        chunks=retrieve_relevant(doc.extracted_text,body.question)
        context="\n\n".join(chunks)
    try: answer=explain_concept(body.question,context,body.mode,body.history)
    except AIUnavailable as e: raise HTTPException(503,str(e))
    db.add(StudyActivity(activity_type="tutor_question",resource_id=body.document_id,detail=body.question[:250])); db.commit()
    return {"answer":answer,"document_id":body.document_id,"context_used":bool(context),"source_note":"Based on retrieved document text and general explanation where appropriate." if context else "No document selected; answer is based on general knowledge."}
@router.post("/document-question")
def ask_document(body:TutorRequest,db:Session=Depends(get_db)):
    if not body.document_id: raise HTTPException(422,"Select a document to ask document-based questions.")
    doc=db.get(Document,body.document_id)
    if not doc: raise HTTPException(404,"Document not found")
    try: answer=answer_document_question(body.question,retrieve_relevant(doc.extracted_text,body.question))
    except AIUnavailable as e: raise HTTPException(503,str(e))
    return {"answer":answer,"document_id":doc.id,"context_used":True}
