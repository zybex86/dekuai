"""
🧠 PHASE 7.1: Advanced ML Features - Price Drop Prediction Models

This module provides ML-powered price prediction and analysis for games,
helping users make informed purchasing decisions based on historical trends.

Components:
- PricePredictionEngine: Main ML prediction system
- Historical price analysis and trend detection
- Price drop probability calculation
- Target price recommendations with confidence levels
- Integration with Smart User Profiler for personalized predictions

Author: AutoGen DekuDeals Team
Version: 7.1.0
"""

import json
import logging
import sqlite3
import statistics
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriceTrend(Enum):
    """Price trend classifications."""

    DECLINING = "declining"
    STABLE = "stable"
    RISING = "rising"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"


class PredictionConfidence(Enum):
    """ML prediction confidence levels."""

    VERY_HIGH = "very_high"  # 90%+
    HIGH = "high"  # 80-89%
    MEDIUM = "medium"  # 60-79%
    LOW = "low"  # 40-59%
    VERY_LOW = "very_low"  # <40%


@dataclass
class PriceDataPoint:
    """Single price observation."""

    date: datetime
    price: float
    source: str = "dekudeals"
    promotion_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "price": self.price,
            "source": self.source,
            "promotion_type": self.promotion_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PriceDataPoint":
        return cls(
            date=datetime.fromisoformat(data["date"]),
            price=data["price"],
            source=data.get("source", "dekudeals"),
            promotion_type=data.get("promotion_type"),
        )


@dataclass
class PricePrediction:
    """ML price prediction result."""

    game_title: str
    current_price: float
    predicted_price: float
    price_drop_probability: float
    trend: PriceTrend
    confidence: PredictionConfidence
    target_price: Optional[float]
    prediction_timeframe: int  # days
    historical_low: Optional[float]
    average_discount_percentage: float
    reasons: List[str]
    next_significant_drop_date: Optional[datetime]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "game_title": self.game_title,
            "current_price": self.current_price,
            "predicted_price": self.predicted_price,
            "price_drop_probability": self.price_drop_probability,
            "trend": self.trend.value,
            "confidence": self.confidence.value,
            "target_price": self.target_price,
            "prediction_timeframe": self.prediction_timeframe,
            "historical_low": self.historical_low,
            "average_discount_percentage": self.average_discount_percentage,
            "reasons": self.reasons,
            "next_significant_drop_date": (
                self.next_significant_drop_date.isoformat()
                if self.next_significant_drop_date
                else None
            ),
        }


class PricePredictionEngine:
    """
    🧠 ML-powered price prediction engine for game pricing analysis.

    Features:
    - Historical price trend analysis
    - ML-based price prediction models
    - Price drop probability calculation
    - Personalized target price recommendations
    - Integration with user behavior patterns
    """

    def __init__(self, data_dir: str = "price_data"):
        """Initialize the price prediction engine."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Database for price history
        self.db_path = self.data_dir / "price_history.db"
        self._init_database()

        # ML models cache
        self.models_dir = self.data_dir / "models"
        self.models_dir.mkdir(exist_ok=True)

        # Prediction parameters
        self.min_data_points = 5
        self.prediction_timeframe_days = 30
        self.significant_drop_threshold = 0.15  # 15% drop

        logger.info(
            f"🧠 PricePredictionEngine initialized with data_dir: {self.data_dir}"
        )

    def _init_database(self):
        """Initialize SQLite database for price history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_title TEXT NOT NULL,
                    date TEXT NOT NULL,
                    price REAL NOT NULL,
                    source TEXT DEFAULT 'dekudeals',
                    promotion_type TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(game_title, date, price)
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_game_date 
                ON price_history(game_title, date)
            """
            )

            logger.info("📊 Price history database initialized")

    def record_price_data(
        self,
        game_title: str,
        price: float,
        date: Optional[datetime] = None,
        promotion_type: Optional[str] = None,
    ) -> bool:
        """Record a price data point."""
        try:
            if date is None:
                date = datetime.now()

            point = PriceDataPoint(
                date=date, price=price, promotion_type=promotion_type
            )

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO price_history 
                    (game_title, date, price, promotion_type)
                    VALUES (?, ?, ?, ?)
                """,
                    (game_title, date.isoformat(), price, promotion_type),
                )

                rows_affected = conn.total_changes

            if rows_affected > 0:
                logger.debug(
                    f"📈 Recorded price data: {game_title} = ${price:.2f} on {date.date()}"
                )
                return True
            else:
                logger.debug(
                    f"📈 Price data already exists: {game_title} = ${price:.2f}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Error recording price data: {e}")
            return False

    def get_price_history(
        self, game_title: str, days_back: int = 365
    ) -> List[PriceDataPoint]:
        """Get historical price data for a game."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT date, price, promotion_type
                    FROM price_history 
                    WHERE game_title = ? AND date >= ?
                    ORDER BY date ASC
                """,
                    (game_title, cutoff_date.isoformat()),
                )

                history = []
                for row in cursor.fetchall():
                    history.append(
                        PriceDataPoint(
                            date=datetime.fromisoformat(row[0]),
                            price=row[1],
                            promotion_type=row[2],
                        )
                    )

                logger.debug(
                    f"📊 Retrieved {len(history)} price points for {game_title}"
                )
                return history

        except Exception as e:
            logger.error(f"❌ Error getting price history: {e}")
            return []

    def analyze_price_trend(
        self, price_history: List[PriceDataPoint]
    ) -> Dict[str, Any]:
        """Analyze price trend from historical data."""
        if len(price_history) < 3:
            return {
                "trend": PriceTrend.UNKNOWN,
                "confidence": 0.0,
                "slope": 0.0,
                "volatility": 0.0,
                "analysis": "Insufficient data for trend analysis",
            }

        # Convert to numerical data
        prices = [point.price for point in price_history]
        dates = [(point.date - price_history[0].date).days for point in price_history]

        # Calculate trend using linear regression
        try:
            X = np.array(dates).reshape(-1, 1)
            y = np.array(prices)

            model = LinearRegression()
            model.fit(X, y)

            slope = model.coef_[0]
            r_squared = model.score(X, y)

            # Calculate volatility (coefficient of variation)
            price_std = np.std(prices)
            price_mean = np.mean(prices)
            volatility = price_std / price_mean if price_mean > 0 else 0

            # Determine trend
            if abs(slope) < 0.01:  # Very small slope
                trend = PriceTrend.STABLE
            elif slope < -0.05:  # Declining
                trend = PriceTrend.DECLINING
            elif slope > 0.05:  # Rising
                trend = PriceTrend.RISING
            elif volatility > 0.3:  # High volatility
                trend = PriceTrend.VOLATILE
            else:
                trend = PriceTrend.STABLE

            return {
                "trend": trend,
                "confidence": r_squared,
                "slope": slope,
                "volatility": volatility,
                "analysis": f"Trend: {trend.value}, R²: {r_squared:.3f}, Volatility: {volatility:.3f}",
            }

        except Exception as e:
            logger.error(f"❌ Error in trend analysis: {e}")
            return {
                "trend": PriceTrend.UNKNOWN,
                "confidence": 0.0,
                "slope": 0.0,
                "volatility": 0.0,
                "analysis": f"Error in analysis: {str(e)}",
            }

    def calculate_price_drop_probability(
        self, game_title: str, price_history: List[PriceDataPoint]
    ) -> float:
        """Calculate probability of significant price drop in next 30 days."""
        if len(price_history) < self.min_data_points:
            return 0.5  # Default uncertainty

        try:
            prices = [point.price for point in price_history]
            current_price = prices[-1]

            # Analyze historical drops
            significant_drops = 0
            total_periods = 0

            for i in range(len(prices) - 30, len(prices)):
                if i < 0:
                    continue

                # Look at 30-day periods
                period_start = max(0, i - 30)
                period_prices = prices[period_start : i + 1]

                if len(period_prices) < 2:
                    continue

                period_high = max(period_prices)
                period_low = min(period_prices)

                if period_high > 0:
                    drop_percentage = (period_high - period_low) / period_high
                    if drop_percentage >= self.significant_drop_threshold:
                        significant_drops += 1

                total_periods += 1

            if total_periods == 0:
                return 0.5

            # Base probability from historical pattern
            base_probability = significant_drops / total_periods

            # Adjust based on trend analysis
            trend_analysis = self.analyze_price_trend(price_history)
            trend = trend_analysis["trend"]

            if trend == PriceTrend.DECLINING:
                base_probability *= 1.3  # Higher chance if already declining
            elif trend == PriceTrend.RISING:
                base_probability *= 0.7  # Lower chance if rising
            elif trend == PriceTrend.VOLATILE:
                base_probability *= 1.1  # Slightly higher for volatile

            # Adjust based on time since last significant drop
            days_since_last_drop = self._days_since_last_significant_drop(price_history)
            if days_since_last_drop > 90:  # 3 months
                base_probability *= 1.2
            elif days_since_last_drop < 30:  # 1 month
                base_probability *= 0.8

            return min(1.0, max(0.0, base_probability))

        except Exception as e:
            logger.error(f"❌ Error calculating drop probability: {e}")
            return 0.5

    def _days_since_last_significant_drop(
        self, price_history: List[PriceDataPoint]
    ) -> int:
        """Calculate days since last significant price drop."""
        if len(price_history) < 2:
            return 999  # Large number indicating no recent drops

        prices = [point.price for point in price_history]
        dates = [point.date for point in price_history]

        # Look for last significant drop
        for i in range(len(prices) - 1, 0, -1):
            current_price = prices[i]
            previous_price = prices[i - 1]

            if previous_price > 0:
                drop_percentage = (previous_price - current_price) / previous_price
                if drop_percentage >= self.significant_drop_threshold:
                    days_ago = (datetime.now() - dates[i]).days
                    return max(0, days_ago)

        return 999

    def predict_target_price(
        self,
        game_title: str,
        price_history: List[PriceDataPoint],
        user_budget_preference: Optional[float] = None,
    ) -> Optional[float]:
        """Predict optimal target price for purchase."""
        if len(price_history) < self.min_data_points:
            return None

        try:
            prices = [point.price for point in price_history]

            # Calculate statistical targets
            historical_low = min(prices)
            median_price = statistics.median(prices)
            q1_price = np.percentile(prices, 25)  # 25th percentile

            # Base target on historical patterns
            base_target = (historical_low + q1_price) / 2

            # Adjust based on trend
            trend_analysis = self.analyze_price_trend(price_history)
            trend = trend_analysis["trend"]

            if trend == PriceTrend.DECLINING:
                # Expect further drops
                base_target = historical_low * 0.95
            elif trend == PriceTrend.RISING:
                # Less likely to drop significantly
                base_target = q1_price
            elif trend == PriceTrend.VOLATILE:
                # Wait for better opportunity
                base_target = historical_low * 1.05

            # Consider user budget preference
            if user_budget_preference:
                base_target = min(base_target, user_budget_preference)

            return round(base_target, 2)

        except Exception as e:
            logger.error(f"❌ Error predicting target price: {e}")
            return None

    def generate_price_prediction(
        self, game_title: str, current_price: float, user_id: Optional[str] = None
    ) -> PricePrediction:
        """
        Generate comprehensive ML price prediction for a game.

        Args:
            game_title: Name of the game
            current_price: Current price of the game
            user_id: Optional user ID for personalized predictions

        Returns:
            PricePrediction: Comprehensive prediction with ML insights
        """
        try:
            logger.info(
                f"🧠 Generating price prediction for: {game_title} (${current_price})"
            )

            # Record current price
            self.record_price_data(game_title, current_price)

            # Get historical data
            price_history = self.get_price_history(game_title)

            if len(price_history) < self.min_data_points:
                return self._generate_limited_prediction(game_title, current_price)

            # Analyze trend
            trend_analysis = self.analyze_price_trend(price_history)
            trend = trend_analysis["trend"]

            # Calculate drop probability
            drop_probability = self.calculate_price_drop_probability(
                game_title, price_history
            )

            # Predict target price
            target_price = self.predict_target_price(game_title, price_history)

            # Determine confidence level
            confidence = self._calculate_prediction_confidence(
                trend_analysis, len(price_history)
            )

            # Generate prediction reasons
            reasons = self._generate_prediction_reasons(
                trend_analysis, drop_probability, price_history, current_price
            )

            # Calculate additional metrics
            prices = [point.price for point in price_history]
            historical_low = min(prices) if prices else current_price
            avg_discount = self._calculate_average_discount(prices, current_price)

            # Predict next significant drop (simplified heuristic)
            next_drop_date = self._predict_next_drop_date(
                price_history, drop_probability
            )

            # ML prediction of future price (30 days)
            predicted_price = self._predict_future_price(price_history, current_price)

            prediction = PricePrediction(
                game_title=game_title,
                current_price=current_price,
                predicted_price=predicted_price,
                price_drop_probability=drop_probability,
                trend=trend,
                confidence=confidence,
                target_price=target_price,
                prediction_timeframe=self.prediction_timeframe_days,
                historical_low=historical_low,
                average_discount_percentage=avg_discount,
                reasons=reasons,
                next_significant_drop_date=next_drop_date,
            )

            logger.info(
                f"✅ Price prediction complete: {trend.value} trend, {drop_probability:.1%} drop probability"
            )
            return prediction

        except Exception as e:
            logger.error(f"❌ Error generating price prediction: {e}")
            return self._generate_error_prediction(game_title, current_price, str(e))

    def _generate_limited_prediction(
        self, game_title: str, current_price: float
    ) -> PricePrediction:
        """Generate prediction with limited historical data."""
        return PricePrediction(
            game_title=game_title,
            current_price=current_price,
            predicted_price=current_price * 0.85,  # Assume 15% future discount
            price_drop_probability=0.5,
            trend=PriceTrend.UNKNOWN,
            confidence=PredictionConfidence.VERY_LOW,
            target_price=current_price * 0.75,
            prediction_timeframe=self.prediction_timeframe_days,
            historical_low=None,
            average_discount_percentage=25.0,
            reasons=[
                "Limited historical data available",
                "Using general gaming market trends",
                "Prediction based on typical discount patterns",
            ],
            next_significant_drop_date=None,
        )

    def _generate_error_prediction(
        self, game_title: str, current_price: float, error: str
    ) -> PricePrediction:
        """Generate fallback prediction on error."""
        return PricePrediction(
            game_title=game_title,
            current_price=current_price,
            predicted_price=current_price,
            price_drop_probability=0.0,
            trend=PriceTrend.UNKNOWN,
            confidence=PredictionConfidence.VERY_LOW,
            target_price=None,
            prediction_timeframe=self.prediction_timeframe_days,
            historical_low=None,
            average_discount_percentage=0.0,
            reasons=[
                f"Error in prediction: {error}",
                "Unable to analyze price patterns",
            ],
            next_significant_drop_date=None,
        )

    def _calculate_prediction_confidence(
        self, trend_analysis: Dict[str, Any], data_points: int
    ) -> PredictionConfidence:
        """Calculate confidence level for prediction."""
        base_confidence = trend_analysis.get("confidence", 0.0)

        # Adjust based on data quantity
        if data_points >= 50:
            data_factor = 1.0
        elif data_points >= 20:
            data_factor = 0.8
        elif data_points >= 10:
            data_factor = 0.6
        else:
            data_factor = 0.4

        final_confidence = base_confidence * data_factor

        if final_confidence >= 0.9:
            return PredictionConfidence.VERY_HIGH
        elif final_confidence >= 0.8:
            return PredictionConfidence.HIGH
        elif final_confidence >= 0.6:
            return PredictionConfidence.MEDIUM
        elif final_confidence >= 0.4:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW

    def _generate_prediction_reasons(
        self,
        trend_analysis: Dict[str, Any],
        drop_probability: float,
        price_history: List[PriceDataPoint],
        current_price: float,
    ) -> List[str]:
        """Generate human-readable reasons for the prediction."""
        reasons = []

        trend = trend_analysis["trend"]
        confidence = trend_analysis["confidence"]
        volatility = trend_analysis.get("volatility", 0)

        # Trend-based reasons
        if trend == PriceTrend.DECLINING:
            reasons.append(f"📉 Price has been declining (R² = {confidence:.2f})")
        elif trend == PriceTrend.RISING:
            reasons.append(f"📈 Price has been rising (R² = {confidence:.2f})")
        elif trend == PriceTrend.VOLATILE:
            reasons.append(f"📊 Price shows high volatility ({volatility:.1%})")
        elif trend == PriceTrend.STABLE:
            reasons.append(f"⚖️ Price has been stable (R² = {confidence:.2f})")

        # Drop probability reasons
        if drop_probability > 0.7:
            reasons.append(
                f"🎯 High probability ({drop_probability:.1%}) of significant drop"
            )
        elif drop_probability > 0.5:
            reasons.append(
                f"⚖️ Moderate probability ({drop_probability:.1%}) of price drop"
            )
        elif drop_probability < 0.3:
            reasons.append(
                f"⬆️ Low probability ({drop_probability:.1%}) of significant drop"
            )

        # Historical context
        if len(price_history) > 0:
            prices = [point.price for point in price_history]
            historical_low = min(prices)
            price_vs_low = (current_price - historical_low) / historical_low * 100

            if price_vs_low < 10:
                reasons.append(f"💎 Near historical low (${historical_low:.2f})")
            elif price_vs_low > 50:
                reasons.append(
                    f"💸 Significantly above historical low (+{price_vs_low:.0f}%)"
                )

        # Time-based patterns
        days_since_drop = self._days_since_last_significant_drop(price_history)
        if days_since_drop > 90:
            reasons.append(f"⏰ {days_since_drop} days since last significant drop")
        elif days_since_drop < 30:
            reasons.append(f"🔄 Recent drop occurred {days_since_drop} days ago")

        return reasons[:5]  # Limit to 5 most important reasons

    def _calculate_average_discount(
        self, prices: List[float], current_price: float
    ) -> float:
        """Calculate average discount percentage from peak prices."""
        if not prices:
            return 0.0

        peak_price = max(prices)
        if peak_price <= 0:
            return 0.0

        discount = (peak_price - current_price) / peak_price * 100
        return max(0.0, discount)

    def _predict_next_drop_date(
        self, price_history: List[PriceDataPoint], drop_probability: float
    ) -> Optional[datetime]:
        """Predict when next significant drop might occur (heuristic)."""
        if drop_probability < 0.3:
            return None

        # Simple heuristic: if high drop probability, expect within 2-6 weeks
        if drop_probability > 0.7:
            days_ahead = 14 + int(drop_probability * 14)  # 2-4 weeks
        else:
            days_ahead = 30 + int(drop_probability * 30)  # 4-8 weeks

        return datetime.now() + timedelta(days=days_ahead)

    def _predict_future_price(
        self, price_history: List[PriceDataPoint], current_price: float
    ) -> float:
        """Use ML to predict price in 30 days."""
        if len(price_history) < 5:
            return current_price * 0.9  # Default 10% reduction assumption

        try:
            # Prepare data for ML model
            prices = [point.price for point in price_history]
            dates = [
                (point.date - price_history[0].date).days for point in price_history
            ]

            # Use last 30 points for training
            recent_points = min(30, len(prices))
            X = np.array(dates[-recent_points:]).reshape(-1, 1)
            y = np.array(prices[-recent_points:])

            # Train simple linear regression
            model = LinearRegression()
            model.fit(X, y)

            # Predict 30 days ahead
            future_date = dates[-1] + 30
            predicted = model.predict([[future_date]])[0]

            # Apply bounds (price shouldn't change too dramatically)
            max_change = current_price * 0.5  # Max 50% change
            predicted = max(
                current_price - max_change, min(current_price + max_change, predicted)
            )

            return round(predicted, 2)

        except Exception as e:
            logger.error(f"❌ Error in ML price prediction: {e}")
            return current_price * 0.9

    def get_prediction_summary(self, game_title: str) -> Optional[Dict[str, Any]]:
        """Get a summary of predictions for a game."""
        try:
            price_history = self.get_price_history(game_title)
            if not price_history:
                return None

            current_price = price_history[-1].price
            prediction = self.generate_price_prediction(game_title, current_price)

            return prediction.to_dict()

        except Exception as e:
            logger.error(f"❌ Error getting prediction summary: {e}")
            return None


# Utility functions for integration with existing system


def integrate_price_prediction_with_game_analysis(
    game_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Integrate price prediction with existing game analysis.

    Args:
        game_data: Standard game data dictionary

    Returns:
        Enhanced game data with price predictions
    """
    try:
        engine = PricePredictionEngine()

        game_title = game_data.get("title", "Unknown")
        current_price_str = game_data.get("current_eshop_price", "0")

        # Extract price from string
        current_price = 0.0
        if isinstance(current_price_str, str):
            import re

            price_match = re.search(r"[\d.,]+", current_price_str.replace(",", "."))
            if price_match:
                current_price = float(price_match.group())
        elif isinstance(current_price_str, (int, float)):
            current_price = float(current_price_str)

        if current_price > 0:
            prediction = engine.generate_price_prediction(game_title, current_price)

            # Add prediction to game data
            game_data["ml_price_prediction"] = prediction.to_dict()

            logger.info(f"🧠 Added ML price prediction for {game_title}")
        else:
            logger.warning(f"⚠️ Invalid price for {game_title}: {current_price_str}")

        return game_data

    except Exception as e:
        logger.error(f"❌ Error integrating price prediction: {e}")
        return game_data


def format_price_prediction_summary(prediction: PricePrediction) -> str:
    """Format price prediction for display."""

    confidence_emoji = {
        PredictionConfidence.VERY_HIGH: "🎯",
        PredictionConfidence.HIGH: "✅",
        PredictionConfidence.MEDIUM: "⚖️",
        PredictionConfidence.LOW: "❓",
        PredictionConfidence.VERY_LOW: "❗",
    }

    trend_emoji = {
        PriceTrend.DECLINING: "📉",
        PriceTrend.STABLE: "⚖️",
        PriceTrend.RISING: "📈",
        PriceTrend.VOLATILE: "📊",
        PriceTrend.UNKNOWN: "❓",
    }

    summary = f"""
🧠 **ML Price Prediction for {prediction.game_title}**

💰 **Current Price**: ${prediction.current_price:.2f}
🔮 **Predicted Price** (30d): ${prediction.predicted_price:.2f}
📊 **Price Drop Probability**: {prediction.price_drop_probability:.1%}
{trend_emoji.get(prediction.trend, '❓')} **Trend**: {prediction.trend.value.title()}
{confidence_emoji.get(prediction.confidence, '❓')} **Confidence**: {prediction.confidence.value.replace('_', ' ').title()}
"""

    if prediction.target_price:
        summary += f"🎯 **Target Price**: ${prediction.target_price:.2f}\n"

    if prediction.historical_low:
        summary += f"💎 **Historical Low**: ${prediction.historical_low:.2f}\n"

    if prediction.next_significant_drop_date:
        summary += f"📅 **Next Drop Expected**: {prediction.next_significant_drop_date.strftime('%Y-%m-%d')}\n"

    if prediction.reasons:
        summary += f"\n**🔍 Key Insights:**\n"
        for reason in prediction.reasons:
            summary += f"• {reason}\n"

    return summary.strip()


# Global price prediction engine instance
_price_engine = None


def get_price_prediction_engine() -> PricePredictionEngine:
    """Get global price prediction engine instance."""
    global _price_engine
    if _price_engine is None:
        _price_engine = PricePredictionEngine()
    return _price_engine
