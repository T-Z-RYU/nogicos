from fastapi import APIRouter, Depends
from .. import db
from ..auth_jwt import require_user

router = APIRouter(prefix="/api", tags=["macro"])


@router.get("/macro")
def macro(user_id: int = Depends(require_user)):
    return {
        "deadlines": db.list_deadlines(user_id),
        "unity": db.list_unity(user_id, limit=10),
        "pending_replies": db.list_pending_replies(user_id),
    }


@router.post("/pending/{pid}/approve")
def approve(pid: int, user_id: int = Depends(require_user)):
    db.update_pending_status(user_id, pid, "approved")
    return {"ok": True}


@router.post("/pending/{pid}/reject")
def reject(pid: int, user_id: int = Depends(require_user)):
    db.update_pending_status(user_id, pid, "rejected")
    return {"ok": True}
