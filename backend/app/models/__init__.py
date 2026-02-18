# ============================================
# Boussole - Models Package
# ============================================

from app.db.base import Base

# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.sector import Sector
from app.models.indicator import Indicator
from app.models.data_point import DataPoint
from app.models.document import Document, DocumentEmbedding
from app.models.wilaya import Wilaya
from app.models.metric import Metric
from app.models.time_series_data import TimeSeriesData
from app.models.forecast import Forecast
from app.models.subscription import Subscription, SubscriptionHistory

__all__ = [
    "Base",
    "User",
    "Sector",
    "Indicator",
    "DataPoint",
    "Document",
    "DocumentEmbedding",
    "Wilaya",
    "Metric",
    "TimeSeriesData",
    "Forecast",
    "Subscription",
    "SubscriptionHistory",
]
