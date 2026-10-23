# AI Study Buddy

An AI-powered study assistant built with React, Vite, Tailwind CSS, FastAPI, SQLAlchemy, SQLite, and the OpenAI API. Upload PDF/DOCX/TXT study material, generate summaries, review flashcards, practice quizzes, and ask contextual questions.

## Features
- Responsive React interface with dashboard, upload, summaries, flashcards, quizzes, tutor, library, and progress pages
- PDF, DOCX, and TXT extraction; configurable upload limit; optional OCR for scanned PDFs
- AI summaries, flashcards, quizzes, tutoring, and document Q&A using an isolated AI service
- SQLite persistence for resources, attempts, activities, and progress
- Keyword-based retrieval with chunking; answers indicate when document context is used
- Quiz answer keys are not exposed until submission; short-answer grading is explicitly an AI estimate
- Pytest coverage for upload validation, persistence, missing AI configuration, and quiz answer protection

## Architecture
`frontend/` is the Vite React SPA. `backend/` is the FastAPI REST API. The API stores metadata and extracted text in SQLite, and stores original files under `uploads/` with randomized names. AI provider configuration is loaded from `backend/.env`.

## Prerequisites
- Python 3.11+
- Node.js LTS and npm
- An OpenAI API key for AI generation (optional for upload/dashboard/local development)

## Backend setup
### Windows PowerShell
```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit backend/.env and set OPENAI_API_KEY=your_key
uvicorn app.main:app --reload
```
### macOS/Linux
```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit backend/.env and set OPENAI_API_KEY=your_key
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs. Health: http://127.0.0.1:8000/api/health.

## Frontend setup
Open a second terminal:
```bash
cd frontend
npm install
```
Windows PowerShell equivalent is the same commands. Then:
```bash
npm run dev
```
Visit http://localhost:5173. Configure `VITE_API_URL` in `frontend/.env` only if your API is not at `http://localhost:8000`.

## OCR for scanned PDFs
Install Tesseract OCR and make sure its executable is available on PATH. Set `OCR_ENABLED=true` in `backend/.env`. OCR is attempted only when extracted PDF text is almost empty. If Tesseract is missing, the API reports an actionable error.

## Database
SQLite is initialized with SQLAlchemy `create_all` on API startup. Local database: `backend/study_buddy.db`. Back up carefully; it contains extracted text. For production, add Alembic migrations and managed database storage.

## Tests
From `backend/` with its virtual environment active:
```bash
pytest -q
```
Tests do not make paid AI calls. They validate missing-key handling and quiz grading with local fixtures.

## API overview
- `POST /api/documents/upload`, `GET /api/documents`, `GET /api/documents/{id}`, `GET /api/documents/{id}/text`, `DELETE /api/documents/{id}`
- `POST /api/documents/{id}/summaries`, `GET /api/documents/{id}/summaries`, `GET/DELETE /api/summaries/{id}`
- `POST /api/documents/{id}/flashcards`, `GET /api/flashcards/{deck_id}`, `PATCH /api/flashcards/{deck_id}/cards/{card_id}`, `DELETE /api/flashcards/{deck_id}`
- `POST /api/documents/{id}/quizzes`, `GET /api/quizzes/{id}`, `POST /api/quizzes/{id}/submit`, `GET /api/quizzes/{id}/results`, `GET /api/quiz-attempts`
- `POST /api/tutor/ask`, `POST /api/tutor/document-question`
- `GET /api/dashboard/stats`, `GET /api/progress`, `GET /api/library`

## Security and privacy notes
- Never commit `.env`, the SQLite database, or uploaded private documents.
- Uploads are size/type checked, stored under randomized server-side names, and never executed.
- Document text is treated as untrusted input in AI prompts.
- This starter is a **single-user local application**. Authentication and per-user authorization are not implemented yet; do not deploy publicly or use it for multiple users until authentication, ownership checks, rate limiting, CSRF/deployment controls, and stronger upload scanning are added.
- Keyword retrieval is an initial RAG implementation, not vector search. OCR depends on external Tesseract installation.
- Add Alembic migrations, request rate limits, structured logging, and production secrets management before commercial deployment.

## Troubleshooting
- `OPENAI_API_KEY` not configured: AI endpoints return 503; set the key in `backend/.env` and restart Uvicorn.
- Frontend cannot reach API: verify backend is running at port 8000 and `VITE_API_URL` is correct.
- `npm` not recognized on Windows: reinstall Node.js LTS, enable PATH option, close and reopen PowerShell, then run `node -v` and `npm -v`.
- PDF has no readable text: install Tesseract and enable OCR, or upload a text-based PDF.
- SQLite locked: stop duplicate server/test processes and retry.

## Screenshots
Add screenshots of the running dashboard, upload workflow, flashcards, and quiz results here after local launch.

## Future improvements
Authentication and per-user isolation, vector embeddings, document citations with page-level chunk metadata, streaming AI responses, spaced repetition, export to PDF/Anki, Alembic migrations, and deployment automation.
