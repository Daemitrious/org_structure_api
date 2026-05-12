from fastapi import APIRouter

from app.api.v1.endpoints import departments

api_router = APIRouter()
api_router.include_router(departments.router)
