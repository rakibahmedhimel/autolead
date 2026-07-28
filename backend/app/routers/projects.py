import io
import re
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.auth.security import get_current_user
from backend.app.database import get_db
from backend.app.models.company import Company
from backend.app.models.job import Job
from backend.app.models.project import Project
from backend.app.models.user import User
from backend.app.schemas.project import ProjectCreate, ProjectResponse
from backend.app.services.company_export_service import (
    company_export_headers,
    company_export_row,
    safe_filename,
)
from backend.app.services.spreadsheet_service import workbook_bytes

router = APIRouter(prefix="/projects", tags=["Projects"])


def normalize_project_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip()).casefold()


def owned_project(db: Session, project_id: int, user: User) -> Project:
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", status_code=201)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    name = re.sub(r"\s+", " ", data.name.strip())
    normalized = normalize_project_name(name)
    if not normalized:
        raise HTTPException(status_code=422, detail="Project name cannot be blank")
    project = Project(
        user_id=user.id,
        name=name,
        normalized_name=normalized,
        description=data.description,
    )
    db.add(project)
    try:
        db.commit()
        db.refresh(project)
        return project
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(Project)
            .filter(Project.user_id == user.id, Project.normalized_name == normalized)
            .first()
        )
        raise HTTPException(
            status_code=409,
            detail={
                "message": "A project with this name already exists.",
                "existing_project_id": existing.id if existing else None,
            },
        )


@router.get("/")
def get_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(Project)
        .filter(Project.user_id == user.id)
        .order_by(Project.created_at.desc())
        .all()
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return owned_project(db, project_id, user)


@router.get("/{project_id}/companies/download.xlsx")
def download_project_companies(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.user_id == user.id,
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    companies = (
        db.query(Company)
        .join(Job, Company.job_id == Job.id)
        .filter(
            Job.project_id == project_id,
            Job.user_id == user.id,
        )
        .order_by(Job.created_at.desc(), Company.id)
        .all()
    )

    headers = company_export_headers()
    rows = [company_export_row(company) for company in companies]

    filename = f"AutoLead_Project_{project.id}_{safe_filename(project.name)}.xlsx"

    workbook = workbook_bytes(
        [
            (
                project.name[:31] or f"Project {project.id}",
                headers,
                rows,
            )
        ]
    )

    return StreamingResponse(
        io.BytesIO(workbook),
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={"Content-Disposition": (f'attachment; filename="{filename}"')},
    )


@router.get("/{project_id}/companies")
def get_project_companies(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    owned_project(db, project_id, user)
    query = (
        db.query(Company)
        .join(Job)
        .filter(Job.project_id == project_id, Job.user_id == user.id)
    )
    total = query.count()
    companies = (
        query.order_by(Company.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": ceil(total / limit) if total else 0,
        "companies": companies,
    }


@router.get("/{project_id}/jobs")
def get_project_jobs(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: str | None = None,
):
    owned_project(db, project_id, user)
    query = db.query(Job).filter(Job.project_id == project_id, Job.user_id == user.id)
    if status:
        query = query.filter(Job.status == status)
    total = query.count()
    jobs = (
        query.order_by(Job.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": ceil(total / limit) if total else 0,
        "jobs": jobs,
    }
