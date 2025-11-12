from fastapi import APIRouter
from fastapi_versioning import versioned_api_route

from wattnet.api.routers.v1.factors import router as factors_router
from wattnet.api.routers.v1.footprints import router as footprints_router
from wattnet.api.routers.v1.status import router as status_router

# from wattnet.api.routers.v1.zones import router as zones_router

api_router = APIRouter(route_class=versioned_api_route(1))

# Incluir todos los routers de v1
# api_router.include_router(zones_router, prefix="/zones", tags=["Zones"])
api_router.include_router(footprints_router, prefix="/footprints", tags=["Footprints"])
api_router.include_router(factors_router, prefix="/factors", tags=["Factors"])
api_router.include_router(status_router, prefix="/status", tags=["Status"])
