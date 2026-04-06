from .disease_files import router as disease_files_router
from .disease_predictions import router as disease_predictions_router
from .knowledge_base import router as knowledge_base_router

__all__ = ["disease_files_router", "disease_predictions_router", "knowledge_base_router"]
