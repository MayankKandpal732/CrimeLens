from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv
from pathlib import Path
from .db import (
    create_report, 
    fetch_report, 
    update_report_status, 
    list_reports,
    get_user_by_email,
    get_departments
)
# Import RAG sync lazily inside endpoint to avoid heavy deps at import time

app = FastAPI(title="CrimeLens API", description="Issue-reporting system")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')

class ReportCreateRequest(BaseModel):
    reportId: str
    type: str  # EMERGENCY or NON_EMERGENCY
    title: str
    description: str
    specificType: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image: Optional[str] = None
    isAnonymous: bool = True
    reporterName: Optional[str] = None
    reporterEmail: Optional[str] = None
    reporterPhone: Optional[str] = None
    reporterId: Optional[int] = None
    departmentId: Optional[int] = None
    departmentName: Optional[str] = None

class ReportUpdateRequest(BaseModel):
    status: str  # PENDING, IN_PROGRESS, RESOLVED, DISMISSED

@app.post("/api/reports/create")
async def create_report_endpoint(report_data: ReportCreateRequest):
    """Create a new report - matches frontend API"""
    try:
        payload = report_data.dict()
        report_id = create_report(payload)
        try:
            from .rag import index_issue
            title = payload.get("title") or ""
            description = payload.get("description") or ""
            location = payload.get("location") or ""
            # Index into Qdrant (best-effort; errors ignored)
            if title and description:
                index_issue(report_id, title, description, location)
        except Exception:
            pass
        return {
            "success": True,
            "reportId": report_id,
            "message": "Report created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports")
async def list_reports_endpoint(
    status: Optional[str] = None,
    type: Optional[str] = None,
    reporterUserId: Optional[int] = None,
    reporterEmail: Optional[str] = None,
    departmentName: Optional[str] = None
):
    """List reports with filters - matches frontend API"""
    try:
        filters = {}
        if status:
            filters["status"] = status
        if type:
            filters["type"] = type
        if reporterUserId:
            filters["reporterUserId"] = reporterUserId
        if reporterEmail:
            filters["reporterEmail"] = reporterEmail
        if departmentName:
            filters["departmentName"] = departmentName
        
        reports = list_reports(filters)
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/{report_id}")
async def get_report_endpoint(report_id: str):
    """Get specific report - matches frontend API"""
    try:
        report = fetch_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/reports/{report_id}")
async def update_report_endpoint(report_id: str, update_data: ReportUpdateRequest):
    """Update report status - matches frontend API"""
    try:
        success = update_report_status(report_id, update_data.status)
        if not success:
            raise HTTPException(status_code=404, detail="Report not found")
        return {"success": True, "message": "Report updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/departments")
async def get_departments_endpoint():
    """Get all departments - matches frontend API"""
    try:
        departments = get_departments()
        return departments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync-qdrant")
async def sync_qdrant_endpoint():
    """Sync database reports to Qdrant for vector search"""
    try:
        from .rag import sync_reports_to_qdrant
        result = await sync_reports_to_qdrant()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "CrimeLens API is running"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "CrimeLens API",
        "version": "1.0.0",
        "endpoints": ["/api/reports/create", "/api/reports", "/api/departments", "/api/sync-qdrant", "/", "/health"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

