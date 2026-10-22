"""FastAPI application entry point."""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.database import check_database_connection

settings = get_settings()
app = FastAPI(title="Quiz Assessment Platform API", version="0.1.0", description="Backend API for the Quiz Assessment Platform.")

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Confirm that the API and its configured database are available."""
    try:
        check_database_connection()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database connection is unavailable.") from error
    return {"status": "ok", "database": "connected"}
