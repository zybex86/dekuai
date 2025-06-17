"""
Review Generator for AutoGen DekuDeals
Generator opinii dla AutoGen DekuDeals

Phase 3 Point 1: Comprehensive game review generation
Faza 3 Punkt 1: Kompleksowe generowanie opinii o grach
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ReviewConfidence(Enum):
    """Poziom pewności opinii."""

    VERY_HIGH = "very_high"  # 90-100% - pełne dane, jasne wnioski
    HIGH = "high"  # 80-89% - większość danych, pewne wnioski
    MEDIUM = "medium"  # 60-79% - podstawowe dane, umiarkowane wnioski
    LOW = "low"  # 40-59% - ograniczone dane, niepewne wnioski
    VERY_LOW = "very_low"  # 0-39% - minimalne dane, spekulatywne wnioski


class RecommendationType(Enum):
    """Typy rekomendacji."""

    INSTANT_BUY = "instant_buy"  # Natychmiast kupuj
    STRONG_BUY = "strong_buy"  # Zdecydowanie kupuj
    BUY = "buy"  # Kupuj
    CONSIDER = "consider"  # Rozważ
    WAIT_FOR_SALE = "wait_for_sale"  # Czekaj na promocję
    WAIT = "wait"  # Czekaj
    SKIP = "skip"  # Omijaj


@dataclass
class GameReview:
    """Kompletna opinia o grze."""

    game_title: str
    overall_rating: float  # 0-10 scale
    recommendation: RecommendationType
    confidence: ReviewConfidence

    # Core analysis
    strengths: List[str]
    weaknesses: List[str]
    target_audience: List[str]

    # Value analysis
    value_assessment: str
    price_recommendation: str
    timing_advice: str

    # Quality metrics
    gameplay_score: Optional[float] = None
    graphics_score: Optional[float] = None
    story_score: Optional[float] = None
    replay_value: Optional[float] = None

    # Market context
    genre_performance: str = ""
    market_position: str = ""
    competition_analysis: str = ""

    # Final verdict
    final_verdict: str = ""
    reviewer_notes: List[str] = field(default_factory=list)

    # Metadata
    review_date: datetime = field(default_factory=datetime.now)
    data_sources: List[str] = field(default_factory=list)


class ReviewGenerator:
    """Główny generator opinii o grach."""

    def __init__(self):
        self.review_templates = self._initialize_templates()
        self.scoring_weights = self._initialize_scoring_weights()

    def _initialize_templates(self) -> Dict[str, str]:
        """Inicjalizuje szablony opinii."""
        return {
            "instant_buy": "This is an exceptional game that delivers outstanding value. {game_title} combines {key_strengths} to create an experience that's both memorable and worth every penny. {value_justification}",
            "strong_buy": "A highly recommended purchase. {game_title} excels in {key_strengths} and offers {value_proposition}. {minor_concerns}",
            "buy": "{game_title} is a solid choice for {target_audience}. While it has {minor_weaknesses}, its {key_strengths} make it a worthwhile purchase. {value_context}",
            "consider": "{game_title} is a decent game with {mixed_aspects}. Whether you should buy depends on {decision_factors}. {alternative_suggestions}",
            "wait_for_sale": "While {game_title} has merit with its {positive_aspects}, the current price doesn't justify immediate purchase. {wait_reasoning} Consider buying during a sale.",
            "wait": "{game_title} shows promise but has {significant_issues}. {improvement_needed} Wait for updates or a significant price drop.",
            "skip": "Unfortunately, {game_title} falls short in {major_weaknesses}. {skip_reasoning} Your money would be better spent elsewhere.",
        }

    def _initialize_scoring_weights(self) -> Dict[str, float]:
        """Inicjalizuje wagi dla różnych aspektów oceny."""
        return {
            "metacritic_score": 0.25,
            "opencritic_score": 0.25,
            "value_score": 0.20,
            "advanced_score": 0.15,
            "user_recommendation": 0.10,
            "market_position": 0.05,
        }

    def generate_comprehensive_review(
        self,
        game_data: Dict[str, Any],
        basic_analysis: Dict[str, Any],
        advanced_analysis: Dict[str, Any],
        recommendation_analysis: Optional[Dict[str, Any]] = None,
    ) -> GameReview:
        """
        Generuje kompleksową opinię o grze.

        Args:
            game_data: Podstawowe dane o grze
            basic_analysis: Podstawowa analiza wartości
            advanced_analysis: Zaawansowana analiza
            recommendation_analysis: Analiza rekomendacji (opcjonalna)

        Returns:
            GameReview: Kompletna opinia o grze
        """
        try:
            logger.info(f"🎬 Starting comprehensive review generation...")

            # Extract podstawowych danych
            game_title = game_data.get("title", "Unknown Game")

            # Calculate overall rating
            overall_rating = self._calculate_overall_rating(
                game_data, basic_analysis, advanced_analysis
            )

            # Determine recommendation type
            recommendation = self._determine_recommendation_type(
                basic_analysis, advanced_analysis, recommendation_analysis
            )

            # Calculate confidence level
            confidence = self._calculate_confidence_level(
                game_data, basic_analysis, advanced_analysis
            )

            # Generate content sections
            strengths = self._identify_game_strengths(
                game_data, basic_analysis, advanced_analysis
            )

            weaknesses = self._identify_game_weaknesses(
                game_data, basic_analysis, advanced_analysis
            )

            target_audience = self._determine_target_audience(
                game_data, advanced_analysis
            )

            # Value assessment
            value_assessment = self._generate_value_assessment(
                basic_analysis, advanced_analysis
            )

            price_recommendation = self._extract_price_recommendation(
                basic_analysis, advanced_analysis
            )

            timing_advice = self._generate_timing_advice(
                basic_analysis, advanced_analysis
            )

            # Quality metrics
            quality_metrics = self._extract_quality_metrics(game_data)

            # Market context
            market_context = self._generate_market_context(
                advanced_analysis, recommendation_analysis
            )

            # Final verdict
            final_verdict = self._generate_final_verdict(
                game_title, recommendation, strengths, value_assessment, overall_rating
            )

            # Reviewer notes
            reviewer_notes = self._generate_reviewer_notes(
                game_data, basic_analysis, advanced_analysis, confidence
            )

            # Data sources
            data_sources = self._identify_data_sources(
                game_data, basic_analysis, advanced_analysis
            )

            review = GameReview(
                game_title=game_title,
                overall_rating=overall_rating,
                recommendation=recommendation,
                confidence=confidence,
                strengths=strengths,
                weaknesses=weaknesses,
                target_audience=target_audience,
                value_assessment=value_assessment,
                price_recommendation=price_recommendation,
                timing_advice=timing_advice,
                gameplay_score=quality_metrics.get("gameplay"),
                graphics_score=quality_metrics.get("graphics"),
                story_score=quality_metrics.get("story"),
                replay_value=quality_metrics.get("replay"),
                genre_performance=market_context.get("genre_performance", ""),
                market_position=market_context.get("market_position", ""),
                competition_analysis=market_context.get("competition", ""),
                final_verdict=final_verdict,
                reviewer_notes=reviewer_notes,
                data_sources=data_sources,
            )

            logger.info(
                f"✅ Review generated: {overall_rating:.1f}/10, {recommendation.value}, {confidence.value}"
            )
            return review

        except Exception as e:
            logger.error(f"❌ Error generating review: {e}")
            # Return minimal review in case of error
            return GameReview(
                game_title=game_data.get("title", "Unknown"),
                overall_rating=5.0,
                recommendation=RecommendationType.CONSIDER,
                confidence=ReviewConfidence.VERY_LOW,
                strengths=["Data incomplete"],
                weaknesses=["Analysis failed"],
                target_audience=["Unknown"],
                value_assessment="Cannot assess due to incomplete data",
                price_recommendation="No recommendation available",
                timing_advice="Wait for more information",
                final_verdict="Review could not be completed due to insufficient data",
                reviewer_notes=[f"Error: {str(e)}"],
            )

    def _calculate_overall_rating(
        self,
        game_data: Dict[str, Any],
        basic_analysis: Dict[str, Any],
        advanced_analysis: Dict[str, Any],
    ) -> float:
        """Oblicza ogólną ocenę gry (0-10)."""
        scores = []
        weights = []

        # Metacritic score
        from utils.price_calculator import extract_score

        metacritic = extract_score(game_data.get("metacritic_score", "0"))
        if metacritic and metacritic > 0:
            scores.append(metacritic / 10)  # Convert to 0-10 scale
            weights.append(self.scoring_weights["metacritic_score"])

        # OpenCritic score
        opencritic = extract_score(game_data.get("opencritic_score", "0"))
        if opencritic and opencritic > 0:
            scores.append(opencritic / 10)  # Convert to 0-10 scale
            weights.append(self.scoring_weights["opencritic_score"])

        # Basic value score
        value_metrics = basic_analysis.get("value_metrics", {})
        value_score = value_metrics.get("value_score", 0)
        if value_score > 0:
            # Normalize value score to 0-10 (assuming 100 is max)
            normalized_value = min(value_score / 10, 10)
            scores.append(normalized_value)
            weights.append(self.scoring_weights["value_score"])

        # Advanced analysis score
        comp_analysis = advanced_analysis.get("comprehensive_analysis", {})
        adv_score = comp_analysis.get("comprehensive_score", 0)
        if adv_score > 0:
            # Normalize advanced score to 0-10
            normalized_adv = min(adv_score / 10, 10)
            scores.append(normalized_adv)
            weights.append(self.scoring_weights["advanced_score"])

        # Calculate weighted average
        if scores and weights:
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            total_weight = sum(weights)
            overall_rating = weighted_sum / total_weight
        else:
            # Fallback to simple average of available scores
            if metacritic and opencritic:
                overall_rating = (
                    metacritic + opencritic
                ) / 20  # Average and convert to 0-10
            elif metacritic:
                overall_rating = metacritic / 10
            elif opencritic:
                overall_rating = opencritic / 10
            else:
                overall_rating = 5.0  # Neutral rating if no scores

        return min(max(overall_rating, 0), 10)  # Clamp to 0-10 range

    def _determine_recommendation_type(
        self,
        basic_analysis: Dict[str, Any],
        advanced_analysis: Dict[str, Any],
        recommendation_analysis: Optional[Dict[str, Any]],
    ) -> RecommendationType:
        """Określa typ rekomendacji na podstawie analiz."""

        # Priority 1: Advanced recommendation if available
        comp_analysis = advanced_analysis.get("comprehensive_analysis", {})
        adv_rec = comp_analysis.get("advanced_recommendation", "")

        if "INSTANT BUY" in adv_rec or "Hidden Gem" in adv_rec:
            return RecommendationType.INSTANT_BUY
        elif "STRONG BUY" in adv_rec:
            return RecommendationType.STRONG_BUY
        elif "BUY" == adv_rec:
            return RecommendationType.BUY
        elif "CONSIDER" in adv_rec:
            return RecommendationType.CONSIDER
        elif "WAIT FOR SALE" in adv_rec:
            return RecommendationType.WAIT_FOR_SALE
        elif "WAIT" in adv_rec:
            return RecommendationType.WAIT
        elif "SKIP" in adv_rec:
            return RecommendationType.SKIP

        # Priority 2: Basic analysis recommendation
        value_metrics = basic_analysis.get("value_metrics", {})
        basic_rec = value_metrics.get("recommendation", "")

        if "STRONG BUY" in basic_rec:
            return RecommendationType.STRONG_BUY
        elif "BUY" in basic_rec:
            return RecommendationType.BUY
        elif "HOLD" in basic_rec:
            return RecommendationType.CONSIDER
        elif "WAIT" in basic_rec:
            return RecommendationType.WAIT_FOR_SALE

        # Priority 3: Score-based fallback
        comp_score = comp_analysis.get("comprehensive_score", 0)
        if comp_score >= 8.0:
            return RecommendationType.STRONG_BUY
        elif comp_score >= 6.5:
            return RecommendationType.BUY
        elif comp_score >= 5.0:
            return RecommendationType.CONSIDER
        elif comp_score >= 3.0:
            return RecommendationType.WAIT_FOR_SALE
        else:
            return RecommendationType.SKIP

    def _calculate_confidence_level(
        self,
        game_data: Dict[str, Any],
        basic_analysis: Dict[str, Any],
        advanced_analysis: Dict[str, Any],
    ) -> ReviewConfidence:
        """Oblicza poziom pewności opinii."""
        confidence_score = 0
        max_score = 100

        # Data completeness (40 points)
        if game_data.get("title"):
            confidence_score += 5
        if game_data.get("current_eshop_price"):
            confidence_score += 10
        if game_data.get("metacritic_score") or game_data.get("opencritic_score"):
            confidence_score += 15
        if game_data.get("genres"):
            confidence_score += 5
        if game_data.get("developer"):
            confidence_score += 5

        # Analysis success (30 points)
        if basic_analysis.get("success", False):
            confidence_score += 15
        if advanced_analysis.get("success", False):
            confidence_score += 15

        # Data quality (30 points)
        adv_confidence = advanced_analysis.get("confidence_level", "")
        if adv_confidence == "HIGH":
            confidence_score += 30
        elif adv_confidence == "MEDIUM":
            confidence_score += 20
        elif adv_confidence == "LOW":
            confidence_score += 10

        # Convert to percentage
        confidence_percentage = (confidence_score / max_score) * 100

        if confidence_percentage >= 90:
            return ReviewConfidence.VERY_HIGH
        elif confidence_percentage >= 80:
            return ReviewConfidence.HIGH
        elif confidence_percentage >= 60:
            return ReviewConfidence.MEDIUM
        elif confidence_percentage >= 40:
            return ReviewConfidence.LOW
        else:
            return ReviewConfidence.VERY_LOW

    def _identify_game_strengths(
        self,
        game_data: Dict[str, Any],
        basic_analysis: Dict[str, Any],
        advanced_analysis: Dict[str, Any],
    ) -> List[str]:
        """Identyfikuje mocne strony gry."""
        strengths = []

        # Score-based strengths
        from utils.price_calculator import extract_score

        metacritic = extract_score(game_data.get("metacritic_score", "0"))
        opencritic = extract_score(game_data.get("opencritic_score", "0"))

        if metacritic and metacritic >= 90:
            strengths.append(f"Exceptional critical acclaim (Metacritic: {metacritic})")
        elif metacritic and metacritic >= 80:
            strengths.append(f"Strong critical reception (Metacritic: {metacritic})")

        if opencritic and opencritic >= 90:
            strengths.append(f"Outstanding OpenCritic score ({opencritic})")
        elif opencritic and opencritic >= 80:
            strengths.append(f"Positive OpenCritic reception ({opencritic})")

        # Value-based strengths
        value_metrics = basic_analysis.get("value_metrics", {})
        recommendation = value_metrics.get("recommendation", "")
        if "STRONG BUY" in recommendation:
            strengths.append("Excellent value for money")
        elif "BUY" in recommendation:
            strengths.append("Good value proposition")

        timing = value_metrics.get("buy_timing", "")
        if timing == "EXCELLENT":
            strengths.append("Perfect timing for purchase")

        # Advanced analysis strengths
        comp_analysis = advanced_analysis.get("comprehensive_analysis", {})
        market_analysis = comp_analysis.get("market_analysis", {})
        market_position = market_analysis.get("market_position", "")

        if "Hidden Gem" in market_position:
            strengths.append("Hidden gem with exceptional value")
        elif "Excellent Value" in market_position:
            strengths.append("Outstanding value in its price range")
        elif "Premium Quality" in market_position:
            strengths.append("Premium quality gaming experience")

        # Genre-specific strengths
        genre_analysis = comp_analysis.get("genre_analysis", {})
        cost_per_hour = genre_analysis.get("cost_per_hour", 0)
        if cost_per_hour and cost_per_hour < 2.0:
            expected_hours = genre_analysis.get("expected_hours", 0)
            strengths.append(f"Excellent playtime value (~{expected_hours}+ hours)")

        # Developer reputation
        dev_multiplier = genre_analysis.get("developer_multiplier", 1.0)
        if dev_multiplier > 1.1:
            strengths.append("Developed by reputable studio")

        return strengths[:5]  # Limit to top 5 strengths

    def _identify_game_weaknesses(
        self,
        game_data: Dict[str, Any],
        basic_analysis: Dict[str, Any],
        advanced_analysis: Dict[str, Any],
    ) -> List[str]:
        """Identyfikuje słabe strony gry."""
        weaknesses = []

        # Score-based weaknesses
        from utils.price_calculator import extract_score

        metacritic = extract_score(game_data.get("metacritic_score", "0"))
        opencritic = extract_score(game_data.get("opencritic_score", "0"))

        if metacritic and metacritic < 60:
            weaknesses.append(
                f"Below average critical reception (Metacritic: {metacritic})"
            )
        if opencritic and opencritic < 60:
            weaknesses.append(f"Poor OpenCritic scores ({opencritic})")

        # Value-based weaknesses
        value_metrics = basic_analysis.get("value_metrics", {})
        timing = value_metrics.get("buy_timing", "")
        if timing in ["POOR", "WAIT"]:
            weaknesses.append("Currently overpriced compared to historical lows")

        # Advanced analysis weaknesses
        comp_analysis = advanced_analysis.get("comprehensive_analysis", {})
        market_analysis = comp_analysis.get("market_analysis", {})
        market_position = market_analysis.get("market_position", "")

        if "Overpriced" in market_position:
            weaknesses.append("Overpriced for the quality offered")
        elif "Poor Value" in market_position:
            weaknesses.append("Poor value proposition")
        elif "Expensive" in market_position:
            weaknesses.append("Expensive compared to alternatives")

        # Genre-specific weaknesses
        genre_analysis = comp_analysis.get("genre_analysis", {})
        cost_per_hour = genre_analysis.get("cost_per_hour", 0)
        if cost_per_hour and cost_per_hour > 5.0:
            weaknesses.append(
                f"High cost per hour of content (~{cost_per_hour:.1f}/hour)"
            )

        # Age-related concerns
        age_factor = comp_analysis.get("age_factor", 1.0)
        if age_factor < 0.85:
            weaknesses.append("Older title that may feel dated")

        return weaknesses[:4]  # Limit to top 4 weaknesses

    def _determine_target_audience(
        self, game_data: Dict[str, Any], advanced_analysis: Dict[str, Any]
    ) -> List[str]:
        """Określa docelową grupę odbiorców."""
        audiences = []

        # Genre-based audiences
        genres = game_data.get("genres", [])
        genre_audiences = {
            "Action": "Action game enthusiasts",
            "Adventure": "Adventure game fans",
            "Role-Playing": "RPG lovers",
            "Strategy": "Strategy game players",
            "Simulation": "Simulation fans",
            "Sports": "Sports game enthusiasts",
            "Racing": "Racing game fans",
            "Puzzle": "Puzzle game lovers",
            "Platformer": "Platformer enthusiasts",
            "Fighting": "Fighting game fans",
            "Shooter": "Shooter game players",
            "Metroidvania": "Metroidvania fans",
            "Indie": "Indie game supporters",
        }

        for genre in genres:
            if genre in genre_audiences:
                audiences.append(genre_audiences[genre])

        # Price-based audiences
        from utils.price_calculator import extract_price

        current_price = extract_price(game_data.get("current_eshop_price", "N/A"))

        if current_price:
            if current_price <= 20:
                audiences.append("Budget-conscious gamers")
            elif current_price <= 40:
                audiences.append("Mid-tier game buyers")
            elif current_price >= 70:
                audiences.append("Premium game purchasers")

        # Quality-based audiences
        from utils.price_calculator import extract_score

        metacritic = extract_score(game_data.get("metacritic_score", "0"))
        if metacritic and metacritic >= 85:
            audiences.append("Quality-focused players")

        # Advanced analysis audiences
        comp_analysis = advanced_analysis.get("comprehensive_analysis", {})
        market_analysis = comp_analysis.get("market_analysis", {})
        market_position = market_analysis.get("market_position", "")

        if "Hidden Gem" in market_position:
            audiences.append("Deal hunters and discovery enthusiasts")

        return list(set(audiences))[:4]  # Remove duplicates and limit to 4

    def _generate_value_assessment(
        self, basic_analysis: Dict[str, Any], advanced_analysis: Dict[str, Any]
    ) -> str:
        """Generuje ocenę wartości za pieniądze."""

        value_metrics = basic_analysis.get("value_metrics", {})
        basic_rec = value_metrics.get("recommendation", "")
        value_score = value_metrics.get("value_score", 0)

        comp_analysis = advanced_analysis.get("comprehensive_analysis", {})
        adv_score = comp_analysis.get("comprehensive_score", 0)
        market_position = comp_analysis.get("market_analysis", {}).get(
            "market_position", ""
        )

        if "Hidden Gem" in market_position:
            return f"Exceptional value - this is a hidden gem offering premium quality at a budget price. Comprehensive score: {adv_score:.1f}/10."
        elif "STRONG BUY" in basic_rec and adv_score >= 7.0:
            return f"Outstanding value for money. Both basic analysis and advanced algorithms strongly recommend this purchase (Value score: {value_score:.1f}, Advanced: {adv_score:.1f})."
        elif adv_score >= 6.5:
            return f"Good value proposition. The game offers solid quality for its current price point (Advanced score: {adv_score:.1f})."
        elif adv_score >= 4.0:
            return f"Moderate value. Consider your budget and preferences carefully (Advanced score: {adv_score:.1f})."
        else:
            return f"Poor value for money. The current price doesn't justify the quality offered (Advanced score: {adv_score:.1f})."

    def _extract_price_recommendation(
        self, basic_analysis: Dict[str, Any], advanced_analysis: Dict[str, Any]
    ) -> str:
        """Wyciąga rekomendację cenową."""

        value_metrics = basic_analysis.get("value_metrics", {})
        basic_rec = value_metrics.get("recommendation", "No recommendation")

        comp_analysis = advanced_analysis.get("comprehensive_analysis", {})
        adv_rec = comp_analysis.get("advanced_recommendation", "")

        if adv_rec:
            return f"Advanced recommendation: {adv_rec} | Basic recommendation: {basic_rec}"
        else:
            return f"Price recommendation: {basic_rec}"

    def _generate_timing_advice(
        self, basic_analysis: Dict[str, Any], advanced_analysis: Dict[str, Any]
    ) -> str:
        """Generuje poradę dotyczącą czasu zakupu."""

        value_metrics = basic_analysis.get("value_metrics", {})
        timing = value_metrics.get("buy_timing", "UNKNOWN")

        timing_advice = {
            "EXCELLENT": "Perfect time to buy - currently at or near historical low price.",
            "GOOD": "Good timing for purchase - reasonable price point.",
            "FAIR": "Acceptable timing, though you might find better deals occasionally.",
            "POOR": "Not ideal timing - consider waiting for a sale.",
            "WAIT": "Poor timing - wait for a significant price drop.",
            "UNKNOWN": "Limited price history - proceed with caution.",
        }

        base_advice = timing_advice.get(timing, "Timing unclear.")

        # Add advanced context
        comp_analysis = advanced_analysis.get("comprehensive_analysis", {})
        market_position = comp_analysis.get("market_analysis", {}).get(
            "market_position", ""
        )

        if "Hidden Gem" in market_position:
            return f"{base_advice} This hidden gem status makes it an especially attractive purchase now."
        elif "Overpriced" in market_position:
            return f"{base_advice} Market analysis suggests waiting for a better deal."

        return base_advice

    def _extract_quality_metrics(
        self, game_data: Dict[str, Any]
    ) -> Dict[str, Optional[float]]:
        """Wyciąga metryki jakości z dostępnych danych."""
        from utils.price_calculator import extract_score

        # For now, use available scores as proxy for quality metrics
        metacritic = extract_score(game_data.get("metacritic_score", "0"))
        opencritic = extract_score(game_data.get("opencritic_score", "0"))

        # Use best available score as overall quality indicator
        best_score = max(metacritic or 0, opencritic or 0)

        if best_score > 0:
            # Estimate individual metrics based on overall score
            # This is a simplified approach - in real implementation you'd want separate data sources
            gameplay = best_score / 10  # Convert to 0-10 scale
            graphics = (
                gameplay * 0.9 if gameplay < 8 else gameplay
            )  # Slightly lower for graphics
            story = (
                gameplay * 0.85 if "Action" in game_data.get("genres", []) else gameplay
            )
            replay = gameplay * 0.8  # Generally lower replay value

            return {
                "gameplay": round(gameplay, 1),
                "graphics": round(graphics, 1),
                "story": round(story, 1),
                "replay": round(replay, 1),
            }

        return {"gameplay": None, "graphics": None, "story": None, "replay": None}

    def _generate_market_context(
        self,
        advanced_analysis: Dict[str, Any],
        recommendation_analysis: Optional[Dict[str, Any]],
    ) -> Dict[str, str]:
        """Generuje kontekst rynkowy."""

        comp_analysis = advanced_analysis.get("comprehensive_analysis", {})

        # Market position
        market_analysis = comp_analysis.get("market_analysis", {})
        market_position = market_analysis.get("market_position", "Unknown position")
        price_category = market_analysis.get("price_category", "Unknown")
        quality_category = market_analysis.get("quality_category", "Unknown")

        # Genre performance
        genre_analysis = comp_analysis.get("genre_analysis", {})
        primary_genre = genre_analysis.get("primary_genre", "Unknown")
        expected_hours = genre_analysis.get("expected_hours", 0)

        genre_performance = f"As a {primary_genre} game, it offers ~{expected_hours} hours of expected content."

        # Competition analysis (simplified)
        competition = f"In the {price_category} price category with {quality_category} quality rating."

        return {
            "genre_performance": genre_performance,
            "market_position": f"Market position: {market_position}",
            "competition": competition,
        }

    def _generate_final_verdict(
        self,
        game_title: str,
        recommendation: RecommendationType,
        strengths: List[str],
        value_assessment: str,
        overall_rating: float,
    ) -> str:
        """Generuje finalny werdykt."""

        # Get template based on recommendation
        template_key = recommendation.value
        template = self.review_templates.get(template_key, "")

        if not template:
            # Fallback verdict
            return f"{game_title} receives a {overall_rating:.1f}/10 rating with a {recommendation.value.replace('_', ' ')} recommendation. {value_assessment}"

        # Prepare template variables
        key_strengths = strengths[:2] if strengths else ["some positive aspects"]
        key_strengths_str = " and ".join(key_strengths)

        # Create context-specific variables
        template_vars = {
            "game_title": game_title,
            "key_strengths": key_strengths_str,
            "value_justification": value_assessment,
            "value_proposition": "good value for money",
            "value_context": value_assessment,
            "target_audience": "its target audience",
            "minor_concerns": "some minor issues don't significantly impact the experience",
            "minor_weaknesses": "minor weaknesses",
            "mixed_aspects": "both strengths and weaknesses",
            "decision_factors": "your personal preferences and budget",
            "alternative_suggestions": "consider similar games in your wishlist",
            "positive_aspects": key_strengths_str,
            "wait_reasoning": "the current price point is too high",
            "significant_issues": "several concerning aspects",
            "improvement_needed": "significant improvements are needed",
            "major_weaknesses": "critical areas",
            "skip_reasoning": f"with an overall rating of {overall_rating:.1f}/10",
        }

        # Format template
        try:
            formatted_verdict = template.format(**template_vars)
            return formatted_verdict
        except KeyError as e:
            # Fallback if template formatting fails
            return f"{game_title} receives a {overall_rating:.1f}/10 rating. {value_assessment}"

    def _generate_reviewer_notes(
        self,
        game_data: Dict[str, Any],
        basic_analysis: Dict[str, Any],
        advanced_analysis: Dict[str, Any],
        confidence: ReviewConfidence,
    ) -> List[str]:
        """Generuje notatki recenzenta."""
        notes = []

        # Data source notes
        if game_data.get("metacritic_score") and game_data.get("opencritic_score"):
            notes.append("Review based on both Metacritic and OpenCritic scores")
        elif game_data.get("metacritic_score"):
            notes.append("Review primarily based on Metacritic data")
        elif game_data.get("opencritic_score"):
            notes.append("Review primarily based on OpenCritic data")

        # Analysis notes
        if basic_analysis.get("success") and advanced_analysis.get("success"):
            notes.append("Comprehensive analysis completed successfully")
        elif confidence in [ReviewConfidence.LOW, ReviewConfidence.VERY_LOW]:
            notes.append(
                "Limited data available - recommendations should be taken with caution"
            )

        # Timing notes
        notes.append(f"Analysis performed on {datetime.now().strftime('%Y-%m-%d')}")

        return notes[:3]  # Limit to 3 notes

    def _identify_data_sources(
        self,
        game_data: Dict[str, Any],
        basic_analysis: Dict[str, Any],
        advanced_analysis: Dict[str, Any],
    ) -> List[str]:
        """Identyfikuje źródła danych użyte w analizie."""
        sources = ["DekuDeals.com"]

        if game_data.get("metacritic_score"):
            sources.append("Metacritic")
        if game_data.get("opencritic_score"):
            sources.append("OpenCritic")
        if basic_analysis.get("success"):
            sources.append("Price Analysis Engine")
        if advanced_analysis.get("success"):
            sources.append("Advanced Value Algorithms")

        return sources


def format_review_for_display(review: GameReview) -> str:
    """Formatuje opinię do wyświetlenia użytkownikowi."""

    output = []

    # Header
    output.append(f"🎮 GAME REVIEW: {review.game_title}")
    output.append("=" * 60)

    # Overall assessment
    output.append(f"📊 OVERALL RATING: {review.overall_rating:.1f}/10")
    output.append(
        f"🎯 RECOMMENDATION: {review.recommendation.value.replace('_', ' ').upper()}"
    )
    output.append(f"🔍 CONFIDENCE: {review.confidence.value.replace('_', ' ').upper()}")

    # Strengths & Weaknesses
    if review.strengths:
        output.append(f"\n✅ STRENGTHS:")
        for strength in review.strengths:
            output.append(f"  • {strength}")

    if review.weaknesses:
        output.append(f"\n⚠️ AREAS FOR IMPROVEMENT:")
        for weakness in review.weaknesses:
            output.append(f"  • {weakness}")

    # Target audience
    if review.target_audience:
        output.append(f"\n👥 TARGET AUDIENCE:")
        output.append(f"  {', '.join(review.target_audience)}")

    # Value assessment
    output.append(f"\n💰 VALUE ASSESSMENT:")
    output.append(f"  {review.value_assessment}")

    # Price recommendation
    output.append(f"\n💡 PRICE RECOMMENDATION:")
    output.append(f"  {review.price_recommendation}")

    # Timing advice
    output.append(f"\n⏰ TIMING ADVICE:")
    output.append(f"  {review.timing_advice}")

    # Quality metrics (if available)
    if review.gameplay_score:
        output.append(f"\n🎯 QUALITY BREAKDOWN:")
        if review.gameplay_score:
            output.append(f"  Gameplay: {review.gameplay_score}/10")
        if review.graphics_score:
            output.append(f"  Graphics: {review.graphics_score}/10")
        if review.story_score:
            output.append(f"  Story: {review.story_score}/10")
        if review.replay_value:
            output.append(f"  Replay Value: {review.replay_value}/10")

    # Final verdict
    output.append(f"\n📝 FINAL VERDICT:")
    output.append(f"  {review.final_verdict}")

    # Reviewer notes (if any)
    if review.reviewer_notes:
        output.append(f"\n📋 REVIEWER NOTES:")
        for note in review.reviewer_notes:
            output.append(f"  • {note}")

    # Data sources
    if review.data_sources:
        output.append(f"\n📚 DATA SOURCES:")
        output.append(f"  {', '.join(review.data_sources)}")

    return "\n".join(output)
