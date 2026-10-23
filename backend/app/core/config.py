from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    app_name: str = "AI Study Buddy API"
    database_url: str = "sqlite:///./study_buddy.db"
    upload_dir: str = "../uploads"
    max_upload_mb: int = 15
    frontend_origin: str = "http://localhost:5173"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ocr_enabled: bool = False
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

def upload_path() -> Path:
    path = Path(settings.upload_dir)
    if not path.is_absolute():
        path = (Path(__file__).resolve().parents[2] / path).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path
