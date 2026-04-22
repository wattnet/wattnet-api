"""This module imports all the models used in the API.

This allows for easier imports in other parts of the application,
as they can be imported from a single location.
"""

from .exports import Export, ExportBlock, ExportSeries
from .factor import Factor, FactorAggregate, FactorSeries
from .flow_share import FlowShare, FlowShareBlock, FlowShareSeries
from .footprint import Footprint, FootprintAggregate, FootprintSeries
from .footprint_share import FootprintShare, FootprintShareBlock, FootprintShareSeries
from .generation import Generation, GenerationSeries, ProductionBlock
from .impact import Impact, ImpactAggregate, ImpactSeries
from .impact_share import ImpactShare, ImpactShareBlock, ImpactShareSeries
from .imports import Import, ImportBlock, ImportSeries
from .load import Load, LoadSeries
from .mix import Mix, MixBlock, MixSeries
from .mix_share import MixShare, MixShareBlock, MixShareSeries
from .score import GreenScore, GreenScoreAggregate, GreenScoreSeries
from .zone import Zone

__all__ = [
    "Export",
    "ExportBlock",
    "ExportSeries",
    "Factor",
    "FactorAggregate",
    "FactorSeries",
    "FlowShare",
    "FlowShareBlock",
    "FlowShareSeries",
    "Footprint",
    "FootprintAggregate",
    "FootprintSeries",
    "Generation",
    "GenerationSeries",
    "ProductionBlock",
    "Import",
    "ImportBlock",
    "ImportSeries",
    "MixShare",
    "MixShareBlock",
    "MixShareSeries",
    "Mix",
    "MixBlock",
    "MixSeries",
    "Impact",
    "ImpactAggregate",
    "ImpactSeries",
    "GreenScore",
    "GreenScoreAggregate",
    "GreenScoreSeries",
    "FootprintShare",
    "FootprintShareBlock",
    "FootprintShareSeries",
    "ImpactShare",
    "ImpactShareBlock",
    "ImpactShareSeries",
    "Load",
    "LoadSeries",
    "Zone",
]
