from fastapi import APIRouter
from backend.app.api.dashboard import router as dashboard_router
from backend.app.api.applicants import router as applicants_router
from backend.app.api.products import router as products_router
from backend.app.api.quotes import router as quotes_router
from backend.app.api.underwriting import router as underwriting_router
from backend.app.api.policies import router as policies_router
from backend.app.api.endorsements import router as endorsements_router
from backend.app.api.renewals import router as renewals_router
from backend.app.api.anomalies import router as anomalies_router
from backend.app.api.admin import router as admin_router
from backend.app.api.exports import router as exports_router

api_router = APIRouter()
api_router.include_router(dashboard_router)
api_router.include_router(applicants_router)
api_router.include_router(products_router)
api_router.include_router(quotes_router)
api_router.include_router(underwriting_router)
api_router.include_router(policies_router)
api_router.include_router(endorsements_router)
api_router.include_router(renewals_router)
api_router.include_router(anomalies_router)
api_router.include_router(admin_router)
api_router.include_router(exports_router)
