import os
os.environ["DATABASE_URL"]="sqlite:///./test_study_buddy.db"
os.environ["UPLOAD_DIR"]="./test_uploads"
os.environ["OPENAI_API_KEY"]=""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import Base, engine

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    with TestClient(app) as c: yield c
