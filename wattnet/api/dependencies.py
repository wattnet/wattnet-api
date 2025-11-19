from wattnet.storage.repository import MetricsRepository

from wattnet.api.service.factors import FactorService
from wattnet.api.service.footprints import FootprintService

# Create a MetricsRepository instance
metrics_repo = MetricsRepository()

# Create Service instances
footprint_service = FootprintService(metrics_repo)
factor_service = FactorService(metrics_repo)
