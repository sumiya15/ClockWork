from fastapi import APIRouter
from .health import router as health_router
from ..modules.auth.routes import router as auth_router
from ..modules.institutions.routes import router as institutions_router
from ..modules.obligations.routes import router as obligations_router
from ..modules.rules.routes import router as rules_router

router = APIRouter()
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(institutions_router)
router.include_router(obligations_router)
router.include_router(rules_router)
