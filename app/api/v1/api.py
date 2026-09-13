from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.mines import router as mines_router
from app.api.v1.compliance import router as compliance_router
from app.api.v1.inspections import router as inspections_router
from app.api.v1.grievances import router as grievances_router
from app.api.v1.documents import router as documents_router
from app.api.v1.audit import router as audit_router
from app.api.v1.dashboard import router as dashboard_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(mines_router)
api_router.include_router(compliance_router)
api_router.include_router(inspections_router)
api_router.include_router(grievances_router)
api_router.include_router(documents_router)
api_router.include_router(audit_router)
api_router.include_router(dashboard_router)
