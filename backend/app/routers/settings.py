import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.auth.security import get_current_user
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.user_api_key import UserApiKey
from backend.app.services.api_key_service import decrypt_key, encrypt_key, masked_key

router = APIRouter(prefix="/settings", tags=["Settings"])


class ApiKeyInput(BaseModel):
    api_key: str = Field(min_length=8, max_length=1000)


@router.get("/firecrawl-key")
def key_status(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(UserApiKey).filter(UserApiKey.user_id == user.id, UserApiKey.provider == "firecrawl").first()
    return {"configured": bool(row), "masked_key": masked_key(row.key_suffix) if row else None,
            "source": "user" if row else "system fallback"}


@router.put("/firecrawl-key")
def save_key(data: ApiKeyInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    value = data.api_key.strip()
    row = db.query(UserApiKey).filter(UserApiKey.user_id == user.id, UserApiKey.provider == "firecrawl").first()
    if row:
        row.encrypted_key, row.key_suffix = encrypt_key(value), value[-4:]
    else:
        row = UserApiKey(user_id=user.id, provider="firecrawl",
                         encrypted_key=encrypt_key(value), key_suffix=value[-4:])
        db.add(row)
    db.commit()
    return {"configured": True, "masked_key": masked_key(row.key_suffix), "source": "user"}


@router.delete("/firecrawl-key", status_code=204)
def delete_key(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db.query(UserApiKey).filter(UserApiKey.user_id == user.id, UserApiKey.provider == "firecrawl").delete()
    db.commit()


@router.post("/firecrawl-key/test")
def test_key(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(UserApiKey).filter(UserApiKey.user_id == user.id, UserApiKey.provider == "firecrawl").first()
    if not row:
        raise HTTPException(status_code=404, detail="No user Firecrawl key is configured")
    try:
        response = requests.get("https://api.firecrawl.dev/v2/team/credit-usage",
                                headers={"Authorization": f"Bearer {decrypt_key(row.encrypted_key)}"}, timeout=15)
        return {"valid": response.status_code < 400}
    except requests.RequestException:
        return {"valid": False}
