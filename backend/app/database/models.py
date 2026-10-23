from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, Boolean, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base

def now(): return datetime.now(timezone.utc)

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    subject: Mapped[str] = mapped_column(String(120), default="General")
    description: Mapped[str] = mapped_column(Text, default="")
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_filename: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(12))
    file_size: Mapped[int] = mapped_column(Integer)
    extracted_text: Mapped[str] = mapped_column(Text)
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    summaries: Mapped[list["Summary"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    decks: Mapped[list["FlashcardDeck"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    quizzes: Mapped[list["Quiz"]] = relationship(back_populates="document", cascade="all, delete-orphan")

class Summary(Base):
    __tablename__ = "summaries"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    length: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    document: Mapped[Document] = relationship(back_populates="summaries")

class FlashcardDeck(Base):
    __tablename__ = "flashcard_decks"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    difficulty: Mapped[str] = mapped_column(String(20), default="Medium")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    document: Mapped[Document] = relationship(back_populates="decks")
    cards: Mapped[list["Flashcard"]] = relationship(back_populates="deck", cascade="all, delete-orphan")

class Flashcard(Base):
    __tablename__ = "flashcards"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    deck_id: Mapped[int] = mapped_column(ForeignKey("flashcard_decks.id", ondelete="CASCADE"), index=True)
    front: Mapped[str] = mapped_column(Text)
    back: Mapped[str] = mapped_column(Text)
    topic: Mapped[str] = mapped_column(String(120), default="General")
    difficulty: Mapped[str] = mapped_column(String(20), default="Medium")
    status: Mapped[str] = mapped_column(String(20), default="new")
    deck: Mapped[FlashcardDeck] = relationship(back_populates="cards")

class Quiz(Base):
    __tablename__ = "quizzes"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    difficulty: Mapped[str] = mapped_column(String(20), default="Medium")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    document: Mapped[Document] = relationship(back_populates="quizzes")
    questions: Mapped[list["QuizQuestion"]] = relationship(back_populates="quiz", cascade="all, delete-orphan", order_by="QuizQuestion.id")
    attempts: Mapped[list["QuizAttempt"]] = relationship(back_populates="quiz", cascade="all, delete-orphan")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    question_type: Mapped[str] = mapped_column(String(20), default="multiple_choice")
    options: Mapped[list] = mapped_column(JSON, default=list)
    correct_answer: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text, default="")
    topic: Mapped[str] = mapped_column(String(120), default="General")
    quiz: Mapped[Quiz] = relationship(back_populates="questions")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True)
    score: Mapped[float] = mapped_column(Float)
    total: Mapped[int] = mapped_column(Integer)
    percentage: Mapped[float] = mapped_column(Float)
    answers: Mapped[dict] = mapped_column(JSON, default=dict)
    feedback: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    quiz: Mapped[Quiz] = relationship(back_populates="attempts")

class StudyActivity(Base):
    __tablename__ = "study_activities"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    activity_type: Mapped[str] = mapped_column(String(40), index=True)
    resource_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    detail: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
