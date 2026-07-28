import csv
import io
import re
import requests
import zipfile
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.auth.security import get_current_user
from backend.app.database import get_db
from backend.app.models.project import Project
from backend.app.models.spreadsheet import CreditLedger, SpreadsheetJob, SpreadsheetRow, SpreadsheetSheet
from backend.app.models.user import User
from backend.app.services.spreadsheet_service import TARGET_FIELDS, crawl_company, parse_upload, safe_cell, workbook_bytes

router = APIRouter(prefix="/spreadsheets", tags=["Spreadsheet Enrichment"])


class MappingInput(BaseModel):
    website_column: str
    field_columns: dict[str, str]


class GoogleSheetInput(BaseModel):
    project_id: int
    url: str
    idempotency_key: str


def owned_job(db, job_id, user):
    job = db.query(SpreadsheetJob).filter(SpreadsheetJob.id == job_id, SpreadsheetJob.user_id == user.id).first()
    if not job: raise HTTPException(status_code=404, detail="Spreadsheet job not found")
    return job


@router.post("/upload", status_code=201)
async def upload(project_id: int = Form(...), file: UploadFile = File(...),
                 idempotency_key: str = Header(..., alias="Idempotency-Key"),
                 db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not db.query(Project.id).filter(Project.id == project_id, Project.user_id == user.id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    existing = db.query(SpreadsheetJob).filter(
        SpreadsheetJob.user_id == user.id, SpreadsheetJob.idempotency_key == idempotency_key).first()
    if existing: return describe(existing)
    content = await file.read()
    if len(content) > 20 * 1024 * 1024: raise HTTPException(status_code=413, detail="File exceeds 20 MB")
    try: parsed = parse_upload(file.filename or "upload", content)
    except ValueError as error: raise HTTPException(status_code=422, detail=str(error))
    job = SpreadsheetJob(user_id=user.id, project_id=project_id, idempotency_key=idempotency_key,
                         original_filename=file.filename or "upload", source_type="upload")
    db.add(job); db.flush()
    total = 0
    for position, (name, headers, rows) in enumerate(parsed):
        sheet = SpreadsheetSheet(job_id=job.id, name=name, position=position, headers=headers)
        db.add(sheet); db.flush()
        for number, values in enumerate(rows, 2):
            db.add(SpreadsheetRow(sheet_id=sheet.id, row_number=number, values=values))
            total += 1
    job.total_rows = total
    try: db.commit()
    except IntegrityError:
        db.rollback()
        return describe(db.query(SpreadsheetJob).filter(
            SpreadsheetJob.user_id == user.id, SpreadsheetJob.idempotency_key == idempotency_key).one())
    db.refresh(job); return describe(job)


@router.post("/google-sheet", status_code=201)
def google_sheet(data: GoogleSheetInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not db.query(Project.id).filter(Project.id == data.project_id, Project.user_id == user.id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    existing = db.query(SpreadsheetJob).filter(
        SpreadsheetJob.user_id == user.id, SpreadsheetJob.idempotency_key == data.idempotency_key).first()
    if existing: return describe(existing)
    match = re.fullmatch(r"https://docs\.google\.com/spreadsheets/d/([A-Za-z0-9_-]+)(?:/.*)?", data.url)
    if not match: raise HTTPException(status_code=422, detail="Use a public Google Sheets link")
    try:
        response = requests.get(f"https://docs.google.com/spreadsheets/d/{match.group(1)}/export?format=xlsx",
                                timeout=30, allow_redirects=True)
        response.raise_for_status()
        parsed = parse_upload("google-sheet.xlsx", response.content)
    except requests.RequestException:
        raise HTTPException(status_code=422, detail="The Google Sheet could not be downloaded. Confirm it is public.")
    job = SpreadsheetJob(user_id=user.id, project_id=data.project_id, idempotency_key=data.idempotency_key,
                         original_filename="Google Sheet", source_type="google_sheets")
    db.add(job); db.flush(); total = 0
    for position, (name, headers, rows) in enumerate(parsed):
        sheet = SpreadsheetSheet(job_id=job.id, name=name, position=position, headers=headers)
        db.add(sheet); db.flush()
        for number, values in enumerate(rows, 2):
            db.add(SpreadsheetRow(sheet_id=sheet.id, row_number=number, values=values)); total += 1
    job.total_rows = total; db.commit(); db.refresh(job)
    return describe(job)


def describe(job):
    return {"id": job.id, "project_id": job.project_id, "filename": job.original_filename,
            "status": job.status, "total_rows": job.total_rows, "processed_rows": job.processed_rows,
            "failed_rows": job.failed_rows, "credits_used": job.credits_used,
            "sheets": [{"name": s.name, "headers": s.headers,
                        "preview": [r.values for r in s.rows[:5]]} for s in job.sheets]}


@router.get("/{job_id}")
def detail(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return describe(owned_job(db, job_id, user))


@router.put("/{job_id}/mapping")
def mapping(job_id: int, data: MappingInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = owned_job(db, job_id, user)
    if any(field not in TARGET_FIELDS for field in data.field_columns):
        raise HTTPException(status_code=422, detail="Unsupported enrichment field")
    job.mapping = data.model_dump(); job.status = "ready"; db.commit()
    return describe(job)


@router.post("/{job_id}/enrich")
def enrich(job_id: int, limit: int = Query(5, ge=1, le=20), db: Session = Depends(get_db),
           user: User = Depends(get_current_user)):
    job = owned_job(db, job_id, user)
    if not job.mapping: raise HTTPException(status_code=422, detail="Map the website and output columns first")
    rows = db.query(SpreadsheetRow).join(SpreadsheetSheet).filter(
        SpreadsheetSheet.job_id == job.id, SpreadsheetRow.status.in_(["pending", "failed"])
    ).order_by(SpreadsheetRow.id).limit(limit).all()
    credits, failed = 0, 0
    for row in rows:
        website = row.values.get(job.mapping["website_column"])
        if not website:
            row.status = "failed"; row.error = "Website is missing"; failed += 1; db.commit(); continue
        try:
            found, evidence = crawl_company(str(website))
            values = dict(row.values)
            for field, column in job.mapping["field_columns"].items():
                if not values.get(column) and found.get(field):
                    values[column] = found[field]
                    db.add(CreditLedger(user_id=user.id, spreadsheet_job_id=job.id, row_id=row.id,
                                        field_name=field, source_url=evidence))
                    credits += 1
            row.values, row.status, row.error = values, "completed", None
            db.commit()
        except Exception as error:
            db.rollback(); row = db.query(SpreadsheetRow).filter(SpreadsheetRow.id == row.id).one()
            row.status, row.error = "failed", str(error)[:500]; failed += 1; db.commit()
    job = owned_job(db, job_id, user)
    job.processed_rows = db.query(SpreadsheetRow).join(SpreadsheetSheet).filter(
        SpreadsheetSheet.job_id == job.id, SpreadsheetRow.status == "completed").count()
    job.failed_rows = db.query(SpreadsheetRow).join(SpreadsheetSheet).filter(
        SpreadsheetSheet.job_id == job.id, SpreadsheetRow.status == "failed").count()
    job.credits_used = db.query(CreditLedger).filter(CreditLedger.spreadsheet_job_id == job.id).count()
    remaining = job.total_rows - job.processed_rows
    job.status = "completed" if remaining == 0 else "processing"; db.commit()
    return {"processed": len(rows), "failed": failed, "credits_added": credits,
            "credits_used": job.credits_used, "remaining": remaining, "status": job.status}


@router.get("/{job_id}/download.xlsx")
def download_xlsx(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = owned_job(db, job_id, user)
    sheets = [(s.name, s.headers, [r.values for r in s.rows]) for s in sorted(job.sheets, key=lambda x: x.position)]
    return StreamingResponse(io.BytesIO(workbook_bytes(sheets)),
                             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f'attachment; filename="spreadsheet-job-{job.id}.xlsx"'})


@router.get("/{job_id}/download.csv")
def download_csv(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = owned_job(db, job_id, user)
    def csv_text(sheet):
        output = io.StringIO(); writer = csv.DictWriter(output, fieldnames=sheet.headers)
        writer.writeheader()
        for row in sheet.rows: writer.writerow({key: safe_cell(row.values.get(key)) for key in sheet.headers})
        return output.getvalue()
    if len(job.sheets) == 1:
        return StreamingResponse(iter([csv_text(job.sheets[0])]), media_type="text/csv",
                                 headers={"Content-Disposition": f'attachment; filename="spreadsheet-job-{job.id}.csv"'})
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for index, sheet in enumerate(job.sheets, 1):
            safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", sheet.name) or f"sheet-{index}"
            bundle.writestr(f"{safe_name}.csv", csv_text(sheet))
    archive.seek(0)
    return StreamingResponse(archive, media_type="application/zip",
                             headers={"Content-Disposition": f'attachment; filename="spreadsheet-job-{job.id}-csv.zip"'})


@router.get("/project-export/{project_id}/download.xlsx")
def download_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not db.query(Project.id).filter(Project.id == project_id, Project.user_id == user.id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    jobs = db.query(SpreadsheetJob).filter(
        SpreadsheetJob.project_id == project_id, SpreadsheetJob.user_id == user.id
    ).order_by(SpreadsheetJob.created_at).all()
    sheets = []
    for job in jobs:
        headers = []
        rows = []
        for source in sorted(job.sheets, key=lambda item: item.position):
            for header in source.headers:
                if header not in headers: headers.append(header)
            for row in source.rows: rows.append({"source_sheet": source.name, **row.values})
        if len(job.sheets) > 1: headers = ["source_sheet", *headers]
        sheets.append((f"Job {job.id}", headers, rows))
    return StreamingResponse(io.BytesIO(workbook_bytes(sheets)), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f'attachment; filename="project-{project_id}.xlsx"'})
