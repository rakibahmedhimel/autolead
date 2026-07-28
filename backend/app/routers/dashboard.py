from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.auth.security import get_current_user, require_admin
from backend.app.database import get_db
from backend.app.models.company import Company
from backend.app.models.job import Job
from backend.app.models.project import Project
from backend.app.models.spreadsheet import CreditLedger, SpreadsheetJob, SpreadsheetRow
from backend.app.models.user import User

router = APIRouter(tags=["Dashboards"])


@router.get("/dashboard")
def user_dashboard(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    statuses = dict(
        db.query(Job.status, func.count(Job.id))
        .filter(Job.user_id == user.id)
        .group_by(Job.status)
        .all()
    )
    company_count = (
        db.query(func.count(Company.id))
        .join(Job)
        .filter(Job.user_id == user.id)
        .scalar()
        or 0
    )
    project_count = (
        db.query(func.count(Project.id)).filter(Project.user_id == user.id).scalar()
        or 0
    )
    job_count = (
        db.query(func.count(Job.id)).filter(Job.user_id == user.id).scalar() or 0
    )
    credits = (
        db.query(func.count(CreditLedger.id))
        .filter(CreditLedger.user_id == user.id)
        .scalar()
        or 0
    )
    recent_projects = (
        db.query(Project)
        .filter(Project.user_id == user.id)
        .order_by(Project.created_at.desc())
        .limit(5)
        .all()
    )
    recent_jobs = (
        db.query(Job)
        .filter(Job.user_id == user.id)
        .order_by(Job.created_at.desc())
        .limit(5)
        .all()
    )
    return {
        "user": {"name": user.name, "is_admin": user.is_admin},
        "total_projects": project_count,
        "total_jobs": job_count,
        "completed_jobs": statuses.get("completed", 0),
        "processing_jobs": statuses.get("processing", 0),
        "failed_jobs": statuses.get("failed", 0),
        "companies": company_count,
        "credits_used": credits,
        "recent_projects": recent_projects,
        "recent_jobs": recent_jobs,
        "jobs_by_status": statuses,
    }


@router.get("/admin/dashboard")
def admin_dashboard(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    total_users = db.query(User).count()
    usage = (
        db.query(
            User,
            func.count(func.distinct(Project.id)),
            func.count(func.distinct(Job.id)),
            func.count(func.distinct(Company.id)),
            func.count(func.distinct(CreditLedger.id)),
        )
        .outerjoin(Project, Project.user_id == User.id)
        .outerjoin(Job, Job.user_id == User.id)
        .outerjoin(Company, Company.job_id == Job.id)
        .outerjoin(CreditLedger, CreditLedger.user_id == User.id)
        .group_by(User.id)
        .order_by(User.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    users = [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "created_at": u.created_at,
            "projects": p,
            "jobs": j,
            "companies": c,
            "credits_used": cr,
            "last_activity_at": u.last_activity_at,
            "is_active": u.is_active,
        }
        for u, p, j, c, cr in usage
    ]
    return {
        "total_users": total_users,
        "total_projects": db.query(Project).count(),
        "total_jobs": db.query(Job).count(),
        "total_companies": db.query(Company).count(),
        "total_spreadsheet_rows": db.query(SpreadsheetRow).count(),
        "credits_used": db.query(CreditLedger).count(),
        "jobs_by_status": dict(
            db.query(Job.status, func.count(Job.id)).group_by(Job.status).all()
        ),
        "jobs_by_tool": dict(
            db.query(Job.tool_type, func.count(Job.id)).group_by(Job.tool_type).all()
        ),
        "users": users,
        "page": page,
        "limit": limit,
    }


@router.get("/admin/users/{user_id}")
def admin_user_detail(
    user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": target.id,
        "name": target.name,
        "email": target.email,
        "created_at": target.created_at,
        "last_activity_at": target.last_activity_at,
        "is_active": target.is_active,
        "projects": db.query(Project).filter(Project.user_id == target.id).count(),
        "jobs": db.query(Job).filter(Job.user_id == target.id).count(),
        "companies": db.query(Company)
        .join(Job)
        .filter(Job.user_id == target.id)
        .count(),
        "credits_used": db.query(CreditLedger)
        .filter(CreditLedger.user_id == target.id)
        .count(),
    }
