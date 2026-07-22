from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import Query
from math import ceil

from backend.app.database import get_db
from backend.app.models.project import Project
from backend.app.models.job import Job
from backend.app.models.company import Company
from backend.app.schemas.project import (
    ProjectCreate,
    ProjectResponse
)


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.post("/")
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db)
):

    project = Project(
        name=data.name,
        description=data.description
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project

@router.get("/")
def get_projects(
    db: Session = Depends(get_db)
):

    projects = db.query(Project).all()

    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        return {
            "error": "Project not found"
        }

    return project

@router.get("/{project_id}/companies")
def get_project_companies(
    project_id: int,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        return {
            "error": "Project not found"
        }

    total = (
        db.query(Company)
        .join(Job)
        .filter(Job.project_id == project_id)
        .count()
    )

    companies = (
        db.query(Company)
        .join(Job)
        .filter(Job.project_id == project_id)
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": ceil(total / limit) if total else 0,
        "companies": companies
    }