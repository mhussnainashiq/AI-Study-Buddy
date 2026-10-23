from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Document, FlashcardDeck, Flashcard, StudyActivity
from app.services.ai_service import generate_flashcards, AIUnavailable
router=APIRouter(tags=["flashcards"])
class DeckRequest(BaseModel): count:int=Field(10,ge=1,le=50); difficulty:str="Medium"
class CardPatch(BaseModel): front:str|None=None; back:str|None=None; status:str|None=None

def deck_out(deck): return {"id":deck.id,"document_id":deck.document_id,"title":deck.title,"difficulty":deck.difficulty,"created_at":deck.created_at.isoformat() if deck.created_at else None,"cards":[{"id":c.id,"front":c.front,"back":c.back,"topic":c.topic,"difficulty":c.difficulty,"status":c.status} for c in deck.cards]}
@router.post("/api/documents/{document_id}/flashcards",status_code=201)
def create_deck(document_id:int,body:DeckRequest,db:Session=Depends(get_db)):
    if body.difficulty not in ("Easy","Medium","Hard"): raise HTTPException(422,"Invalid difficulty")
    d=db.get(Document,document_id)
    if not d: raise HTTPException(404,"Document not found")
    try: cards=generate_flashcards(d.extracted_text,body.count,body.difficulty)
    except AIUnavailable as e: raise HTTPException(503,str(e))
    deck=FlashcardDeck(document_id=d.id,title=f"{d.title} flashcards",difficulty=body.difficulty)
    db.add(deck); db.flush()
    for c in cards: db.add(Flashcard(deck_id=deck.id,front=c["front"],back=c["back"],topic=c["topic"],difficulty=body.difficulty))
    db.add(StudyActivity(activity_type="flashcards_generated",resource_id=deck.id,detail=d.title)); db.commit(); db.refresh(deck)
    return deck_out(deck)
@router.get("/api/flashcards/{deck_id}")
def get_deck(deck_id:int,db:Session=Depends(get_db)):
    d=db.get(FlashcardDeck,deck_id)
    if not d: raise HTTPException(404,"Deck not found")
    return deck_out(d)
@router.patch("/api/flashcards/{deck_id}/cards/{card_id}")
def update_card(deck_id:int,card_id:int,body:CardPatch,db:Session=Depends(get_db)):
    deck=db.get(FlashcardDeck,deck_id); card=db.get(Flashcard,card_id)
    if not deck or not card or card.deck_id!=deck_id: raise HTTPException(404,"Flashcard not found")
    if body.front is not None: card.front=body.front[:4000]
    if body.back is not None: card.back=body.back[:8000]
    if body.status is not None:
        if body.status not in ("new","known","practice"): raise HTTPException(422,"status must be new, known, or practice")
        card.status=body.status
        db.add(StudyActivity(activity_type="flashcard_review",resource_id=card.id,detail=body.status))
    db.commit(); db.refresh(card)
    return {"id":card.id,"front":card.front,"back":card.back,"topic":card.topic,"difficulty":card.difficulty,"status":card.status}
@router.delete("/api/flashcards/{deck_id}",status_code=204)
def delete_deck(deck_id:int,db:Session=Depends(get_db)):
    d=db.get(FlashcardDeck,deck_id)
    if not d: raise HTTPException(404,"Deck not found")
    db.delete(d); db.commit()
