from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Document, StudyActivity
from app.services.document_processor import read_upload, extract_text
from app.core.config import upload_path

router=APIRouter(prefix="/api/documents", tags=["documents"])

def doc_out(d, include_text=False):
    out={"id":d.id,"title":d.title,"subject":d.subject,"description":d.description,"original_filename":d.original_filename,"file_type":d.file_type,"file_size":d.file_size,"page_count":d.page_count,"text_length":len(d.extracted_text),"created_at":d.created_at.isoformat() if d.created_at else None}
    if include_text: out["extracted_text"]=d.extracted_text
    return out

@router.post("/upload", status_code=201)
async def upload_document(file: UploadFile=File(...), title: str=Form(""), subject: str=Form("General"), description: str=Form(""), db: Session=Depends(get_db)):
    data,suffix=await read_upload(file)
    text,pages=extract_text(data,suffix)
    safe_name=f"{uuid4().hex}{suffix}"
    dest=upload_path()/safe_name
    dest.write_bytes(data)
    doc=Document(title=(title.strip() or Path(file.filename or "Study material").stem)[:200],subject=subject.strip()[:120] or "General",description=description.strip()[:2000],original_filename=Path(file.filename or "upload").name[:255],stored_filename=safe_name,file_type=suffix[1:],file_size=len(data),extracted_text=text,page_count=pages)
    db.add(doc); db.flush(); db.add(StudyActivity(activity_type="document_upload",resource_id=doc.id,detail=doc.title)); db.commit(); db.refresh(doc)
    return doc_out(doc)

@router.get("")
def list_documents(q: str="", limit: int=50, offset: int=0, db: Session=Depends(get_db)):
    query=db.query(Document)
    if q: query=query.filter((Document.title.contains(q))|(Document.subject.contains(q)))
    docs=query.order_by(Document.created_at.desc()).offset(max(offset,0)).limit(min(max(limit,1),100)).all()
    return {"items":[doc_out(d) for d in docs],"limit":min(max(limit,1),100),"offset":max(offset,0)}

@router.get("/{document_id}")
def get_document(document_id:int, db:Session=Depends(get_db)):
    d=db.get(Document,document_id)
    if not d: raise HTTPException(404,"Document not found")
    return doc_out(d)

@router.get("/{document_id}/text")
def get_document_text(document_id:int, db:Session=Depends(get_db)):
    d=db.get(Document,document_id)
    if not d: raise HTTPException(404,"Document not found")
    return {"document_id":d.id,"title":d.title,"extracted_text":d.extracted_text}

@router.delete("/{document_id}", status_code=204)
def delete_document(document_id:int, db:Session=Depends(get_db)):
    d=db.get(Document,document_id)
    if not d: raise HTTPException(404,"Document not found")
    try: (upload_path()/d.stored_filename).unlink(missing_ok=True)
    except OSError: pass
    db.delete(d); db.commit()
