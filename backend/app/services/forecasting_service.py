# ============================================
# Boussole - Forecasting Service
# ============================================

"""
Forecasting service using Prophet for time-series predictions.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import logging
import pandas as pd
from datetime import datetime, timedelta
from prophet import Prophet

from app.models.metric import Metric
from app.models.time_series_data import TimeSeriesData
from app.models.forecast import Forecast
from app.schemas.forecast import (
    ForecastCreate,
    Forecast,
    ForecastGenerateRequest,
    ForecastGenerateResponse,
    ForecastTrend,
)

logger = logging.getLogger(__name__)


class ForecastingService:
    """
    Service layer for forecasting operations using Prophet.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_forecast(
        self,
        request: ForecastGenerateRequest
    ) -> ForecastGenerateResponse:
        """
        Generate forecast for a metric using Prophet.
        
        Args:
            request: Forecast generation request
            
        Returns:
            Forecast generation response with forecasts
        """
        # Get metric
        result = await self.db.execute(
            select(Metric).where(Metric.id == request.metric_id)
        )
        metric = result.scalar_one_or_none()
        
        if not metric:
            raise ValueError("Metric not found")
        
        # Get historical time-series data
        time_series_result = await self.db.execute(
            select(TimeSeriesData)
            .where(TimeSeriesData.metric_id == request.metric_id)
            .where(TimeSeriesData.is_verified == True)
            .order_by(TimeSeriesData.period)
        )
        time_series_data = time_series_result.scalars().all()
        
        if len(time_series_data) < 12:
            raise ValueError("Insufficient historical data for forecasting (minimum 12 data points required)")
        
        # Prepare data for Prophet
        df = pd.DataFrame([
            {
                "ds": ts.period,
                "y": ts.value,
            }
            for ts in time_series_data
        ])
        
        # Fit Prophet model
        try:
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
            )
            model.fit(df)
            
            # Generate future predictions
            future = model.make_future_dataframe(periods=request.periods)
            forecast = model.predict(future)
            
            # Calculate confidence intervals
            forecast = model.predict(future)
            forecast_lower = model.predict(future)
            forecast_upper = model.predict(future)
            
            # Calculate error metrics
            # Use last 20% of data for testing
            test_size = int(len(df) * 0.2)
            if test_size > 0:
                train_df = df[:-test_size]
                test_df = df[-test_size:]
                
                # Fit on training data
                model_test = Prophet(
                    yearly_seasonality=True,
                    weekly_seasonality=False,
                    daily_seasonality=False,
                )
                model_test.fit(train_df)
                
                # Predict on test data
                test_forecast = model_test.predict(test_df)
                
                # Calculate MAE
                mae = abs(test_df["y"].values - test_forecast["yhat"].values).mean()
                
                # Calculate MAPE
                mape = (
                    abs((test_df["y"].values - test_forecast["yhat"].values) / test_df["y"].values)
                    .mean()
                    * 100
                )
                
                # Calculate RMSE
                rmse = (
                    ((test_df["y"].values - test_forecast["yhat"].values) ** 2).mean()
                    ** 0.5
                )
            else:
                mae = None
                mape = None
                rmse = None
            
            # Create forecast records
            forecasts = []
            for _, row in forecast.iterrows():
                forecast_record = Forecast(
                    metric_id=metric.id,
                    forecast_period=row["ds"],
                    forecast_value=row["yhat"],
                    lower_bound=row["yhat_lower"],
                    upper_bound=row["yhat_upper"],
                    confidence_interval=request.confidence_interval,
                    forecast_horizon=request.periods,
                    model_version="prophet-" + Prophet.__version__,
                    model_params='{"yearly_seasonality": true}',
                    mae=mae,
                    mape=mape,
                    rmse=rmse,
                    is_published=False,
                )
                self.db.add(forecast_record)
                forecasts.append(forecast_record)
            
            self.db.commit()
            
            # Refresh forecasts
            for f in forecasts:
                await self.db.refresh(f)
            
            logger.info(f"Generated {len(forecasts)} forecasts for metric {request.metric_id}")
            
            return ForecastGenerateResponse(
                metric_id=request.metric_id,
                forecasts=[
                    {
                        "id": f.id,
                        "metric_id": f.metric_id,
                        "forecast_period": f.forecast_period,
                        "forecast_value": f.forecast_value,
                        "lower_bound": f.lower_bound,
                        "upper_bound": f.upper_bound,
                        "confidence_interval": f.confidence_interval,
                        "forecast_horizon": f.forecast_horizon,
                        "model_version": f.model_version,
                        "mae": f.mae,
                        "mape": f.mape,
                        "rmse": f.rmse,
                        "is_published": f.is_published,
                        "created_at": f.created_at,
                        "updated_at": f.updated_at,
                    }
                    for f in forecasts
                ],
                model_version="prophet-" + Prophet.__version__,
                mae=mae,
                mape=mape,
                rmse=rmse,
                generated_at=datetime.utcnow(),
            )
        
        except Exception as e:
            logger.error(f"Failed to generate forecast: {e}", exc_info=True)
            raise
    
    async def get_forecasts(
        self,
        metric_id: int,
        published_only: bool = True
    ) -> List[Forecast]:
        """
        Get forecasts for a metric.
        
        Args:
            metric_id: Metric ID
            published_only: Only return published forecasts
            
        Returns:
            List of forecasts
        """
        query = select(Forecast).where(Forecast.metric_id == metric_id)
        
        if published_only:
            query = query.where(Forecast.is_published == True)
        
        query = query.order_by(Forecast.forecast_period)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def publish_forecast(self, forecast_id: int) -> Optional[Forecast]:
        """
        Publish a forecast (make it visible to users).
        
        Args:
            forecast_id: Forecast ID
            
        Returns:
            Published forecast or None
        """
        result = await self.db.execute(
            select(Forecast).where(Forecast.id == forecast_id)
        )
        forecast = result.scalar_one_or_none()
        
        if not forecast:
            return None
        
        forecast.is_published = True
        await self.db.commit()
        await self.db.refresh(forecast)
        
        logger.info(f"Published forecast {forecast_id}")
        return forecast
    
    async def get_forecast_trends(
        self,
        metric_id: int,
        periods: int = 12
    ) -> List[ForecastTrend]:
        """
        Get forecast trends for visualization.
        
        Args:
            metric_id: Metric ID
            periods: Number of periods to return
            
        Returns:
            List of forecast trends
        """
        # Get historical data
        time_series_result = await self.db.execute(
            select(TimeSeriesData)
            .where(TimeSeriesData.metric_id == metric_id)
            .where(TimeSeriesData.is_verified == True)
            .order_by(TimeSeriesData.period.desc())
            .limit(periods)
        )
        time_series_data = time_series_result.scalars().all()
        
        # Get forecasts
        forecast_result = await self.db.execute(
            select(Forecast)
            .where(Forecast.metric_id == metric_id)
            .where(Forecast.is_published == True)
            .order_by(Forecast.forecast_period)
            .limit(periods)
        )
        forecasts = forecast_result.scalars().all()
        
        # Create trend data
        trends = []
        
        # Add historical data points
        for ts in reversed(time_series_data):
            trends.append(ForecastTrend(
                period=ts.period,
                actual_value=ts.value,
                forecast_value=ts.value,  # Same value for historical
                lower_bound=None,
                upper_bound=None,
            ))
        
        # Add forecast points
        for f in forecasts:
            trends.append(ForecastTrend(
                period=f.forecast_period,
                actual_value=None,
                forecast_value=f.forecast_value,
                lower_bound=f.lower_bound,
                upper_bound=f.upper_bound,
            ))
        
        return trends
    
    async def delete_forecast(self, forecast_id: int) -> bool:
        """
        Delete a forecast.
        
        Args:
            forecast_id: Forecast ID
            
        Returns:
            True if successful, False otherwise
        """
        result = await self.db.execute(
            select(Forecast).where(Forecast.id == forecast_id)
        )
        forecast = result.scalar_one_or_none()
        
        if not forecast:
            return False
        
        await self.db.delete(forecast)
        await self.db.commit()
        
        logger.info(f"Deleted forecast {forecast_id}")
        return True
    
    async def batch_generate_forecasts(
        self,
        metric_ids: List[int],
        periods: int = 12
    ) -> dict:
        """
        Batch generate forecasts for multiple metrics.
        
        Args:
            metric_ids: List of metric IDs
            periods: Number of periods to forecast
            
        Returns:
            Batch generation results
        """
        results = {}
        
        for metric_id in metric_ids:
            try:
                request = ForecastGenerateRequest(
                    metric_id=metric_id,
                    periods=periods,
                    confidence_interval=0.95,
                )
                response = await self.generate_forecast(request)
                results[metric_id] = {
                    "status": "success",
                    "forecasts": response.forecasts,
                }
            except Exception as e:
                logger.error(f"Failed to generate forecast for metric {metric_id}: {e}")
                results[metric_id] = {
                    "status": "error",
                    "error": str(e),
                }
        
        return results
