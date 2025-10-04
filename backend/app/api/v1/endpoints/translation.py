"""Translation endpoints"""
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def list_translations():
    return {"message": "Translation endpoints - implementation in progress"}