from fastapi import FastAPI

from app.api.v1.router import api_router
from app.config import get_settings
from app.logging_config import configure_logging

configure_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="API for organization departments and employees tree.",
)

app.include_router(api_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
