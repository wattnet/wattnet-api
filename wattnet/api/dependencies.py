"""Dependency management for the wattnet API application."""

from wattnet.storage.repository import MetricsRepository

from wattnet.api.service.exports import ExportService
from wattnet.api.service.factors import FactorService
from wattnet.api.service.flow_share import FlowShareService
from wattnet.api.service.footprint_share import FootprintShareService
from wattnet.api.service.footprints import FootprintService
from wattnet.api.service.generation import GenerationService
from wattnet.api.service.impact_share import ImpactShareService
from wattnet.api.service.impacts import ImpactService
from wattnet.api.service.imports import ImportService
from wattnet.api.service.load import LoadService
from wattnet.api.service.mix_share import MixShareService
from wattnet.api.service.mix import MixService
from wattnet.api.service.scores import ScoreService
from wattnet.api.service.zones import ZoneService
from wattnet.api.settings import settings

# Create a MetricsRepository instance
metrics_repo = MetricsRepository()

# Create Service instances
generation_service = GenerationService(metrics_repo)
import_service = ImportService(metrics_repo)
export_service = ExportService(metrics_repo)
footprint_service = FootprintService(metrics_repo)
factor_service = FactorService(metrics_repo)
flow_share_service = FlowShareService(metrics_repo)
mix_share_service = MixShareService(metrics_repo)
mix_service = MixService(metrics_repo)
footprint_share_service = FootprintShareService(metrics_repo)
impact_service = ImpactService(metrics_repo)
load_service = LoadService(metrics_repo)
impact_share_service = ImpactShareService(metrics_repo)
score_service = ScoreService(metrics_repo)
zone_service = ZoneService(
    zones_file_path=settings.zones_file_path,
    crossborders_file_path=settings.crossborders_file_path,
)
