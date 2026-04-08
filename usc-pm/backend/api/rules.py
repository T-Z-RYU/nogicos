from fastapi import APIRouter, Depends
from pydantic import BaseModel
from .. import db
from ..auth_jwt import require_user

router = APIRouter(prefix="/api/rules", tags=["rules"])


class RuleIn(BaseModel):
    scenario: str
    source_filter: str | None = None
    template: str
    auto_send: bool = False


@router.get("")
def list_rules(user_id: int = Depends(require_user)):
    return db.list_rules(user_id)


@router.post("")
def create_rule(payload: RuleIn, user_id: int = Depends(require_user)):
    rid = db.add_rule(user_id, payload.scenario, payload.source_filter,
                      payload.template, payload.auto_send)
    return {"id": rid}


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, user_id: int = Depends(require_user)):
    db.delete_rule(user_id, rule_id)
    return {"ok": True}
