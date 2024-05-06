from datetime import datetime

from fastapi import APIRouter, HTTPException

from src.config.db.mongo_management.mongo_manager import waitlist_collection

router = APIRouter(prefix="/v1")

@router.post("/add")
async def add_to_waitlist(email: str):
    current_time = datetime.now()

    if waitlist_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already in the waitlist")

    waitlist_collection.insert_one({"email": email, "date_added": current_time})

    return {"message": "Email added to waitlist successfully"}
