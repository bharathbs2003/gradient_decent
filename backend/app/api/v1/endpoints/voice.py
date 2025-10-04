"""Voice synthesis endpoints"""
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def list_voices():
    return {"message": "Voice endpoints - implementation in progress"}