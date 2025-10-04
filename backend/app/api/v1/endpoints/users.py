"""User management endpoints"""
from fastapi import APIRouter
router = APIRouter()

@router.get("/me")
async def get_current_user_info():
    return {"message": "User endpoints - implementation in progress"}