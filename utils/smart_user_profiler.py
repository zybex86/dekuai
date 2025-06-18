"""
Smart User Profiler for AutoGen DekuDeals
Intelligent user preference detection and dynamic profiling

Enhanced Phase 6.5: ML Intelligence Enhancement
Automatically learns user preferences from interactions and game choices
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from enum import Enum

from utils.recommendation_engine import UserPreference, UserProfile
from utils.usage_analytics import get_usage_analytics, EventType, UserSegment

logger = logging.getLogger(__name__)


class GamePreferencePattern(Enum):
    """Detected game preference patterns"""

    INDIE_ENTHUSIAST = "indie_enthusiast"
    PUZZLE_LOVER = "puzzle_lover"
    ACTION_SEEKER = "action_seeker"
    RPG_FANATIC = "rpg_fanatic"
    PLATFORMER_FAN = "platformer_fan"
    QUALITY_FOCUSED = "quality_focused"
    BUDGET_CONSCIOUS = "budget_conscious"
    SALE_HUNTER = "sale_hunter"
    RECENT_GAMES = "recent_games"
    RETRO_GAMER = "retro_gamer"


@dataclass
class UserInteraction:
    """Single user interaction with analysis"""

    game_name: str
    timestamp: datetime
    interaction_type: str  # "analyzed", "compared", "quick_check"
    game_data: Dict[str, Any]
    user_response: Optional[str] = None  # Future: user feedback
    session_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PreferenceInsight:
    """Insight about user preferences"""

    pattern: GamePreferencePattern
    confidence: float  # 0.0 to 1.0
    evidence: List[str]
    weight: float = 1.0


@dataclass
class DynamicUserProfile:
    """Dynamically evolved user profile"""

    user_id: str
    detected_preferences: List[PreferenceInsight]
    favorite_genres: List[Tuple[str, float]]  # (genre, confidence)
    price_sensitivity: float  # 0.0 = price insensitive, 1.0 = very price sensitive
    quality_threshold: float  # minimum acceptable score
    discovered_patterns: Dict[str, Any]
    interaction_history: List[UserInteraction]
    last_updated: datetime
    confidence_level: str  # "low", "medium", "high", "very_high"

    # Learning metadata
    total_interactions: int = 0
    learning_velocity: float = 0.0  # how fast preferences are changing
    profile_stability: float = 0.0  # how stable the profile is


class SmartUserProfiler:
    """
    Intelligent user profiling system that learns from interactions

    Features:
    - Automatic preference detection from game choices
    - Dynamic profile evolution
    - Pattern recognition in user behavior
    - Confidence-based recommendations
    - Learning from implicit feedback
    """

    def __init__(self, data_dir: str = "user_profiles"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Storage
        self.profiles_file = self.data_dir / "dynamic_user_profiles.json"
        self.interactions_file = self.data_dir / "user_interactions.json"

        # In-memory data
        self.user_profiles: Dict[str, DynamicUserProfile] = {}
        self.interaction_history: List[UserInteraction] = []

        # Learning parameters
        self.min_interactions_for_profiling = 3
        self.confidence_threshold = 0.6
        self.pattern_detection_window_days = 30

        # Initialize analytics integration
        self.analytics = get_usage_analytics()

        # Load existing data
        self._load_existing_data()

        logger.info("✅ Smart User Profiler initialized")

    def _load_existing_data(self):
        """Load existing user profiles and interactions"""
        try:
            # Load profiles
            if self.profiles_file.exists():
                with open(self.profiles_file, "r") as f:
                    data = json.load(f)
                    for user_id, profile_data in data.get("profiles", {}).items():
                        profile = DynamicUserProfile(
                            user_id=profile_data["user_id"],
                            detected_preferences=[
                                PreferenceInsight(
                                    pattern=GamePreferencePattern(p["pattern"]),
                                    confidence=p["confidence"],
                                    evidence=p["evidence"],
                                    weight=p.get("weight", 1.0),
                                )
                                for p in profile_data.get("detected_preferences", [])
                            ],
                            favorite_genres=[
                                (g, c)
                                for g, c in profile_data.get("favorite_genres", [])
                            ],
                            price_sensitivity=profile_data.get(
                                "price_sensitivity", 0.5
                            ),
                            quality_threshold=profile_data.get(
                                "quality_threshold", 70.0
                            ),
                            discovered_patterns=profile_data.get(
                                "discovered_patterns", {}
                            ),
                            interaction_history=[],  # Load separately
                            last_updated=datetime.fromisoformat(
                                profile_data["last_updated"]
                            ),
                            confidence_level=profile_data.get(
                                "confidence_level", "low"
                            ),
                            total_interactions=profile_data.get(
                                "total_interactions", 0
                            ),
                            learning_velocity=profile_data.get(
                                "learning_velocity", 0.0
                            ),
                            profile_stability=profile_data.get(
                                "profile_stability", 0.0
                            ),
                        )
                        self.user_profiles[user_id] = profile

            # Load recent interactions (last 30 days)
            if self.interactions_file.exists():
                with open(self.interactions_file, "r") as f:
                    data = json.load(f)
                    cutoff = datetime.now() - timedelta(days=30)
                    for interaction_data in data.get("interactions", []):
                        timestamp = datetime.fromisoformat(
                            interaction_data["timestamp"]
                        )
                        if timestamp > cutoff:
                            interaction = UserInteraction(
                                game_name=interaction_data["game_name"],
                                timestamp=timestamp,
                                interaction_type=interaction_data["interaction_type"],
                                game_data=interaction_data["game_data"],
                                user_response=interaction_data.get("user_response"),
                                session_context=interaction_data.get(
                                    "session_context", {}
                                ),
                            )
                            self.interaction_history.append(interaction)

        except Exception as e:
            logger.warning(f"Could not load existing profiler data: {e}")

    def record_interaction(
        self,
        game_name: str,
        game_data: Dict[str, Any],
        interaction_type: str = "analyzed",
        user_response: Optional[str] = None,
        session_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Record a user interaction with a game"""

        interaction = UserInteraction(
            game_name=game_name,
            timestamp=datetime.now(),
            interaction_type=interaction_type,
            game_data=game_data,
            user_response=user_response,
            session_context=session_context or {},
        )

        self.interaction_history.append(interaction)

        # Update user profile
        current_user_id = self.analytics.current_user_id
        self._update_user_profile_from_interaction(current_user_id, interaction)

        # Save periodically
        if len(self.interaction_history) % 5 == 0:  # Save every 5 interactions
            self._save_data()

        logger.debug(f"Recorded interaction: {game_name} ({interaction_type})")
        return interaction.timestamp.isoformat()

    def _update_user_profile_from_interaction(
        self, user_id: str, interaction: UserInteraction
    ):
        """Update user profile based on new interaction"""

        if user_id not in self.user_profiles:
            # Create new profile
            self.user_profiles[user_id] = DynamicUserProfile(
                user_id=user_id,
                detected_preferences=[],
                favorite_genres=[],
                price_sensitivity=0.5,
                quality_threshold=70.0,
                discovered_patterns={},
                interaction_history=[],
                last_updated=datetime.now(),
                confidence_level="low",
            )

        profile = self.user_profiles[user_id]
        profile.interaction_history.append(interaction)
        profile.total_interactions += 1
        profile.last_updated = datetime.now()

        # Re-analyze patterns if enough interactions
        if profile.total_interactions >= self.min_interactions_for_profiling:
            self._analyze_user_patterns(profile)

    def _analyze_user_patterns(self, profile: DynamicUserProfile):
        """Analyze user interaction patterns to detect preferences"""

        # Get recent interactions
        recent_cutoff = datetime.now() - timedelta(
            days=self.pattern_detection_window_days
        )
        recent_interactions = [
            i for i in profile.interaction_history if i.timestamp > recent_cutoff
        ]

        if len(recent_interactions) < 2:
            return

        # Analyze patterns
        new_preferences = []

        # 1. Genre preferences
        genre_analysis = self._analyze_genre_preferences(recent_interactions)
        new_preferences.extend(genre_analysis)

        # 2. Price sensitivity
        price_analysis = self._analyze_price_sensitivity(recent_interactions)
        new_preferences.extend(price_analysis)

        # 3. Quality preferences
        quality_analysis = self._analyze_quality_preferences(recent_interactions)
        new_preferences.extend(quality_analysis)

        # Update profile
        profile.detected_preferences = new_preferences
        profile.confidence_level = self._calculate_confidence_level(profile)

        # Update favorite genres
        profile.favorite_genres = self._extract_favorite_genres(recent_interactions)

        logger.info(
            f"Updated profile for {profile.user_id}: {len(new_preferences)} preferences detected"
        )

        # Force save after profile updates
        self._save_data()

    def _analyze_genre_preferences(
        self, interactions: List[UserInteraction]
    ) -> List[PreferenceInsight]:
        """Analyze genre preferences from interactions"""
        preferences = []

        # Count genres
        genre_counter = Counter()
        for interaction in interactions:
            genres = interaction.game_data.get("genres", [])
            for genre in genres:
                genre_counter[genre] += 1

        total_interactions = len(interactions)

        # Detect strong genre preferences
        for genre, count in genre_counter.most_common(5):
            if count >= 2 and count / total_interactions >= 0.4:  # 40%+ of interactions
                confidence = min(count / total_interactions * 1.5, 1.0)

                # Map to preference patterns
                pattern = None
                if genre.lower() in ["puzzle", "brain training"]:
                    pattern = GamePreferencePattern.PUZZLE_LOVER
                elif genre.lower() in ["action", "shooter", "fighting"]:
                    pattern = GamePreferencePattern.ACTION_SEEKER
                elif genre.lower() in ["role-playing", "rpg"]:
                    pattern = GamePreferencePattern.RPG_FANATIC
                elif genre.lower() in ["platformer", "metroidvania"]:
                    pattern = GamePreferencePattern.PLATFORMER_FAN
                elif genre.lower() in ["indie", "independent"]:
                    pattern = GamePreferencePattern.INDIE_ENTHUSIAST

                if pattern:
                    preferences.append(
                        PreferenceInsight(
                            pattern=pattern,
                            confidence=confidence,
                            evidence=[
                                f"Analyzed {count} {genre} games out of {total_interactions} total"
                            ],
                            weight=count / total_interactions,
                        )
                    )

        return preferences

    def _analyze_price_sensitivity(
        self, interactions: List[UserInteraction]
    ) -> List[PreferenceInsight]:
        """Analyze price sensitivity patterns"""
        preferences = []

        # Extract prices from interactions
        prices = []
        discount_seeking = 0

        for interaction in interactions:
            game_data = interaction.game_data
            try:
                from utils.price_calculator import extract_price

                current_price = extract_price(
                    game_data.get("current_eshop_price", "N/A")
                )
                msrp = extract_price(game_data.get("MSRP", "N/A"))

                if current_price:
                    prices.append(current_price)

                # Check if user is looking at games on sale
                if (
                    current_price and msrp and current_price < msrp * 0.8
                ):  # 20%+ discount
                    discount_seeking += 1

            except:
                continue

        if len(prices) >= 3:
            avg_price = sum(prices) / len(prices)

            # Budget conscious if average price is low
            if avg_price <= 25:
                preferences.append(
                    PreferenceInsight(
                        pattern=GamePreferencePattern.BUDGET_CONSCIOUS,
                        confidence=min(1.0, (30 - avg_price) / 15),
                        evidence=[f"Average analyzed game price: ${avg_price:.2f}"],
                        weight=1.0,
                    )
                )

            # Sale hunter if frequently looks at discounted games
            if discount_seeking / len(interactions) >= 0.5:
                preferences.append(
                    PreferenceInsight(
                        pattern=GamePreferencePattern.SALE_HUNTER,
                        confidence=discount_seeking / len(interactions),
                        evidence=[
                            f"Analyzed {discount_seeking} discounted games out of {len(interactions)}"
                        ],
                        weight=discount_seeking / len(interactions),
                    )
                )

        return preferences

    def _analyze_quality_preferences(
        self, interactions: List[UserInteraction]
    ) -> List[PreferenceInsight]:
        """Analyze quality threshold preferences"""
        preferences = []

        # Extract scores
        scores = []
        for interaction in interactions:
            game_data = interaction.game_data
            try:
                from utils.price_calculator import extract_score

                metacritic = extract_score(game_data.get("metacritic_score", "0"))
                opencritic = extract_score(game_data.get("opencritic_score", "0"))

                best_score = max(metacritic or 0, opencritic or 0)
                if best_score > 0:
                    scores.append(best_score)
            except:
                continue

        if len(scores) >= 3:
            avg_score = sum(scores) / len(scores)

            # Quality focused if consistently analyzes high-rated games
            if avg_score >= 80:
                preferences.append(
                    PreferenceInsight(
                        pattern=GamePreferencePattern.QUALITY_FOCUSED,
                        confidence=min(1.0, (avg_score - 75) / 20),
                        evidence=[f"Average analyzed game score: {avg_score:.1f}"],
                        weight=1.0,
                    )
                )

        return preferences

    def _calculate_confidence_level(self, profile: DynamicUserProfile) -> str:
        """Calculate overall confidence level of the profile"""

        if profile.total_interactions < 3:
            return "low"
        elif profile.total_interactions < 7:
            return "medium"
        elif profile.total_interactions < 15:
            return "high"
        else:
            return "very_high"

    def _extract_favorite_genres(
        self, interactions: List[UserInteraction]
    ) -> List[Tuple[str, float]]:
        """Extract favorite genres with confidence scores"""

        genre_counter = Counter()
        for interaction in interactions:
            genres = interaction.game_data.get("genres", [])
            for genre in genres:
                genre_counter[genre] += 1

        total = len(interactions)
        favorite_genres = []

        for genre, count in genre_counter.most_common(10):
            confidence = count / total
            if confidence >= 0.2:  # At least 20% of interactions
                favorite_genres.append((genre, confidence))

        return favorite_genres

    def get_smart_user_profile(
        self, user_id: Optional[str] = None
    ) -> Optional[DynamicUserProfile]:
        """Get the smart user profile for a user"""

        if not user_id:
            user_id = self.analytics.current_user_id

        return self.user_profiles.get(user_id)

    def get_personalized_recommendation_adjustments(
        self, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get recommendation adjustments based on learned user preferences"""

        profile = self.get_smart_user_profile(user_id)
        if not profile or profile.confidence_level == "low":
            return {"adjustments": None, "reason": "insufficient_data"}

        adjustments = {
            "weight_adjustments": {},
            "preference_boosts": {},
            "personalized_thresholds": {},
            "detected_patterns": [
                p.pattern.value for p in profile.detected_preferences
            ],
        }

        # Adjust recommendation weights based on detected preferences
        for preference in profile.detected_preferences:
            pattern = preference.pattern
            confidence = preference.confidence

            if pattern == GamePreferencePattern.BUDGET_CONSCIOUS:
                adjustments["weight_adjustments"]["price_fit"] = 1.5 * confidence
                adjustments["personalized_thresholds"]["max_acceptable_price"] = 30.0

            elif pattern == GamePreferencePattern.QUALITY_FOCUSED:
                adjustments["weight_adjustments"]["quality_score"] = 1.3 * confidence
                adjustments["personalized_thresholds"]["min_quality_score"] = 80.0

            elif pattern == GamePreferencePattern.SALE_HUNTER:
                adjustments["preference_boosts"]["on_sale"] = 2.0 * confidence

            elif pattern == GamePreferencePattern.INDIE_ENTHUSIAST:
                adjustments["preference_boosts"]["indie_games"] = 1.5 * confidence
                adjustments["personalized_thresholds"]["indie_price_bonus"] = 0.2

        # Add favorite genres
        for genre, confidence in profile.favorite_genres[:3]:  # Top 3 genres
            adjustments["preference_boosts"][f"genre_{genre.lower()}"] = 1.0 + (
                confidence * 0.5
            )

        return {
            "adjustments": adjustments,
            "confidence": profile.confidence_level,
            "based_on_interactions": profile.total_interactions,
        }

    def _save_data(self):
        """Save user profiles and interactions to disk"""
        try:
            # Save profiles
            profiles_data = {"profiles": {}, "last_updated": datetime.now().isoformat()}

            for user_id, profile in self.user_profiles.items():
                profiles_data["profiles"][user_id] = {
                    "user_id": profile.user_id,
                    "detected_preferences": [
                        {
                            "pattern": p.pattern.value,
                            "confidence": p.confidence,
                            "evidence": p.evidence,
                            "weight": p.weight,
                        }
                        for p in profile.detected_preferences
                    ],
                    "favorite_genres": profile.favorite_genres,
                    "price_sensitivity": profile.price_sensitivity,
                    "quality_threshold": profile.quality_threshold,
                    "discovered_patterns": profile.discovered_patterns,
                    "last_updated": profile.last_updated.isoformat(),
                    "confidence_level": profile.confidence_level,
                    "total_interactions": profile.total_interactions,
                    "learning_velocity": profile.learning_velocity,
                    "profile_stability": profile.profile_stability,
                }

            with open(self.profiles_file, "w") as f:
                json.dump(profiles_data, f, indent=2)

            # Save recent interactions
            interactions_data = {
                "interactions": [
                    {
                        "game_name": i.game_name,
                        "timestamp": i.timestamp.isoformat(),
                        "interaction_type": i.interaction_type,
                        "game_data": i.game_data,
                        "user_response": i.user_response,
                        "session_context": i.session_context,
                    }
                    for i in self.interaction_history[-100:]  # Keep last 100
                ],
                "last_updated": datetime.now().isoformat(),
            }

            with open(self.interactions_file, "w") as f:
                json.dump(interactions_data, f, indent=2)

            logger.debug("Smart User Profiler data saved")

        except Exception as e:
            logger.error(f"Error saving profiler data: {e}")


# Global instance
_smart_profiler_instance = None


def get_smart_user_profiler() -> SmartUserProfiler:
    """Get global smart user profiler instance"""
    global _smart_profiler_instance
    if _smart_profiler_instance is None:
        _smart_profiler_instance = SmartUserProfiler()
    return _smart_profiler_instance


def record_user_interaction(
    game_name: str, game_data: Dict[str, Any], interaction_type: str = "analyzed"
) -> str:
    """Convenience function to record user interaction"""
    profiler = get_smart_user_profiler()
    return profiler.record_interaction(game_name, game_data, interaction_type)


def get_personalized_adjustments(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to get personalized recommendation adjustments"""
    profiler = get_smart_user_profiler()
    return profiler.get_personalized_recommendation_adjustments(user_id)


if __name__ == "__main__":
    # Test the profiler
    profiler = get_smart_user_profiler()
    print("✅ Smart User Profiler initialized successfully")
