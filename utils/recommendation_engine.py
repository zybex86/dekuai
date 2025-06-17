"""
Recommendation Engine for AutoGen DekuDeals
System rekomendacji dla AutoGen DekuDeals

Point 3 of Phase 2: Integration with recommendation system
Punkt 3 Fazy 2: Integracja z systemem rekomendacji
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class UserPreference(Enum):
    """Enum dla preferencji użytkowników."""

    BARGAIN_HUNTER = "bargain_hunter"  # Szuka najlepszych ofert
    QUALITY_SEEKER = "quality_seeker"  # Priorytet jakości nad ceną
    GENRE_ENTHUSIAST = "genre_enthusiast"  # Skupia się na konkretnych gatunkach
    NEW_RELEASES = "new_releases"  # Chce najnowsze gry
    INDIE_LOVER = "indie_lover"  # Preferuje gry indie
    AAA_GAMER = "aaa_gamer"  # Preferuje gry AAA
    COMPLETIONIST = "completionist"  # Chce długie gry z dużą zawartością
    CASUAL_PLAYER = "casual_player"  # Preferuje krótkie, łatwe gry


class RecommendationReason(Enum):
    """Powody rekomendacji."""

    EXCELLENT_VALUE = "excellent_value"
    HIDDEN_GEM = "hidden_gem"
    PERFECT_MATCH = "perfect_match"
    GREAT_DEAL = "great_deal"
    TRENDING = "trending"
    SIMILAR_GAMES = "similar_games"
    PRICE_DROP = "price_drop"
    CRITICALLY_ACCLAIMED = "critically_acclaimed"


@dataclass
class UserProfile:
    """Profil użytkownika z preferencjami."""

    user_id: str
    primary_preference: UserPreference
    secondary_preferences: List[UserPreference] = field(default_factory=list)
    preferred_genres: List[str] = field(default_factory=list)
    budget_range: Tuple[float, float] = (0.0, 100.0)  # (min, max)
    avoided_genres: List[str] = field(default_factory=list)
    minimum_score: float = 70.0
    maximum_price: float = 100.0
    preferred_platforms: List[str] = field(default_factory=lambda: ["Nintendo Switch"])
    playtime_preference: str = "any"  # "short", "medium", "long", "any"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GameRecommendation:
    """Rekomendacja gry z uzasadnieniem."""

    game_title: str
    recommendation_score: float
    confidence_level: str
    primary_reason: RecommendationReason
    reasons: List[str]
    match_percentage: float
    price_info: Dict[str, Any]
    analysis_summary: str
    personalized_message: str
    warnings: List[str] = field(default_factory=list)


class RecommendationEngine:
    """Główny engine rekomendacji."""

    def __init__(self):
        self.user_profiles: Dict[str, UserProfile] = {}
        self.recommendation_weights = self._initialize_weights()

    def _initialize_weights(self) -> Dict[str, float]:
        """Inicjalizuje wagi dla różnych czynników rekomendacji."""
        return {
            "value_score": 0.25,
            "advanced_score": 0.25,
            "user_preference_match": 0.20,
            "genre_match": 0.15,
            "price_fit": 0.10,
            "quality_score": 0.05,
        }

    def create_user_profile(
        self, user_id: str, primary_preference: UserPreference, **kwargs
    ) -> UserProfile:
        """
        Tworzy profil użytkownika.

        Args:
            user_id: Identyfikator użytkownika
            primary_preference: Główna preferencja użytkownika
            **kwargs: Dodatkowe parametry profilu

        Returns:
            UserProfile: Utworzony profil użytkownika
        """
        profile = UserProfile(
            user_id=user_id, primary_preference=primary_preference, **kwargs
        )

        self.user_profiles[user_id] = profile
        logger.info(
            f"✅ Created user profile for {user_id} with preference {primary_preference.value}"
        )

        return profile

    def get_predefined_profiles(self) -> Dict[str, UserProfile]:
        """Zwraca predefiniowane profile użytkowników."""
        profiles = {
            "bargain_hunter": UserProfile(
                user_id="bargain_hunter",
                primary_preference=UserPreference.BARGAIN_HUNTER,
                budget_range=(0.0, 30.0),
                minimum_score=60.0,
                preferred_genres=["Indie", "Puzzle", "Platformer"],
                playtime_preference="any",
            ),
            "quality_seeker": UserProfile(
                user_id="quality_seeker",
                primary_preference=UserPreference.QUALITY_SEEKER,
                budget_range=(30.0, 100.0),
                minimum_score=85.0,
                preferred_genres=["Action", "Adventure", "Role-Playing"],
                playtime_preference="long",
            ),
            "indie_lover": UserProfile(
                user_id="indie_lover",
                primary_preference=UserPreference.INDIE_LOVER,
                budget_range=(0.0, 40.0),
                minimum_score=75.0,
                preferred_genres=["Indie", "Metroidvania", "Puzzle", "Platformer"],
                playtime_preference="medium",
            ),
            "aaa_gamer": UserProfile(
                user_id="aaa_gamer",
                primary_preference=UserPreference.AAA_GAMER,
                budget_range=(50.0, 200.0),
                minimum_score=80.0,
                preferred_genres=["Action", "Adventure", "Role-Playing", "Shooter"],
                playtime_preference="long",
            ),
            "casual_player": UserProfile(
                user_id="casual_player",
                primary_preference=UserPreference.CASUAL_PLAYER,
                budget_range=(0.0, 50.0),
                minimum_score=70.0,
                preferred_genres=["Puzzle", "Simulation", "Sports"],
                playtime_preference="short",
            ),
        }

        # Dodaj do cache
        self.user_profiles.update(profiles)
        return profiles

    def calculate_recommendation_score(
        self,
        game_data: Dict[str, Any],
        basic_analysis: Dict[str, Any],
        advanced_analysis: Dict[str, Any],
        user_profile: UserProfile,
    ) -> float:
        """
        Oblicza score rekomendacji dla użytkownika.

        Args:
            game_data: Dane gry
            basic_analysis: Podstawowa analiza wartości
            advanced_analysis: Zaawansowana analiza wartości
            user_profile: Profil użytkownika

        Returns:
            float: Score rekomendacji (0-100)
        """
        try:
            # Extract scores from analyses
            basic_score = (
                basic_analysis.get("value_metrics", {}).get("value_score", 0) / 100 * 10
            )
            advanced_score = advanced_analysis.get("comprehensive_analysis", {}).get(
                "comprehensive_score", 0
            )

            # Normalize scores to 0-10 range
            normalized_basic = min(max(basic_score, 0), 10)
            normalized_advanced = min(max(advanced_score, 0), 10)

            # Calculate user preference match
            preference_match = self._calculate_preference_match(
                game_data, advanced_analysis, user_profile
            )

            # Calculate genre match
            genre_match = self._calculate_genre_match(game_data, user_profile)

            # Calculate price fit
            price_fit = self._calculate_price_fit(game_data, user_profile)

            # Calculate quality score
            quality_score = self._calculate_quality_score(game_data, user_profile)

            # Weighted combination
            weights = self.recommendation_weights
            final_score = (
                normalized_basic * weights["value_score"]
                + normalized_advanced * weights["advanced_score"]
                + preference_match * weights["user_preference_match"]
                + genre_match * weights["genre_match"]
                + price_fit * weights["price_fit"]
                + quality_score * weights["quality_score"]
            ) * 10  # Scale to 0-100

            return min(max(final_score, 0), 100)

        except Exception as e:
            logger.error(f"Error calculating recommendation score: {e}")
            return 0.0

    def _calculate_preference_match(
        self,
        game_data: Dict[str, Any],
        advanced_analysis: Dict[str, Any],
        user_profile: UserProfile,
    ) -> float:
        """Oblicza dopasowanie do preferencji użytkownika."""
        match_score = 5.0  # Base score

        primary_pref = user_profile.primary_preference
        market_analysis = advanced_analysis.get("comprehensive_analysis", {}).get(
            "market_analysis", {}
        )
        market_position = market_analysis.get("market_position", "")

        # Dopasowanie do głównej preferencji
        if primary_pref == UserPreference.BARGAIN_HUNTER:
            if "Hidden Gem" in market_position or "Great Deal" in market_position:
                match_score += 3.0
            elif "Excellent Value" in market_position:
                match_score += 2.0
            elif "Overpriced" in market_position or "Expensive" in market_position:
                match_score -= 2.0

        elif primary_pref == UserPreference.QUALITY_SEEKER:
            if "Exceptional" in market_analysis.get("quality_category", ""):
                match_score += 3.0
            elif "Great" in market_analysis.get("quality_category", ""):
                match_score += 2.0
            elif "Poor" in market_analysis.get("quality_category", ""):
                match_score -= 3.0

        elif primary_pref == UserPreference.INDIE_LOVER:
            current_price = game_data.get("current_eshop_price", "")
            if any(price_str in current_price for price_str in ["$", "€", "£"]):
                # Extract price for indie check
                try:
                    price_num = float(
                        current_price.replace("$", "")
                        .replace("€", "")
                        .replace("£", "")
                        .replace(",", ".")
                    )
                    if price_num < 30:
                        match_score += 2.0
                except:
                    pass

        elif primary_pref == UserPreference.AAA_GAMER:
            if "Flagship" in market_position or "Premium" in market_position:
                match_score += 2.0
            elif "Budget" in market_analysis.get("price_category", ""):
                match_score -= 1.0

        return min(max(match_score, 0), 10)

    def _calculate_genre_match(
        self, game_data: Dict[str, Any], user_profile: UserProfile
    ) -> float:
        """Oblicza dopasowanie gatunku."""
        game_genres = game_data.get("genres", [])
        preferred_genres = user_profile.preferred_genres
        avoided_genres = user_profile.avoided_genres

        if not game_genres:
            return 5.0  # Neutral score

        # Check avoided genres
        for genre in avoided_genres:
            if genre in game_genres:
                return 2.0  # Low score for avoided genres

        # Check preferred genres
        match_count = sum(1 for genre in preferred_genres if genre in game_genres)
        if match_count == 0:
            return 4.0  # No match
        elif match_count == 1:
            return 7.0  # One match
        elif match_count >= 2:
            return 9.0  # Multiple matches

        return 5.0

    def _calculate_price_fit(
        self, game_data: Dict[str, Any], user_profile: UserProfile
    ) -> float:
        """Oblicza dopasowanie cenowe."""
        from utils.price_calculator import extract_price

        current_price = extract_price(game_data.get("current_eshop_price", "N/A"))
        if not current_price:
            return 5.0

        min_budget, max_budget = user_profile.budget_range

        if current_price <= min_budget:
            return 8.0  # Very cheap
        elif current_price <= max_budget:
            # Linear interpolation within budget
            ratio = (current_price - min_budget) / (max_budget - min_budget)
            return 8.0 - (ratio * 3.0)  # 8.0 to 5.0
        elif current_price <= max_budget * 1.2:
            return 3.0  # Slightly over budget
        else:
            return 1.0  # Way over budget

    def _calculate_quality_score(
        self, game_data: Dict[str, Any], user_profile: UserProfile
    ) -> float:
        """Oblicza score jakości."""
        from utils.price_calculator import extract_score

        metacritic = extract_score(game_data.get("metacritic_score", "0"))
        opencritic = extract_score(game_data.get("opencritic_score", "0"))

        best_score = max(metacritic or 0, opencritic or 0)

        if best_score >= user_profile.minimum_score:
            return 8.0 + (best_score - user_profile.minimum_score) / 10
        else:
            return max(1.0, best_score / user_profile.minimum_score * 5.0)

    def generate_personalized_recommendations(
        self,
        games_data: List[Dict[str, Any]],
        user_profile: UserProfile,
        max_recommendations: int = 5,
    ) -> List[GameRecommendation]:
        """
        Generuje spersonalizowane rekomendacje.

        Args:
            games_data: Lista danych gier
            user_profile: Profil użytkownika
            max_recommendations: Maksymalna liczba rekomendacji

        Returns:
            List[GameRecommendation]: Lista rekomendacji
        """
        recommendations = []

        for game_data in games_data:
            try:
                # Import here to avoid circular imports
                from agent_tools import (
                    calculate_value_score,
                    calculate_advanced_value_analysis,
                )

                # Get analyses
                basic_analysis = calculate_value_score(game_data)
                advanced_analysis = calculate_advanced_value_analysis(game_data)

                if not basic_analysis.get("success") or not advanced_analysis.get(
                    "success"
                ):
                    continue

                # Calculate recommendation score
                rec_score = self.calculate_recommendation_score(
                    game_data, basic_analysis, advanced_analysis, user_profile
                )

                # Generate recommendation
                recommendation = self._create_game_recommendation(
                    game_data,
                    basic_analysis,
                    advanced_analysis,
                    user_profile,
                    rec_score,
                )

                recommendations.append(recommendation)

            except Exception as e:
                logger.error(
                    f"Error processing game {game_data.get('title', 'Unknown')}: {e}"
                )
                continue

        # Sort by recommendation score
        recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)

        return recommendations[:max_recommendations]

    def _create_game_recommendation(
        self,
        game_data: Dict[str, Any],
        basic_analysis: Dict[str, Any],
        advanced_analysis: Dict[str, Any],
        user_profile: UserProfile,
        rec_score: float,
    ) -> GameRecommendation:
        """Tworzy rekomendację gry."""

        # Determine primary reason
        market_analysis = advanced_analysis.get("comprehensive_analysis", {}).get(
            "market_analysis", {}
        )
        market_position = market_analysis.get("market_position", "")

        primary_reason = RecommendationReason.PERFECT_MATCH
        if "Hidden Gem" in market_position:
            primary_reason = RecommendationReason.HIDDEN_GEM
        elif "Excellent Value" in market_position or "Great Deal" in market_position:
            primary_reason = RecommendationReason.EXCELLENT_VALUE
        elif "Overpriced" in market_position:
            primary_reason = (
                RecommendationReason.GREAT_DEAL
            )  # Ironic, but for notification

        # Generate reasons
        reasons = self._generate_recommendation_reasons(
            game_data, basic_analysis, advanced_analysis, user_profile
        )

        # Calculate match percentage
        match_percentage = min(rec_score, 100)

        # Generate personalized message
        personalized_message = self._generate_personalized_message(
            game_data, user_profile, primary_reason, match_percentage
        )

        # Check for warnings
        warnings = self._generate_warnings(game_data, user_profile, advanced_analysis)

        return GameRecommendation(
            game_title=game_data.get("title", "Unknown"),
            recommendation_score=rec_score,
            confidence_level=advanced_analysis.get("confidence_level", "MEDIUM"),
            primary_reason=primary_reason,
            reasons=reasons,
            match_percentage=match_percentage,
            price_info={
                "current_price": game_data.get("current_eshop_price", "N/A"),
                "lowest_price": game_data.get("lowest_historical_price", "N/A"),
                "msrp": game_data.get("MSRP", "N/A"),
            },
            analysis_summary=advanced_analysis.get("comprehensive_analysis", {}).get(
                "analysis_summary", ""
            ),
            personalized_message=personalized_message,
            warnings=warnings,
        )

    def _generate_recommendation_reasons(
        self,
        game_data: Dict[str, Any],
        basic_analysis: Dict[str, Any],
        advanced_analysis: Dict[str, Any],
        user_profile: UserProfile,
    ) -> List[str]:
        """Generuje listę powodów rekomendacji."""
        reasons = []

        # Value-based reasons
        basic_rec = basic_analysis.get("value_metrics", {}).get("recommendation", "")
        if "BUY" in basic_rec:
            reasons.append("Excellent value for money")

        # Market position reasons
        market_analysis = advanced_analysis.get("comprehensive_analysis", {}).get(
            "market_analysis", {}
        )
        market_position = market_analysis.get("market_position", "")

        if "Hidden Gem" in market_position:
            reasons.append("Hidden gem - exceptional quality at low price")
        elif "Excellent Value" in market_position:
            reasons.append("Excellent value proposition")

        # Genre matching
        game_genres = game_data.get("genres", [])
        preferred_genres = user_profile.preferred_genres
        matching_genres = [g for g in game_genres if g in preferred_genres]
        if matching_genres:
            reasons.append(
                f"Matches your preferred genres: {', '.join(matching_genres)}"
            )

        # Quality reasons
        from utils.price_calculator import extract_score

        best_score = max(
            extract_score(game_data.get("metacritic_score", "0")) or 0,
            extract_score(game_data.get("opencritic_score", "0")) or 0,
        )
        if best_score >= 90:
            reasons.append("Critically acclaimed (90+ score)")
        elif best_score >= 80:
            reasons.append("High quality game (80+ score)")

        return reasons[:4]  # Limit to 4 reasons

    def _generate_personalized_message(
        self,
        game_data: Dict[str, Any],
        user_profile: UserProfile,
        primary_reason: RecommendationReason,
        match_percentage: float,
    ) -> str:
        """Generuje spersonalizowaną wiadomość."""
        game_title = game_data.get("title", "Unknown")
        pref = user_profile.primary_preference

        base_messages = {
            UserPreference.BARGAIN_HUNTER: f"Perfect bargain for you! {game_title} offers exceptional value.",
            UserPreference.QUALITY_SEEKER: f"High-quality experience awaits in {game_title}.",
            UserPreference.INDIE_LOVER: f"Discover this indie gem: {game_title}.",
            UserPreference.AAA_GAMER: f"Premium gaming experience with {game_title}.",
            UserPreference.CASUAL_PLAYER: f"Easy to pick up and enjoy: {game_title}.",
        }

        base_message = base_messages.get(pref, f"Great match for you: {game_title}")

        if match_percentage >= 90:
            return f"🎯 {base_message} ({match_percentage:.0f}% match!)"
        elif match_percentage >= 80:
            return f"⭐ {base_message} ({match_percentage:.0f}% match)"
        else:
            return f"👍 {base_message} ({match_percentage:.0f}% match)"

    def _generate_warnings(
        self,
        game_data: Dict[str, Any],
        user_profile: UserProfile,
        advanced_analysis: Dict[str, Any],
    ) -> List[str]:
        """Generuje ostrzeżenia dla użytkownika."""
        warnings = []

        # Price warnings
        from utils.price_calculator import extract_price

        current_price = extract_price(game_data.get("current_eshop_price", "N/A"))
        if current_price and current_price > user_profile.maximum_price:
            warnings.append(f"Price ({current_price}) exceeds your maximum budget")

        # Genre warnings
        game_genres = game_data.get("genres", [])
        avoided_genres = user_profile.avoided_genres
        avoided_found = [g for g in game_genres if g in avoided_genres]
        if avoided_found:
            warnings.append(f"Contains avoided genres: {', '.join(avoided_found)}")

        # Quality warnings
        from utils.price_calculator import extract_score

        best_score = max(
            extract_score(game_data.get("metacritic_score", "0")) or 0,
            extract_score(game_data.get("opencritic_score", "0")) or 0,
        )
        if best_score < user_profile.minimum_score:
            warnings.append(
                f"Score ({best_score}) below your minimum ({user_profile.minimum_score})"
            )

        return warnings
