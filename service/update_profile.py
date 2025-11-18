from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import BaseModel

from model.user import User


def _to_plain(obj: Any) -> Dict:
    """
    Convert a Pydantic model or dict to a plain dict.
    Keep None values so the client can explicitly clear fields.
    """
    if isinstance(obj, BaseModel):
        try:
            return obj.model_dump(exclude_unset=False)  # pydantic v2
        except AttributeError:
            return obj.dict(exclude_unset=False)        # pydantic v1
    if isinstance(obj, dict):
        return dict(obj)
    raise HTTPException(status_code=400, detail="Each address must be an object")


def _id_or_none(v) -> Optional[str]:
  
    if v is None:
        return None
    s = str(v).strip()
    if s == "" or s.lower() == "string":
        return None
    return s


def update_user_profile(db: Session, user_id: int, payload: BaseModel) -> User:
   
    try:
        user: Optional[User] = (
            db.query(User)
              .filter(User.id == user_id)
              .with_for_update()
              .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

        # --- Top-level ---
        if not hasattr(payload, "email") or getattr(payload, "email") is None:
            raise HTTPException(status_code=400, detail="Email is required")
        user.email = payload.email

        if hasattr(payload, "name"):
            user.name = payload.name
        if hasattr(payload, "phone"):
            user.phone = payload.phone

        # --- Addresses (authoritative list + auto id) ---
        if hasattr(payload, "addresses") and payload.addresses is not None:
            incoming: List[Dict] = [_to_plain(a) for a in payload.addresses]

            # Normalize and backfill existing DB addresses
            existing = list(user.addresses or [])
            changed = False
            for a in existing:
                if isinstance(a, dict):
                    norm_id = _id_or_none(a.get("id"))
                    if not norm_id:
                        a["id"] = str(uuid.uuid4())
                        changed = True
                    else:
                        a["id"] = norm_id
            if changed:
                user.addresses = existing  # persist backfilled ids

            existing_by_id: Dict[str, Dict] = {
                a["id"]: a for a in existing if isinstance(a, dict) and a.get("id")
            }

            new_list: List[Dict] = []
            for inc in incoming:
                inc_id = _id_or_none(inc.get("id"))
                if inc_id and inc_id in existing_by_id:
                    # update -> replace entire object, ensure id stays
                    inc["id"] = inc_id
                    new_list.append(inc)
                else:
                    # add -> generate id if missing/placeholder
                    if not inc_id:
                        inc["id"] = str(uuid.uuid4())
                    else:
                        inc["id"] = inc_id
                    new_list.append(inc)

            # Delete: rebuild list from incoming only
            user.addresses = new_list

        db.add(user)
        db.commit()
        db.refresh(user)

        if getattr(user, "addresses", None) is None:
            user.addresses = []

        return user

    except IntegrityError as ie:
        try:
            db.rollback()
        except Exception:
            pass
        raise ie

    except HTTPException:
        try:
            db.rollback()
        except Exception:
            pass
        raise

    except SQLAlchemyError as sqle:
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail="Database error while updating profile") from sqle

    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail="Unexpected error while updating profile")
