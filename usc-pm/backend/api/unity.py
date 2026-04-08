from fastapi import APIRouter, Depends
from pydantic import BaseModel
from .. import db
from ..auth_jwt import require_user

router = APIRouter(prefix="/api/unity", tags=["unity"])


class UnityIn(BaseModel):
    entry: str


@router.get("")
def list_entries(user_id: int = Depends(require_user)):
    return db.list_unity(user_id, limit=100)


@router.post("")
def add_entry(payload: UnityIn, user_id: int = Depends(require_user)):
    eid = db.add_unity_entry(user_id, payload.entry)
    return {"id": eid}
