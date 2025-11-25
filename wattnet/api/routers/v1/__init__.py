from fastapi import APIRouter
from fastapi_versioning import versioned_api_route

from wattnet.api.routers.v1.exports import router as exports_router
from wattnet.api.routers.v1.factors import router as factors_router
from wattnet.api.routers.v1.flow_share import router as flow_share_router
from wattnet.api.routers.v1.footprint_share import router as footprint_share_router
from wattnet.api.routers.v1.footprints import router as footprints_router
from wattnet.api.routers.v1.generation import router as generation_router
from wattnet.api.routers.v1.imports import router as imports_router
from wattnet.api.routers.v1.mix_share import router as mix_share_router
from wattnet.api.routers.v1.status import router as status_router

api_router_v1 = APIRouter(route_class=versioned_api_route(1))

# Incluir todos los routers de v1

# Energy-related endpoints
api_router_v1.include_router(
    generation_router, prefix="/generation", tags=["Generation"]
)
api_router_v1.include_router(imports_router, prefix="/imports", tags=["Imports"])
api_router_v1.include_router(exports_router, prefix="/exports", tags=["Exports"])

# Environmental-related endpoints
api_router_v1.include_router(
    footprints_router, prefix="/footprints", tags=["Footprints"]
)

# Shares-related endpoints
api_router_v1.include_router(
    flow_share_router, prefix="/flow_share", tags=["Flow Share"]
)
api_router_v1.include_router(mix_share_router, prefix="/mix_share", tags=["Mix Share"])
api_router_v1.include_router(
    footprint_share_router, prefix="/footprint_share", tags=["Footprint Share"]
)

# Factor-related endpoints
api_router_v1.include_router(factors_router, prefix="/factors", tags=["Factors"])

# Status endpoints
api_router_v1.include_router(status_router, prefix="/status", tags=["Status"])
