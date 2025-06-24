#!/usr/bin/env python3

"""
Collection-Based Recommendation Engine for AutoGen DekuDeals
===========================================================

Advanced recommendation system that analyzes user's game collection
to generate personalized recommendations based on owned games.

Features:
- Collection preference analysis (genres, developers, themes)
- Similarity-based recommendations
- Discovery recommendations (new genres/developers)
- Complementary recommendations (fill collection gaps)
- ML integration with Smart User Profiler
- Multiple recommendation types and algorithms

Phase 7.3.2 - Collection-Based Game Recommendations
Author: AutoGen DekuDeals Team
Version: 1.0.0
"""

import json
import logging
import numpy as np
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import existing system components
from .game_collection_manager import GameCollectionManager, GameEntry, GameStatus
from .smart_user_profiler import SmartUserProfiler, GamePreferencePattern
from .recommendation_engine import RecommendationEngine, UserProfile, UserPreference
from .user_management import UserManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    """Types of collection-based recommendations."""

    SIMILAR = "similar"  # Games similar to highly-rated owned games
    DISCOVERY = "discovery"  # New genres/developers to explore
    DEVELOPER = "developer"  # More games from favorite developers
    COMPLEMENTARY = "complementary"  # Games that complement collection gaps
    THEME_BASED = "theme_based"  # Games with similar themes/mechanics
    RATING_BASED = "rating_based"  # Games matching user's rating patterns


class RecommendationConfidence(Enum):
    """Confidence levels for recommendations."""

    VERY_HIGH = "very_high"  # 90%+ confidence
    HIGH = "high"  # 75-90% confidence
    MEDIUM = "medium"  # 60-75% confidence
    LOW = "low"  # 40-60% confidence
    VERY_LOW = "very_low"  # <40% confidence


@dataclass
class CollectionPreferences:
    """Analyzed preferences from user's collection."""

    # Genre preferences with confidence scores
    favorite_genres: List[Tuple[str, float]] = field(default_factory=list)
    underrepresented_genres: List[str] = field(default_factory=list)
    avoided_genres: List[str] = field(default_factory=list)

    # Developer preferences
    favorite_developers: List[Tuple[str, float]] = field(default_factory=list)
    developer_diversity_score: float = 0.0

    # Rating patterns
    average_rating: float = 0.0
    rating_distribution: Dict[int, int] = field(default_factory=dict)
    high_rated_games: List[str] = field(default_factory=list)  # Games with rating >= 8

    # Price preferences
    preferred_price_range: Tuple[float, float] = (0.0, 100.0)
    price_sensitivity: float = 0.5  # 0.0 = not sensitive, 1.0 = very sensitive

    # Platform preferences
    platform_preferences: Dict[str, int] = field(default_factory=dict)

    # Collection characteristics
    collection_size: int = 0
    completion_rate: float = 0.0  # Percentage of completed games
    diversity_score: float = 0.0  # How diverse the collection is

    # Temporal patterns
    recent_preferences: List[str] = field(default_factory=list)  # Recent additions
    seasonal_patterns: Dict[str, List[str]] = field(default_factory=dict)

    # Analysis metadata
    confidence_level: RecommendationConfidence = RecommendationConfidence.MEDIUM
    analysis_date: datetime = field(default_factory=datetime.now)
    games_analyzed: int = 0


@dataclass
class CollectionRecommendation:
    """Single recommendation based on collection analysis."""

    game_title: str
    recommendation_type: RecommendationType
    similarity_score: float  # 0.0 to 1.0
    confidence: RecommendationConfidence

    # Recommendation reasons
    primary_reason: str
    detailed_reasons: List[str] = field(default_factory=list)
    match_details: Dict[str, Any] = field(default_factory=dict)

    # Comparison to collection
    similar_owned_games: List[str] = field(default_factory=list)
    genre_matches: List[str] = field(default_factory=list)
    developer_matches: List[str] = field(default_factory=list)

    # Scoring details
    base_score: float = 0.0
    preference_bonus: float = 0.0
    diversity_bonus: float = 0.0
    ml_adjustment: float = 0.0
    final_score: float = 0.0

    # Game information
    game_data: Dict[str, Any] = field(default_factory=dict)

    # Warnings and notes
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)


class CollectionRecommendationEngine:
    """
    Advanced collection-based recommendation engine.

    Analyzes user's game collection to generate personalized recommendations
    based on owned games, preferences, and ML-detected patterns.
    """

    def __init__(self, data_dir: str = "collection_recommendations"):
        """Initialize the Collection Recommendation Engine."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Initialize system components
        self.collection_manager = GameCollectionManager()
        self.smart_profiler = SmartUserProfiler()
        self.recommendation_engine = RecommendationEngine()
        self.user_manager = UserManager()

        # Algorithm weights for recommendation scoring
        self.similarity_weights = {
            "genre_match": 0.3,
            "developer_match": 0.2,
            "rating_correlation": 0.2,
            "theme_similarity": 0.15,
            "price_match": 0.1,
            "platform_match": 0.05,
        }

        # Recommendation type configurations (more realistic requirements)
        self.recommendation_configs = {
            RecommendationType.SIMILAR: {
                "min_collection_size": 3,
                "min_rating_threshold": 6.0,  # Lower from 7.0 to 6.0
                "similarity_threshold": 0.5,  # Lower from 0.6 to 0.5
                "max_recommendations": 10,
            },
            RecommendationType.DISCOVERY: {
                "min_collection_size": 5,
                "diversity_threshold": 0.3,  # Lower from 0.5 to 0.3
                "exploration_factor": 0.7,  # Lower from 0.8 to 0.7
                "max_recommendations": 8,
            },
            RecommendationType.DEVELOPER: {
                "min_games_per_developer": 1,  # Lower from 2 to 1
                "min_avg_rating": 5.0,  # Lower from 6.0 to 5.0
                "max_recommendations": 6,
            },
            RecommendationType.COMPLEMENTARY: {
                "min_collection_size": 6,  # Lower from 8 to 6
                "gap_threshold": 0.2,  # Lower from 0.3 to 0.2
                "max_recommendations": 5,
            },
        }

        # Cache for analyzed preferences
        self.preferences_cache: Dict[str, CollectionPreferences] = {}
        self.cache_ttl = timedelta(hours=24)  # Cache for 24 hours

        logger.info("✅ Collection Recommendation Engine initialized")

    def analyze_collection_preferences(
        self, user_id: Optional[str] = None
    ) -> CollectionPreferences:
        """
        Analyze user's collection to extract preferences and patterns.

        Args:
            user_id: Optional user ID, defaults to current user

        Returns:
            CollectionPreferences: Analyzed preferences from collection
        """
        if not user_id:
            user_id = self._get_current_user_id()

        # Check cache first
        cache_key = f"{user_id}_preferences"
        if cache_key in self.preferences_cache:
            cached_prefs = self.preferences_cache[cache_key]
            if datetime.now() - cached_prefs.analysis_date < self.cache_ttl:
                logger.debug(f"Using cached preferences for user {user_id}")
                return cached_prefs

        # Get user's collection
        collection = self._get_user_collection(user_id)
        if not collection:
            logger.warning(f"No collection found for user {user_id}")
            return CollectionPreferences()

        logger.info(
            f"🔍 Analyzing collection preferences for user {user_id} ({len(collection)} games)"
        )

        # Initialize preferences
        preferences = CollectionPreferences()
        preferences.collection_size = len(collection)
        preferences.games_analyzed = len(collection)

        # Analyze different aspects
        self._analyze_genre_preferences(collection, preferences)
        self._analyze_developer_preferences(collection, preferences)
        self._analyze_rating_patterns(collection, preferences)
        self._analyze_price_preferences(collection, preferences)
        self._analyze_platform_preferences(collection, preferences)
        self._analyze_collection_characteristics(collection, preferences)
        self._analyze_temporal_patterns(collection, preferences)

        # Calculate overall confidence
        preferences.confidence_level = self._calculate_confidence_level(preferences)

        # Cache the results
        self.preferences_cache[cache_key] = preferences

        logger.info(
            f"✅ Collection analysis complete: {len(preferences.favorite_genres)} genre preferences, "
            f"{len(preferences.favorite_developers)} developer preferences"
        )

        return preferences

    def generate_recommendations(
        self,
        recommendation_type: RecommendationType = RecommendationType.SIMILAR,
        max_recommendations: int = 10,
        candidate_games: Optional[List[Dict[str, Any]]] = None,
        user_id: Optional[str] = None,
    ) -> List[CollectionRecommendation]:
        """
        Generate collection-based recommendations.

        Args:
            recommendation_type: Type of recommendations to generate
            max_recommendations: Maximum number of recommendations
            candidate_games: Optional list of candidate games, will fetch if not provided
            user_id: Optional user ID, defaults to current user

        Returns:
            List[CollectionRecommendation]: Generated recommendations
        """
        if not user_id:
            user_id = self._get_current_user_id()

        # Analyze collection preferences
        preferences = self.analyze_collection_preferences(user_id)

        # Check if collection meets minimum requirements
        config = self.recommendation_configs.get(recommendation_type, {})
        min_size = config.get("min_collection_size", 3)

        if preferences.collection_size < min_size:
            logger.warning(
                f"Collection too small for {recommendation_type.value} recommendations "
                f"({preferences.collection_size} < {min_size})"
            )
            return []

        # Get candidate games if not provided
        if not candidate_games:
            candidate_games = self._get_candidate_games(
                recommendation_type, preferences
            )

        if not candidate_games:
            logger.warning("No candidate games available for recommendations")
            return []

        logger.info(
            f"🎯 Generating {recommendation_type.value} recommendations for {len(candidate_games)} candidates"
        )

        # Generate recommendations based on type
        recommendations = []

        if recommendation_type == RecommendationType.SIMILAR:
            recommendations = self._generate_similar_recommendations(
                preferences, candidate_games, max_recommendations
            )
        elif recommendation_type == RecommendationType.DISCOVERY:
            recommendations = self._generate_discovery_recommendations(
                preferences, candidate_games, max_recommendations
            )
        elif recommendation_type == RecommendationType.DEVELOPER:
            recommendations = self._generate_developer_recommendations(
                preferences, candidate_games, max_recommendations
            )
        elif recommendation_type == RecommendationType.COMPLEMENTARY:
            recommendations = self._generate_complementary_recommendations(
                preferences, candidate_games, max_recommendations
            )
        else:
            logger.error(f"Unsupported recommendation type: {recommendation_type}")
            return []

        # Apply ML adjustments from Smart User Profiler
        recommendations = self._apply_ml_adjustments(recommendations, user_id)

        # Sort by final score and return top recommendations
        recommendations.sort(key=lambda x: x.final_score, reverse=True)
        final_recommendations = recommendations[:max_recommendations]

        logger.info(
            f"✅ Generated {len(final_recommendations)} {recommendation_type.value} recommendations"
        )

        return final_recommendations

    def _get_current_user_id(self) -> str:
        """Get current user ID from Multi-User system."""
        try:
            current_user = self.user_manager.get_current_user()
            if current_user:
                return current_user.user_id
        except Exception as e:
            logger.debug(f"Could not get current user: {e}")
        return "default_user"

    def _get_user_collection(self, user_id: str) -> List[GameEntry]:
        """Get user's collection from GameCollectionManager."""
        try:
            # Switch to the specified user temporarily
            original_user = self.user_manager.get_current_user()

            # Get collection for the user
            collection = self.collection_manager.get_collection()

            # Filter to only owned and completed games for analysis
            analyzed_collection = [
                game
                for game in collection
                if game.status in [GameStatus.OWNED, GameStatus.COMPLETED]
            ]

            return analyzed_collection

        except Exception as e:
            logger.error(f"Error getting collection for user {user_id}: {e}")
            return []

    def _analyze_genre_preferences(
        self, collection: List[GameEntry], preferences: CollectionPreferences
    ):
        """Analyze genre preferences from collection."""
        genre_ratings = defaultdict(list)
        genre_counts = Counter()

        # Collect genre data from available sources
        for game in collection:
            genres = []

            # Primary source: tags (if available and not empty)
            if hasattr(game, "tags") and game.tags:
                genres.extend(game.tags)

            # Secondary source: extract from notes if they contain genre keywords
            if hasattr(game, "notes") and game.notes:
                genre_keywords = [
                    "action",
                    "adventure",
                    "rpg",
                    "puzzle",
                    "platformer",
                    "indie",
                    "metroidvania",
                    "roguelike",
                    "strategy",
                    "simulation",
                    "sports",
                    "racing",
                    "fighting",
                    "shooter",
                    "horror",
                    "survival",
                ]
                notes_lower = game.notes.lower()
                for keyword in genre_keywords:
                    if keyword in notes_lower:
                        genres.append(keyword.title())

            # Fallback: use platform as a broad category
            if not genres and game.platform:
                genres = [game.platform]

            # If still no genres, create a general category
            if not genres:
                genres = ["General"]

            for genre in genres:
                genre_counts[genre] += 1
                if game.user_rating:
                    genre_ratings[genre].append(game.user_rating)

        # Calculate favorite genres with more lenient requirements
        favorite_genres = []
        for genre in genre_counts:  # Loop over ALL genres, not just rated ones
            ratings = genre_ratings.get(genre, [])  # Get ratings (might be empty)
            frequency = genre_counts[genre] / len(collection)

            if len(ratings) >= 1:  # At least 1 rated game
                avg_rating = sum(ratings) / len(ratings)
                # Combine rating and frequency for preference score
                preference_score = (avg_rating / 10.0) * 0.7 + frequency * 0.3

                if avg_rating >= 6.0:  # Lower threshold: 6.0 instead of 7.0
                    favorite_genres.append((genre, preference_score))
            else:
                # For unrated games, use frequency-based scoring
                if frequency >= 0.15:  # At least 15% of collection
                    # Default to neutral rating for unrated games
                    preference_score = (
                        0.5 * 0.7 + frequency * 0.3
                    )  # Assume 5.0/10 rating
                    favorite_genres.append((genre, preference_score))

        # Sort by preference score
        favorite_genres.sort(key=lambda x: x[1], reverse=True)
        preferences.favorite_genres = favorite_genres[:8]  # Top 8 genres

        # Identify underrepresented genres (low frequency but available)
        all_genres = set(genre_counts.keys())
        represented_genres = {genre for genre, _ in favorite_genres}
        underrepresented = list(all_genres - represented_genres)
        preferences.underrepresented_genres = underrepresented[:5]  # Top 5 gaps

        # Identify avoided genres (low ratings)
        avoided_genres = []
        for genre, ratings in genre_ratings.items():
            if len(ratings) >= 1:  # At least 1 rating
                avg_rating = sum(ratings) / len(ratings)
                if avg_rating < 5.0:  # Low average rating
                    avoided_genres.append(genre)

        preferences.avoided_genres = avoided_genres

    def _analyze_developer_preferences(
        self, collection: List[GameEntry], preferences: CollectionPreferences
    ):
        """Analyze developer preferences from collection."""
        developer_ratings = defaultdict(list)
        developer_counts = Counter()

        # Collect developer data from available sources
        for game in collection:
            developers = []

            # Try to extract developer info from notes
            if hasattr(game, "notes") and game.notes:
                # Look for common developer patterns in notes
                notes = game.notes.lower()
                developer_keywords = [
                    "nintendo",
                    "capcom",
                    "team cherry",
                    "supergiant",
                    "playdead",
                    "motion twin",
                    "moon studios",
                    "ori",
                    "celeste",
                    "matt makes games",
                    "indie",
                    "ubisoft",
                    "ea",
                    "activision",
                    "bethesda",
                    "square enix",
                ]
                for keyword in developer_keywords:
                    if keyword in notes:
                        developers.append(keyword.title())

            # Extract potential developer from game title (common patterns)
            if hasattr(game, "title") and game.title:
                title_lower = game.title.lower()
                # Some games have developer in title
                if "team cherry" in title_lower or "hollow knight" in title_lower:
                    developers.append("Team Cherry")
                elif (
                    "supergiant" in title_lower
                    or "hades" in title_lower
                    or "bastion" in title_lower
                ):
                    developers.append("Supergiant Games")
                elif (
                    "nintendo" in title_lower
                    or "mario" in title_lower
                    or "zelda" in title_lower
                ):
                    developers.append("Nintendo")
                elif (
                    "playdead" in title_lower
                    or "inside" in title_lower
                    or "limbo" in title_lower
                ):
                    developers.append("Playdead")

            # Fallback: use platform as publisher/developer category
            if not developers and game.platform:
                if "nintendo" in game.platform.lower():
                    developers.append("Nintendo Platform")
                elif "steam" in game.platform.lower():
                    developers.append("PC/Steam Platform")
                else:
                    developers.append(f"{game.platform} Platform")

            # If still no developers, create a general category based on import source
            if not developers:
                if hasattr(game, "import_source"):
                    developers.append(f"{game.import_source.value.title()} Games")
                else:
                    developers.append("Independent Games")

            for developer in developers:
                developer_counts[developer] += 1
                if game.user_rating:
                    developer_ratings[developer].append(game.user_rating)

        # Calculate favorite developers with more lenient requirements
        favorite_developers = []
        for (
            developer
        ) in developer_counts:  # Loop over ALL developers, not just rated ones
            ratings = developer_ratings.get(
                developer, []
            )  # Get ratings (might be empty)
            game_count = developer_counts[developer]

            if len(ratings) >= 1:  # At least 1 rated game
                avg_rating = sum(ratings) / len(ratings)
                # Preference score based on rating and number of games
                preference_score = (avg_rating / 10.0) * 0.8 + min(
                    game_count / 3, 1.0
                ) * 0.2

                if avg_rating >= 6.0:  # Lower threshold: 6.0 instead of 7.0
                    favorite_developers.append((developer, preference_score))
            else:
                # For unrated games, use frequency-based scoring
                if game_count >= 2:  # At least 2 games from this developer
                    # Default to neutral rating for unrated games
                    preference_score = (
                        0.5 * 0.8 + min(game_count / 3, 1.0) * 0.2
                    )  # Assume 5.0/10 rating
                    favorite_developers.append((developer, preference_score))

        # Sort by preference score
        favorite_developers.sort(key=lambda x: x[1], reverse=True)
        preferences.favorite_developers = favorite_developers[:5]  # Top 5 developers

        # Calculate developer diversity (more realistic calculation)
        unique_developers = len(set(developer_counts.keys()))
        total_games = len(collection)
        preferences.developer_diversity_score = min(
            unique_developers / max(total_games * 0.3, 1), 1.0
        )  # More realistic expectation

    def _analyze_rating_patterns(
        self, collection: List[GameEntry], preferences: CollectionPreferences
    ):
        """Analyze rating patterns from collection."""
        ratings = [game.user_rating for game in collection if game.user_rating]

        if not ratings:
            return

        # Calculate average rating
        preferences.average_rating = sum(ratings) / len(ratings)

        # Calculate rating distribution
        rating_dist = Counter()
        for rating in ratings:
            rating_bucket = int(rating)  # Group by integer ratings
            rating_dist[rating_bucket] += 1

        preferences.rating_distribution = dict(rating_dist)

        # Identify high-rated games (8+)
        high_rated_games = [
            game.title
            for game in collection
            if game.user_rating and game.user_rating >= 8.0
        ]
        preferences.high_rated_games = high_rated_games

    def _analyze_price_preferences(
        self, collection: List[GameEntry], preferences: CollectionPreferences
    ):
        """Analyze price preferences from collection."""
        prices = []

        for game in collection:
            if game.purchase_price:
                prices.append(game.purchase_price)
            elif game.current_price:
                prices.append(game.current_price)

        if prices:
            # Calculate preferred price range (25th to 75th percentile)
            sorted_prices = sorted(prices)
            q1_idx = len(sorted_prices) // 4
            q3_idx = 3 * len(sorted_prices) // 4

            min_price = (
                sorted_prices[q1_idx]
                if q1_idx < len(sorted_prices)
                else sorted_prices[0]
            )
            max_price = (
                sorted_prices[q3_idx]
                if q3_idx < len(sorted_prices)
                else sorted_prices[-1]
            )

            preferences.preferred_price_range = (min_price, max_price)

            # Calculate price sensitivity (lower average price = higher sensitivity)
            avg_price = sum(prices) / len(prices)
            preferences.price_sensitivity = max(
                0.0, min(1.0, 1.0 - (avg_price / 100.0))
            )

    def _analyze_platform_preferences(
        self, collection: List[GameEntry], preferences: CollectionPreferences
    ):
        """Analyze platform preferences from collection."""
        platform_counts = Counter()

        for game in collection:
            platform_counts[game.platform] += 1

        preferences.platform_preferences = dict(platform_counts)

    def _analyze_collection_characteristics(
        self, collection: List[GameEntry], preferences: CollectionPreferences
    ):
        """Analyze overall collection characteristics."""
        if not collection:
            return

        # Calculate completion rate
        completed_games = len(
            [game for game in collection if game.status == GameStatus.COMPLETED]
        )
        preferences.completion_rate = completed_games / len(collection)

        # Calculate diversity score based on genre and developer spread
        genre_diversity = len(
            set(tag for game in collection for tag in (game.tags or []))
        )
        developer_diversity = len(
            set(getattr(game, "developer", "Unknown") for game in collection)
        )

        # Normalize diversity scores
        max_possible_diversity = max(len(collection), 10)  # Reasonable max
        normalized_genre_diversity = min(genre_diversity / max_possible_diversity, 1.0)
        normalized_dev_diversity = min(
            developer_diversity / max_possible_diversity, 1.0
        )

        preferences.diversity_score = (
            normalized_genre_diversity + normalized_dev_diversity
        ) / 2

    def _analyze_temporal_patterns(
        self, collection: List[GameEntry], preferences: CollectionPreferences
    ):
        """Analyze temporal patterns in collection."""
        # Get recent additions (last 3 months)
        recent_cutoff = datetime.now() - timedelta(days=90)
        recent_games = [game for game in collection if game.date_added >= recent_cutoff]

        # Extract preferences from recent games
        recent_preferences = []
        for game in recent_games:
            if game.tags:
                recent_preferences.extend(game.tags)

        # Get most common recent preferences
        recent_counter = Counter(recent_preferences)
        preferences.recent_preferences = [
            genre for genre, _ in recent_counter.most_common(5)
        ]

    def _calculate_confidence_level(
        self, preferences: CollectionPreferences
    ) -> RecommendationConfidence:
        """Calculate confidence level for recommendations based on collection analysis."""
        confidence_factors = []

        # Collection size factor
        size_factor = min(preferences.collection_size / 20, 1.0)  # Max at 20 games
        confidence_factors.append(size_factor)

        # Rating coverage factor
        rated_games = len([game for game in preferences.rating_distribution.values()])
        rating_factor = (
            min(rated_games / preferences.collection_size, 1.0)
            if preferences.collection_size > 0
            else 0
        )
        confidence_factors.append(rating_factor)

        # Preference clarity factor
        preference_factor = min(
            len(preferences.favorite_genres) / 5, 1.0
        )  # Max at 5 genres
        confidence_factors.append(preference_factor)

        # Diversity factor (balanced collections are more reliable)
        diversity_factor = preferences.diversity_score
        confidence_factors.append(diversity_factor)

        # Overall confidence
        overall_confidence = sum(confidence_factors) / len(confidence_factors)

        if overall_confidence >= 0.9:
            return RecommendationConfidence.VERY_HIGH
        elif overall_confidence >= 0.75:
            return RecommendationConfidence.HIGH
        elif overall_confidence >= 0.6:
            return RecommendationConfidence.MEDIUM
        elif overall_confidence >= 0.4:
            return RecommendationConfidence.LOW
        else:
            return RecommendationConfidence.VERY_LOW

    def _get_candidate_games(
        self,
        recommendation_type: RecommendationType,
        preferences: CollectionPreferences,
    ) -> List[Dict[str, Any]]:
        """Get candidate games for recommendations based on type and preferences."""
        logger.info(
            f"Getting candidate games for {recommendation_type.value} recommendations"
        )

        try:
            # Import the scraping function
            from agent_tools import scrape_dekudeals_category

            # Get user's owned games to filter out
            owned_games = self._get_owned_games_filter()

            candidates = []

            # Get games from different DekuDeals categories based on recommendation type
            if recommendation_type == RecommendationType.SIMILAR:
                # For similar recommendations, get popular and highly-rated games
                categories = ["hottest", "most-wanted", "highest-rated"]
                games_per_category = 15

            elif recommendation_type == RecommendationType.DISCOVERY:
                # For discovery, focus on diverse categories - use actual DekuDeals categories
                categories = [
                    "recently-released",
                    "upcoming-releases",
                    "staff-picks",
                    "trending",
                ]
                games_per_category = 12

            elif recommendation_type == RecommendationType.DEVELOPER:
                # For developer recs, focus on popular and high-rated games
                categories = ["hottest", "highest-rated", "staff-picks"]
                games_per_category = 15

            elif recommendation_type == RecommendationType.COMPLEMENTARY:
                # For complementary, get diverse selection from multiple categories
                categories = [
                    "hottest",
                    "recently-released",
                    "staff-picks",
                    "highest-rated",
                    "most-wanted",
                ]
                games_per_category = 10

            else:
                # Default selection
                categories = ["hottest", "recently-released"]
                games_per_category = 20

            # Scrape games from selected categories
            for category in categories:
                try:
                    result = scrape_dekudeals_category(
                        category=category,
                        max_games=games_per_category,
                        include_details=False,
                    )

                    if result.get("success", False):
                        category_games = result.get("games", [])

                        # Filter out owned games
                        filtered_games = []
                        for game in category_games:
                            game_title = game.get("title", "").lower().strip()
                            if game_title and game_title not in owned_games:
                                # Add category info for scoring
                                game["source_category"] = category
                                filtered_games.append(game)

                        candidates.extend(filtered_games)
                        logger.info(
                            f"Found {len(filtered_games)} new candidates from {category}"
                        )

                    else:
                        logger.warning(
                            f"Failed to scrape category {category}: {result.get('error', 'Unknown error')}"
                        )

                except Exception as e:
                    logger.error(f"Error scraping category {category}: {e}")
                    continue

            # Remove duplicates based on title
            unique_candidates = []
            seen_titles = set()

            for game in candidates:
                title = game.get("title", "").lower().strip()
                if title and title not in seen_titles:
                    unique_candidates.append(game)
                    seen_titles.add(title)

            logger.info(
                f"✅ Found {len(unique_candidates)} unique candidate games for {recommendation_type.value} recommendations"
            )

            # Limit to reasonable number to avoid overwhelming the system
            max_candidates = 100
            if len(unique_candidates) > max_candidates:
                # Prioritize games from certain categories
                priority_categories = ["hottest", "highest-rated", "most-wanted"]
                priority_games = [
                    g
                    for g in unique_candidates
                    if g.get("source_category") in priority_categories
                ]
                other_games = [
                    g
                    for g in unique_candidates
                    if g.get("source_category") not in priority_categories
                ]

                # Take priority games first, then fill with others
                unique_candidates = (
                    priority_games[: max_candidates // 2]
                    + other_games[: max_candidates // 2]
                )

            return unique_candidates[:max_candidates]

        except Exception as e:
            logger.error(f"Error getting candidate games: {e}")
            # Fallback: try to get at least some popular games
            try:
                from agent_tools import scrape_dekudeals_category

                result = scrape_dekudeals_category(
                    "hottest", max_games=20, include_details=False
                )
                if result.get("success", False):
                    games = result.get("games", [])
                    owned_games = self._get_owned_games_filter()
                    filtered_games = [
                        g
                        for g in games
                        if g.get("title", "").lower().strip() not in owned_games
                    ]
                    logger.info(
                        f"✅ Fallback: Found {len(filtered_games)} candidate games"
                    )
                    return filtered_games
            except Exception as fallback_error:
                logger.error(f"Fallback candidate retrieval failed: {fallback_error}")

            return []

    def _get_owned_games_filter(self) -> set:
        """Get set of owned game titles (normalized) to filter out from recommendations."""
        try:
            user_id = self._get_current_user_id()
            collection = self._get_user_collection(user_id)

            owned_titles = set()
            for game in collection:
                # Normalize title for comparison
                normalized_title = game.title.lower().strip()
                owned_titles.add(normalized_title)

                # Also add alternative forms
                # Remove common suffixes
                for suffix in [
                    " definitive edition",
                    " ultimate edition",
                    " collection",
                    " remastered",
                    " hd",
                ]:
                    if normalized_title.endswith(suffix):
                        owned_titles.add(normalized_title.replace(suffix, "").strip())

                # Remove common prefixes
                for prefix in ["the ", "a "]:
                    if normalized_title.startswith(prefix):
                        owned_titles.add(normalized_title[len(prefix) :].strip())

            logger.info(
                f"📚 Filtering out {len(owned_titles)} owned games from recommendations"
            )
            return owned_titles

        except Exception as e:
            logger.error(f"Error getting owned games filter: {e}")
            return set()

    def _generate_similar_recommendations(
        self,
        preferences: CollectionPreferences,
        candidate_games: List[Dict[str, Any]],
        max_recommendations: int,
    ) -> List[CollectionRecommendation]:
        """Generate recommendations for games similar to highly-rated owned games."""
        recommendations = []

        if not candidate_games:
            logger.warning("No candidate games available for similar recommendations")
            return recommendations

        logger.info(
            f"Generating similar recommendations from {len(candidate_games)} candidates"
        )

        # Get favorite genres and their scores
        favorite_genres = dict(preferences.favorite_genres[:5])  # Top 5 genres
        high_rated_games = preferences.high_rated_games[:10]  # Top 10 rated games

        for game in candidate_games:
            try:
                # Calculate similarity score
                similarity_score = self._calculate_similarity_score(game, preferences)

                if similarity_score < 0.3:  # Skip games with very low similarity
                    continue

                # Create recommendation
                recommendation = self._create_recommendation(
                    game=game,
                    recommendation_type=RecommendationType.SIMILAR,
                    score=similarity_score,
                    preferences=preferences,
                    reason_type="similar",
                )

                if recommendation:
                    recommendations.append(recommendation)

            except Exception as e:
                logger.error(
                    f"Error processing candidate game {game.get('title', 'Unknown')}: {e}"
                )
                continue

        # Sort by similarity score and return top recommendations
        recommendations.sort(key=lambda x: x.final_score, reverse=True)
        final_recommendations = recommendations[:max_recommendations]

        logger.info(
            f"✅ Generated {len(final_recommendations)} similar recommendations"
        )
        return final_recommendations

    def _calculate_similarity_score(
        self, game: Dict[str, Any], preferences: CollectionPreferences
    ) -> float:
        """Calculate similarity score between a candidate game and user preferences."""
        score = 0.0

        # Genre similarity (40% weight)
        genre_score = self._calculate_genre_similarity(game, preferences)
        score += genre_score * 0.4

        # Developer similarity (20% weight)
        dev_score = self._calculate_developer_similarity(game, preferences)
        score += dev_score * 0.2

        # Rating compatibility (20% weight)
        rating_score = self._calculate_rating_compatibility(game, preferences)
        score += rating_score * 0.2

        # Popularity bonus (10% weight)
        popularity_score = self._calculate_popularity_score(game)
        score += popularity_score * 0.1

        # Category bonus (10% weight)
        category_score = self._calculate_category_score(game)
        score += category_score * 0.1

        return min(1.0, max(0.0, score))  # Clamp between 0 and 1

    def _calculate_genre_similarity(
        self, game: Dict[str, Any], preferences: CollectionPreferences
    ) -> float:
        """Calculate genre similarity score."""
        if not preferences.favorite_genres:
            return 0.5  # Default score if no preferences

        # Get game genres from different sources
        game_genres = set()

        # From game data
        if "genres" in game and game["genres"]:
            if isinstance(game["genres"], list):
                game_genres.update([g.lower() for g in game["genres"]])
            elif isinstance(game["genres"], str):
                game_genres.update(
                    [g.lower().strip() for g in game["genres"].split(",")]
                )

        # From title (common keywords)
        title = game.get("title", "").lower()
        genre_keywords = {
            "action": ["action", "fighter", "shooter", "beat"],
            "adventure": ["adventure", "quest", "journey"],
            "rpg": ["rpg", "role", "fantasy", "dragon", "quest"],
            "strategy": ["strategy", "tactical", "civilization", "war"],
            "puzzle": ["puzzle", "brain", "logic", "tetris"],
            "platformer": ["platform", "mario", "sonic", "jump"],
            "indie": ["indie", "pixel", "retro"],
            "simulation": ["simulation", "sim", "city", "farm"],
        }

        for genre, keywords in genre_keywords.items():
            if any(keyword in title for keyword in keywords):
                game_genres.add(genre)

        if not game_genres:
            return 0.3  # Low score for games without identifiable genres

        # Calculate match score
        match_score = 0.0
        total_preference_weight = sum(score for _, score in preferences.favorite_genres)

        for genre, pref_score in preferences.favorite_genres:
            if genre.lower() in game_genres:
                normalized_pref = (
                    pref_score / total_preference_weight
                    if total_preference_weight > 0
                    else 0
                )
                match_score += normalized_pref

        return min(1.0, match_score)

    def _calculate_developer_similarity(
        self, game: Dict[str, Any], preferences: CollectionPreferences
    ) -> float:
        """Calculate developer similarity score."""
        if not preferences.favorite_developers:
            return 0.5  # Neutral score

        game_title = game.get("title", "").lower()

        # Check for developer patterns in title
        dev_patterns = {
            "nintendo": ["mario", "zelda", "metroid", "kirby", "pokemon", "nintendo"],
            "supergiant": ["hades", "bastion", "transistor", "pyre"],
            "team cherry": ["hollow knight"],
            "indie": ["pixel", "retro", "indie", "8-bit", "16-bit"],
        }

        game_developers = set()
        for dev, patterns in dev_patterns.items():
            if any(pattern in game_title for pattern in patterns):
                game_developers.add(dev)

        # If no specific developer found, assign based on category
        category = game.get("source_category", "")
        if "indie" in category:
            game_developers.add("indie")

        if not game_developers:
            return 0.5  # Neutral score

        # Calculate match score
        for dev, pref_score in preferences.favorite_developers:
            if dev.lower() in [g.lower() for g in game_developers]:
                return min(1.0, pref_score)

        return 0.3  # Low score for unmatched developers

    def _calculate_rating_compatibility(
        self, game: Dict[str, Any], preferences: CollectionPreferences
    ) -> float:
        """Calculate rating compatibility score."""
        if preferences.average_rating == 0:
            return 0.7  # Default score

        # Estimate game quality based on category and title
        estimated_rating = 7.0  # Default

        category = game.get("source_category", "")
        title = game.get("title", "").lower()

        # Adjust based on category
        if "highest-rated" in category:
            estimated_rating = 8.5
        elif "hottest" in category or "most-wanted" in category:
            estimated_rating = 8.0
        elif "indie" in category:
            estimated_rating = 7.5
        elif "recent-releases" in category:
            estimated_rating = 7.0

        # Adjust based on known high-quality titles
        quality_indicators = [
            "award",
            "goty",
            "deluxe",
            "ultimate",
            "remastered",
            "definitive",
            "collection",
            "trilogy",
            "chronicles",
            "legend",
            "final fantasy",
            "zelda",
            "mario",
            "metroid",
        ]

        if any(indicator in title for indicator in quality_indicators):
            estimated_rating += 0.5

        # Calculate compatibility (prefer games close to user's average rating)
        rating_diff = abs(estimated_rating - preferences.average_rating)
        compatibility = max(0.0, 1.0 - (rating_diff / 5.0))  # 5-point scale difference

        return compatibility

    def _calculate_popularity_score(self, game: Dict[str, Any]) -> float:
        """Calculate popularity score based on category."""
        category = game.get("source_category", "")

        popularity_scores = {
            "hottest": 1.0,
            "most-wanted": 0.9,
            "highest-rated": 0.8,
            "recent-releases": 0.7,
            "indie": 0.6,
            "new-releases": 0.6,
            "coming-soon": 0.5,
        }

        return popularity_scores.get(category, 0.5)

    def _calculate_category_score(self, game: Dict[str, Any]) -> float:
        """Calculate category relevance score."""
        category = game.get("source_category", "")

        # Prefer certain categories for similarity recommendations
        preferred_categories = ["hottest", "highest-rated", "most-wanted"]

        if category in preferred_categories:
            return 0.8
        elif category in ["recent-releases", "indie"]:
            return 0.6
        else:
            return 0.4

    def _create_recommendation(
        self,
        game: Dict[str, Any],
        recommendation_type: RecommendationType,
        score: float,
        preferences: CollectionPreferences,
        reason_type: str,
    ) -> Optional[CollectionRecommendation]:
        """Create a CollectionRecommendation object."""
        try:
            title = game.get("title", "Unknown Game")

            # Generate reasons
            reasons = self._generate_recommendation_reasons(
                game, preferences, reason_type
            )
            primary_reason = (
                reasons[0] if reasons else "Matches your gaming preferences"
            )

            # Create recommendation
            recommendation = CollectionRecommendation(
                game_title=title,
                recommendation_type=recommendation_type,
                similarity_score=score,
                confidence=self._determine_confidence(score),
                primary_reason=primary_reason,
                detailed_reasons=reasons,
                base_score=score * 100,
                preference_bonus=0.0,
                diversity_bonus=0.0,
                ml_adjustment=0.0,
                final_score=score * 100,
                game_data=game,
            )

            return recommendation

        except Exception as e:
            logger.error(
                f"Error creating recommendation for {game.get('title', 'Unknown')}: {e}"
            )
            return None

    def _generate_recommendation_reasons(
        self, game: Dict[str, Any], preferences: CollectionPreferences, reason_type: str
    ) -> List[str]:
        """Generate reasons for the recommendation."""
        reasons = []
        title = game.get("title", "Unknown Game")
        category = game.get("source_category", "")
        game_genres = self._extract_game_genres(game)

        if reason_type == "similar":
            # Genre-based reasons for similar games
            if preferences.favorite_genres:
                top_genre = preferences.favorite_genres[0][0]
                matching_genres = [
                    g for g in game_genres if g.lower() == top_genre.lower()
                ]
                if matching_genres:
                    reasons.append(f"Matches your preference for {top_genre} games")

            # Quality match
            if preferences.average_rating >= 8.0:
                reasons.append("High quality game matching your standards")

            # Category-based reasons
            if category == "hottest":
                reasons.append("Currently trending and popular")
            elif category == "highest-rated":
                reasons.append("Highly rated by critics and players")

        elif reason_type == "discovery":
            # Discovery-specific reasons
            if preferences.underrepresented_genres:
                underrep = preferences.underrepresented_genres[0]
                if any(g.lower() == underrep.lower() for g in game_genres):
                    reasons.append(f"Explores {underrep} genre, new to your collection")

            if category == "staff-picks":
                reasons.append("Staff-curated gem to broaden your horizons")
            elif category == "recently-released":
                reasons.append("Recent release with fresh gameplay")
            elif category == "trending":
                reasons.append("Trending game gaining popularity")
            elif category == "upcoming-releases":
                reasons.append("Upcoming title to look forward to")

            reasons.append("Adds variety to your game collection")

        elif reason_type == "developer":
            # Developer-specific reasons
            if preferences.favorite_developers:
                top_dev = preferences.favorite_developers[0][0]
                reasons.append(f"From {top_dev}, a developer you enjoy")

            # Nintendo-specific messaging
            if "nintendo" in title.lower() or any(
                "mario" in title.lower() or "zelda" in title.lower()
                for title in [title]
            ):
                reasons.append("Nintendo first-party quality game")

            if category == "highest-rated":
                reasons.append("Critically acclaimed from your preferred developers")

        elif reason_type == "complementary":
            # Complementary-specific reasons
            represented_genres = set(g[0].lower() for g in preferences.favorite_genres)
            new_genres = [g for g in game_genres if g.lower() not in represented_genres]

            if new_genres:
                reasons.append(
                    f"Fills gap in your collection with {new_genres[0]} gameplay"
                )

            if preferences.diversity_score < 0.5:
                reasons.append("Increases diversity in your game collection")

            reasons.append("Complements your existing games nicely")

        # Universal category-based reasons
        if category == "most-wanted":
            reasons.append("Popular on wishlists")
        elif category == "staff-picks" and reason_type != "discovery":
            reasons.append("Staff-recommended game you might enjoy")

        # Quality baseline for all types
        if preferences.average_rating >= 7.0 and reason_type != "similar":
            reasons.append("Well-reviewed game in your preferred range")

        # Default reason if none generated
        if not reasons:
            reasons.append("Based on your gaming preferences and collection")

        return reasons[:3]  # Limit to top 3 reasons

    def _determine_confidence(self, score: float) -> RecommendationConfidence:
        """Determine confidence level based on similarity score."""
        if score >= 0.9:
            return RecommendationConfidence.VERY_HIGH
        elif score >= 0.8:
            return RecommendationConfidence.HIGH
        elif score >= 0.6:
            return RecommendationConfidence.MEDIUM
        elif score >= 0.4:
            return RecommendationConfidence.LOW
        else:
            return RecommendationConfidence.VERY_LOW

    def _extract_game_genres(self, game: Dict[str, Any]) -> set:
        """Extract genres from game data."""
        game_genres = set()

        # From game data
        if "genres" in game and game["genres"]:
            if isinstance(game["genres"], list):
                game_genres.update([g.lower() for g in game["genres"]])
            elif isinstance(game["genres"], str):
                game_genres.update(
                    [g.lower().strip() for g in game["genres"].split(",")]
                )

        # From title (common keywords)
        title = game.get("title", "").lower()
        genre_keywords = {
            "action": ["action", "fighter", "shooter", "beat"],
            "adventure": ["adventure", "quest", "journey"],
            "rpg": ["rpg", "role", "fantasy", "dragon", "quest"],
            "strategy": ["strategy", "tactical", "civilization", "war"],
            "puzzle": ["puzzle", "brain", "logic", "tetris"],
            "platformer": ["platform", "mario", "sonic", "jump"],
            "indie": ["indie", "pixel", "retro"],
            "simulation": ["simulation", "sim", "city", "farm"],
            "racing": ["racing", "kart", "speed", "motor"],
            "sports": ["sports", "football", "soccer", "tennis"],
            "fighting": ["fighting", "fighter", "combat", "brawl"],
        }

        for genre, keywords in genre_keywords.items():
            if any(keyword in title for keyword in keywords):
                game_genres.add(genre)

        return game_genres

    def _generate_discovery_recommendations(
        self,
        preferences: CollectionPreferences,
        candidate_games: List[Dict[str, Any]],
        max_recommendations: int,
    ) -> List[CollectionRecommendation]:
        """Generate recommendations for discovering new genres/developers."""
        recommendations = []

        if not candidate_games:
            logger.warning("No candidate games available for discovery recommendations")
            return recommendations

        logger.info(
            f"Generating discovery recommendations from {len(candidate_games)} candidates"
        )

        # Get underrepresented genres and avoided genres
        underrepresented = set(
            g.lower() for g in preferences.underrepresented_genres[:5]
        )
        favorite_genres = set(g[0].lower() for g in preferences.favorite_genres[:3])

        # Focus on recent releases and curated picks for discovery
        discovery_categories = [
            "recently-released",
            "upcoming-releases",
            "staff-picks",
            "trending",
        ]

        for game in candidate_games:
            try:
                # Calculate discovery score
                discovery_score = self._calculate_discovery_score(
                    game, preferences, underrepresented, favorite_genres
                )

                if discovery_score < 0.25:  # Skip games with very low discovery value
                    continue

                # Boost games from discovery-focused categories
                category = game.get("source_category", "")
                if category in discovery_categories:
                    discovery_score += 0.15

                # Create recommendation
                recommendation = self._create_recommendation(
                    game=game,
                    recommendation_type=RecommendationType.DISCOVERY,
                    score=discovery_score,
                    preferences=preferences,
                    reason_type="discovery",
                )

                if recommendation:
                    recommendations.append(recommendation)

            except Exception as e:
                logger.error(
                    f"Error processing discovery candidate {game.get('title', 'Unknown')}: {e}"
                )
                continue

        # Sort by discovery score and return top recommendations
        recommendations.sort(key=lambda x: x.final_score, reverse=True)
        final_recommendations = recommendations[:max_recommendations]

        logger.info(
            f"✅ Generated {len(final_recommendations)} discovery recommendations"
        )
        return final_recommendations

    def _calculate_discovery_score(
        self,
        game: Dict[str, Any],
        preferences: CollectionPreferences,
        underrepresented: set,
        favorite_genres: set,
    ) -> float:
        """Calculate discovery score for exploring new genres/types."""
        score = 0.0

        # Get game genres
        game_genres = self._extract_game_genres(game)

        # Bonus for underrepresented genres (40% weight)
        underrep_bonus = 0.0
        for genre in game_genres:
            if genre.lower() in underrepresented:
                underrep_bonus += 0.3
        score += min(underrep_bonus, 0.4) * 0.4

        # Penalty for over-represented genres (reduce familiar choices)
        familiar_penalty = 0.0
        for genre in game_genres:
            if genre.lower() in favorite_genres:
                familiar_penalty += 0.2
        score -= min(familiar_penalty, 0.3) * 0.2

        # Indie/innovation bonus (30% weight)
        innovation_score = self._calculate_innovation_score(game)
        score += innovation_score * 0.3

        # Quality baseline (20% weight) - still want good games
        quality_score = self._calculate_rating_compatibility(game, preferences)
        score += quality_score * 0.2

        # Diversity bonus (10% weight)
        diversity_score = self._calculate_diversity_bonus(game, preferences)
        score += diversity_score * 0.1

        return min(1.0, max(0.0, score))

    def _calculate_innovation_score(self, game: Dict[str, Any]) -> float:
        """Calculate innovation/novelty score."""
        title = game.get("title", "").lower()
        category = game.get("source_category", "")

        # Staff picks and trending games often showcase innovation
        if "staff-picks" in category:
            return 0.8
        elif "recently-released" in category or "upcoming-releases" in category:
            return 0.7
        elif "trending" in category:
            return 0.6

        # Check for innovative keywords in title
        innovation_keywords = [
            "vr",
            "ar",
            "roguelike",
            "procedural",
            "experimental",
            "unique",
            "innovative",
            "creative",
            "artistic",
            "narrative",
            "indie",
            "pixel",
            "retro",  # indie-style keywords
        ]

        if any(keyword in title for keyword in innovation_keywords):
            return 0.7

        return 0.5

    def _calculate_diversity_bonus(
        self, game: Dict[str, Any], preferences: CollectionPreferences
    ) -> float:
        """Calculate bonus for adding diversity to collection."""
        # Games that are different from user's typical choices get bonus
        game_genres = self._extract_game_genres(game)

        # If no genres identified, give neutral score
        if not game_genres:
            return 0.5

        # Calculate how different this is from collection
        familiar_count = 0
        favorite_genres = set(g[0].lower() for g in preferences.favorite_genres)

        for genre in game_genres:
            if genre.lower() in favorite_genres:
                familiar_count += 1

        # More unfamiliar = higher diversity score
        unfamiliarity = 1.0 - (familiar_count / max(len(game_genres), 1))
        return unfamiliarity

    def _generate_developer_recommendations(
        self,
        preferences: CollectionPreferences,
        candidate_games: List[Dict[str, Any]],
        max_recommendations: int,
    ) -> List[CollectionRecommendation]:
        """Generate recommendations from favorite developers."""
        recommendations = []

        if not candidate_games:
            logger.warning("No candidate games available for developer recommendations")
            return recommendations

        if not preferences.favorite_developers:
            logger.warning("No favorite developers identified for recommendations")
            return recommendations

        logger.info(
            f"Generating developer recommendations from {len(candidate_games)} candidates"
        )

        # Get favorite developers
        favorite_devs = dict(preferences.favorite_developers[:3])  # Top 3 developers

        for game in candidate_games:
            try:
                # Calculate developer match score
                dev_score = self._calculate_developer_match_score(
                    game, preferences, favorite_devs
                )

                if dev_score < 0.3:  # Skip games with low developer relevance
                    continue

                # Create recommendation
                recommendation = self._create_recommendation(
                    game=game,
                    recommendation_type=RecommendationType.DEVELOPER,
                    score=dev_score,
                    preferences=preferences,
                    reason_type="developer",
                )

                if recommendation:
                    recommendations.append(recommendation)

            except Exception as e:
                logger.error(
                    f"Error processing developer candidate {game.get('title', 'Unknown')}: {e}"
                )
                continue

        # Sort by developer score and return top recommendations
        recommendations.sort(key=lambda x: x.final_score, reverse=True)
        final_recommendations = recommendations[:max_recommendations]

        logger.info(
            f"✅ Generated {len(final_recommendations)} developer recommendations"
        )
        return final_recommendations

    def _calculate_developer_match_score(
        self,
        game: Dict[str, Any],
        preferences: CollectionPreferences,
        favorite_devs: dict,
    ) -> float:
        """Calculate developer match score."""
        score = 0.0
        game_title = game.get("title", "").lower()
        category = game.get("source_category", "")

        # Check for developer patterns in title
        dev_patterns = {
            "nintendo": [
                "mario",
                "zelda",
                "metroid",
                "kirby",
                "pokemon",
                "nintendo",
                "splatoon",
                "pikmin",
            ],
            "supergiant games": ["hades", "bastion", "transistor", "pyre"],
            "team cherry": ["hollow knight"],
            "indie": ["pixel", "retro", "indie", "8-bit", "16-bit"],
            "nintendo platform": [
                "mario",
                "zelda",
                "metroid",
                "kirby",
                "pokemon",
                "splatoon",
            ],
        }

        game_developers = set()
        for dev, patterns in dev_patterns.items():
            if any(pattern in game_title for pattern in patterns):
                game_developers.add(dev)

        # Category-based developer assignment
        if "staff-picks" in category:
            game_developers.add("curated developers")
            game_developers.add("staff favorites")

        # Check for indie keywords in title for indie developer classification
        if any(
            keyword in game_title
            for keyword in ["indie", "pixel", "retro", "8-bit", "16-bit"]
        ):
            game_developers.add("indie")
            game_developers.add("independent games")

        # Check for matches with favorite developers
        developer_match_score = 0.0
        for fav_dev, pref_score in favorite_devs.items():
            fav_dev_lower = fav_dev.lower()
            for game_dev in game_developers:
                if (
                    fav_dev_lower in game_dev.lower()
                    or game_dev.lower() in fav_dev_lower
                ):
                    developer_match_score = max(developer_match_score, pref_score)

        # Developer match is primary factor (70% weight)
        score += developer_match_score * 0.7

        # Quality compatibility (20% weight)
        quality_score = self._calculate_rating_compatibility(game, preferences)
        score += quality_score * 0.2

        # Popularity bonus (10% weight)
        popularity_score = self._calculate_popularity_score(game)
        score += popularity_score * 0.1

        return min(1.0, max(0.0, score))

    def _generate_complementary_recommendations(
        self,
        preferences: CollectionPreferences,
        candidate_games: List[Dict[str, Any]],
        max_recommendations: int,
    ) -> List[CollectionRecommendation]:
        """Generate recommendations that complement collection gaps."""
        recommendations = []

        if not candidate_games:
            logger.warning(
                "No candidate games available for complementary recommendations"
            )
            return recommendations

        logger.info(
            f"Generating complementary recommendations from {len(candidate_games)} candidates"
        )

        # Identify collection gaps
        collection_gaps = self._identify_collection_gaps(preferences)
        represented_genres = set(g[0].lower() for g in preferences.favorite_genres)

        for game in candidate_games:
            try:
                # Calculate complementary score
                complement_score = self._calculate_complementary_score(
                    game, preferences, collection_gaps, represented_genres
                )

                if complement_score < 0.25:  # Skip games that don't fill gaps
                    continue

                # Create recommendation
                recommendation = self._create_recommendation(
                    game=game,
                    recommendation_type=RecommendationType.COMPLEMENTARY,
                    score=complement_score,
                    preferences=preferences,
                    reason_type="complementary",
                )

                if recommendation:
                    recommendations.append(recommendation)

            except Exception as e:
                logger.error(
                    f"Error processing complementary candidate {game.get('title', 'Unknown')}: {e}"
                )
                continue

        # Sort by complementary score and return top recommendations
        recommendations.sort(key=lambda x: x.final_score, reverse=True)
        final_recommendations = recommendations[:max_recommendations]

        logger.info(
            f"✅ Generated {len(final_recommendations)} complementary recommendations"
        )
        return final_recommendations

    def _identify_collection_gaps(self, preferences: CollectionPreferences) -> dict:
        """Identify gaps in the user's collection."""
        gaps = {
            "missing_genres": [],
            "underrepresented_mechanics": [],
            "style_gaps": [],
        }

        # Common genres that most collections should have
        essential_genres = {
            "action",
            "adventure",
            "rpg",
            "strategy",
            "puzzle",
            "platformer",
            "simulation",
            "racing",
            "sports",
        }

        represented = set(g[0].lower() for g in preferences.favorite_genres)

        # Find missing essential genres
        for genre in essential_genres:
            if genre not in represented:
                gaps["missing_genres"].append(genre)

        # Identify style gaps based on collection characteristics
        if preferences.diversity_score < 0.5:
            gaps["style_gaps"].append("more_diverse_styles")

        if not any(
            "multiplayer" in g or "party" in g or "co-op" in g
            for g, _ in preferences.favorite_genres
        ):
            gaps["underrepresented_mechanics"].append("multiplayer")

        return gaps

    def _calculate_complementary_score(
        self,
        game: Dict[str, Any],
        preferences: CollectionPreferences,
        collection_gaps: dict,
        represented_genres: set,
    ) -> float:
        """Calculate how well a game complements the collection."""
        score = 0.0
        game_genres = self._extract_game_genres(game)

        # Gap-filling bonus (50% weight)
        gap_score = 0.0
        missing_genres = set(collection_gaps.get("missing_genres", []))

        for genre in game_genres:
            if genre.lower() in missing_genres:
                gap_score += 0.4  # Strong bonus for filling genre gaps
            elif genre.lower() not in represented_genres:
                gap_score += 0.2  # Moderate bonus for new genres

        score += min(gap_score, 0.5) * 0.5

        # Quality assurance (25% weight) - still want good games
        quality_score = self._calculate_rating_compatibility(game, preferences)
        score += quality_score * 0.25

        # Diversity bonus (15% weight)
        diversity_bonus = self._calculate_diversity_bonus(game, preferences)
        score += diversity_bonus * 0.15

        # Popularity factor (10% weight) - some recognition is good
        popularity_score = self._calculate_popularity_score(game)
        score += popularity_score * 0.1

        return min(1.0, max(0.0, score))

    def _apply_ml_adjustments(
        self, recommendations: List[CollectionRecommendation], user_id: str
    ) -> List[CollectionRecommendation]:
        """Apply ML adjustments from Smart User Profiler."""
        try:
            # Get ML adjustments from Smart User Profiler
            ml_adjustments = (
                self.smart_profiler.get_personalized_recommendation_adjustments(user_id)
            )

            if not ml_adjustments:
                return recommendations

            # Apply ML adjustments to each recommendation
            for rec in recommendations:
                # Apply genre bonuses
                genre_bonus = 0.0
                if rec.genre_matches:
                    for genre in rec.genre_matches:
                        genre_bonus += ml_adjustments.get("genre_bonuses", {}).get(
                            genre, 0.0
                        )

                # Apply preference multipliers
                preference_multiplier = ml_adjustments.get("preference_multiplier", 1.0)

                # Calculate ML adjustment
                rec.ml_adjustment = genre_bonus * preference_multiplier
                rec.final_score = (
                    rec.base_score
                    + rec.preference_bonus
                    + rec.diversity_bonus
                    + rec.ml_adjustment
                )

                # Ensure score stays within bounds
                rec.final_score = max(0.0, min(100.0, rec.final_score))

            logger.info(
                f"Applied ML adjustments to {len(recommendations)} recommendations"
            )

        except Exception as e:
            logger.error(f"Error applying ML adjustments: {e}")
            # Fallback to base scoring
            for rec in recommendations:
                rec.final_score = (
                    rec.base_score + rec.preference_bonus + rec.diversity_bonus
                )

        return recommendations

    def get_collection_insights(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed insights about user's collection for recommendations."""
        preferences = self.analyze_collection_preferences(user_id)

        insights = {
            "collection_summary": {
                "total_games": preferences.collection_size,
                "average_rating": round(preferences.average_rating, 2),
                "completion_rate": round(preferences.completion_rate * 100, 1),
                "diversity_score": round(preferences.diversity_score * 100, 1),
                "confidence_level": preferences.confidence_level.value,
            },
            "genre_preferences": {
                "favorites": preferences.favorite_genres[:3],
                "underrepresented": preferences.underrepresented_genres[:3],
                "avoided": preferences.avoided_genres,
            },
            "developer_preferences": {
                "favorites": preferences.favorite_developers[:3],
                "diversity_score": round(
                    preferences.developer_diversity_score * 100, 1
                ),
            },
            "rating_patterns": {
                "distribution": preferences.rating_distribution,
                "high_rated_count": len(preferences.high_rated_games),
            },
            "recent_trends": {"recent_preferences": preferences.recent_preferences[:3]},
            "recommendations_readiness": {
                "similar": preferences.collection_size >= 3
                and len(preferences.favorite_genres) >= 1,
                "discovery": preferences.collection_size >= 5,
                "developer": len(preferences.favorite_developers) >= 1,
                "complementary": preferences.collection_size >= 6,
            },
        }

        return insights


def get_collection_recommendation_engine() -> CollectionRecommendationEngine:
    """Get singleton instance of CollectionRecommendationEngine."""
    if not hasattr(get_collection_recommendation_engine, "_instance"):
        get_collection_recommendation_engine._instance = (
            CollectionRecommendationEngine()
        )
    return get_collection_recommendation_engine._instance


# Convenience functions for easy access
def analyze_user_collection_preferences(
    user_id: Optional[str] = None,
) -> CollectionPreferences:
    """Analyze user's collection preferences."""
    engine = get_collection_recommendation_engine()
    return engine.analyze_collection_preferences(user_id)


def generate_collection_recommendations(
    recommendation_type: str = "similar",
    max_recommendations: int = 10,
    user_id: Optional[str] = None,
) -> List[CollectionRecommendation]:
    """Generate collection-based recommendations."""
    engine = get_collection_recommendation_engine()
    rec_type = RecommendationType(recommendation_type.lower())
    return engine.generate_recommendations(
        rec_type, max_recommendations, user_id=user_id
    )


def get_collection_insights(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get collection insights for recommendations."""
    engine = get_collection_recommendation_engine()
    return engine.get_collection_insights(user_id)
