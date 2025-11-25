from wattnet.storage.repository import MetricsRepository

from wattnet.api.service.exports import ExportService
from wattnet.api.service.factors import FactorService
from wattnet.api.service.flow_share import FlowShareService
from wattnet.api.service.footprint_share import FootprintShareService
from wattnet.api.service.footprints import FootprintService
from wattnet.api.service.generation import GenerationService
from wattnet.api.service.imports import ImportService
from wattnet.api.service.mix_share import MixShareService

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
footprint_share_service = FootprintShareService(metrics_repo)
