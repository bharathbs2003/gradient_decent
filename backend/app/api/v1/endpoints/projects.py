"""Project management endpoints"""
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def list_projects():
    return {"message": "Project endpoints - implementation in progress"}