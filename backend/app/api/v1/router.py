from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as projects_router
from app.api.v1.documents import router as documents_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.findings import router as findings_router
from app.api.v1.checklist import router as checklist_router
from app.api.v1.reports import router as reports_router
from app.api.v1.jurisdictions import router as jurisdictions_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(documents_router)
api_router.include_router(analysis_router)
api_router.include_router(findings_router)
api_router.include_router(checklist_router)
api_router.include_router(reports_router)
api_router.include_router(jurisdictions_router)
