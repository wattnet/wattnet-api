"""API routers for version 1 of the wattnet API."""

from enum import Enum
from typing import List, Union

from fastapi import APIRouter
from fastapi_versioning import versioned_api_route

from wattnet.api.routers.v1.exports import router as exports_router
from wattnet.api.routers.v1.factors import router as factors_router
from wattnet.api.routers.v1.flow_share import router as flow_share_router
from wattnet.api.routers.v1.footprint_share import router as footprint_share_router
from wattnet.api.routers.v1.footprints import router as footprints_router
from wattnet.api.routers.v1.generation import router as generation_router
from wattnet.api.routers.v1.impact_share import router as impact_share_router
from wattnet.api.routers.v1.impacts import router as impacts_router
from wattnet.api.routers.v1.imports import router as imports_router
from wattnet.api.routers.v1.load import router as load_router
from wattnet.api.routers.v1.mix_share import router as mix_share_router
from wattnet.api.routers.v1.scores import router as scores_router
from wattnet.api.routers.v1.status import router as status_router

api_router_v1 = APIRouter(route_class=versioned_api_route(1))

# TAGS:
TagType = Union[str, Enum]

energy_metrics_tags: List[TagType] = ["Energy Metrics"]
environmental_metrics_tags: List[TagType] = ["Environmental Metrics"]
shares_metrics_tags: List[TagType] = ["Shares Metrics"]
factors_tags: List[TagType] = ["Factors"]
status_tags: List[TagType] = ["Status"]

# Incluir todos los routers de v1

# Energy-related endpoints
api_router_v1.include_router(
    generation_router, prefix="/generation", tags=energy_metrics_tags
)
api_router_v1.include_router(load_router, prefix="/load", tags=energy_metrics_tags)
api_router_v1.include_router(
    imports_router, prefix="/imports", tags=energy_metrics_tags
)
api_router_v1.include_router(
    exports_router, prefix="/exports", tags=energy_metrics_tags
)

# Environmental-related endpoints
api_router_v1.include_router(
    footprints_router, prefix="/footprints", tags=environmental_metrics_tags
)
api_router_v1.include_router(
    impacts_router, prefix="/impacts", tags=environmental_metrics_tags
)
api_router_v1.include_router(
    scores_router, prefix="/green-score", tags=environmental_metrics_tags
)

# Shares-related endpoints
api_router_v1.include_router(
    flow_share_router, prefix="/flow-share", tags=shares_metrics_tags
)
api_router_v1.include_router(
    mix_share_router, prefix="/mix-share", tags=shares_metrics_tags
)
api_router_v1.include_router(
    footprint_share_router, prefix="/footprint-share", tags=shares_metrics_tags
)
api_router_v1.include_router(
    impact_share_router, prefix="/impact-share", tags=shares_metrics_tags
)

# Factor-related endpoints
api_router_v1.include_router(factors_router, prefix="/factors", tags=factors_tags)

# Status endpoints
api_router_v1.include_router(status_router, prefix="/status", tags=status_tags)
api_router_v1.include_router(status_router, prefix="/status", tags=status_tags)
