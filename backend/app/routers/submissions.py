from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from backend.app.auth.security import get_current_user, require_admin
from backend.app.database import get_db
from backend.app.models.submission import ContactSubmission, ToolRequest
from backend.app.models.user import User

router = APIRouter(tags=["Submissions"])


class ContactInput(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    subject: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=10, max_length=5000)
    website: str = ""


class ToolRequestInput(BaseModel):
    tool_name: str = Field(min_length=2, max_length=150)
    business_problem: str = Field(min_length=10, max_length=5000)
    desired_input: str = Field(min_length=2, max_length=2000)
    desired_output: str = Field(min_length=2, max_length=2000)
    additional_details: str | None = None
    contact_preference: str | None = None


@router.post("/contact", status_code=201)
def contact(data: ContactInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if data.website:
        return {"message": "Thank you."}
    recent = db.query(ContactSubmission).filter(
        ContactSubmission.user_id == user.id,
        ContactSubmission.created_at > datetime.utcnow() - timedelta(minutes=1)).count()
    if recent >= 3:
        raise HTTPException(status_code=429, detail="Please wait before sending another message.")
    db.add(ContactSubmission(user_id=user.id, name=data.name.strip(), email=str(data.email).lower(),
                             subject=data.subject.strip(), message=data.message.strip()))
    db.commit()
    return {"message": "Your message has been received."}


@router.post("/tool-requests", status_code=201)
def request_tool(data: ToolRequestInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    request = ToolRequest(user_id=user.id, **data.model_dump(), status="new")
    db.add(request); db.commit()
    return {"message": "Your tool request has been submitted.", "id": request.id}


@router.get("/admin/contact-submissions")
def contacts(page: int = Query(1, ge=1), db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(ContactSubmission).order_by(ContactSubmission.created_at.desc()).offset((page - 1) * 20).limit(20).all()


@router.get("/admin/tool-requests")
def requests(page: int = Query(1, ge=1), db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(ToolRequest).order_by(ToolRequest.created_at.desc()).offset((page - 1) * 20).limit(20).all()
