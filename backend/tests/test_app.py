from unittest.mock import patch
from app.database.connection import SessionLocal
from app.database.models import Document, Quiz, QuizQuestion

def test_health(client):
    r=client.get("/api/health"); assert r.status_code==200 and r.json()["status"]=="ok"

def test_rejects_unsupported_file(client):
    r=client.post("/api/documents/upload",files={"file":("notes.exe",b"nope","application/octet-stream")})
    assert r.status_code==415

def test_upload_txt_and_dashboard(client):
    r=client.post("/api/documents/upload",files={"file":("lesson.txt",b"Photosynthesis converts light energy into chemical energy.","text/plain")},data={"subject":"Biology"})
    assert r.status_code==201, r.text
    d=r.json(); assert d["subject"]=="Biology" and d["text_length"]>10
    stats=client.get("/api/dashboard/stats").json(); assert stats["documents"]==1

def test_ai_unconfigured_returns_clear_error(client):
    up=client.post("/api/documents/upload",files={"file":("lesson.txt",b"Photosynthesis converts light energy into chemical energy and supports plant growth.","text/plain")})
    r=client.post(f"/api/documents/{up.json()['id']}/summaries",json={"length":"Short"})
    assert r.status_code==503 and "OPENAI_API_KEY" in r.json()["detail"]

def test_quiz_does_not_leak_answer_before_submit(client):
    db=SessionLocal()
    doc=Document(title="Test",subject="Science",description="",original_filename="x.txt",stored_filename="none.txt",file_type="txt",file_size=1,extracted_text="test",page_count=1)
    db.add(doc); db.flush(); quiz=Quiz(document_id=doc.id,title="Test quiz",difficulty="Easy"); db.add(quiz); db.flush()
    db.add(QuizQuestion(quiz_id=quiz.id,prompt="2 + 2?",question_type="multiple_choice",options=["3","4"],correct_answer="4",explanation="Addition",topic="Math")); db.commit(); qid=quiz.id; db.close()
    result=client.get(f"/api/quizzes/{qid}"); assert result.status_code==200
    assert "correct_answer" not in result.json()["questions"][0]
    assert "explanation" not in result.json()["questions"][0]
    submitted=client.post(f"/api/quizzes/{qid}/submit",json={"answers":{str(result.json()["questions"][0]["id"]):"4"}})
    assert submitted.status_code==200 and submitted.json()["percentage"]==100
