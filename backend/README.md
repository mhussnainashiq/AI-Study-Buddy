# AI Study Buddy Backend

## Requirements
- Python 3.11+
- Optional: OpenAI API key for live AI features
- Optional OCR: Tesseract OCR installed on the OS and `OCR_ENABLED=true`

## Windows PowerShell
```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and set OPENAI_API_KEY
uvicorn app.main:app --reload
```

## macOS/Linux
```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

The SQLite database is initialized automatically on first startup. This starter uses `create_all`; use Alembic migrations before production schema changes.

## OCR setup
Install Tesseract OCR using your operating system's package manager or official installer, ensure `tesseract` is on PATH, then set `OCR_ENABLED=true`. OCR is attempted only when a PDF has little extractable text.

## Tests
```bash
pytest -q
```
Tests use local SQLite and do not call a paid AI API. AI-dependent routes return HTTP 503 with setup guidance when no key is configured.
