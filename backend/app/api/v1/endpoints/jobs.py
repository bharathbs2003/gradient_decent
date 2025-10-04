"""Job management endpoints"""
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def list_jobs():
    return {"message": "Job endpoints - implementation in progress"}