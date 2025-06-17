"""
Phase 3 Point 1: Review Generation Integration
Punkt 1 Fazy 3: Integracja generowania recenzji

Core review generation module wrapping agent_tools review functionality
Główny moduł generowania recenzji opakowujący funkcjonalność z agent_tools
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Import review generation functions from agent_tools
from agent_tools import (
    generate_comprehensive_game_review as _generate_comprehensive_game_review,
    generate_quick_game_opinion as _generate_quick_game_opinion,
    compare_games_with_reviews as _compare_games_with_reviews,
)


def generate_comprehensive_game_review(
    game_name: str, include_recommendations: bool = True
) -> Dict[str, Any]:
    """
    Generuje kompleksową recenzję gry łączącą wszystkie analizy.

    Core interface for comprehensive game review generation.
    Główny interfejs dla generowania kompleksowych recenzji gier.

    Args:
        game_name (str): Nazwa gry do analizy
        include_recommendations (bool): Czy dołączyć rekomendacje zakupu

    Returns:
        Dict: Pełna recenzja z ratingiem, verdyktem, strengths, weaknesses

    Example:
        >>> review = generate_comprehensive_game_review("Hollow Knight")
        >>> print(review["review_data"]["overall_rating"])
        >>> print(review["review_data"]["final_verdict"])
    """
    try:
        logger.info(f"📝 Core: Generating comprehensive review for '{game_name}'...")

        result = _generate_comprehensive_game_review(game_name, include_recommendations)

        if result.get("success", False):
            review_data = result.get("review_data", {})
            rating = review_data.get("overall_rating", 0)
            recommendation = review_data.get("recommendation", "Unknown")
            confidence = review_data.get("confidence", "Unknown")

            logger.info(
                f"✅ Core: Review generated - Rating: {rating}/10, "
                f"Recommendation: {recommendation}, Confidence: {confidence}"
            )
        else:
            logger.warning(
                f"⚠️ Core: Review generation failed - {result.get('error', 'Unknown error')}"
            )

        return result

    except Exception as e:
        error_msg = f"Core review generation error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.review_generation.generate_comprehensive_game_review",
        }


def generate_quick_game_opinion(game_name: str) -> Dict[str, Any]:
    """
    Generuje szybką opinię o grze z kluczowymi punktami.

    Core interface for quick game opinion generation.
    Główny interfejs dla generowania szybkich opinii o grach.

    Args:
        game_name (str): Nazwa gry do analizy

    Returns:
        Dict: Skrócona opinia z rating, recommendation i key points

    Example:
        >>> opinion = generate_quick_game_opinion("Celeste")
        >>> print(opinion["quick_opinion"]["summary_rating"])
        >>> print(opinion["quick_opinion"]["key_points"])
    """
    try:
        logger.info(f"⚡ Core: Generating quick opinion for '{game_name}'...")

        result = _generate_quick_game_opinion(game_name)

        if result.get("success", False):
            quick_data = result.get("quick_opinion", {})
            rating = quick_data.get("summary_rating", 0)
            recommendation = quick_data.get("recommendation", "Unknown")

            logger.info(
                f"✅ Core: Quick opinion generated - Rating: {rating}/10, "
                f"Recommendation: {recommendation}"
            )
        else:
            logger.warning(
                f"⚠️ Core: Quick opinion failed - {result.get('error', 'Unknown error')}"
            )

        return result

    except Exception as e:
        error_msg = f"Core quick opinion error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.review_generation.generate_quick_game_opinion",
        }


def compare_games_with_reviews(
    game_names: List[str], comparison_focus: str = "overall"
) -> Dict[str, Any]:
    """
    Porównuje gry z pełną analizą recenzji i rankingiem.

    Core interface for games comparison with detailed reviews.
    Główny interfejs dla porównania gier ze szczegółowymi recenzjami.

    Args:
        game_names (List[str]): Lista nazw gier do porównania (minimum 2)
        comparison_focus (str): Fokus porównania ('overall', 'value', 'quality')

    Returns:
        Dict: Szczegółowe porównanie z winner, ranking i wyjaśnieniami

    Example:
        >>> comparison = compare_games_with_reviews(["Hollow Knight", "Celeste"], "overall")
        >>> print(comparison["comparison_results"]["winner"]["game_title"])
        >>> print(comparison["comparison_results"]["ranking"])
    """
    try:
        logger.info(f"🆚 Core: Comparing {len(game_names)} games with reviews...")
        logger.info(f"🎯 Focus: {comparison_focus}")

        if len(game_names) < 2:
            error_msg = "Core comparison requires at least 2 games"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "minimum_games_required": 2,
            }

        result = _compare_games_with_reviews(game_names, comparison_focus)

        if result.get("success", False):
            comparison_results = result.get("comparison_results", {})
            winner = comparison_results.get("winner", {})
            ranking_size = len(comparison_results.get("ranking", []))

            logger.info(
                f"✅ Core: Games comparison complete - "
                f"Winner: {winner.get('game_title', 'Unknown')}, "
                f"Ranked: {ranking_size} games"
            )
        else:
            logger.warning(
                f"⚠️ Core: Games comparison failed - {result.get('error', 'Unknown error')}"
            )

        return result

    except Exception as e:
        error_msg = f"Core games comparison error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.review_generation.compare_games_with_reviews",
        }


def get_review_generation_capabilities() -> Dict[str, Any]:
    """
    Zwraca informacje o możliwościach systemu generowania recenzji.

    Returns information about review generation system capabilities.
    Zwraca informacje o możliwościach systemu generowania recenzji.

    Returns:
        Dict: Dostępne opcje i możliwości systemu
    """
    try:
        logger.info("📋 Core: Getting review generation capabilities...")

        capabilities = {
            "success": True,
            "review_types": {
                "comprehensive_review": {
                    "description": "Complete professional-level game review",
                    "features": [
                        "10-point rating scale",
                        "Strengths and weaknesses analysis",
                        "Target audience identification",
                        "Value assessment integration",
                        "Confidence level scoring",
                        "Final verdict generation",
                    ],
                    "estimated_time": "30-60 seconds",
                },
                "quick_opinion": {
                    "description": "Fast summary for quick decision making",
                    "features": [
                        "Summary rating",
                        "Key points extraction",
                        "Quick recommendation",
                        "Essential information only",
                    ],
                    "estimated_time": "15-30 seconds",
                },
                "games_comparison": {
                    "description": "Detailed comparison with ranking",
                    "features": [
                        "Head-to-head analysis",
                        "Ranking with explanations",
                        "Winner determination",
                        "Focus-specific comparison",
                    ],
                    "estimated_time": "60-120 seconds",
                },
            },
            "comparison_focus_options": [
                "overall",  # Complete comparison
                "value",  # Value-for-money focus
                "quality",  # Quality and ratings focus
            ],
            "integration_features": [
                "Phase 1 data collection integration",
                "Phase 2 value analysis integration",
                "Phase 2 recommendation system integration",
                "Automatic confidence scoring",
                "Error handling and fallbacks",
            ],
            "output_quality": {
                "professional_level": True,
                "structured_format": True,
                "metadata_included": True,
                "confidence_scoring": True,
            },
        }

        logger.info("✅ Core: Review capabilities retrieved successfully")
        return capabilities

    except Exception as e:
        error_msg = f"Core capabilities error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.review_generation.get_review_generation_capabilities",
        }
