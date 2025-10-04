"""Media file endpoints"""
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def list_media():
    return {"message": "Media endpoints - implementation in progress"}