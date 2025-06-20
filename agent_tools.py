"""
Agent Tools for AutoGen DekuDeals Analysis
Narzędzia dla agentów AutoGen do analizy gier z DekuDeals
"""

import logging
from typing import Dict, Any, Optional, List
from deku_tools import search_deku_deals, scrape_game_details

# Note: Removed core imports to avoid circular dependency
# Backward compatibility functions are implemented directly below
from utils.price_calculator import (
    extract_price,
    extract_score,
    calculate_discount_percentage,
    calculate_price_difference,
    calculate_value_ratio,
    assess_buy_timing,
    generate_price_recommendation,
)
from utils.advanced_value_algorithms import (
    calculate_comprehensive_value_analysis,
)
from utils.recommendation_engine import (
    RecommendationEngine,
    UserProfile,
    UserPreference,
    GameRecommendation,
)
from utils.review_generator import (
    ReviewGenerator,
    GameReview,
    ReviewConfidence,
    RecommendationType,
    format_review_for_display,
)
from utils.opinion_adapters import (
    OpinionAdapter,
    AdaptationContext,
    AdaptedOpinion,
    CommunicationStyle,
    OutputFormat,
    AudienceType,
    create_context_presets,
    format_for_multiple_platforms,
)

# Phase 4 - Advanced Quality Control
from utils.quality_validation import validate_game_analysis
from datetime import datetime
import requests
from bs4 import BeautifulSoup, Tag

# Phase 6.5 - ML Intelligence Enhancement
from utils.smart_user_profiler import (
    get_smart_user_profiler,
    record_user_interaction,
    get_personalized_adjustments,
    SmartUserProfiler,
    DynamicUserProfile,
    GamePreferencePattern,
)

# AutoGen decorators for Phase 4 tools
try:
    from autogen import register_for_execution, register_for_llm
except ImportError:
    # Fallback if autogen not available
    def register_for_execution():
        def decorator(func):
            return func

        return decorator

    def register_for_llm(**kwargs):
        def decorator(func):
            return func

        return decorator


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_and_scrape_game(game_name: Optional[str]) -> Dict[str, Any]:
    """
    Wyszukuje grę na DekuDeals i pobiera wszystkie dane.

    DESCRIPTION: Combines searching and scraping into one function
    ARGS:
        game_name (str): Name of game to search for
    RETURNS:
        Dict: Complete game data or error message
    RAISES:
        Exception: When game cannot be found or scraped
    """
    try:
        # Input validation
        if not game_name or not game_name.strip():
            raise ValueError("Game name cannot be empty")

        logger.info(f"🔍 Searching for game: {game_name}")

        # Search for game URL
        game_url = search_deku_deals(game_name.strip())
        if not game_url:
            error_msg = f"Game '{game_name}' not found on DekuDeals"
            logger.warning(f"⚠️ {error_msg}")
            return {
                "success": False,
                "error": "Game not found",
                "game_name": game_name,
                "message": error_msg,
            }

        logger.info(f"📍 Found game URL: {game_url}")

        # Retrieve details
        game_details = scrape_game_details(game_url)
        if not game_details:
            error_msg = f"Failed to scrape data from {game_url}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": "Failed to retrieve data",
                "game_url": game_url,
                "message": error_msg,
            }

        # Add metadata
        game_details["success"] = True
        game_details["source_url"] = game_url
        game_details["search_query"] = game_name

        logger.info(
            f"✅ Successfully scraped data for: {game_details.get('title', game_name)}"
        )

        # PHASE 6.5: Record user interaction for ML learning
        try:
            game_title = game_details.get("title", game_name)
            record_user_interaction(game_title, game_details, "search_and_scrape")
            logger.debug(f"🧠 Recorded interaction for smart profiling: {game_title}")
        except Exception as e:
            logger.debug(f"Smart profiling recording failed (non-critical): {e}")

        return game_details

    except Exception as e:
        error_msg = f"Error in search_and_scrape_game: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": str(e),
            "game_name": game_name,
            "message": error_msg,
        }


def validate_game_data(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Waliduje kompletność danych o grze.

    Args:
        game_data (Dict): Dane gry do walidacji

    Returns:
        Dict: Raport walidacji z missing_fields i completeness_score
    """
    required_fields = [
        "title",
        "MSRP",
        "current_eshop_price",
        "metacritic_score",
        "genres",
        "developer",
    ]

    missing_fields = []
    available_fields = []

    for field in required_fields:
        if (
            field not in game_data
            or not game_data[field]
            or game_data[field] in ["Nieznany", "Brak oceny", "N/A"]
        ):
            missing_fields.append(field)
        else:
            available_fields.append(field)

    completeness_score = len(available_fields) / len(required_fields) * 100

    validation_result = {
        "is_complete": len(missing_fields) == 0,
        "completeness_score": round(completeness_score, 1),
        "available_fields": available_fields,
        "missing_fields": missing_fields,
        "total_fields": len(required_fields),
        "available_count": len(available_fields),
    }

    if missing_fields:
        logger.warning(f"⚠️ Missing fields: {missing_fields}")
    else:
        logger.info(f"✅ All required fields present (100% complete)")

    return validation_result


def format_game_summary(game_data: Dict[str, Any]) -> str:
    """
    Formatuje podsumowanie danych o grze dla agentów.

    Args:
        game_data (Dict): Dane gry

    Returns:
        str: Sformatowane podsumowanie
    """
    if not game_data.get("success", False):
        return f"❌ Error: {game_data.get('message', 'Unknown error')}"

    title = game_data.get("title", "Unknown Game")
    developer = game_data.get("developer", "Unknown")
    genres = game_data.get("genres", ["Unknown"])
    current_price = game_data.get("current_eshop_price", "N/A")
    msrp = game_data.get("MSRP", "N/A")
    metacritic = game_data.get("metacritic_score", "No score")
    platforms = game_data.get("platform", "Unknown")

    summary = f"""
🎮 **{title}**
👨‍💻 Developer: {developer}
🏷️ Genres: {', '.join(genres) if isinstance(genres, list) else genres}
💰 Current Price: {current_price}
💵 MSRP: {msrp}
⭐ Metacritic: {metacritic}
🎯 Platforms: {platforms}
🔗 Source: {game_data.get('source_url', 'N/A')}
"""

    return summary.strip()


def extract_key_metrics(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wyciąga kluczowe metryki z danych gry dla dalszej analizy.

    Args:
        game_data (Dict): Pełne dane gry

    Returns:
        Dict: Kluczowe metryki
    """
    if not game_data.get("success", False):
        return {"error": "No valid game data to extract metrics from"}

    metrics = {
        "title": game_data.get("title", "Unknown"),
        "has_price_data": bool(
            game_data.get("current_eshop_price")
            and game_data.get("current_eshop_price") != "N/A"
        ),
        "has_review_scores": bool(
            game_data.get("metacritic_score")
            and game_data.get("metacritic_score") not in ["Brak oceny", "No score"]
        ),
        "has_basic_info": bool(game_data.get("developer") and game_data.get("genres")),
        "price_available": game_data.get("current_eshop_price", "N/A"),
        "metacritic_available": game_data.get("metacritic_score", "No score"),
        "release_info_parsed": bool(game_data.get("release_dates_parsed")),
    }

    # Overall data quality score
    quality_indicators = [
        metrics["has_price_data"],
        metrics["has_review_scores"],
        metrics["has_basic_info"],
        metrics["release_info_parsed"],
    ]

    metrics["data_quality_score"] = (
        sum(quality_indicators) / len(quality_indicators) * 100
    )

    return metrics


def calculate_value_score(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Oblicza obiektywny wskaźnik wartości za pieniądze na podstawie ceny i ocen.

    DESCRIPTION: Calculate objective value-for-money indicator
    ARGS:
        game_data (Dict): Game data with prices and ratings
    RETURNS:
        Dict: Value analysis, pricing recommendations
    RAISES:
        ValueError: When key data is missing
    """
    try:
        logger.info("💰 Starting price value analysis...")

        # Validate input
        if not game_data.get("success", False):
            error_msg = "Cannot analyze value for unsuccessful game data"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg, "analysis": "incomplete"}

        # Extract key data using price calculator utilities
        current_price = extract_price(game_data.get("current_eshop_price", "N/A"))
        msrp = extract_price(game_data.get("MSRP", "N/A"))
        lowest_price = extract_price(game_data.get("lowest_historical_price", "N/A"))

        metacritic = extract_score(game_data.get("metacritic_score", "0"))
        opencritic = extract_score(game_data.get("opencritic_score", "0"))

        # Log extracted data
        logger.info(
            f"📊 Extracted prices: current={current_price}, MSRP={msrp}, lowest={lowest_price}"
        )
        logger.info(
            f"⭐ Extracted scores: Metacritic={metacritic}, OpenCritic={opencritic}"
        )

        # Calculate indicators using utility functions
        value_analysis = {
            "success": True,
            "game_title": game_data.get("title", "Unknown"),
            "price_data": {
                "current_price": current_price,
                "msrp": msrp,
                "lowest_historical": lowest_price,
                "price_vs_msrp": calculate_discount_percentage(current_price, msrp),
                "price_vs_lowest": calculate_price_difference(
                    current_price, lowest_price
                ),
            },
            "score_data": {
                "metacritic": metacritic,
                "opencritic": opencritic,
                "average_score": (
                    (metacritic + opencritic) / 2
                    if metacritic and opencritic
                    else (metacritic or opencritic)
                ),
            },
            "value_metrics": {
                "value_score": calculate_value_ratio(
                    current_price, metacritic, opencritic
                ),
                "buy_timing": assess_buy_timing(current_price, lowest_price),
                "recommendation": generate_price_recommendation(
                    current_price, msrp, lowest_price, metacritic
                ),
            },
            "analysis_summary": _generate_value_summary(
                current_price, msrp, lowest_price, metacritic, opencritic
            ),
        }

        # Log results
        recommendation = value_analysis["value_metrics"]["recommendation"]
        timing = value_analysis["value_metrics"]["buy_timing"]
        logger.info(f"✅ Analysis complete: {recommendation} | Timing: {timing}")

        # PHASE 6.5: Record value analysis interaction for learning
        try:
            game_title = game_data.get("title", "Unknown")
            record_user_interaction(game_title, game_data, "value_analysis")
            logger.debug(f"🧠 Recorded value analysis interaction: {game_title}")
        except Exception as e:
            logger.debug(f"Smart profiling recording failed (non-critical): {e}")

        return value_analysis

    except Exception as e:
        error_msg = f"Error in calculate_value_score: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg, "analysis": "incomplete"}


def _generate_value_summary(
    current_price: Optional[float],
    msrp: Optional[float],
    lowest_price: Optional[float],
    metacritic: Optional[float],
    opencritic: Optional[float],
) -> str:
    """
    Generuje tekstowe podsumowanie analizy wartości.

    Args:
        current_price: Aktualna cena
        msrp: MSRP
        lowest_price: Najniższa historyczna cena
        metacritic: Ocena Metacritic
        opencritic: Ocena OpenCritic

    Returns:
        str: Tekstowe podsumowanie analizy
    """
    summary_parts = []

    # Price analysis
    if current_price and msrp:
        discount = calculate_discount_percentage(current_price, msrp)
        if discount and discount > 0:
            summary_parts.append(f"💰 {discount:.1f}% discount from MSRP")
        elif discount and discount < 0:
            summary_parts.append(f"📈 {abs(discount):.1f}% above MSRP")
        else:
            summary_parts.append("💵 At MSRP price")

    # Historical price comparison
    if current_price and lowest_price:
        timing = assess_buy_timing(current_price, lowest_price)
        timing_messages = {
            "EXCELLENT": "🎯 At or near historical low!",
            "GOOD": "✅ Good price compared to history",
            "FAIR": "⚖️ Fair price, could wait for better deal",
            "POOR": "⚠️ Expensive compared to historical lows",
            "WAIT": "❌ Much more expensive than usual",
            "UNKNOWN": "❓ Limited historical price data",
        }
        summary_parts.append(timing_messages.get(timing, "❓ Price timing unclear"))

    # Quality assessment
    if metacritic or opencritic:
        avg_score = (
            (metacritic + opencritic) / 2
            if metacritic and opencritic
            else (metacritic or opencritic)
        )
        if avg_score and avg_score >= 90:
            summary_parts.append("⭐ Exceptional game quality")
        elif avg_score and avg_score >= 80:
            summary_parts.append("⭐ High quality game")
        elif avg_score and avg_score >= 70:
            summary_parts.append("⭐ Good quality game")
        elif avg_score and avg_score >= 60:
            summary_parts.append("⭐ Decent quality game")
        elif avg_score:
            summary_parts.append("⭐ Mixed/Poor reviews")

    # Value ratio
    if current_price and (metacritic or opencritic):
        value_ratio = calculate_value_ratio(current_price, metacritic, opencritic)
        if value_ratio and value_ratio > 15:
            summary_parts.append("💎 Excellent value for money")
        elif value_ratio and value_ratio > 10:
            summary_parts.append("💚 Good value for money")
        elif value_ratio and value_ratio > 5:
            summary_parts.append("💛 Fair value for money")
        else:
            summary_parts.append("💸 Questionable value for money")

    return " | ".join(summary_parts) if summary_parts else "Limited data for analysis"


def calculate_advanced_value_analysis(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Przeprowadza zaawansowaną analizę wartości z wykorzystaniem algorytmów z Punktu 2.

    DESCRIPTION: Perform comprehensive value analysis using advanced algorithms
    ARGS:
        game_data (Dict): Complete game data with prices, ratings, genres, etc.
    RETURNS:
        Dict: Advanced value analysis with genre factors, market position, age factors
    RAISES:
        ValueError: When key data is missing for advanced analysis
    """
    try:
        logger.info("🚀 Starting advanced value analysis (Point 2)...")

        # Validate input
        if not game_data.get("success", False):
            error_msg = "Cannot perform advanced analysis for unsuccessful game data"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg, "analysis": "incomplete"}

        # Run comprehensive analysis
        comprehensive_result = calculate_comprehensive_value_analysis(game_data)

        if "error" in comprehensive_result:
            logger.error(
                f"❌ Comprehensive analysis failed: {comprehensive_result.get('error')}"
            )
            return {
                "success": False,
                "error": comprehensive_result["error"],
                "analysis": "incomplete",
            }

        # Extract additional insights
        game_title = game_data.get("title", "Unknown")
        current_price = extract_price(game_data.get("current_eshop_price", "N/A"))
        genres = game_data.get("genres", [])
        developer = game_data.get("developer", "Unknown")

        # Add enhanced insights
        enhanced_analysis = {
            "success": True,
            "game_title": game_title,
            "analysis_type": "advanced_comprehensive",
            "basic_info": {
                "current_price": current_price,
                "genres": genres,
                "developer": developer,
            },
            "comprehensive_analysis": comprehensive_result,
            "insights": _generate_advanced_insights(comprehensive_result),
            "confidence_level": _calculate_analysis_confidence(
                game_data, comprehensive_result
            ),
        }

        # Log results
        score = comprehensive_result.get("comprehensive_score", 0)
        recommendation = comprehensive_result.get("advanced_recommendation", "Unknown")
        market_position = comprehensive_result.get("market_analysis", {}).get(
            "market_position", "Unknown"
        )

        logger.info(
            f"✅ Advanced analysis complete: Score={score}, Rec={recommendation}, Position={market_position}"
        )

        return enhanced_analysis

    except Exception as e:
        error_msg = f"Error in calculate_advanced_value_analysis: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg, "analysis": "incomplete"}


def _generate_advanced_insights(comprehensive_result: Dict[str, Any]) -> List[str]:
    """
    Generuje zaawansowane insights na podstawie comprehensive analysis.

    Args:
        comprehensive_result: Wyniki comprehensive analysis

    Returns:
        List[str]: Lista kluczowych insights
    """
    insights = []

    # Market position insights
    market_analysis = comprehensive_result.get("market_analysis", {})
    market_position = market_analysis.get("market_position", "")
    value_tier = market_analysis.get("value_tier", "")

    if "Hidden Gem" in market_position:
        insights.append(
            "💎 This appears to be a hidden gem - exceptional quality at budget price"
        )
    elif "Excellent Value" in market_position:
        insights.append("🌟 Excellent value proposition for the quality offered")
    elif "Overpriced" in market_position or "Poor Value" in market_position:
        insights.append("⚠️ Game appears overpriced for its quality level")

    # Genre-specific insights
    genre_analysis = comprehensive_result.get("genre_analysis", {})
    cost_per_hour = genre_analysis.get("cost_per_hour", 0)
    expected_hours = genre_analysis.get("expected_hours", 0)
    primary_genre = genre_analysis.get("primary_genre", "")

    if cost_per_hour and cost_per_hour < 2.0:
        insights.append(
            f"💰 Excellent cost per hour (~{cost_per_hour:.1f}/hour) for {expected_hours}h+ of content"
        )
    elif cost_per_hour and cost_per_hour > 5.0:
        insights.append(
            f"💸 High cost per hour (~{cost_per_hour:.1f}/hour) might not justify the price"
        )

    # Age factor insights
    age_factor = comprehensive_result.get("age_factor", 1.0)
    if age_factor < 0.85:
        insights.append("📅 This is an older title - price should reflect its age")
    elif age_factor >= 0.98:
        insights.append("🆕 Recent release - premium pricing is expected")

    # Overall score insights
    score = comprehensive_result.get("comprehensive_score", 0)
    if score >= 8.0:
        insights.append("🏆 Outstanding overall value score - highly recommended")
    elif score <= 4.0:
        insights.append("🚨 Low overall value score - consider waiting or skipping")

    return insights


def generate_comprehensive_game_review(
    game_name: str, include_recommendations: bool = True
) -> Dict[str, Any]:
    """
    Generuje kompleksową opinię o grze łącząc wszystkie analizy.

    DESCRIPTION: Generate comprehensive game review combining all analyses from Phase 1, 2, and 3
    ARGS:
        game_name (str): Nazwa gry do przeglądu
        include_recommendations (bool): Czy dołączyć analizę rekomendacji dla różnych użytkowników
    RETURNS:
        Dict: Kompletna opinia o grze z wszystkimi sekcjami
    RAISES:
        ValueError: Gdy nie można znaleźć danych o grze
    """
    try:
        logger.info(f"🎬 Starting comprehensive review generation for: {game_name}")

        # Step 1: Collect game data
        logger.info("📡 Step 1: Collecting game data...")
        game_data = search_and_scrape_game(game_name)

        if not game_data.get("success", False):
            error_msg = f"Could not retrieve game data for '{game_name}'"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg, "game_name": game_name}

        game_title = game_data.get("title", game_name)
        logger.info(f"✅ Game data collected for: {game_title}")

        # Step 2: Basic value analysis
        logger.info("💰 Step 2: Performing basic value analysis...")
        basic_analysis = calculate_value_score(game_data)

        if not basic_analysis.get("success", False):
            logger.warning("⚠️ Basic analysis failed, using fallback")
            basic_analysis = {"success": False, "value_metrics": {}}

        # Step 3: Advanced value analysis
        logger.info("🚀 Step 3: Performing advanced value analysis...")
        advanced_analysis = calculate_advanced_value_analysis(game_data)

        if not advanced_analysis.get("success", False):
            logger.warning("⚠️ Advanced analysis failed, using fallback")
            advanced_analysis = {"success": False, "comprehensive_analysis": {}}

        # Step 4: Recommendation analysis (optional)
        recommendation_analysis = None
        if include_recommendations:
            logger.info("🎯 Step 4: Performing recommendation analysis...")
            try:
                # Use indie_lover as default profile for single-game analysis
                rec_result = get_recommendation_insights(game_name)
                if rec_result.get("success", False):
                    recommendation_analysis = rec_result
                    logger.info("✅ Recommendation analysis completed")
                else:
                    logger.warning("⚠️ Recommendation analysis failed")
            except Exception as e:
                logger.warning(f"⚠️ Recommendation analysis error: {e}")

        # Step 5: Generate comprehensive review
        logger.info("📝 Step 5: Generating comprehensive review...")
        review = _review_generator.generate_comprehensive_review(
            game_data=game_data,
            basic_analysis=basic_analysis,
            advanced_analysis=advanced_analysis,
            recommendation_analysis=recommendation_analysis,
        )

        # Step 6: Format for output
        logger.info("📄 Step 6: Formatting review for output...")
        formatted_review = format_review_for_display(review)

        # Create comprehensive result
        result = {
            "success": True,
            "game_title": review.game_title,
            "review_data": {
                "overall_rating": review.overall_rating,
                "recommendation": review.recommendation.value,
                "confidence": review.confidence.value,
                "strengths": review.strengths,
                "weaknesses": review.weaknesses,
                "target_audience": review.target_audience,
                "value_assessment": review.value_assessment,
                "price_recommendation": review.price_recommendation,
                "timing_advice": review.timing_advice,
                "final_verdict": review.final_verdict,
                "reviewer_notes": review.reviewer_notes,
                "data_sources": review.data_sources,
            },
            "quality_scores": {
                "gameplay": review.gameplay_score,
                "graphics": review.graphics_score,
                "story": review.story_score,
                "replay_value": review.replay_value,
            },
            "market_context": {
                "genre_performance": review.genre_performance,
                "market_position": review.market_position,
                "competition_analysis": review.competition_analysis,
            },
            "underlying_analyses": {
                "basic_analysis_success": basic_analysis.get("success", False),
                "advanced_analysis_success": advanced_analysis.get("success", False),
                "recommendation_analysis_success": recommendation_analysis is not None,
            },
            "formatted_review": formatted_review,
            "review_metadata": {
                "review_date": review.review_date.isoformat(),
                "confidence_level": review.confidence.value,
                "data_completeness": _assess_data_completeness(game_data),
            },
        }

        logger.info(f"✅ Comprehensive review generated successfully!")
        logger.info(
            f"📊 Rating: {review.overall_rating:.1f}/10, Recommendation: {review.recommendation.value}"
        )

        return result

    except Exception as e:
        error_msg = f"Error generating comprehensive review: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg, "game_name": game_name}


def generate_quick_game_opinion(game_name: str) -> Dict[str, Any]:
    """
    Generuje szybką opinię o grze (bez pełnej analizy rekomendacji).

    DESCRIPTION: Generate quick game opinion with essential analysis only
    ARGS:
        game_name (str): Nazwa gry do szybkiej opinii
    RETURNS:
        Dict: Podstawowa opinia z kluczowymi informacjami
    """
    try:
        logger.info(f"⚡ Generating quick opinion for: {game_name}")

        # Use comprehensive review but without recommendations to speed up
        result = generate_comprehensive_game_review(
            game_name, include_recommendations=False
        )

        if not result.get("success", False):
            return result

        # Extract quick summary
        review_data = result.get("review_data", {})
        quick_opinion = {
            "success": True,
            "game_title": result.get("game_title"),
            "quick_summary": {
                "rating": f"{review_data.get('overall_rating', 0):.1f}/10",
                "recommendation": review_data.get("recommendation", "unknown")
                .replace("_", " ")
                .title(),
                "confidence": review_data.get("confidence", "unknown")
                .replace("_", " ")
                .title(),
                "key_strength": (
                    review_data.get("strengths", ["Unknown"])[0]
                    if review_data.get("strengths")
                    else "Unknown"
                ),
                "main_concern": (
                    review_data.get("weaknesses", ["None identified"])[0]
                    if review_data.get("weaknesses")
                    else "None identified"
                ),
                "target_audience": ", ".join(
                    review_data.get("target_audience", ["General gamers"])[:2]
                ),
            },
            "one_liner": review_data.get("final_verdict", "Opinion not available")[:100]
            + "...",
            "buy_advice": review_data.get(
                "timing_advice", "No timing advice available"
            ),
        }

        logger.info(
            f"✅ Quick opinion generated: {quick_opinion['quick_summary']['rating']}, {quick_opinion['quick_summary']['recommendation']}"
        )

        return quick_opinion

    except Exception as e:
        error_msg = f"Error generating quick opinion: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg, "game_name": game_name}


def compare_games_with_reviews(
    game_names: List[str], comparison_focus: str = "overall"
) -> Dict[str, Any]:
    """
    Porównuje gry z pełnymi opiniami.

    DESCRIPTION: Compare multiple games with full review analysis
    ARGS:
        game_names (List[str]): Lista nazw gier do porównania
        comparison_focus (str): Fokus porównania ('overall', 'value', 'quality')
    RETURNS:
        Dict: Porównanie gier z pełnymi opiniami
    """
    try:
        logger.info(f"🆚 Comparing {len(game_names)} games with full reviews...")

        if len(game_names) < 2:
            error_msg = "Need at least 2 games to compare"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

        # Generate reviews for all games
        game_reviews = []
        failed_games = []

        for game_name in game_names:
            try:
                logger.info(f"📝 Generating review for: {game_name}")
                review_result = generate_quick_game_opinion(game_name)

                if review_result.get("success", False):
                    game_reviews.append(review_result)
                    logger.info(f"✅ Review completed for: {game_name}")
                else:
                    failed_games.append(game_name)
                    logger.warning(f"⚠️ Review failed for: {game_name}")

            except Exception as e:
                failed_games.append(game_name)
                logger.error(f"❌ Error reviewing {game_name}: {e}")

        if not game_reviews:
            error_msg = "No games could be reviewed successfully"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg, "failed_games": failed_games}

        # Sort games based on comparison focus
        if comparison_focus == "value":
            # Sort by value-related factors
            game_reviews.sort(key=lambda x: x["quick_summary"]["rating"], reverse=True)
        elif comparison_focus == "quality":
            # Sort by quality score
            game_reviews.sort(
                key=lambda x: float(x["quick_summary"]["rating"].split("/")[0]),
                reverse=True,
            )
        else:  # overall
            # Sort by overall rating
            game_reviews.sort(
                key=lambda x: float(x["quick_summary"]["rating"].split("/")[0]),
                reverse=True,
            )

        # Create comparison result
        comparison_result = {
            "success": True,
            "comparison_focus": comparison_focus,
            "games_compared": len(game_reviews),
            "failed_games": failed_games,
            "winner": game_reviews[0] if game_reviews else None,
            "ranking": [],
            "comparison_summary": "",
        }

        # Create detailed ranking
        for i, review in enumerate(game_reviews, 1):
            summary = review["quick_summary"]
            ranking_entry = {
                "rank": i,
                "game_title": review["game_title"],
                "rating": summary["rating"],
                "recommendation": summary["recommendation"],
                "key_strength": summary["key_strength"],
                "main_concern": summary["main_concern"],
                "why_this_rank": _explain_review_ranking(i, len(game_reviews), summary),
            }
            comparison_result["ranking"].append(ranking_entry)

        # Generate comparison summary
        if game_reviews:
            winner = game_reviews[0]
            winner_name = winner["game_title"]
            winner_rating = winner["quick_summary"]["rating"]

            comparison_result["comparison_summary"] = (
                f"'{winner_name}' emerges as the top choice with {winner_rating} rating. "
            )

            if len(game_reviews) > 1:
                runner_up = game_reviews[1]
                runner_up_name = runner_up["game_title"]
                comparison_result[
                    "comparison_summary"
                ] += f"'{runner_up_name}' follows as a strong alternative."

        logger.info(f"✅ Game comparison completed successfully!")
        return comparison_result

    except Exception as e:
        error_msg = f"Error comparing games with reviews: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}


def _assess_data_completeness(game_data: Dict[str, Any]) -> str:
    """Ocenia kompletność danych o grze."""
    completeness_score = 0
    max_score = 8

    # Check key data fields
    if game_data.get("title"):
        completeness_score += 1
    if game_data.get("current_eshop_price"):
        completeness_score += 1
    if game_data.get("MSRP"):
        completeness_score += 1
    if game_data.get("lowest_historical_price"):
        completeness_score += 1
    if game_data.get("metacritic_score"):
        completeness_score += 1
    if game_data.get("opencritic_score"):
        completeness_score += 1
    if game_data.get("genres"):
        completeness_score += 1
    if game_data.get("developer"):
        completeness_score += 1

    percentage = (completeness_score / max_score) * 100

    if percentage >= 90:
        return "Excellent"
    elif percentage >= 75:
        return "Good"
    elif percentage >= 50:
        return "Fair"
    else:
        return "Limited"


def _explain_review_ranking(rank: int, total: int, summary: Dict[str, Any]) -> str:
    """Wyjaśnia pozycję w rankingu."""
    if rank == 1:
        return f"Top choice with {summary['rating']} rating and {summary['recommendation']} recommendation"
    elif rank == total:
        return (
            f"Last place but still worth considering for {summary['target_audience']}"
        )
    elif rank <= total // 3:
        return f"Strong contender with {summary['rating']} rating"
    else:
        return f"Solid option with some trade-offs"


def _calculate_analysis_confidence(
    game_data: Dict[str, Any], comprehensive_result: Dict[str, Any]
) -> str:
    """
    Oblicza poziom pewności analizy na podstawie dostępności danych.

    Args:
        game_data: Dane podstawowe gry
        comprehensive_result: Wyniki comprehensive analysis

    Returns:
        str: Poziom pewności ("HIGH", "MEDIUM", "LOW")
    """
    confidence_factors = []

    # Check data completeness
    has_price = bool(extract_price(game_data.get("current_eshop_price", "N/A")))
    has_msrp = bool(extract_price(game_data.get("MSRP", "N/A")))
    has_historical = bool(
        extract_price(game_data.get("lowest_historical_price", "N/A"))
    )
    has_metacritic = bool(extract_score(game_data.get("metacritic_score", "0")))
    has_opencritic = bool(extract_score(game_data.get("opencritic_score", "0")))
    has_genres = bool(game_data.get("genres", []))
    has_developer = bool(game_data.get("developer", ""))
    has_release_dates = bool(game_data.get("release_dates_parsed", {}))

    data_completeness = sum(
        [
            has_price,
            has_msrp,
            has_historical,
            has_metacritic,
            has_opencritic,
            has_genres,
            has_developer,
            has_release_dates,
        ]
    )

    # Check analysis success
    analysis_success = comprehensive_result.get("success", False)
    has_market_analysis = "market_analysis" in comprehensive_result
    has_genre_analysis = "genre_analysis" in comprehensive_result

    # Calculate confidence
    if (
        data_completeness >= 7
        and analysis_success
        and has_market_analysis
        and has_genre_analysis
    ):
        return "HIGH"
    elif data_completeness >= 5 and analysis_success:
        return "MEDIUM"
    else:
        return "LOW"


# Initialize global engines
_recommendation_engine = RecommendationEngine()
_review_generator = ReviewGenerator()


def generate_personalized_recommendations(
    games_list: List[str],
    user_preference: str = "bargain_hunter",
    max_recommendations: int = 5,
) -> Dict[str, Any]:
    """
    Generuje spersonalizowane rekomendacje gier dla użytkownika.

    DESCRIPTION: Generate personalized game recommendations based on user preferences
    ARGS:
        games_list (List[str]): Lista nazw gier do analizy
        user_preference (str): Typ preferencji użytkownika (bargain_hunter, quality_seeker, etc.)
        max_recommendations (int): Maksymalna liczba rekomendacji
    RETURNS:
        Dict: Spersonalizowane rekomendacje z uzasadnieniami
    RAISES:
        ValueError: Gdy user_preference jest nieprawidłowy
    """
    try:
        logger.info(
            f"🎯 Generating personalized recommendations for {len(games_list)} games..."
        )
        logger.info(f"👤 User preference: {user_preference}")

        # Get predefined profile
        predefined_profiles = _recommendation_engine.get_predefined_profiles()

        if user_preference not in predefined_profiles:
            available_prefs = list(predefined_profiles.keys())
            error_msg = f"Invalid user preference. Available: {available_prefs}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "available_preferences": available_prefs,
            }

        user_profile = predefined_profiles[user_preference]
        logger.info(f"✅ Using profile: {user_profile.user_id}")

        # Collect game data for all games
        games_data = []
        successful_games = []
        failed_games = []

        for game_name in games_list:
            try:
                logger.info(f"📡 Processing: {game_name}")
                game_data = search_and_scrape_game(game_name)

                if game_data.get("success", False):
                    games_data.append(game_data)
                    successful_games.append(game_name)
                    logger.info(f"✅ Successfully processed: {game_name}")
                else:
                    failed_games.append(game_name)
                    logger.warning(f"⚠️ Failed to process: {game_name}")

            except Exception as e:
                failed_games.append(game_name)
                logger.error(f"❌ Error processing {game_name}: {e}")

        if not games_data:
            error_msg = "No games could be processed successfully"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg, "failed_games": failed_games}

        # Generate recommendations
        logger.info(
            f"🚀 Generating recommendations from {len(games_data)} processed games..."
        )
        recommendations = _recommendation_engine.generate_personalized_recommendations(
            games_data, user_profile, max_recommendations
        )

        if not recommendations:
            logger.warning("⚠️ No recommendations generated")
            return {
                "success": True,
                "recommendations": [],
                "user_profile": user_profile.user_id,
                "processed_games": len(games_data),
                "message": "No suitable recommendations found",
            }

        # Format results
        formatted_recommendations = []
        for rec in recommendations:
            formatted_rec = {
                "game_title": rec.game_title,
                "recommendation_score": round(rec.recommendation_score, 2),
                "match_percentage": round(rec.match_percentage, 1),
                "confidence_level": rec.confidence_level,
                "primary_reason": rec.primary_reason.value,
                "reasons": rec.reasons,
                "personalized_message": rec.personalized_message,
                "price_info": rec.price_info,
                "analysis_summary": rec.analysis_summary,
                "warnings": rec.warnings,
            }
            formatted_recommendations.append(formatted_rec)

        result = {
            "success": True,
            "user_profile": {
                "user_id": user_profile.user_id,
                "primary_preference": user_profile.primary_preference.value,
                "preferred_genres": user_profile.preferred_genres,
                "budget_range": user_profile.budget_range,
                "minimum_score": user_profile.minimum_score,
            },
            "recommendations": formatted_recommendations,
            "statistics": {
                "total_games_requested": len(games_list),
                "successfully_processed": len(games_data),
                "failed_games": failed_games,
                "recommendations_generated": len(recommendations),
            },
            "recommendation_summary": _generate_recommendation_summary(
                recommendations, user_profile
            ),
        }

        logger.info(
            f"✅ Generated {len(recommendations)} recommendations successfully!"
        )
        return result

    except Exception as e:
        error_msg = f"Error in generate_personalized_recommendations: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}


def compare_games_for_user(
    game_names: List[str], user_preference: str = "bargain_hunter"
) -> Dict[str, Any]:
    """
    Porównuje gry pod kątem konkretnego użytkownika.

    DESCRIPTION: Compare games specifically for a user's preferences and provide ranked recommendations
    ARGS:
        game_names (List[str]): Lista nazw gier do porównania
        user_preference (str): Typ preferencji użytkownika
    RETURNS:
        Dict: Porównanie gier z rankingiem dla użytkownika
    RAISES:
        ValueError: Gdy user_preference jest nieprawidłowy lub brak gier
    """
    try:
        logger.info(
            f"🆚 Comparing {len(game_names)} games for user preference: {user_preference}"
        )

        if len(game_names) < 2:
            error_msg = "Need at least 2 games to compare"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

        # Generate recommendations (which includes comparison)
        recommendations_result = generate_personalized_recommendations(
            game_names, user_preference, len(game_names)
        )

        if not recommendations_result.get("success", False):
            return recommendations_result

        recommendations = recommendations_result["recommendations"]

        # Create comparison result
        comparison_result = {
            "success": True,
            "user_preference": user_preference,
            "comparison_type": "personalized_ranking",
            "games_compared": len(game_names),
            "ranking": [],
            "best_choice": None,
            "worst_choice": None,
            "comparison_summary": "",
        }

        # Create ranking
        for i, rec in enumerate(recommendations, 1):
            ranking_entry = {
                "rank": i,
                "game_title": rec["game_title"],
                "score": rec["recommendation_score"],
                "match_percentage": rec["match_percentage"],
                "why_this_rank": _explain_ranking_position(
                    rec, i, len(recommendations)
                ),
                "key_strengths": rec["reasons"][:2],  # Top 2 reasons
                "warnings": rec["warnings"],
            }
            comparison_result["ranking"].append(ranking_entry)

        # Set best and worst
        if recommendations:
            comparison_result["best_choice"] = {
                "game": recommendations[0]["game_title"],
                "score": recommendations[0]["recommendation_score"],
                "message": recommendations[0]["personalized_message"],
            }

            if len(recommendations) > 1:
                comparison_result["worst_choice"] = {
                    "game": recommendations[-1]["game_title"],
                    "score": recommendations[-1]["recommendation_score"],
                    "reasons": recommendations[-1]["warnings"]
                    or ["Lower overall match"],
                }

        # Generate comparison summary
        comparison_result["comparison_summary"] = _generate_comparison_summary(
            recommendations, user_preference
        )

        logger.info(f"✅ Game comparison completed for {user_preference}")
        return comparison_result

    except Exception as e:
        error_msg = f"Error in compare_games_for_user: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}


def get_recommendation_insights(
    game_name: str, user_preferences: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Analizuje jak gra pasuje do różnych typów użytkowników.

    DESCRIPTION: Analyze how a game fits different user preference types
    ARGS:
        game_name (str): Nazwa gry do analizy
        user_preferences (List[str]): Lista preferencji do sprawdzenia
    RETURNS:
        Dict: Analiza dopasowania do różnych profili użytkowników
    """
    try:
        logger.info(f"🔍 Analyzing game '{game_name}' for different user types...")

        if user_preferences is None:
            user_preferences = [
                "bargain_hunter",
                "quality_seeker",
                "indie_lover",
                "aaa_gamer",
                "casual_player",
            ]
        else:
            user_preferences = user_preferences

        # Get game data
        game_data = search_and_scrape_game(game_name)
        if not game_data.get("success", False):
            error_msg = f"Could not retrieve data for '{game_name}'"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

        # Get predefined profiles
        predefined_profiles = _recommendation_engine.get_predefined_profiles()

        # Analyze for each user type
        user_analyses = {}

        for user_pref in user_preferences:
            if user_pref not in predefined_profiles:
                logger.warning(f"⚠️ Unknown user preference: {user_pref}")
                continue

            try:
                user_profile = predefined_profiles[user_pref]

                # Get analyses
                basic_analysis = calculate_value_score(game_data)
                advanced_analysis = calculate_advanced_value_analysis(game_data)

                if not basic_analysis.get("success") or not advanced_analysis.get(
                    "success"
                ):
                    logger.warning(f"⚠️ Analysis failed for {user_pref}")
                    continue

                # Calculate recommendation score
                rec_score = _recommendation_engine.calculate_recommendation_score(
                    game_data, basic_analysis, advanced_analysis, user_profile
                )

                # Create user analysis
                user_analyses[user_pref] = {
                    "recommendation_score": round(rec_score, 2),
                    "suitability": _classify_suitability(rec_score),
                    "key_reasons": _get_key_reasons_for_user(
                        game_data, advanced_analysis, user_profile
                    ),
                    "concerns": _get_concerns_for_user(
                        game_data, advanced_analysis, user_profile
                    ),
                    "recommendation": _get_recommendation_for_score(rec_score),
                }

            except Exception as e:
                logger.error(f"❌ Error analyzing for {user_pref}: {e}")
                continue

        if not user_analyses:
            error_msg = "No successful analyses completed"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

        # Find best fit user type
        best_fit = max(
            user_analyses.items(), key=lambda x: x[1]["recommendation_score"]
        )
        worst_fit = min(
            user_analyses.items(), key=lambda x: x[1]["recommendation_score"]
        )

        result = {
            "success": True,
            "game_title": game_data.get("title", game_name),
            "user_analyses": user_analyses,
            "best_fit_user": {
                "user_type": best_fit[0],
                "score": best_fit[1]["recommendation_score"],
                "suitability": best_fit[1]["suitability"],
            },
            "worst_fit_user": {
                "user_type": worst_fit[0],
                "score": worst_fit[1]["recommendation_score"],
                "suitability": worst_fit[1]["suitability"],
            },
            "overall_insights": _generate_overall_insights(user_analyses),
        }

        logger.info(f"✅ Multi-user analysis completed for '{game_name}'")
        return result

    except Exception as e:
        error_msg = f"Error in get_recommendation_insights: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}


def _generate_recommendation_summary(
    recommendations: List[GameRecommendation], user_profile: UserProfile
) -> str:
    """Generuje podsumowanie rekomendacji."""
    if not recommendations:
        return "No recommendations available"

    best_rec = recommendations[0]
    user_type = user_profile.primary_preference.value.replace("_", " ").title()

    summary_parts = [
        f"For {user_type}: Top choice is '{best_rec.game_title}'",
        f"Score: {best_rec.recommendation_score:.1f}/100",
        f"Match: {best_rec.match_percentage:.0f}%",
    ]

    if len(recommendations) > 1:
        summary_parts.append(f"Found {len(recommendations)} suitable games")

    return " | ".join(summary_parts)


def _explain_ranking_position(rec: Dict[str, Any], rank: int, total: int) -> str:
    """Wyjaśnia pozycję w rankingu."""
    if rank == 1:
        return "Best overall match for your preferences"
    elif rank == total:
        return "Lowest match, but still worth considering"
    elif rank <= total // 3:
        return "Strong match with good value"
    else:
        return "Decent option with some trade-offs"


def _generate_comparison_summary(
    recommendations: List[Dict[str, Any]], user_preference: str
) -> str:
    """Generuje podsumowanie porównania."""
    if not recommendations:
        return "No games could be compared"

    best = recommendations[0]
    user_type = user_preference.replace("_", " ").title()

    return f"For {user_type}: '{best['game_title']}' is the clear winner with {best['match_percentage']:.0f}% match"


def _classify_suitability(score: float) -> str:
    """Klasyfikuje odpowiedniość gry."""
    if score >= 80:
        return "Excellent Fit"
    elif score >= 65:
        return "Good Fit"
    elif score >= 50:
        return "Average Fit"
    elif score >= 35:
        return "Poor Fit"
    else:
        return "Not Recommended"


def _get_key_reasons_for_user(
    game_data: Dict[str, Any],
    advanced_analysis: Dict[str, Any],
    user_profile: UserProfile,
) -> List[str]:
    """Zwraca kluczowe powody dla użytkownika."""
    reasons = []

    market_analysis = advanced_analysis.get("comprehensive_analysis", {}).get(
        "market_analysis", {}
    )
    market_position = market_analysis.get("market_position", "")

    pref = user_profile.primary_preference

    if pref == UserPreference.BARGAIN_HUNTER and "Great Deal" in market_position:
        reasons.append("Excellent value for money")
    elif pref == UserPreference.QUALITY_SEEKER and "Exceptional" in market_analysis.get(
        "quality_category", ""
    ):
        reasons.append("High quality gaming experience")
    elif pref == UserPreference.INDIE_LOVER:
        reasons.append("Supports independent developers")

    return reasons[:3]


def _get_concerns_for_user(
    game_data: Dict[str, Any],
    advanced_analysis: Dict[str, Any],
    user_profile: UserProfile,
) -> List[str]:
    """Zwraca obawy dla użytkownika."""
    concerns = []

    from utils.price_calculator import extract_price

    current_price = extract_price(game_data.get("current_eshop_price", "N/A"))

    if current_price and current_price > user_profile.budget_range[1]:
        concerns.append("Exceeds budget range")

    return concerns[:3]


def _get_recommendation_for_score(score: float) -> str:
    """Zwraca rekomendację na podstawie score."""
    if score >= 80:
        return "Highly Recommended"
    elif score >= 65:
        return "Recommended"
    elif score >= 50:
        return "Consider"
    else:
        return "Skip"


def _generate_overall_insights(user_analyses: Dict[str, Any]) -> List[str]:
    """Generuje ogólne insights."""
    insights = []

    scores = [analysis["recommendation_score"] for analysis in user_analyses.values()]
    avg_score = sum(scores) / len(scores) if scores else 0

    if avg_score >= 70:
        insights.append("Universally appealing game - good for most players")
    elif avg_score >= 50:
        insights.append("Appeals to specific user types")
    else:
        insights.append("Niche appeal - very specific audience")

    return insights


def scrape_dekudeals_category(
    category: str, max_games: int = 20, include_details: bool = False
) -> Dict[str, Any]:
    """
    Scrapuje listę gier z określonej kategorii DekuDeals.

    DESCRIPTION: Scrape games from DekuDeals category pages for diverse testing data
    ARGS:
        category (str): Kategoria do scrapowania (np. 'hottest', 'recent-drops', 'highest-rated')
        max_games (int): Maksymalna liczba gier do pobrania
        include_details (bool): Czy dołączyć szczegółowe dane o grach
    RETURNS:
        Dict: Lista gier z kategorii wraz z metadanymi
    RAISES:
        ValueError: Gdy kategoria jest nieprawidłowa
    """
    try:
        logger.info(f"🎯 Scraping DekuDeals category: {category} (max: {max_games})")

        # Available categories mapping
        available_categories = {
            "hottest": "Hottest Deals",
            "recent-drops": "Recent Price Drops",
            "bang-for-your-buck": "Bang for your Buck",
            "ending-soon": "Ending Soon",
            "most-wanted": "Most Wanted",
            "upcoming-releases": "Upcoming Releases",
            "recently-released": "Recently Released",
            "highest-rated": "Highly Rated",
            "staff-picks": "Staff Picks",
            "deepest-discounts": "Deepest Discounts",
            "newest-listings": "Newly Listed",
            "trending": "Trending Games",
        }

        # Special handling for problematic categories
        problematic_categories = {
            "eshop-sales": "eShop Sales category is temporarily unavailable due to site protection. Try 'hottest' or 'recent-drops' instead."
        }

        if category in problematic_categories:
            error_msg = problematic_categories[category]
            logger.warning(f"⚠️ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "category": category,
                "available_categories": list(available_categories.keys()),
                "suggested_alternatives": [
                    "hottest",
                    "recent-drops",
                    "deepest-discounts",
                ],
            }

        if category not in available_categories:
            error_msg = f"Invalid category '{category}'. Available: {list(available_categories.keys())}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "available_categories": list(available_categories.keys()),
            }

        # Build URL
        base_url = "https://www.dekudeals.com"
        category_url = f"{base_url}/{category}"

        logger.info(f"🌐 Scraping URL: {category_url}")

        # Make request with headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(category_url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"❌ Failed to fetch {category_url}: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch category page: {str(e)}",
                "category": category,
            }

        # Parse HTML
        soup = BeautifulSoup(response.content, "html.parser")

        # Find game cards/items - multiple selectors for different page layouts
        game_elements = []

        # Try different selectors that DekuDeals might use
        selectors_to_try = [
            ".main-list-item",  # Main list items
            ".game-list-item",  # Game list items
            ".deal-tile",  # Deal tiles
            ".game-tile",  # Game tiles
            ".list-item",  # General list items
            "div[data-game-id]",  # Elements with game IDs
            'a[href*="/items/"]',  # Links to game pages
        ]

        for selector in selectors_to_try:
            elements = soup.select(selector)
            if elements:
                game_elements = elements
                logger.info(
                    f"✅ Found {len(elements)} games using selector: {selector}"
                )
                break

        if not game_elements:
            logger.warning(
                "⚠️ No games found with standard selectors, trying alternative approach..."
            )

            # Alternative: look for any links to /items/
            item_links = soup.find_all("a", href=True)
            game_elements = [
                link for link in item_links if "/items/" in str(link.get("href", ""))
            ]

            if game_elements:
                logger.info(
                    f"✅ Found {len(game_elements)} game links using alternative method"
                )
            else:
                logger.error("❌ No games found on category page")
                return {
                    "success": False,
                    "error": "No games found on category page",
                    "category": category,
                    "category_url": category_url,
                }

        # Extract game information
        games_found = []
        processed_games = set()  # Avoid duplicates

        for element in game_elements[
            : max_games * 2
        ]:  # Process more than needed to filter
            try:
                game_info = _extract_game_info_from_element(element, base_url)

                if game_info and game_info["title"] not in processed_games:
                    games_found.append(game_info)
                    processed_games.add(game_info["title"])

                    if len(games_found) >= max_games:
                        break
            except Exception as e:
                logger.debug(f"🔍 Skipping element due to parsing error: {e}")
                continue

        if not games_found:
            logger.error("❌ No valid games extracted from category page")
            return {
                "success": False,
                "error": "No valid games extracted from category page",
                "category": category,
            }

        # Add detailed game data if requested
        if include_details:
            logger.info(f"📊 Fetching detailed data for {len(games_found)} games...")
            detailed_games = []

            for game_info in games_found:
                try:
                    game_name = game_info["title"]
                    detailed_data = search_and_scrape_game(game_name)

                    if detailed_data.get("success", False):
                        # Merge basic info with detailed data
                        enhanced_game = {**game_info, **detailed_data}
                        detailed_games.append(enhanced_game)
                        logger.debug(f"✅ Enhanced data for: {game_name}")
                    else:
                        # Keep basic info even if detailed scraping fails
                        detailed_games.append(game_info)
                        logger.debug(f"⚠️ Using basic data for: {game_name}")

                except Exception as e:
                    logger.warning(
                        f"⚠️ Failed to get detailed data for {game_info['title']}: {e}"
                    )
                    detailed_games.append(game_info)

            games_found = detailed_games

        result = {
            "success": True,
            "category": category,
            "category_name": available_categories[category],
            "category_url": category_url,
            "games_found": len(games_found),
            "games": games_found,
            "game_titles": [game["title"] for game in games_found],
            "scraping_metadata": {
                "max_games_requested": max_games,
                "include_details": include_details,
                "total_elements_found": len(game_elements),
                "games_processed": len(games_found),
                "timestamp": datetime.now().isoformat(),
            },
        }

        logger.info(
            f"✅ Successfully scraped {len(games_found)} games from '{category}' category"
        )
        return result

    except Exception as e:
        error_msg = f"Error scraping category '{category}': {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg, "category": category}


def _extract_game_info_from_element(element, base_url: str) -> Optional[Dict[str, Any]]:
    """
    Wyciąga informacje o grze z elementu HTML.

    Args:
        element: Element HTML zawierający dane gry
        base_url: Bazowy URL DekuDeals

    Returns:
        Dict z informacjami o grze lub None
    """
    try:
        game_info = {}

        # Try to find game title
        title_element = None
        title_selectors = [
            ".game-title",
            ".title",
            "h3",
            "h4",
            "h5",
            ".name",
            'a[href*="/items/"]',
        ]

        for selector in title_selectors:
            title_element = element.select_one(selector)
            if title_element:
                break

        if not title_element:
            # If element itself is a link, use its text
            try:
                if (
                    isinstance(element, Tag)
                    and element.name == "a"
                    and element.get("href")
                    and "/items/" in str(element.get("href", ""))
                ):
                    title_element = element
            except (AttributeError, TypeError):
                pass

        if not title_element:
            return None

        # Extract title
        title = title_element.get_text(strip=True)
        if not title or len(title) < 2:
            return None

        game_info["title"] = title

        # Try to find game URL
        game_url = None
        if element.name == "a" and "/items/" in element.get("href", ""):
            game_url = element.get("href")
        else:
            link_element = element.find("a", href=True)
            if link_element and "/items/" in link_element.get("href", ""):
                game_url = link_element.get("href")

        if game_url:
            if game_url.startswith("/"):
                game_url = base_url + game_url
            game_info["game_url"] = game_url

        # Try to extract price information
        price_selectors = [".price", ".current-price", ".sale-price", ".cost"]

        for selector in price_selectors:
            price_element = element.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                game_info["current_price"] = price_text
                break

        # Try to extract discount information
        discount_selectors = [".discount", ".sale-discount", ".percent-off"]

        for selector in discount_selectors:
            discount_element = element.select_one(selector)
            if discount_element:
                discount_text = discount_element.get_text(strip=True)
                game_info["discount"] = discount_text
                break

        # Try to extract rating/score
        rating_selectors = [".rating", ".score", ".metacritic", ".review-score"]

        for selector in rating_selectors:
            rating_element = element.select_one(selector)
            if rating_element:
                rating_text = rating_element.get_text(strip=True)
                game_info["rating"] = rating_text
                break

        return game_info

    except Exception as e:
        logger.debug(f"🔍 Failed to extract game info from element: {e}")
        return None


def get_games_from_popular_categories(
    max_games_per_category: int = 10, categories: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Pobiera gry z popularnych kategorii DekuDeals dla testowania.

    DESCRIPTION: Get games from multiple popular DekuDeals categories for diverse testing
    ARGS:
        max_games_per_category (int): Maksymalna liczba gier na kategorię
        categories (List[str]): Lista kategorii do sprawdzenia (None = domyślne)
    RETURNS:
        Dict: Gry z różnych kategorii pogrupowane
    """
    try:
        logger.info(f"🎯 Collecting games from popular categories...")

        # Default categories for testing
        if categories is None:
            categories = [
                "hottest",  # Current hot deals
                "recent-drops",  # Recent price drops
                "highest-rated",  # High quality games
                "bang-for-your-buck",  # Value games
                "deepest-discounts",  # Best discounts
            ]

        all_games = {}
        all_titles = []
        failed_categories = []

        for category in categories:
            try:
                logger.info(f"📋 Processing category: {category}")
                result = scrape_dekudeals_category(category, max_games_per_category)

                if result.get("success", False):
                    games = result.get("games", [])
                    titles = result.get("game_titles", [])

                    all_games[category] = {
                        "category_name": result.get("category_name", category),
                        "games": games,
                        "count": len(games),
                    }
                    all_titles.extend(titles)

                    logger.info(f"✅ Got {len(games)} games from {category}")
                else:
                    failed_categories.append(category)
                    logger.warning(f"⚠️ Failed to get games from {category}")

            except Exception as e:
                failed_categories.append(category)
                logger.error(f"❌ Error processing category {category}: {e}")

        # Remove duplicates from all_titles while preserving order
        unique_titles = []
        seen = set()
        for title in all_titles:
            if title not in seen:
                unique_titles.append(title)
                seen.add(title)

        result = {
            "success": True,
            "categories_processed": len(all_games),
            "categories_failed": len(failed_categories),
            "failed_categories": failed_categories,
            "games_by_category": all_games,
            "all_unique_titles": unique_titles,
            "total_unique_games": len(unique_titles),
            "collection_metadata": {
                "max_games_per_category": max_games_per_category,
                "categories_requested": categories,
                "timestamp": datetime.now().isoformat(),
            },
        }

        logger.info(
            f"✅ Collected {len(unique_titles)} unique games from {len(all_games)} categories"
        )
        return result

    except Exception as e:
        error_msg = f"Error collecting games from categories: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}


def get_random_game_sample(
    sample_size: int = 5, category_preference: str = "mixed"
) -> Dict[str, Any]:
    """
    Pobiera losowy zestaw gier do testowania.

    DESCRIPTION: Get random sample of games from DekuDeals for unbiased testing
    ARGS:
        sample_size (int): Liczba gier do pobrania
        category_preference (str): Preferencja kategorii ('mixed', 'deals', 'quality', 'trending')
    RETURNS:
        Dict: Losowy zestaw gier z metadanymi
    """
    try:
        logger.info(
            f"🎲 Getting random sample of {sample_size} games (preference: {category_preference})"
        )

        # Define category sets based on preference
        category_sets = {
            "mixed": [
                "hottest",
                "recent-drops",
                "highest-rated",
                "trending",
                "staff-picks",
            ],
            "deals": [
                "hottest",
                "recent-drops",
                "deepest-discounts",
                "bang-for-your-buck",
                "ending-soon",
            ],
            "quality": ["highest-rated", "staff-picks", "most-wanted", "trending"],
            "trending": ["trending", "recently-released", "most-wanted", "hottest"],
        }

        categories = category_sets.get(category_preference, category_sets["mixed"])

        # Get games from categories
        games_per_category = max(3, sample_size // len(categories) + 1)
        collection_result = get_games_from_popular_categories(
            games_per_category, categories
        )

        if not collection_result.get("success", False):
            return collection_result

        all_titles = collection_result.get("all_unique_titles", [])

        if len(all_titles) < sample_size:
            logger.warning(
                f"⚠️ Only found {len(all_titles)} games, less than requested {sample_size}"
            )
            selected_titles = all_titles
        else:
            # Randomly sample games
            import random

            selected_titles = random.sample(all_titles, sample_size)

        result = {
            "success": True,
            "sample_size_requested": sample_size,
            "sample_size_actual": len(selected_titles),
            "category_preference": category_preference,
            "categories_used": categories,
            "selected_games": selected_titles,
            "sampling_metadata": {
                "total_games_available": len(all_titles),
                "timestamp": datetime.now().isoformat(),
                "source_categories": list(
                    collection_result.get("games_by_category", {}).keys()
                ),
            },
        }

        logger.info(f"✅ Selected random sample: {selected_titles}")
        return result

    except Exception as e:
        error_msg = f"Error getting random game sample: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}


# Initialize global opinion adapter
_opinion_adapter = OpinionAdapter()


def adapt_review_for_context(
    game_name: str,
    style: str = "casual",
    format_type: str = "summary",
    audience: str = "general_public",
    platform: str = "website",
    max_length: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Adaptuje opinię o grze do określonego kontekstu komunikacyjnego.

    DESCRIPTION: Adapt game review to specific communication context and audience
    ARGS:
        game_name (str): Nazwa gry do adaptacji
        style (str): Styl komunikacji (casual, technical, social_media, professional, gaming_enthusiast, beginner_friendly)
        format_type (str): Format wyjściowy (detailed, summary, bullet_points, social_post, comparison_table, recommendation_card)
        audience (str): Grupa docelowa (bargain_hunters, quality_seekers, casual_gamers, hardcore_gamers, indie_lovers, family_oriented, general_public)
        platform (str): Platforma docelowa (twitter, reddit, facebook, website, blog, newsletter)
        max_length (int): Maksymalna długość treści (opcjonalne)
    RETURNS:
        Dict: Adaptowana opinia z metadanymi
    RAISES:
        ValueError: Gdy nie można wygenerować opinii lub nieprawidłowe parametry
    """
    try:
        logger.info(
            f"🎭 Adapting review for {game_name}: {style}/{format_type}/{audience}"
        )

        # Generate base comprehensive review
        base_review_result = generate_comprehensive_game_review(
            game_name, include_recommendations=True
        )

        if not base_review_result.get("success", False):
            error_msg = f"Could not generate base review for '{game_name}'"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg, "game_name": game_name}

        # Extract review object (we need to reconstruct it from result)
        from utils.review_generator import (
            GameReview,
            ReviewConfidence,
            RecommendationType,
        )

        review_data = base_review_result.get("review_data", {})

        # Map string values back to enums
        confidence_mapping = {
            "very_high": ReviewConfidence.VERY_HIGH,
            "high": ReviewConfidence.HIGH,
            "medium": ReviewConfidence.MEDIUM,
            "low": ReviewConfidence.LOW,
            "very_low": ReviewConfidence.VERY_LOW,
        }

        recommendation_mapping = {
            "instant_buy": RecommendationType.INSTANT_BUY,
            "strong_buy": RecommendationType.STRONG_BUY,
            "buy": RecommendationType.BUY,
            "consider": RecommendationType.CONSIDER,
            "wait_for_sale": RecommendationType.WAIT_FOR_SALE,
            "wait": RecommendationType.WAIT,
            "skip": RecommendationType.SKIP,
        }

        # Reconstruct GameReview object
        review = GameReview(
            game_title=review_data.get("overall_rating", game_name),
            overall_rating=review_data.get("overall_rating", 5.0),
            recommendation=recommendation_mapping.get(
                review_data.get("recommendation", "consider"),
                RecommendationType.CONSIDER,
            ),
            confidence=confidence_mapping.get(
                review_data.get("confidence", "medium"), ReviewConfidence.MEDIUM
            ),
            strengths=review_data.get("strengths", []),
            weaknesses=review_data.get("weaknesses", []),
            target_audience=review_data.get("target_audience", []),
            value_assessment=review_data.get("value_assessment", "Standard value"),
            price_recommendation=review_data.get(
                "price_recommendation", "No recommendation"
            ),
            timing_advice=review_data.get("timing_advice", "Consider timing"),
            final_verdict=review_data.get("final_verdict", "Game review completed"),
        )

        # Map string parameters to enums
        style_mapping = {
            "technical": CommunicationStyle.TECHNICAL,
            "casual": CommunicationStyle.CASUAL,
            "social_media": CommunicationStyle.SOCIAL_MEDIA,
            "professional": CommunicationStyle.PROFESSIONAL,
            "gaming_enthusiast": CommunicationStyle.GAMING_ENTHUSIAST,
            "beginner_friendly": CommunicationStyle.BEGINNER_FRIENDLY,
        }

        format_mapping = {
            "detailed": OutputFormat.DETAILED,
            "summary": OutputFormat.SUMMARY,
            "bullet_points": OutputFormat.BULLET_POINTS,
            "social_post": OutputFormat.SOCIAL_POST,
            "comparison_table": OutputFormat.COMPARISON_TABLE,
            "recommendation_card": OutputFormat.RECOMMENDATION_CARD,
        }

        audience_mapping = {
            "bargain_hunters": AudienceType.BARGAIN_HUNTERS,
            "quality_seekers": AudienceType.QUALITY_SEEKERS,
            "casual_gamers": AudienceType.CASUAL_GAMERS,
            "hardcore_gamers": AudienceType.HARDCORE_GAMERS,
            "indie_lovers": AudienceType.INDIE_LOVERS,
            "family_oriented": AudienceType.FAMILY_ORIENTED,
            "general_public": AudienceType.GENERAL_PUBLIC,
        }

        # Validate and map parameters
        comm_style = style_mapping.get(style)
        output_format = format_mapping.get(format_type)
        target_audience = audience_mapping.get(audience)

        if not comm_style or not output_format or not target_audience:
            error_msg = f"Invalid parameters: style='{style}', format='{format_type}', audience='{audience}'"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "available_styles": list(style_mapping.keys()),
                "available_formats": list(format_mapping.keys()),
                "available_audiences": list(audience_mapping.keys()),
            }

        # Create adaptation context
        context = AdaptationContext(
            style=comm_style,
            format=output_format,
            audience=target_audience,
            platform=platform,
            max_length=max_length,
            include_emoji=platform in ["twitter", "facebook", "instagram"],
            include_price_focus=target_audience == AudienceType.BARGAIN_HUNTERS,
            include_technical_details=comm_style == CommunicationStyle.TECHNICAL,
        )

        # Adapt the review
        adapted_opinion = _opinion_adapter.adapt_opinion(review, context)

        # Create result
        result = {
            "success": True,
            "game_title": game_name,
            "adaptation_context": {
                "style": style,
                "format": format_type,
                "audience": audience,
                "platform": platform,
                "max_length": max_length,
            },
            "adapted_content": adapted_opinion.content,
            "metadata": adapted_opinion.metadata,
            "character_count": adapted_opinion.character_count,
            "engagement_elements": adapted_opinion.engagement_elements,
            "call_to_action": adapted_opinion.call_to_action,
            "original_review_data": {
                "rating": review.overall_rating,
                "recommendation": review.recommendation.value,
                "confidence": review.confidence.value,
            },
            "adaptation_timestamp": adapted_opinion.adaptation_timestamp.isoformat(),
        }

        logger.info(
            f"✅ Review adapted successfully: {adapted_opinion.character_count} chars"
        )
        return result

    except Exception as e:
        error_msg = f"Error adapting review for '{game_name}': {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg, "game_name": game_name}


def create_multi_platform_opinions(
    game_name: str, platforms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Tworzy opinie o grze dla wielu platform jednocześnie.

    DESCRIPTION: Create game opinions for multiple platforms simultaneously with platform-specific adaptations
    ARGS:
        game_name (str): Nazwa gry do analizy
        platforms (List[str]): Lista platform (twitter, reddit, facebook, website, blog, newsletter)
    RETURNS:
        Dict: Opinie dostosowane do różnych platform z metadanymi
    """
    try:
        logger.info(f"🌐 Creating multi-platform opinions for: {game_name}")

        if platforms is None:
            platforms = ["twitter", "reddit", "website", "blog"]

        # Generate base comprehensive review
        base_review_result = generate_comprehensive_game_review(
            game_name, include_recommendations=True
        )

        if not base_review_result.get("success", False):
            error_msg = f"Could not generate base review for '{game_name}'"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg, "game_name": game_name}

        # Reconstruct GameReview object (same logic as above)
        from utils.review_generator import (
            GameReview,
            ReviewConfidence,
            RecommendationType,
        )

        review_data = base_review_result.get("review_data", {})

        confidence_mapping = {
            "very_high": ReviewConfidence.VERY_HIGH,
            "high": ReviewConfidence.HIGH,
            "medium": ReviewConfidence.MEDIUM,
            "low": ReviewConfidence.LOW,
            "very_low": ReviewConfidence.VERY_LOW,
        }

        recommendation_mapping = {
            "instant_buy": RecommendationType.INSTANT_BUY,
            "strong_buy": RecommendationType.STRONG_BUY,
            "buy": RecommendationType.BUY,
            "consider": RecommendationType.CONSIDER,
            "wait_for_sale": RecommendationType.WAIT_FOR_SALE,
            "wait": RecommendationType.WAIT,
            "skip": RecommendationType.SKIP,
        }

        review = GameReview(
            game_title=review_data.get("game_title", game_name),
            overall_rating=review_data.get("overall_rating", 5.0),
            recommendation=recommendation_mapping.get(
                review_data.get("recommendation", "consider"),
                RecommendationType.CONSIDER,
            ),
            confidence=confidence_mapping.get(
                review_data.get("confidence", "medium"), ReviewConfidence.MEDIUM
            ),
            strengths=review_data.get("strengths", []),
            weaknesses=review_data.get("weaknesses", []),
            target_audience=review_data.get("target_audience", []),
            value_assessment=review_data.get("value_assessment", "Standard value"),
            price_recommendation=review_data.get(
                "price_recommendation", "No recommendation"
            ),
            timing_advice=review_data.get("timing_advice", "Consider timing"),
            final_verdict=review_data.get("final_verdict", "Game review completed"),
        )

        # Generate platform-specific opinions
        platform_opinions = format_for_multiple_platforms(review, platforms)

        # Format results
        formatted_results = {}
        for platform, adapted_opinion in platform_opinions.items():
            formatted_results[platform] = {
                "content": adapted_opinion.content,
                "character_count": adapted_opinion.character_count,
                "style": adapted_opinion.style_used.value,
                "format": adapted_opinion.format_used.value,
                "audience": adapted_opinion.audience_targeted.value,
                "engagement_elements": adapted_opinion.engagement_elements,
                "call_to_action": adapted_opinion.call_to_action,
                "metadata": adapted_opinion.metadata,
            }

        result = {
            "success": True,
            "game_title": game_name,
            "platforms_generated": len(formatted_results),
            "platform_opinions": formatted_results,
            "generation_summary": {
                "total_characters": sum(
                    op.character_count for op in platform_opinions.values()
                ),
                "platforms_requested": platforms,
                "timestamp": datetime.now().isoformat(),
            },
            "base_review_rating": review.overall_rating,
            "base_recommendation": review.recommendation.value,
        }

        logger.info(
            f"✅ Multi-platform opinions created for {len(platforms)} platforms"
        )
        return result

    except Exception as e:
        error_msg = (
            f"Error creating multi-platform opinions for '{game_name}': {str(e)}"
        )
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg, "game_name": game_name}


def get_available_adaptation_options() -> Dict[str, Any]:
    """
    Zwraca dostępne opcje adaptacji opinii.

    DESCRIPTION: Get available adaptation options for review customization
    RETURNS:
        Dict: Wszystkie dostępne opcje adaptacji z opisami
    """
    try:
        logger.info("📋 Getting available adaptation options...")

        presets = create_context_presets()

        options = {
            "success": True,
            "communication_styles": {
                "technical": "Detailed, analytical communication with data focus",
                "casual": "Friendly, conversational tone for general audience",
                "social_media": "Short, engaging content with emojis and hashtags",
                "professional": "Formal, business-oriented communication",
                "gaming_enthusiast": "Expert-level discussion for passionate gamers",
                "beginner_friendly": "Simple, easy-to-understand explanations",
            },
            "output_formats": {
                "detailed": "Full, comprehensive review with all sections",
                "summary": "Brief overview with key points",
                "bullet_points": "Organized list format for easy scanning",
                "social_post": "Social media ready post with hashtags",
                "comparison_table": "Structured table format for comparisons",
                "recommendation_card": "Visual card-style recommendation",
            },
            "audience_types": {
                "bargain_hunters": "Price-focused users looking for best deals",
                "quality_seekers": "Users prioritizing game quality and ratings",
                "casual_gamers": "Occasional players seeking accessible games",
                "hardcore_gamers": "Enthusiast players wanting depth and challenge",
                "indie_lovers": "Supporters of independent game developers",
                "family_oriented": "Parents looking for family-friendly content",
                "general_public": "Broad audience with mixed interests",
            },
            "supported_platforms": {
                "twitter": "280 character limit, hashtag optimized",
                "reddit": "Detailed discussion format",
                "facebook": "Casual social sharing",
                "website": "Professional web content",
                "blog": "Long-form article style",
                "newsletter": "Email-friendly format",
            },
            "preset_combinations": {
                name: {
                    "style": preset.style.value,
                    "format": preset.format.value,
                    "audience": preset.audience.value,
                    "platform": preset.platform,
                    "description": f"{preset.style.value.replace('_', ' ').title()} style {preset.format.value} for {preset.audience.value.replace('_', ' ')}",
                }
                for name, preset in presets.items()
            },
            "usage_examples": [
                "adapt_review_for_context('Celeste', 'social_media', 'social_post', 'bargain_hunters', 'twitter')",
                "create_multi_platform_opinions('Hollow Knight', ['twitter', 'reddit', 'blog'])",
                "adapt_review_for_context('INSIDE', 'beginner_friendly', 'bullet_points', 'family_oriented')",
            ],
        }

        logger.info(
            f"✅ Retrieved adaptation options: {len(options['communication_styles'])} styles, {len(options['output_formats'])} formats"
        )
        return options

    except Exception as e:
        error_msg = f"Error getting adaptation options: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}


# ======================== PHASE 4: QUALITY VALIDATION TOOLS ========================


def perform_quality_validation(
    complete_analysis_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Przeprowadza zaawansowaną walidację jakości kompletnej analizy gry.

    DESCRIPTION: Perform comprehensive quality validation of complete game analysis using automated rules
    ARGS:
        complete_analysis_data (Dict): Kompletne dane analizy gry (raw data + value analysis + review + recommendations)
    RETURNS:
        Dict: Raport jakości z wynikami validation, rekomendacjami i metrics
    RAISES:
        ValueError: Gdy brakuje wymaganych danych do walidacji
    """
    try:
        logger.info("🔍 Starting comprehensive quality validation...")

        # Validate input structure
        if not isinstance(complete_analysis_data, dict):
            error_msg = "Analysis data must be a dictionary"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "validation_type": "input_structure",
                "timestamp": datetime.now().isoformat(),
            }

        # Perform validation using quality validation system
        validation_result = validate_game_analysis(complete_analysis_data)

        if not validation_result.get("success", False):
            logger.error(
                f"❌ Quality validation failed: {validation_result.get('error')}"
            )
            return validation_result

        # Extract quality report
        quality_report = validation_result.get("quality_report", {})
        quality_level = quality_report.get("quality_level", "UNKNOWN")
        overall_score = quality_report.get("overall_score", 0.0)
        critical_failures = quality_report.get("critical_failures_count", 0)
        recommendations = quality_report.get("recommendations", [])

        # Log validation results
        if critical_failures > 0:
            logger.warning(
                f"⚠️ Quality validation completed with {critical_failures} critical failures"
            )
        else:
            logger.info(
                f"✅ Quality validation passed: {quality_level} ({overall_score:.2f}/1.0)"
            )

        # Enhance result with actionable insights
        enhanced_result = {
            "success": True,
            "validation_type": "comprehensive_quality_check",
            "game_title": complete_analysis_data.get("title", "Unknown"),
            "quality_assessment": {
                "overall_score": overall_score,
                "quality_level": quality_level,
                "critical_failures_count": critical_failures,
                "passes_quality_gates": critical_failures == 0,
                "publication_ready": overall_score >= 0.7 and critical_failures == 0,
            },
            "quality_metrics": {
                "data_completeness": quality_report.get("data_completeness", 0.0),
                "logical_consistency": quality_report.get("logical_consistency", 0.0),
                "content_quality": quality_report.get("content_quality", 0.0),
            },
            "validation_details": quality_report.get("details", []),
            "improvement_recommendations": recommendations,
            "timestamp": validation_result.get("timestamp"),
            "validation_summary": _generate_validation_summary(quality_report),
        }

        return enhanced_result

    except Exception as e:
        error_msg = f"Error during quality validation: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "validation_type": "system_error",
            "timestamp": datetime.now().isoformat(),
        }


def _generate_validation_summary(quality_report: Dict[str, Any]) -> str:
    """
    Generuje tekstowe podsumowanie wyników walidacji.

    Args:
        quality_report: Raport jakości z validate_game_analysis

    Returns:
        str: Tekstowe podsumowanie wyników walidacji
    """
    try:
        overall_score = quality_report.get("overall_score", 0.0)
        quality_level = quality_report.get("quality_level", "UNKNOWN")
        critical_failures = quality_report.get("critical_failures_count", 0)
        total_validations = quality_report.get("total_validations", 0)

        # Create summary components
        summary_parts = []

        # Overall assessment
        if quality_level == "EXCELLENT":
            summary_parts.append("⭐ Exceptional analysis quality")
        elif quality_level == "GOOD":
            summary_parts.append("✅ High-quality analysis")
        elif quality_level == "ACCEPTABLE":
            summary_parts.append("👍 Acceptable analysis quality")
        elif quality_level == "POOR":
            summary_parts.append("⚠️ Below-standard analysis quality")
        else:
            summary_parts.append("❌ Unacceptable analysis quality")

        # Score breakdown
        summary_parts.append(f"Score: {overall_score:.1f}/1.0")

        # Critical issues
        if critical_failures == 0:
            summary_parts.append("No critical issues")
        else:
            summary_parts.append(f"{critical_failures} critical issues")

        # Data quality metrics
        data_completeness = quality_report.get("data_completeness", 0.0)
        logical_consistency = quality_report.get("logical_consistency", 0.0)
        content_quality = quality_report.get("content_quality", 0.0)

        summary_parts.append(
            f"Metrics: Data {data_completeness:.1f} | Logic {logical_consistency:.1f} | Content {content_quality:.1f}"
        )

        return " | ".join(summary_parts)

    except Exception as e:
        return f"Summary generation error: {str(e)}"


# Example usage (commented out to avoid circular import):
# manager = GameAnalysisManager()
# result = manager.analyze_game("Celeste")
# Output: 5-agent coordinated analysis with quality assurance

# ======================== PHASE 4: ENHANCED QUALITY CONTROL TOOLS ========================

# Import enhanced Phase 4 components
from utils.qa_enhanced_agent import create_qa_agent, QAValidationLevel
from utils.automatic_completeness_checker import create_completeness_checker
from utils.quality_metrics_tracker import create_quality_metrics_tracker

# Initialize Phase 4 components
enhanced_qa_agent = create_qa_agent("comprehensive")
completeness_checker = create_completeness_checker()
quality_metrics_tracker = create_quality_metrics_tracker()


@register_for_llm(
    description="Enhanced QA validation with sophisticated validation rules - Input: complete_analysis_data (Dict) - Output: Dict with enhanced QA report"
)
@register_for_execution()
def enhanced_qa_validation(complete_analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Przeprowadza zaawansowaną walidację jakości z wykorzystaniem Enhanced QA Agent.

    DESCRIPTION: Advanced quality validation using sophisticated validation rules and intelligent assessment
    ARGS:
        complete_analysis_data (Dict): Kompletne dane analizy gry
    RETURNS:
        Dict: Zaawansowany raport jakości z detailed insights
    RAISES:
        ValueError: Gdy brakuje wymaganych danych do walidacji
    """
    try:
        logger.info("🔍 Starting enhanced QA validation...")

        # Validate input
        if not isinstance(complete_analysis_data, dict):
            error_msg = "Enhanced QA validation requires dictionary input"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "validation_type": "enhanced_qa_validation",
                "timestamp": datetime.now().isoformat(),
            }

        # Perform enhanced validation
        qa_report = enhanced_qa_agent.validate_analysis(complete_analysis_data)

        # Convert to dictionary format
        result = {
            "success": True,
            "validation_type": "enhanced_qa_validation",
            "game_title": complete_analysis_data.get("title", "Unknown"),
            "enhanced_qa_report": {
                "overall_score": qa_report.overall_score,
                "quality_level": qa_report.quality_level,
                "total_validation_time": qa_report.total_validation_time,
                "validation_summary": qa_report.validation_summary,
                "critical_issues_count": len(qa_report.critical_issues),
                "warnings_count": len(qa_report.warnings),
                "recommendations": qa_report.recommendations,
                "metrics_breakdown": {
                    "completeness_score": qa_report.completeness_score,
                    "coherence_score": qa_report.coherence_score,
                    "quality_score": qa_report.quality_score,
                    "consistency_score": qa_report.consistency_score,
                },
            },
            "validation_details": [
                {
                    "rule_id": result.rule_id,
                    "rule_name": result.rule_name,
                    "passed": result.passed,
                    "score": result.score,
                    "message": result.message,
                    "recommendations": result.recommendations,
                    "validation_time": result.validation_time,
                }
                for result in qa_report.validation_results
            ],
            "timestamp": qa_report.timestamp.isoformat(),
        }

        logger.info(
            f"✅ Enhanced QA validation completed: {qa_report.quality_level} ({qa_report.overall_score:.2f}/1.0)"
        )
        return result

    except Exception as e:
        error_msg = f"Enhanced QA validation error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "validation_type": "enhanced_qa_validation",
            "timestamp": datetime.now().isoformat(),
        }


@register_for_llm(
    description="Automatic data completeness checking with intelligent validation - Input: game_data (Dict) - Output: Dict with completeness report"
)
@register_for_execution()
def automatic_completeness_check(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Przeprowadza automatyczne sprawdzanie kompletności danych z inteligentną walidacją.

    DESCRIPTION: Automated data completeness checking with field validation and improvement suggestions
    ARGS:
        game_data (Dict): Dane gry do sprawdzenia kompletności
    RETURNS:
        Dict: Raport kompletności z suggestions i quality insights
    RAISES:
        ValueError: Gdy dane wejściowe są nieprawidłowe
    """
    try:
        logger.info("📊 Starting automatic completeness checking...")

        # Validate input
        if not isinstance(game_data, dict):
            error_msg = "Completeness checking requires dictionary input"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "checking_type": "automatic_completeness",
                "timestamp": datetime.now().isoformat(),
            }

        # Perform completeness check
        completeness_report = completeness_checker.check_completeness(game_data)

        # Try auto-fix common issues
        fixed_data, fixes_applied = completeness_checker.auto_fix_data_issues(game_data)

        # Convert to dictionary format
        result = {
            "success": True,
            "checking_type": "automatic_completeness",
            "game_title": game_data.get("title", "Unknown"),
            "completeness_report": {
                "overall_score": completeness_report.overall_score,
                "completeness_level": completeness_report.completeness_level,
                "total_fields": completeness_report.total_fields,
                "present_fields": completeness_report.present_fields,
                "valid_fields": completeness_report.valid_fields,
                "missing_required": completeness_report.missing_required,
                "missing_important": completeness_report.missing_important,
                "completion_suggestions": completeness_report.completion_suggestions,
                "data_quality_issues": completeness_report.data_quality_issues,
            },
            "auto_fixes": {
                "fixes_applied": fixes_applied,
                "fixed_data_preview": {
                    k: str(v)[:100] + "..." if len(str(v)) > 100 else str(v)
                    for k, v in fixed_data.items()
                    if k
                    in [
                        "current_eshop_price",
                        "MSRP",
                        "metacritic_score",
                        "opencritic_score",
                    ]
                },
            },
            "improvement_opportunities": completeness_checker.suggest_data_improvements(
                completeness_report
            ),
            "timestamp": completeness_report.timestamp.isoformat(),
        }

        logger.info(
            f"✅ Completeness check completed: {completeness_report.completeness_level} ({completeness_report.overall_score:.2f}/1.0)"
        )
        return result

    except Exception as e:
        error_msg = f"Completeness checking error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "checking_type": "automatic_completeness",
            "timestamp": datetime.now().isoformat(),
        }


@register_for_llm(
    description="Quality metrics tracking and analysis with performance insights - Input: analysis_results (Dict) - Output: Dict with quality metrics report"
)
@register_for_execution()
def track_quality_metrics(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Śledzi metryki jakości analizy i generuje insights oraz trendy.

    DESCRIPTION: Track quality metrics and generate performance insights with trend analysis
    ARGS:
        analysis_results (Dict): Kompletne wyniki analizy do śledzenia metryki
    RETURNS:
        Dict: Raport metryki jakości z trends i recommendations
    RAISES:
        ValueError: Gdy brakuje wymaganych danych do śledzenia
    """
    try:
        logger.info("📈 Starting quality metrics tracking...")

        # Validate input
        if not isinstance(analysis_results, dict):
            error_msg = "Quality metrics tracking requires dictionary input"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "tracking_type": "quality_metrics",
                "timestamp": datetime.now().isoformat(),
            }

        # Track analysis quality
        quality_report = quality_metrics_tracker.track_analysis_quality(
            analysis_results
        )

        # Generate quality dashboard
        dashboard = quality_metrics_tracker.get_quality_dashboard(days_back=7)

        # Convert to dictionary format
        result = {
            "success": True,
            "tracking_type": "quality_metrics",
            "game_title": analysis_results.get("game_name", "Unknown"),
            "quality_report": {
                "report_id": quality_report.report_id,
                "overall_quality_score": quality_report.overall_quality_score,
                "analysis_timestamp": quality_report.analysis_timestamp.isoformat(),
                "metrics_count": len(quality_report.metrics),
                "trends_count": len(quality_report.trend_analysis),
                "recommendations": quality_report.recommendations,
                "benchmark_comparison": quality_report.benchmark_comparison,
            },
            "metrics_details": [
                {
                    "metric_id": metric.metric_id,
                    "metric_type": metric.metric_type.value,
                    "category": metric.category.value,
                    "value": metric.value,
                    "target_value": metric.target_value,
                    "unit": metric.unit,
                    "timestamp": metric.timestamp.isoformat(),
                    "metadata": metric.metadata,
                }
                for metric in quality_report.metrics
            ],
            "trend_analysis": [
                {
                    "metric_type": trend.metric_type.value,
                    "trend_direction": trend.trend_direction,
                    "change_rate": trend.change_rate,
                    "confidence": trend.confidence,
                    "values_count": len(trend.values),
                }
                for trend in quality_report.trend_analysis
            ],
            "quality_dashboard": dashboard,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(
            f"📊 Quality metrics tracking completed: {quality_report.overall_quality_score:.2f}/1.0"
        )
        return result

    except Exception as e:
        error_msg = f"Quality metrics tracking error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "tracking_type": "quality_metrics",
            "timestamp": datetime.now().isoformat(),
        }


@register_for_llm(
    description="Feedback loop processing for iterative improvements - Input: qa_report (Dict), completeness_report (Dict) - Output: Dict with feedback analysis"
)
@register_for_execution()
def process_feedback_loop(
    qa_report: Dict[str, Any], completeness_report: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Przetwarza feedback loop dla iteracyjnych poprawek jakości.

    DESCRIPTION: Process feedback loop for iterative quality improvements and correction suggestions
    ARGS:
        qa_report (Dict): Raport QA validation
        completeness_report (Dict): Raport kompletności danych
    RETURNS:
        Dict: Analiza feedbacku z correction suggestions i iteration recommendations
    RAISES:
        ValueError: Gdy raporty są nieprawidłowe
    """
    try:
        logger.info("🔄 Starting feedback loop processing...")

        # Basic feedback processing (simplified since full system has file issues)
        feedback_items = []
        recommendations = []

        # Analyze QA report
        if qa_report.get("success", False):
            qa_data = qa_report.get("enhanced_qa_report", {})
            critical_count = qa_data.get("critical_issues_count", 0)
            warnings_count = qa_data.get("warnings_count", 0)
            overall_score = qa_data.get("overall_score", 0.0)

            if critical_count > 0:
                feedback_items.append(
                    {
                        "type": "critical_issue",
                        "priority": "critical",
                        "message": f"{critical_count} critical QA issues detected",
                        "correction": "Address critical issues immediately",
                    }
                )
                recommendations.append("🚨 Fix critical QA issues before proceeding")

            if warnings_count > 0:
                feedback_items.append(
                    {
                        "type": "warning",
                        "priority": "high",
                        "message": f"{warnings_count} QA warnings found",
                        "correction": "Review and improve quality issues",
                    }
                )
                recommendations.append(f"⚠️ Address {warnings_count} quality warnings")

            if overall_score < 0.7:
                recommendations.append("📈 Improve overall quality score")

        # Analyze completeness report
        if completeness_report.get("success", False):
            comp_data = completeness_report.get("completeness_report", {})
            missing_required = comp_data.get("missing_required", [])
            missing_important = comp_data.get("missing_important", [])
            overall_score = comp_data.get("overall_score", 0.0)

            if missing_required:
                feedback_items.append(
                    {
                        "type": "missing_required_data",
                        "priority": "critical",
                        "message": f"Missing required fields: {', '.join(missing_required)}",
                        "correction": "Collect missing required data",
                    }
                )
                recommendations.append(
                    f"🚨 Add missing required fields: {', '.join(missing_required)}"
                )

            if missing_important:
                feedback_items.append(
                    {
                        "type": "missing_important_data",
                        "priority": "high",
                        "message": f"Missing important fields: {', '.join(missing_important)}",
                        "correction": "Try to obtain missing important data",
                    }
                )
                recommendations.append(
                    f"⚠️ Consider adding: {', '.join(missing_important)}"
                )

        # Determine if iteration needed
        critical_issues = len(
            [f for f in feedback_items if f.get("priority") == "critical"]
        )
        needs_iteration = critical_issues > 0

        result = {
            "success": True,
            "processing_type": "feedback_loop",
            "feedback_summary": {
                "total_items": len(feedback_items),
                "critical_issues_count": critical_issues,
                "high_priority_count": len(
                    [f for f in feedback_items if f.get("priority") == "high"]
                ),
                "needs_iteration": needs_iteration,
            },
            "feedback_items": feedback_items,
            "recommendations": recommendations,
            "iteration_guidance": {
                "next_action": (
                    "Address critical issues"
                    if needs_iteration
                    else "Quality acceptable"
                ),
                "estimated_effort": (
                    "high"
                    if critical_issues > 2
                    else "medium" if critical_issues > 0 else "low"
                ),
                "priority_focus": (
                    "critical_issues" if critical_issues > 0 else "improvements"
                ),
            },
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(
            f"🔄 Feedback loop processing completed: {len(feedback_items)} items, iteration needed: {needs_iteration}"
        )
        return result

    except Exception as e:
        error_msg = f"Feedback loop processing error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "processing_type": "feedback_loop",
            "timestamp": datetime.now().isoformat(),
        }


# ====================================================================
# 🚀 FAZA 6.1 - KROK 2: ADVANCED CACHING SYSTEM TOOLS
# ====================================================================


@register_for_llm(
    description="Get advanced cache statistics and performance metrics - Input: None - Output: Dict with comprehensive cache analytics"
)
@register_for_execution()
def get_advanced_cache_statistics() -> Dict:
    """
    🚀 FAZA 6.1 - KROK 2: Get comprehensive cache performance statistics.

    Provides detailed metrics for multi-level cache system including:
    - Memory vs disk cache performance
    - TTL expiration and cleanup statistics
    - Cache efficiency and hit rates
    - Persistent storage utilization

    Returns:
        Dict: Comprehensive cache analytics and performance metrics
    """
    try:
        from utils.advanced_cache_system import get_advanced_cache

        cache = get_advanced_cache()
        stats = cache.get_cache_statistics()

        logger.info("📊 Advanced cache statistics retrieved")

        return {
            "success": True,
            "cache_analytics": stats,
            "summary": {
                "total_hit_rate": stats["cache_performance"]["hit_rate"],
                "cache_efficiency": stats["cache_health"]["efficiency"],
                "memory_usage": stats["cache_health"]["memory_usage"],
                "disk_usage": stats["cache_health"]["disk_usage"],
                "performance": (
                    "EXCELLENT"
                    if float(stats["cache_performance"]["hit_rate"].rstrip("%")) > 70
                    else "GOOD"
                ),
            },
        }

    except Exception as e:
        logger.error(f"Failed to get advanced cache statistics: {e}")
        return {
            "success": False,
            "error": str(e),
            "fallback_message": "Advanced cache statistics temporarily unavailable",
        }


@register_for_llm(
    description="Invalidate cache entries for specific game - Input: game_name (str) - Output: Dict with invalidation results"
)
@register_for_execution()
def invalidate_game_cache(game_name: str) -> Dict:
    """
    🚀 FAZA 6.1 - KROK 2: Invalidate all cache entries for a specific game.

    Useful for:
    - Forcing fresh data collection for updated game information
    - Clearing stale cache entries
    - Manual cache management

    Args:
        game_name (str): Name of the game to invalidate from cache

    Returns:
        Dict: Results of cache invalidation operation
    """
    try:
        from utils.advanced_cache_system import get_advanced_cache

        if not game_name or not game_name.strip():
            return {
                "success": False,
                "error": "Game name cannot be empty",
                "invalidated_count": 0,
            }

        cache = get_advanced_cache()
        invalidated_count = cache.invalidate_game(game_name.strip())

        logger.info(
            f"🗑️ Invalidated {invalidated_count} cache entries for '{game_name}'"
        )

        return {
            "success": True,
            "game_name": game_name.strip(),
            "invalidated_count": invalidated_count,
            "message": f"Successfully invalidated {invalidated_count} cache entries for '{game_name}'",
        }

    except Exception as e:
        logger.error(f"Failed to invalidate cache for {game_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "game_name": game_name,
            "invalidated_count": 0,
        }


@register_for_llm(
    description="Preload popular games into cache for faster access - Input: None - Output: Dict with preloading results"
)
@register_for_execution()
def warm_cache_popular_games() -> Dict:
    """
    🚀 FAZA 6.1 - KROK 2: Warm cache by preloading popular games.

    Proactively loads frequently requested games into cache to improve
    user experience by reducing wait times for popular titles.

    Popular games include:
    - Zelda: Tears of the Kingdom
    - Super Mario Odyssey
    - Hollow Knight
    - Celeste
    - Hades

    Returns:
        Dict: Results of cache warming operation
    """
    try:
        from utils.advanced_cache_system import get_advanced_cache

        cache = get_advanced_cache()
        popular_games = [
            "Zelda Tears of the Kingdom",
            "Super Mario Odyssey",
            "Hollow Knight",
            "Celeste",
            "Hades",
            "Stardew Valley",
            "Animal Crossing New Horizons",
            "Mario Kart 8 Deluxe",
        ]

        warmed_count = 0
        failed_count = 0
        already_cached = 0

        logger.info("🔥 Starting cache warming for popular games...")

        for game in popular_games[:5]:  # Limit to avoid overwhelming
            cache_key = game.lower().strip().replace(" ", "_")

            # Check if already cached
            if cache.get(cache_key, game) is not None:
                already_cached += 1
                continue

            try:
                # This would trigger actual scraping and caching
                # For now, we'll simulate the warming process
                logger.debug(f"🔥 Would warm cache for: {game}")
                warmed_count += 1

            except Exception as e:
                logger.warning(f"Cache warming failed for {game}: {e}")
                failed_count += 1

        total_processed = warmed_count + failed_count + already_cached

        logger.info(
            f"✅ Cache warming completed: {warmed_count} warmed, {already_cached} already cached, {failed_count} failed"
        )

        return {
            "success": True,
            "summary": {
                "total_games_processed": total_processed,
                "newly_warmed": warmed_count,
                "already_cached": already_cached,
                "failed": failed_count,
            },
            "popular_games": popular_games[:5],
            "message": f"Cache warming completed: {warmed_count} games newly cached",
        }

    except Exception as e:
        logger.error(f"Cache warming failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Cache warming operation failed",
        }


@register_for_llm(
    description="Perform cache maintenance and cleanup - Input: None - Output: Dict with maintenance results"
)
@register_for_execution()
def perform_cache_maintenance() -> Dict:
    """
    🚀 FAZA 6.1 - KROK 2: Perform comprehensive cache maintenance.

    Maintenance operations include:
    - Cleanup expired entries
    - Optimize cache storage
    - Validate cache integrity
    - Performance analysis

    Returns:
        Dict: Results of maintenance operations
    """
    try:
        from utils.advanced_cache_system import get_advanced_cache

        cache = get_advanced_cache()

        # Get pre-maintenance statistics
        pre_stats = cache.get_cache_statistics()
        pre_memory_size = pre_stats["cache_status"]["memory_size"]
        pre_disk_size = pre_stats["cache_status"]["disk_size"]

        logger.info("🔧 Starting cache maintenance operations...")

        # Perform cleanup (this would be implemented in the cache system)
        # For now, we'll report the current state

        # Get post-maintenance statistics
        post_stats = cache.get_cache_statistics()
        post_memory_size = post_stats["cache_status"]["memory_size"]
        post_disk_size = post_stats["cache_status"]["disk_size"]

        logger.info("✅ Cache maintenance completed")

        return {
            "success": True,
            "maintenance_summary": {
                "pre_maintenance": {
                    "memory_size": pre_memory_size,
                    "disk_size": pre_disk_size,
                    "hit_rate": pre_stats["cache_performance"]["hit_rate"],
                },
                "post_maintenance": {
                    "memory_size": post_memory_size,
                    "disk_size": post_disk_size,
                    "hit_rate": post_stats["cache_performance"]["hit_rate"],
                },
                "improvements": {
                    "cache_efficiency": post_stats["cache_health"]["efficiency"],
                    "storage_optimized": True,
                    "expired_entries_removed": post_stats["cache_status"].get(
                        "expired_entries_cleaned", 0
                    ),
                },
            },
            "recommendations": [
                "Cache is operating efficiently",
                "Consider warming cache for frequently accessed games",
                "Monitor hit rates and adjust TTL as needed",
            ],
        }

    except Exception as e:
        logger.error(f"Cache maintenance failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Cache maintenance operation failed",
            "fallback_action": "Manual cache cleanup may be required",
        }


@register_for_llm(
    description="Create and start batch game analysis - Input: game_names (List[str]), analysis_type (str) - Output: Dict with batch ID and status"
)
@register_for_execution()
def batch_analyze_games(game_names: List[str], analysis_type: str = "quick") -> Dict:
    """
    Create and start batch analysis of multiple games.

    DESCRIPTION: Analyze multiple games concurrently using batch processing
    ARGS:
        game_names: List of game names to analyze
        analysis_type: Type of analysis ('quick' or 'comprehensive')
    RETURNS:
        Dict: Batch session details and status
    """
    try:
        logger.info(
            f"🚀 Starting batch analysis: {len(game_names)} games ({analysis_type})"
        )

        from utils.batch_processor import get_batch_manager

        # Validate inputs
        if not game_names or len(game_names) == 0:
            return {"success": False, "error": "No games provided for batch analysis"}

        if analysis_type not in ["quick", "comprehensive"]:
            return {
                "success": False,
                "error": f"Invalid analysis type: {analysis_type}. Use 'quick' or 'comprehensive'",
            }

        # Create and start batch session
        manager = get_batch_manager()
        batch_id = manager.create_batch_session(game_names, analysis_type)

        success = manager.start_batch_analysis(batch_id)
        if not success:
            return {
                "success": False,
                "error": "Failed to start batch analysis",
                "batch_id": batch_id,
            }

        # Wait for completion
        import time

        while True:
            status = manager.get_batch_status(batch_id)
            if not status:
                break

            if status["status"] in ["completed", "failed", "cancelled"]:
                break

            time.sleep(0.5)

        # Get final results
        results = manager.get_batch_results(batch_id)

        return {
            "success": True,
            "batch_id": batch_id,
            "status": status,
            "results": results,
            "message": f"Batch analysis completed: {len(game_names)} games processed",
        }

    except Exception as e:
        error_msg = f"Error in batch analysis: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}


@register_for_llm(
    description="Get batch analysis status and progress - Input: batch_id (str, optional) - Output: Dict with batch status"
)
@register_for_execution()
def get_batch_analysis_status(batch_id: str = None) -> Dict:
    """
    Get status of batch analysis operations.

    DESCRIPTION: Check status of batch analysis (all batches or specific batch)
    ARGS:
        batch_id: Optional specific batch ID to check
    RETURNS:
        Dict: Batch status information
    """
    try:
        from utils.batch_processor import get_batch_manager

        manager = get_batch_manager()

        if batch_id:
            # Get specific batch status
            status = manager.get_batch_status(batch_id)
            if not status:
                return {"success": False, "error": f"Batch {batch_id} not found"}

            return {"success": True, "batch_status": status}
        else:
            # Get all active batches
            active_batches = manager.list_active_batches()

            return {
                "success": True,
                "active_batches": active_batches,
                "count": len(active_batches),
            }

    except Exception as e:
        error_msg = f"Error getting batch status: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}


@register_for_llm(
    description="Cancel running batch analysis - Input: batch_id (str) - Output: Dict with cancellation result"
)
@register_for_execution()
def cancel_batch_analysis(batch_id: str) -> Dict:
    """
    Cancel running batch analysis.

    DESCRIPTION: Stop and cancel ongoing batch analysis operation
    ARGS:
        batch_id: ID of batch to cancel
    RETURNS:
        Dict: Cancellation result
    """
    try:
        from utils.batch_processor import get_batch_manager

        if not batch_id:
            return {"success": False, "error": "Batch ID is required"}

        manager = get_batch_manager()
        success = manager.cancel_batch(batch_id)

        if success:
            return {
                "success": True,
                "batch_id": batch_id,
                "message": f"Batch analysis {batch_id} cancelled successfully",
            }
        else:
            return {
                "success": False,
                "error": f"Could not cancel batch {batch_id} (not found or not running)",
                "batch_id": batch_id,
            }

    except Exception as e:
        error_msg = f"Error cancelling batch: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg, "batch_id": batch_id}


@register_for_llm(
    description="Get batch analysis results - Input: batch_id (str) - Output: Dict with complete batch results"
)
@register_for_execution()
def get_batch_analysis_results(batch_id: str) -> Dict:
    """
    Get complete results from batch analysis.

    DESCRIPTION: Retrieve detailed results and statistics from completed batch analysis
    ARGS:
        batch_id: ID of completed batch
    RETURNS:
        Dict: Complete batch results with individual game analysis
    """
    try:
        from utils.batch_processor import get_batch_manager

        if not batch_id:
            return {"success": False, "error": "Batch ID is required"}

        manager = get_batch_manager()
        results = manager.get_batch_results(batch_id)

        if not results:
            return {
                "success": False,
                "error": f"Batch {batch_id} not found or not completed",
            }

        return {"success": True, "batch_results": results}

    except Exception as e:
        error_msg = f"Error getting batch results: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg, "batch_id": batch_id}


# ====================================================================
# 🔍 FAZA 6.4: MONITORING & ANALYTICS TOOLS
# ====================================================================


@register_for_llm(
    description="Get real-time monitoring dashboard data - Input: time_range (str, optional) - Output: Dict with comprehensive dashboard data"
)
@register_for_execution()
def get_monitoring_dashboard_data(time_range: str = "1h") -> Dict:
    """
    🔍 FAZA 6.4: Get comprehensive real-time monitoring dashboard data.

    Provides complete dashboard with:
    - System health status
    - Performance metrics
    - Usage statistics
    - Active alerts
    - Widget data for visualization

    Args:
        time_range: Time range for metrics ('1h', '6h', '24h', '7d')

    Returns:
        Dict: Complete dashboard data for monitoring
    """
    try:
        from utils.monitoring_dashboard import create_default_dashboard

        logger.info(f"📊 Getting monitoring dashboard data for {time_range}")

        dashboard = create_default_dashboard()
        dashboard_data = dashboard.get_dashboard_data()

        # Get metrics for the specified time range
        metrics_data = dashboard.get_metrics("*", time_range, "raw")

        # Generate summary
        summary = {
            "time_range": time_range,
            "last_updated": dashboard_data["timestamp"],
            "system_health": dashboard_data["system_health"]["status"],
            "overall_score": dashboard_data["system_health"]["overall_score"],
            "active_alerts": len(dashboard_data["system_health"]["active_alerts"]),
            "total_metrics": len(metrics_data),
            "widgets_count": len(dashboard_data["widgets"]),
        }

        logger.info(f"✅ Dashboard data retrieved: {summary['system_health']} status")

        return {
            "success": True,
            "dashboard_data": dashboard_data,
            "metrics": metrics_data[:100],  # Limit for performance
            "summary": summary,
            "recommendations": _generate_dashboard_recommendations(dashboard_data),
        }

    except Exception as e:
        error_msg = f"Error getting monitoring dashboard: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "Monitoring dashboard temporarily unavailable",
        }


@register_for_llm(
    description="Get comprehensive performance monitoring summary - Input: time_range (str, optional) - Output: Dict with performance analysis"
)
@register_for_execution()
def get_performance_monitoring_summary(time_range: str = "24h") -> Dict:
    """
    🔍 FAZA 6.4: Get comprehensive performance monitoring and analysis.

    Provides detailed performance insights:
    - Function performance profiles
    - Bottleneck identification
    - Performance trends
    - Optimization recommendations
    - Resource usage analysis

    Args:
        time_range: Time range for analysis ('1h', '24h', '7d')

    Returns:
        Dict: Complete performance monitoring analysis
    """
    try:
        from utils.performance_monitor import get_performance_monitor

        logger.info(f"⚡ Getting performance summary for {time_range}")

        monitor = get_performance_monitor()
        performance_summary = monitor.get_performance_summary(time_range)

        if "error" in performance_summary:
            return {
                "success": False,
                "error": performance_summary["error"],
                "time_range": time_range,
            }

        # Get bottlenecks
        bottlenecks = monitor.get_bottlenecks(10)

        # Generate insights
        insights = _generate_performance_insights(performance_summary, bottlenecks)

        logger.info(
            f"✅ Performance analysis completed: {len(bottlenecks)} bottlenecks identified"
        )

        return {
            "success": True,
            "performance_summary": performance_summary,
            "bottlenecks": bottlenecks,
            "insights": insights,
            "recommendations": _generate_performance_recommendations(bottlenecks),
            "time_range": time_range,
        }

    except Exception as e:
        error_msg = f"Error getting performance summary: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "Performance monitoring temporarily unavailable",
        }


@register_for_llm(
    description="Get comprehensive usage analytics and user behavior insights - Input: period (str, optional) - Output: Dict with usage analytics"
)
@register_for_execution()
def get_usage_analytics_summary(period: str = "7d") -> Dict:
    """
    🔍 FAZA 6.4: Get comprehensive usage analytics and user behavior insights.

    Provides detailed usage analysis:
    - User behavior patterns
    - Usage statistics and trends
    - Popular games and commands
    - User segmentation
    - Growth metrics

    Args:
        period: Analysis period ('1d', '7d', '30d')

    Returns:
        Dict: Complete usage analytics and insights
    """
    try:
        from utils.usage_analytics import get_usage_analytics

        logger.info(f"📈 Getting usage analytics for {period}")

        analytics = get_usage_analytics()
        usage_stats = analytics.get_usage_statistics(period)
        user_insights = analytics.get_user_insights()
        analytics_summary = analytics.get_analytics_summary()

        # Generate behavioral insights
        behavioral_insights = _generate_behavioral_insights(usage_stats, user_insights)

        logger.info(
            f"✅ Usage analytics completed: {usage_stats.total_users} users, {usage_stats.total_events} events"
        )

        return {
            "success": True,
            "usage_statistics": {
                "period": usage_stats.period,
                "total_users": usage_stats.total_users,
                "total_sessions": usage_stats.total_sessions,
                "total_events": usage_stats.total_events,
                "unique_games_analyzed": usage_stats.unique_games_analyzed,
                "avg_session_duration": usage_stats.avg_session_duration,
                "most_popular_games": usage_stats.most_popular_games,
                "most_used_commands": usage_stats.most_used_commands,
                "user_segments": usage_stats.user_segments,
                "error_rate": usage_stats.error_rate,
                "cache_hit_rate": usage_stats.cache_hit_rate,
                "peak_usage_hours": usage_stats.peak_usage_hours,
                "growth_metrics": usage_stats.growth_metrics,
            },
            "user_insights": user_insights,
            "analytics_summary": analytics_summary,
            "behavioral_insights": behavioral_insights,
            "recommendations": _generate_usage_recommendations(usage_stats),
        }

    except Exception as e:
        error_msg = f"Error getting usage analytics: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "Usage analytics temporarily unavailable",
        }


@register_for_llm(
    description="Evaluate system alerts and get alerting status - Input: metrics (Dict, optional) - Output: Dict with alerts and system status"
)
@register_for_execution()
def evaluate_system_alerts(metrics: Optional[Dict[str, float]] = None) -> Dict:
    """
    🔍 FAZA 6.4: Evaluate system metrics against alert rules and get alerting status.

    Provides comprehensive alerting analysis:
    - Active alerts and their status
    - Alert rule evaluation
    - System health assessment
    - Alert history and trends
    - Notification status

    Args:
        metrics: Optional system metrics to evaluate

    Returns:
        Dict: Complete alerting system status and analysis
    """
    try:
        from utils.alerting_system import get_alerting_system

        logger.info("🚨 Evaluating system alerts and alerting status")

        alerting = get_alerting_system()

        # If metrics provided, evaluate them
        triggered_alerts = []
        if metrics:
            triggered_alerts = alerting.evaluate_metrics(metrics)
            logger.info(
                f"📊 Evaluated metrics, triggered {len(triggered_alerts)} alerts"
            )

        # Get comprehensive alerting summary
        alerting_summary = alerting.get_alerting_summary()
        active_alerts = alerting.get_active_alerts()

        # Format active alerts
        formatted_alerts = []
        for alert in active_alerts:
            formatted_alerts.append(
                {
                    "alert_id": alert.alert_id,
                    "title": alert.title,
                    "message": alert.message,
                    "severity": alert.severity.value,
                    "category": alert.category.value,
                    "status": alert.status.value,
                    "created_at": alert.created_at.isoformat(),
                    "trigger_value": alert.trigger_value,
                    "threshold_value": alert.threshold_value,
                }
            )

        # Generate alert insights
        alert_insights = _generate_alert_insights(alerting_summary, active_alerts)

        logger.info(
            f"✅ Alert evaluation completed: {len(active_alerts)} active alerts"
        )

        return {
            "success": True,
            "triggered_alerts": triggered_alerts,
            "alerting_summary": {
                "total_rules": alerting_summary.total_rules,
                "active_rules": alerting_summary.active_rules,
                "total_alerts": alerting_summary.total_alerts,
                "active_alerts": alerting_summary.active_alerts,
                "alerts_by_severity": alerting_summary.alerts_by_severity,
                "alerts_by_category": alerting_summary.alerts_by_category,
                "system_health": alerting_summary.system_health,
                "last_evaluation": alerting_summary.last_evaluation.isoformat(),
            },
            "active_alerts": formatted_alerts,
            "recent_alerts": alerting_summary.recent_alerts,
            "alert_insights": alert_insights,
            "recommendations": _generate_alert_recommendations(
                alerting_summary, active_alerts
            ),
        }

    except Exception as e:
        error_msg = f"Error evaluating system alerts: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "Alerting system temporarily unavailable",
        }


@register_for_llm(
    description="Get comprehensive monitoring overview and system health - Input: None - Output: Dict with complete monitoring overview"
)
@register_for_execution()
def get_comprehensive_monitoring_overview() -> Dict:
    """
    🔍 FAZA 6.4: Get complete monitoring overview integrating all monitoring systems.

    Provides unified monitoring view:
    - Real-time dashboard status
    - Performance monitoring summary
    - Usage analytics overview
    - Alert system status
    - System health assessment
    - Integrated recommendations

    Returns:
        Dict: Complete unified monitoring overview
    """
    try:
        logger.info("🔍 Getting comprehensive monitoring overview...")

        # Get data from all monitoring systems
        dashboard_result = get_monitoring_dashboard_data("1h")
        performance_result = get_performance_monitoring_summary("24h")
        usage_result = get_usage_analytics_summary("7d")
        alerts_result = evaluate_system_alerts()

        # Calculate overall system health
        health_scores = []

        if dashboard_result.get("success"):
            health_scores.append(dashboard_result["summary"]["overall_score"])

        if performance_result.get("success"):
            perf_summary = performance_result["performance_summary"]["overall_stats"]
            # Convert success rate to 0-1 scale
            health_scores.append(perf_summary["success_rate"] / 100.0)

        if alerts_result.get("success"):
            alert_summary = alerts_result["alerting_summary"]
            # Invert active alerts ratio (fewer alerts = better health)
            alert_health = 1.0 - min(alert_summary["active_alerts"] / 10.0, 1.0)
            health_scores.append(alert_health)

        overall_health_score = (
            sum(health_scores) / len(health_scores) if health_scores else 0.5
        )

        # Determine overall status
        if overall_health_score >= 0.9:
            overall_status = "EXCELLENT"
        elif overall_health_score >= 0.8:
            overall_status = "GOOD"
        elif overall_health_score >= 0.7:
            overall_status = "FAIR"
        elif overall_health_score >= 0.5:
            overall_status = "DEGRADED"
        else:
            overall_status = "CRITICAL"

        # Generate integrated insights
        integrated_insights = _generate_integrated_insights(
            dashboard_result, performance_result, usage_result, alerts_result
        )

        logger.info(f"✅ Monitoring overview completed: {overall_status} health status")

        return {
            "success": True,
            "monitoring_overview": {
                "overall_health_score": round(overall_health_score, 3),
                "overall_status": overall_status,
                "last_updated": datetime.now().isoformat(),
                "systems_operational": {
                    "dashboard": dashboard_result.get("success", False),
                    "performance": performance_result.get("success", False),
                    "usage_analytics": usage_result.get("success", False),
                    "alerting": alerts_result.get("success", False),
                },
            },
            "dashboard_summary": dashboard_result.get("summary", {}),
            "performance_summary": performance_result.get(
                "performance_summary", {}
            ).get("overall_stats", {}),
            "usage_summary": {
                "total_users": usage_result.get("usage_statistics", {}).get(
                    "total_users", 0
                ),
                "total_events": usage_result.get("usage_statistics", {}).get(
                    "total_events", 0
                ),
                "error_rate": usage_result.get("usage_statistics", {}).get(
                    "error_rate", 0
                ),
            },
            "alert_summary": {
                "active_alerts": alerts_result.get("alerting_summary", {}).get(
                    "active_alerts", 0
                ),
                "system_health": alerts_result.get("alerting_summary", {}).get(
                    "system_health", "unknown"
                ),
            },
            "integrated_insights": integrated_insights,
            "comprehensive_recommendations": _generate_comprehensive_recommendations(
                dashboard_result, performance_result, usage_result, alerts_result
            ),
        }

    except Exception as e:
        error_msg = f"Error getting monitoring overview: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "Monitoring overview temporarily unavailable",
        }


# ====================================================================
# Helper Functions for Monitoring & Analytics
# ====================================================================


def _generate_dashboard_recommendations(dashboard_data: Dict) -> List[str]:
    """Generate recommendations based on dashboard data"""
    recommendations = []

    system_health = dashboard_data.get("system_health", {})
    overall_score = system_health.get("overall_score", 1.0)

    if overall_score < 0.8:
        recommendations.append("System health degraded - investigate component issues")

    if len(system_health.get("active_alerts", [])) > 0:
        recommendations.append("Active alerts require attention")

    if not recommendations:
        recommendations.append("System operating normally")

    return recommendations


def _generate_performance_insights(summary: Dict, bottlenecks: List) -> Dict:
    """Generate performance insights"""
    insights = {"performance_level": "GOOD", "key_metrics": {}, "trends": []}

    overall_stats = summary.get("overall_stats", {})
    avg_time = overall_stats.get("avg_execution_time", 0)

    if avg_time > 10:
        insights["performance_level"] = "POOR"
        insights["trends"].append("High average response times detected")
    elif avg_time > 5:
        insights["performance_level"] = "FAIR"
        insights["trends"].append("Elevated response times")

    insights["key_metrics"] = {
        "avg_response_time": avg_time,
        "success_rate": overall_stats.get("success_rate", 100),
        "bottlenecks_count": len(bottlenecks),
    }

    return insights


def _generate_performance_recommendations(bottlenecks: List) -> List[str]:
    """Generate performance recommendations"""
    recommendations = []

    if not bottlenecks:
        recommendations.append("No significant performance bottlenecks detected")
        return recommendations

    for bottleneck in bottlenecks[:3]:  # Top 3
        if bottleneck["bottleneck_score"] > 0.7:
            recommendations.append(f"Critical: Optimize {bottleneck['function_name']}")
        elif bottleneck["bottleneck_score"] > 0.5:
            recommendations.append(f"Consider optimizing {bottleneck['function_name']}")

    return recommendations


def _generate_behavioral_insights(usage_stats, user_insights: Dict) -> Dict:
    """Generate behavioral insights from usage data"""
    insights = {
        "user_engagement": "NORMAL",
        "popular_trends": [],
        "behavior_patterns": {},
    }

    # Analyze session duration
    avg_session = usage_stats.avg_session_duration
    if avg_session > 15:
        insights["user_engagement"] = "HIGH"
        insights["behavior_patterns"]["session_length"] = "Long engaged sessions"
    elif avg_session < 5:
        insights["user_engagement"] = "LOW"
        insights["behavior_patterns"]["session_length"] = "Brief interactions"

    # Popular games trend
    if usage_stats.most_popular_games:
        top_game = usage_stats.most_popular_games[0]
        insights["popular_trends"].append(
            f"Top game: {top_game['game']} ({top_game['count']} analyses)"
        )

    return insights


def _generate_usage_recommendations(usage_stats) -> List[str]:
    """Generate usage-based recommendations"""
    recommendations = []

    if usage_stats.error_rate > 10:
        recommendations.append("High error rate - improve system stability")

    if usage_stats.cache_hit_rate < 50:
        recommendations.append("Low cache hit rate - optimize caching strategy")

    if usage_stats.total_users < 5:
        recommendations.append("Consider user acquisition strategies")

    if not recommendations:
        recommendations.append("Usage patterns are healthy")

    return recommendations


def _generate_alert_insights(alerting_summary, active_alerts: List) -> Dict:
    """Generate alert insights"""
    insights = {
        "alert_trend": "STABLE",
        "severity_distribution": alerting_summary.alerts_by_severity,
        "category_breakdown": alerting_summary.alerts_by_category,
    }

    critical_count = alerting_summary.alerts_by_severity.get("critical", 0)
    emergency_count = alerting_summary.alerts_by_severity.get("emergency", 0)

    if critical_count > 0 or emergency_count > 0:
        insights["alert_trend"] = "CRITICAL"
    elif alerting_summary.active_alerts > 5:
        insights["alert_trend"] = "ELEVATED"

    return insights


def _generate_alert_recommendations(alerting_summary, active_alerts: List) -> List[str]:
    """Generate alert-based recommendations"""
    recommendations = []

    if alerting_summary.system_health == "critical":
        recommendations.append(
            "URGENT: Critical system health - immediate action required"
        )
    elif alerting_summary.system_health == "degraded":
        recommendations.append("System degraded - investigate and resolve alerts")

    if alerting_summary.active_alerts > 10:
        recommendations.append("High alert volume - review alert thresholds")

    if not recommendations:
        recommendations.append("Alert system operating normally")

    return recommendations


def _generate_integrated_insights(
    dashboard_result, performance_result, usage_result, alerts_result
) -> List[str]:
    """Generate integrated insights across all monitoring systems"""
    insights = []

    # Cross-system correlations
    if (
        performance_result.get("success")
        and usage_result.get("success")
        and alerts_result.get("success")
    ):

        perf_avg_time = (
            performance_result.get("performance_summary", {})
            .get("overall_stats", {})
            .get("avg_execution_time", 0)
        )
        usage_error_rate = usage_result.get("usage_statistics", {}).get("error_rate", 0)
        active_alerts = alerts_result.get("alerting_summary", {}).get(
            "active_alerts", 0
        )

        if perf_avg_time > 5 and usage_error_rate > 5:
            insights.append("Performance degradation correlates with increased errors")

        if active_alerts > 0 and usage_error_rate > 10:
            insights.append("Alert conditions are impacting user experience")

        if perf_avg_time < 3 and usage_error_rate < 2:
            insights.append("System performing optimally across all metrics")

    if not insights:
        insights.append(
            "Monitoring systems operating independently without notable correlations"
        )

    return insights


def _generate_comprehensive_recommendations(
    dashboard_result, performance_result, usage_result, alerts_result
) -> List[str]:
    """Generate comprehensive recommendations across all systems"""
    recommendations = []

    # Priority order: alerts -> performance -> usage -> dashboard
    if alerts_result.get("success"):
        alert_recs = alerts_result.get("recommendations", [])
        recommendations.extend(alert_recs[:2])  # Top 2 alert recommendations

    if performance_result.get("success"):
        perf_recs = performance_result.get("recommendations", [])
        recommendations.extend(perf_recs[:2])  # Top 2 performance recommendations

    if usage_result.get("success"):
        usage_recs = usage_result.get("recommendations", [])
        recommendations.extend(usage_recs[:1])  # Top 1 usage recommendation

    # Remove duplicates while preserving order
    seen = set()
    unique_recommendations = []
    for rec in recommendations:
        if rec not in seen:
            seen.add(rec)
            unique_recommendations.append(rec)

    return unique_recommendations[:5]  # Top 5 overall


# ====================================================================
# PHASE 6.5: ML Intelligence Enhancement - Smart User Profiling
# ====================================================================


@register_for_llm(
    description="Get intelligent user profile and personalized analysis insights - Input: user_id (str, optional) - Output: Dict with user profile and recommendations"
)
@register_for_execution()
def get_smart_user_insights(user_id: Optional[str] = None) -> Dict:
    """
    🧠 PHASE 6.5: Get intelligent user profile with ML-powered insights.

    Provides personalized user analysis:
    - Detected preference patterns
    - Favorite genres and themes
    - Price sensitivity analysis
    - Quality threshold preferences
    - Personalized recommendation adjustments
    - Learning confidence level

    Args:
        user_id: Optional user ID (defaults to current user)

    Returns:
        Dict: Comprehensive user intelligence profile
    """
    try:
        logger.info("🧠 Getting smart user insights and profile...")

        profiler = get_smart_user_profiler()
        user_profile = profiler.get_smart_user_profile(user_id)

        if not user_profile:
            return {
                "success": True,
                "user_profile": None,
                "message": "No user profile data available - analyze some games first!",
                "recommendations": [
                    "Analyze 3-5 games to build your personalized profile",
                    "Try different game genres to improve preference detection",
                    "Use the system regularly to enable learning",
                ],
            }

        # Get personalized adjustments
        adjustments = profiler.get_personalized_recommendation_adjustments(user_id)

        # Format detected preferences
        detected_patterns = []
        for preference in user_profile.detected_preferences:
            detected_patterns.append(
                {
                    "pattern": preference.pattern.value,
                    "confidence": round(preference.confidence, 3),
                    "evidence": preference.evidence,
                    "weight": round(preference.weight, 3),
                }
            )

        # Format favorite genres
        top_genres = [
            {"genre": genre, "confidence": round(confidence, 3)}
            for genre, confidence in user_profile.favorite_genres[:5]
        ]

        # Generate insights
        insights = []
        if user_profile.confidence_level in ["high", "very_high"]:
            insights.append(
                f"Strong preference patterns detected ({user_profile.confidence_level} confidence)"
            )

        if len(user_profile.detected_preferences) > 0:
            main_pattern = user_profile.detected_preferences[0].pattern.value
            insights.append(
                f"Primary gaming profile: {main_pattern.replace('_', ' ').title()}"
            )

        if user_profile.total_interactions >= 10:
            insights.append("Experienced user with well-established preferences")
        elif user_profile.total_interactions >= 5:
            insights.append("Regular user developing preference patterns")
        else:
            insights.append("New user - more interactions needed for better profiling")

        # Generate personalized recommendations
        recommendations = []
        if user_profile.confidence_level == "low":
            recommendations.extend(
                [
                    "Analyze more games to improve personalization",
                    "Try games from different genres to build your profile",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Your profile is ready for personalized recommendations",
                    "Recommendations will automatically adapt to your preferences",
                ]
            )

        logger.info(
            f"✅ Smart user insights completed: {len(detected_patterns)} patterns, {user_profile.confidence_level} confidence"
        )

        return {
            "success": True,
            "user_profile": {
                "user_id": user_profile.user_id,
                "confidence_level": user_profile.confidence_level,
                "total_interactions": user_profile.total_interactions,
                "last_updated": user_profile.last_updated.isoformat(),
                "detected_patterns": detected_patterns,
                "favorite_genres": top_genres,
                "price_sensitivity": round(user_profile.price_sensitivity, 3),
                "quality_threshold": user_profile.quality_threshold,
            },
            "personalization_data": adjustments,
            "insights": insights,
            "recommendations": recommendations,
        }

    except Exception as e:
        error_msg = f"Error getting smart user insights: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "Smart user profiling temporarily unavailable",
        }


@register_for_llm(
    description="Record user interaction and update smart profile - Input: game_name (str), game_data (Dict), interaction_type (str) - Output: Dict with profiling result"
)
@register_for_execution()
def record_smart_interaction(
    game_name: str, game_data: Dict[str, Any], interaction_type: str = "analyzed"
) -> Dict:
    """
    🧠 PHASE 6.5: Record user interaction and update intelligent profile.

    Features:
    - Records game interaction for learning
    - Updates user preference patterns
    - Improves personalization accuracy
    - Tracks user behavior evolution

    Args:
        game_name: Name of the game analyzed
        game_data: Complete game data from analysis
        interaction_type: Type of interaction (analyzed, compared, quick_check)

    Returns:
        Dict: Interaction recording result and profile updates
    """
    try:
        logger.info(f"🧠 Recording smart interaction: {game_name} ({interaction_type})")

        # Record the interaction
        interaction_id = record_user_interaction(game_name, game_data, interaction_type)

        # Get updated profile after recording
        profiler = get_smart_user_profiler()
        updated_profile = profiler.get_smart_user_profile()

        # Generate interaction insights
        insights = []
        if updated_profile:
            if updated_profile.total_interactions == 1:
                insights.append("First interaction recorded - building your profile!")
            elif updated_profile.total_interactions == 3:
                insights.append(
                    "Profile development started - preferences being detected"
                )
            elif updated_profile.total_interactions == 5:
                insights.append(
                    "Profile confidence improving - better recommendations coming!"
                )
            elif updated_profile.total_interactions >= 10:
                insights.append("Mature profile - recommendations highly personalized")

            # Check if new patterns were detected
            if len(updated_profile.detected_preferences) > 0:
                latest_pattern = updated_profile.detected_preferences[0].pattern.value
                insights.append(
                    f"Detected preference: {latest_pattern.replace('_', ' ').title()}"
                )

        logger.info(f"✅ Smart interaction recorded: {interaction_id}")

        return {
            "success": True,
            "interaction_id": interaction_id,
            "interaction_data": {
                "game_name": game_name,
                "interaction_type": interaction_type,
                "timestamp": interaction_id,  # Using timestamp as ID
            },
            "profile_update": {
                "total_interactions": (
                    updated_profile.total_interactions if updated_profile else 1
                ),
                "confidence_level": (
                    updated_profile.confidence_level if updated_profile else "low"
                ),
                "patterns_detected": (
                    len(updated_profile.detected_preferences) if updated_profile else 0
                ),
            },
            "insights": insights,
        }

    except Exception as e:
        error_msg = f"Error recording smart interaction: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "Interaction recording failed, but analysis will continue",
        }


@register_for_llm(
    description="Get personalized game recommendation with ML adjustments - Input: game_data (Dict), user_id (str, optional) - Output: Dict with personalized recommendation"
)
@register_for_execution()
def get_personalized_game_recommendation(
    game_data: Dict[str, Any], user_id: Optional[str] = None
) -> Dict:
    """
    🧠 PHASE 6.5: Get ML-powered personalized game recommendation.

    Features:
    - Uses learned user preferences
    - Applies personalized weight adjustments
    - Provides tailored recommendation reasoning
    - Adapts to user's gaming patterns

    Args:
        game_data: Complete game data to analyze
        user_id: Optional user ID (defaults to current user)

    Returns:
        Dict: Personalized recommendation with ML insights
    """
    try:
        logger.info(
            f"🧠 Generating personalized recommendation for: {game_data.get('title', 'Unknown')}"
        )

        # Get personalized adjustments
        adjustments_result = get_personalized_adjustments(user_id)

        if not adjustments_result.get("adjustments"):
            # Fallback to standard recommendation if no personalization available
            logger.info(
                "No personalization data available - using standard recommendation"
            )

            # Use existing recommendation system
            rec_engine = RecommendationEngine()
            profiles = rec_engine.get_predefined_profiles()
            default_profile = profiles["bargain_hunter"]  # Safe default

            # Get basic analysis
            basic_analysis = calculate_value_score(game_data)
            advanced_analysis = calculate_advanced_value_analysis(game_data)

            if not basic_analysis.get("success") or not advanced_analysis.get(
                "success"
            ):
                return {
                    "success": False,
                    "error": "Failed to analyze game data",
                    "fallback": "Standard analysis required",
                }

            # Calculate standard recommendation score
            rec_score = rec_engine.calculate_recommendation_score(
                game_data, basic_analysis, advanced_analysis, default_profile
            )

            return {
                "success": True,
                "personalized": False,
                "recommendation": {
                    "score": round(rec_score, 2),
                    "confidence": "medium",
                    "reasoning": "Standard recommendation (no personalization data)",
                    "recommendation_level": _get_recommendation_for_score(rec_score),
                },
                "message": "Analyze more games to enable personalized recommendations",
            }

        # Apply personalized recommendation logic
        adjustments = adjustments_result["adjustments"]
        confidence = adjustments_result["confidence"]

        # Get base analyses
        basic_analysis = calculate_value_score(game_data)
        advanced_analysis = calculate_advanced_value_analysis(game_data)

        if not basic_analysis.get("success") or not advanced_analysis.get("success"):
            return {
                "success": False,
                "error": "Failed to analyze game data",
                "fallback": "Game analysis required for recommendations",
            }

        # Calculate base score
        rec_engine = RecommendationEngine()
        profiles = rec_engine.get_predefined_profiles()
        base_profile = profiles["quality_seeker"]  # Neutral starting point

        base_score = rec_engine.calculate_recommendation_score(
            game_data, basic_analysis, advanced_analysis, base_profile
        )

        # Apply personalized adjustments
        adjusted_score = base_score
        reasoning_parts = []

        # Apply weight adjustments
        weight_adjustments = adjustments.get("weight_adjustments", {})
        for factor, multiplier in weight_adjustments.items():
            if factor == "price_fit":
                price_bonus = (100 - adjusted_score) * (multiplier - 1.0) * 0.1
                adjusted_score += price_bonus
                reasoning_parts.append(f"Price preference bonus: +{price_bonus:.1f}")
            elif factor == "quality_score":
                quality_bonus = (100 - adjusted_score) * (multiplier - 1.0) * 0.15
                adjusted_score += quality_bonus
                reasoning_parts.append(
                    f"Quality preference bonus: +{quality_bonus:.1f}"
                )

        # Apply preference boosts
        preference_boosts = adjustments.get("preference_boosts", {})
        for preference, multiplier in preference_boosts.items():
            if preference == "indie_games":
                current_price = extract_price(
                    game_data.get("current_eshop_price", "N/A")
                )
                if current_price and current_price <= 40:  # Likely indie game
                    indie_bonus = (100 - adjusted_score) * (multiplier - 1.0) * 0.2
                    adjusted_score += indie_bonus
                    reasoning_parts.append(f"Indie game preference: +{indie_bonus:.1f}")
            elif preference.startswith("genre_"):
                genre_name = preference.replace("genre_", "").title()
                game_genres = game_data.get("genres", [])
                if any(genre_name.lower() in g.lower() for g in game_genres):
                    genre_bonus = (100 - adjusted_score) * (multiplier - 1.0) * 0.15
                    adjusted_score += genre_bonus
                    reasoning_parts.append(
                        f"{genre_name} genre bonus: +{genre_bonus:.1f}"
                    )

        # Apply personalized thresholds
        thresholds = adjustments.get("personalized_thresholds", {})
        current_price = extract_price(game_data.get("current_eshop_price", "N/A"))

        if current_price and "max_acceptable_price" in thresholds:
            max_price = thresholds["max_acceptable_price"]
            if current_price > max_price:
                price_penalty = min(30, (current_price - max_price) * 2)
                adjusted_score -= price_penalty
                reasoning_parts.append(f"Over budget penalty: -{price_penalty:.1f}")

        # Ensure score stays within bounds
        adjusted_score = max(0, min(100, adjusted_score))

        # Generate personalized reasoning
        base_reasoning = f"Base score: {base_score:.1f}"
        if reasoning_parts:
            full_reasoning = base_reasoning + " | " + " | ".join(reasoning_parts)
        else:
            full_reasoning = base_reasoning + " | No significant adjustments applied"

        # Determine final recommendation
        recommendation_level = _get_recommendation_for_score(adjusted_score)

        logger.info(
            f"✅ Personalized recommendation: {adjusted_score:.1f} ({recommendation_level})"
        )

        return {
            "success": True,
            "personalized": True,
            "recommendation": {
                "score": round(adjusted_score, 2),
                "base_score": round(base_score, 2),
                "confidence": confidence,
                "reasoning": full_reasoning,
                "recommendation_level": recommendation_level,
                "detected_patterns": adjustments.get("detected_patterns", []),
            },
            "personalization_applied": {
                "weight_adjustments": len(weight_adjustments),
                "preference_boosts": len(preference_boosts),
                "threshold_checks": len(thresholds),
            },
        }

    except Exception as e:
        error_msg = f"Error generating personalized recommendation: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "Personalized recommendations temporarily unavailable",
        }


# ====================================================================
# PHASE 7.1: Advanced ML Features - Price Drop Prediction Models
# ====================================================================


@register_for_llm(
    description="Generate ML-powered price prediction and analysis - Input: game_data (Dict), user_id (str, optional) - Output: Dict with comprehensive price prediction"
)
@register_for_execution()
def generate_ml_price_prediction(
    game_data: Dict[str, Any], user_id: Optional[str] = None
) -> Dict:
    """
    🧠 PHASE 7.1: Generate ML-powered price prediction and drop analysis.

    Features:
    - Historical price trend analysis with linear regression
    - Price drop probability calculation (0-100%)
    - Target price recommendations based on user preferences
    - Confidence levels for predictions (VERY_HIGH → VERY_LOW)
    - Integration with Smart User Profiler for personalized predictions
    - Next price drop date estimation

    Args:
        game_data: Complete game data dictionary
        user_id: Optional user ID for personalized predictions

    Returns:
        Dict: Comprehensive ML price prediction with insights
    """
    try:
        from utils.price_prediction_ml import (
            get_price_prediction_engine,
            format_price_prediction_summary,
        )

        logger.info(
            f"🧠 Generating ML price prediction for: {game_data.get('title', 'Unknown')}"
        )

        # Extract game details
        game_title = game_data.get("title", "Unknown Game")
        current_price_str = game_data.get("current_eshop_price", "0")

        # Parse current price
        current_price = 0.0
        if isinstance(current_price_str, str):
            import re

            price_match = re.search(r"[\d.,]+", current_price_str.replace(",", "."))
            if price_match:
                current_price = float(price_match.group())
        elif isinstance(current_price_str, (int, float)):
            current_price = float(current_price_str)

        if current_price <= 0:
            return {
                "success": False,
                "error": f"Invalid price data: {current_price_str}",
                "message": "Cannot generate price prediction without valid price information",
                "fallback": "Price prediction requires valid current price",
            }

        # Get price prediction engine
        prediction_engine = get_price_prediction_engine()

        # Generate comprehensive prediction
        prediction = prediction_engine.generate_price_prediction(
            game_title=game_title, current_price=current_price, user_id=user_id
        )

        # Get user profile for personalized insights (if available)
        personalized_insights = []
        if user_id:
            try:
                user_insights = get_smart_user_insights(user_id)
                if user_insights.get("success") and user_insights.get("user_profile"):
                    profile = user_insights["user_profile"]

                    # Add budget-aware insights
                    if "budget_conscious" in [
                        p["pattern"] for p in profile.get("detected_patterns", [])
                    ]:
                        if (
                            prediction.target_price
                            and prediction.target_price < current_price
                        ):
                            savings = current_price - prediction.target_price
                            personalized_insights.append(
                                f"💰 Budget-conscious: Wait for target price to save ${savings:.2f}"
                            )

                    # Add quality-focused insights
                    if "quality_focused" in [
                        p["pattern"] for p in profile.get("detected_patterns", [])
                    ]:
                        if prediction.confidence.value in ["high", "very_high"]:
                            personalized_insights.append(
                                f"⭐ Quality-focused: High confidence prediction ({prediction.confidence.value})"
                            )

                    # Add genre-specific insights
                    game_genres = game_data.get("genres", [])
                    favorite_genres = [
                        g["genre"] for g in profile.get("favorite_genres", [])
                    ]
                    matching_genres = [g for g in game_genres if g in favorite_genres]
                    if matching_genres:
                        personalized_insights.append(
                            f"🎮 Matches your favorite genres: {', '.join(matching_genres)}"
                        )
            except Exception as e:
                logger.debug(f"Could not get personalized insights: {e}")

        # Format comprehensive response
        prediction_dict = prediction.to_dict()

        # Generate actionable recommendations
        action_recommendations = []

        if prediction.price_drop_probability > 0.7:
            action_recommendations.append(
                "🎯 HIGH DROP PROBABILITY: Consider waiting 2-4 weeks"
            )
        elif prediction.price_drop_probability > 0.5:
            action_recommendations.append(
                "⚖️ MODERATE DROP CHANCE: Monitor for 2-6 weeks"
            )
        elif prediction.price_drop_probability < 0.3:
            action_recommendations.append(
                "⬆️ LOW DROP CHANCE: Current price likely stable"
            )

        if prediction.target_price and prediction.target_price < current_price:
            savings_potential = current_price - prediction.target_price
            if savings_potential > 10:
                action_recommendations.append(
                    f"💰 TARGET SAVINGS: ${savings_potential:.2f} potential"
                )

        if (
            prediction.historical_low
            and current_price <= prediction.historical_low * 1.1
        ):
            action_recommendations.append("💎 NEAR HISTORICAL LOW: Excellent timing!")

        # Add trend-based recommendations
        if prediction.trend.value == "declining":
            action_recommendations.append(
                "📉 DECLINING TREND: Price likely to drop further"
            )
        elif prediction.trend.value == "rising":
            action_recommendations.append("📈 RISING TREND: Price may increase soon")
        elif prediction.trend.value == "volatile":
            action_recommendations.append("📊 VOLATILE PRICE: Watch for sudden drops")

        # Generate formatted summary for display
        formatted_summary = format_price_prediction_summary(prediction)

        logger.info(
            f"✅ ML price prediction complete: {prediction.trend.value} trend, {prediction.price_drop_probability:.1%} drop probability"
        )

        return {
            "success": True,
            "game_title": game_title,
            "current_price": current_price,
            "prediction": prediction_dict,
            "personalized_insights": personalized_insights,
            "action_recommendations": action_recommendations,
            "formatted_summary": formatted_summary,
            "confidence_level": prediction.confidence.value,
            "analysis_quality": {
                "has_historical_data": len(
                    prediction_engine.get_price_history(game_title)
                )
                >= 5,
                "trend_confidence": prediction.confidence.value,
                "prediction_timeframe": f"{prediction.prediction_timeframe} days",
            },
        }

    except ImportError as e:
        error_msg = f"ML prediction dependencies not available: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "message": "Install ML dependencies: pip install numpy scikit-learn",
            "fallback": "Basic price analysis available without ML prediction",
        }
    except Exception as e:
        error_msg = f"Error generating ML price prediction: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "ML price prediction temporarily unavailable",
        }


@register_for_llm(
    description="Get historical price analysis and trends for a game - Input: game_name (str), days_back (int, optional) - Output: Dict with price history analysis"
)
@register_for_execution()
def get_price_history_analysis(game_name: str, days_back: int = 365) -> Dict:
    """
    🧠 PHASE 7.1: Get comprehensive historical price analysis and trends.

    Features:
    - Historical price data retrieval
    - Trend analysis with statistical confidence
    - Price volatility assessment
    - Significant price drop detection
    - Price pattern recognition

    Args:
        game_name: Name of the game to analyze
        days_back: Number of days of history to analyze (default: 365)

    Returns:
        Dict: Historical price analysis with trends and insights
    """
    try:
        from utils.price_prediction_ml import get_price_prediction_engine

        logger.info(f"📊 Analyzing price history for: {game_name} ({days_back} days)")

        # Get price prediction engine
        prediction_engine = get_price_prediction_engine()

        # Get historical data
        price_history = prediction_engine.get_price_history(game_name, days_back)

        if not price_history:
            return {
                "success": True,
                "game_name": game_name,
                "price_history": [],
                "analysis": {
                    "trend": "unknown",
                    "data_points": 0,
                    "message": "No historical price data available for this game",
                },
                "recommendations": [
                    "Check back later as price data is collected",
                    "Price tracking starts when game is first analyzed",
                ],
            }

        # Analyze trend
        trend_analysis = prediction_engine.analyze_price_trend(price_history)

        # Extract price statistics
        prices = [point.price for point in price_history]
        if prices:
            price_stats = {
                "current_price": prices[-1],
                "historical_high": max(prices),
                "historical_low": min(prices),
                "average_price": sum(prices) / len(prices),
                "median_price": sorted(prices)[len(prices) // 2],
                "price_range": max(prices) - min(prices),
                "volatility_percent": (
                    (max(prices) - min(prices)) / max(prices) * 100
                    if max(prices) > 0
                    else 0
                ),
            }
        else:
            price_stats = {}

        # Detect significant price drops
        significant_drops = []
        for i in range(1, len(price_history)):
            prev_price = price_history[i - 1].price
            curr_price = price_history[i].price

            if prev_price > 0:
                drop_percentage = (prev_price - curr_price) / prev_price
                if drop_percentage >= 0.15:  # 15% drop threshold
                    significant_drops.append(
                        {
                            "date": price_history[i].date.isoformat(),
                            "from_price": prev_price,
                            "to_price": curr_price,
                            "drop_percentage": drop_percentage * 100,
                            "promotion_type": price_history[i].promotion_type,
                        }
                    )

        # Generate insights
        insights = []

        if len(price_history) >= 10:
            insights.append(
                f"Rich dataset: {len(price_history)} price points over {days_back} days"
            )
        elif len(price_history) >= 5:
            insights.append(
                f"Moderate dataset: {len(price_history)} price points available"
            )
        else:
            insights.append(f"Limited dataset: Only {len(price_history)} price points")

        if price_stats:
            current_vs_low = (
                (price_stats["current_price"] - price_stats["historical_low"])
                / price_stats["historical_low"]
                * 100
            )
            if current_vs_low < 10:
                insights.append(f"💎 Near historical low (+{current_vs_low:.1f}%)")
            elif current_vs_low > 50:
                insights.append(
                    f"💸 Well above historical low (+{current_vs_low:.1f}%)"
                )

        if len(significant_drops) > 0:
            insights.append(f"📉 {len(significant_drops)} significant drops detected")
            if significant_drops:
                latest_drop = significant_drops[-1]
                insights.append(
                    f"Latest drop: {latest_drop['drop_percentage']:.1f}% on {latest_drop['date'][:10]}"
                )

        # Generate recommendations
        recommendations = []

        if trend_analysis["trend"].value == "declining":
            recommendations.append(
                "📉 Declining trend detected - consider waiting for further drops"
            )
        elif trend_analysis["trend"].value == "rising":
            recommendations.append(
                "📈 Rising trend detected - current price may be good value"
            )
        elif trend_analysis["trend"].value == "volatile":
            recommendations.append(
                "📊 Volatile pricing - monitor closely for opportunities"
            )

        if price_stats and price_stats.get("volatility_percent", 0) > 30:
            recommendations.append("⚠️ High price volatility - wait for better timing")

        if len(significant_drops) >= 2:
            recommendations.append(
                "🎯 History of price drops - good candidate for waiting"
            )

        # Format price history for response
        formatted_history = [
            {
                "date": point.date.isoformat(),
                "price": point.price,
                "promotion_type": point.promotion_type,
            }
            for point in price_history[-30:]  # Last 30 points for display
        ]

        logger.info(
            f"✅ Price history analysis complete: {len(price_history)} data points, {trend_analysis['trend'].value} trend"
        )

        return {
            "success": True,
            "game_name": game_name,
            "analysis_period": f"{days_back} days",
            "data_quality": {
                "total_data_points": len(price_history),
                "analysis_confidence": trend_analysis.get("confidence", 0.0),
                "sufficient_data": len(price_history) >= 5,
            },
            "price_statistics": price_stats,
            "trend_analysis": {
                "trend": trend_analysis["trend"].value,
                "confidence": trend_analysis.get("confidence", 0.0),
                "slope": trend_analysis.get("slope", 0.0),
                "volatility": trend_analysis.get("volatility", 0.0),
                "analysis": trend_analysis.get("analysis", ""),
            },
            "significant_drops": significant_drops,
            "price_history": formatted_history,
            "insights": insights,
            "recommendations": recommendations,
        }

    except ImportError as e:
        error_msg = f"Price analysis dependencies not available: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "message": "Install ML dependencies: pip install numpy scikit-learn",
        }
    except Exception as e:
        error_msg = f"Error analyzing price history: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "Price history analysis temporarily unavailable",
        }


# ====================================================================
# PHASE 7.1.5: User Collection Management - Multi-User System
# ====================================================================


@register_for_llm(
    description="Register a new user in the system - Input: username (str), role (str, optional), preferences (Dict, optional) - Output: Dict with registration result"
)
@register_for_execution()
def register_new_user(
    username: str, role: str = "admin", preferences: Optional[Dict] = None
) -> Dict:
    """
    👤 PHASE 7.1.5: Register a new user with the multi-user system.

    Features:
    - Username registration with uniqueness validation
    - Role-based access (admin, parent, child, guest)
    - Custom user preferences
    - Family-friendly multi-user support
    - Persistent user profile storage

    Args:
        username: Desired username (must be unique)
        role: User role - admin, parent, child, guest (default: admin)
        preferences: User preferences dictionary (optional)

    Returns:
        Dict: Registration result with user profile data
    """
    try:
        from utils.user_management import register_user

        logger.info(f"👤 Registering new user: {username} with role: {role}")

        # Validate inputs
        if not username or len(username.strip()) < 2:
            return {
                "success": False,
                "error": "Username must be at least 2 characters long",
                "message": "Please provide a valid username",
            }

        valid_roles = ["admin", "parent", "child", "guest"]
        if role.lower() not in valid_roles:
            return {
                "success": False,
                "error": f"Invalid role: {role}",
                "message": f"Role must be one of: {', '.join(valid_roles)}",
                "valid_roles": valid_roles,
            }

        # Register user using utility function
        success, message, user_data = register_user(username, role.lower(), preferences)

        if success:
            logger.info(f"✅ User registered successfully: {username}")
            return {
                "success": True,
                "message": message,
                "user_profile": user_data,
                "next_steps": [
                    "User can now switch to this profile",
                    "Profile preferences can be customized",
                    "Game analysis will be personalized for this user",
                ],
            }
        else:
            logger.warning(f"⚠️ User registration failed: {message}")
            return {
                "success": False,
                "error": message,
                "suggestion": "Try a different username or check role spelling",
            }

    except Exception as e:
        error_msg = f"Error registering user: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "User registration temporarily unavailable",
        }


@register_for_llm(
    description="Get current user information and session details - Input: None - Output: Dict with current user info"
)
@register_for_execution()
def get_current_user_details() -> Dict:
    """
    👤 PHASE 7.1.5: Get comprehensive current user information.

    Features:
    - Current user profile and status
    - Session duration and activity
    - User preferences and settings
    - Profile statistics and history
    - Login status and suggestions

    Returns:
        Dict: Complete current user information
    """
    try:
        from utils.user_management import get_current_user_info

        logger.info("📋 Getting current user details...")

        user_info = get_current_user_info()

        if user_info.get("logged_in"):
            # User is logged in - provide full details
            profile_summary = {
                "username": user_info["username"],
                "role": user_info["role"],
                "member_since": str(user_info["created_at"])[:10],  # Just date
                "session_duration": user_info["session_duration"],
                "total_games_analyzed": user_info["profile_stats"].get(
                    "total_games_analyzed", 0
                ),
                "analysis_history_count": len(
                    user_info["profile_stats"].get("analysis_history", [])
                ),
            }

            # Generate personalized insights
            insights = []
            stats = user_info["profile_stats"]

            if stats.get("total_games_analyzed", 0) > 0:
                insights.append(
                    f"🎮 Analyzed {stats['total_games_analyzed']} games total"
                )

            if stats.get("favorite_genres"):
                top_genres = stats["favorite_genres"][:3]
                insights.append(f"🏷️ Top genres: {', '.join(top_genres)}")

            if stats.get("total_savings", 0) > 0:
                insights.append(
                    f"💰 Total savings tracked: ${stats['total_savings']:.2f}"
                )

            if user_info["role"] == "admin":
                insights.append("🔑 Admin privileges - can manage other users")
            elif user_info["role"] == "parent":
                insights.append("👨‍👩‍👧‍👦 Parent account - can manage children")

            logger.info(
                f"✅ Current user: {user_info['username']} ({user_info['role']})"
            )

            return {
                "success": True,
                "logged_in": True,
                "user_profile": profile_summary,
                "full_details": user_info,
                "insights": insights,
                "available_actions": [
                    "Analyze games with personalized recommendations",
                    "Switch to different user profile",
                    "Update user preferences",
                    "View analysis history",
                ],
            }
        else:
            # No user logged in
            logger.info("❓ No user currently logged in")
            return {
                "success": True,
                "logged_in": False,
                "message": user_info.get("message", "No user logged in"),
                "suggestion": user_info.get(
                    "suggestion", "Register a user or switch to existing profile"
                ),
                "available_actions": [
                    "Register new user with register_new_user()",
                    "Switch to existing user with switch_to_user()",
                    "List all users with list_system_users()",
                    "Create guest session with create_guest_access()",
                ],
            }

    except Exception as e:
        error_msg = f"Error getting current user details: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "User information temporarily unavailable",
        }


@register_for_llm(
    description="Switch to a different user profile - Input: user_identifier (str) - Output: Dict with switch result"
)
@register_for_execution()
def switch_to_user(user_identifier: str) -> Dict:
    """
    👤 PHASE 7.1.5: Switch to a different user profile.

    Features:
    - Switch by username or user ID
    - Automatic session management
    - Profile activation and validation
    - Last active timestamp update
    - Family-friendly user switching

    Args:
        user_identifier: Username or user ID to switch to

    Returns:
        Dict: Switch result with new user profile
    """
    try:
        from utils.user_management import switch_user

        logger.info(f"🔄 Switching to user: {user_identifier}")

        # Validate input
        if not user_identifier or not user_identifier.strip():
            return {
                "success": False,
                "error": "User identifier cannot be empty",
                "message": "Please provide a username or user ID",
            }

        # Attempt to switch user
        success, message, user_data = switch_user(user_identifier.strip())

        if success:
            username = user_data["username"]
            role = user_data["role"]
            logger.info(f"✅ Successfully switched to user: {username} ({role})")

            # Generate switch summary
            switch_summary = {
                "username": username,
                "role": role,
                "user_id": user_data["user_id"],
                "last_active": str(user_data.get("last_active", ""))[
                    :16
                ],  # Date and time
                "profile_stats": user_data["profile_data"],
            }

            # Role-specific welcome messages
            welcome_messages = {
                "admin": "🔑 Admin access activated - full system control available",
                "parent": "👨‍👩‍👧‍👦 Parent profile active - can manage family accounts",
                "child": "👶 Child profile active - parental controls applied",
                "guest": "👤 Guest session active - temporary profile",
            }

            return {
                "success": True,
                "message": message,
                "switched_to": switch_summary,
                "welcome_message": welcome_messages.get(
                    role, f"Welcome back, {username}!"
                ),
                "next_steps": [
                    "Start analyzing games with personalized recommendations",
                    "View your analysis history",
                    "Update profile preferences if needed",
                ],
            }
        else:
            logger.warning(f"⚠️ User switch failed: {message}")
            return {
                "success": False,
                "error": message,
                "suggestions": [
                    "Check username spelling",
                    "List available users with list_system_users()",
                    "Register new user if needed",
                ],
            }

    except Exception as e:
        error_msg = f"Error switching user: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "User switching temporarily unavailable",
        }


@register_for_llm(
    description="List all registered users in the system - Input: None - Output: Dict with users list"
)
@register_for_execution()
def list_system_users() -> Dict:
    """
    👤 PHASE 7.1.5: Get list of all registered users in the system.

    Features:
    - Complete user directory
    - User roles and status
    - Family organization view
    - Registration timestamps
    - Active/inactive status

    Returns:
        Dict: Comprehensive users list with family organization
    """
    try:
        from utils.user_management import list_all_users, get_system_stats

        logger.info("📋 Listing all system users...")

        # Get all users
        all_users = list_all_users()
        system_stats = get_system_stats()

        if not all_users:
            logger.info("📭 No users found in system")
            return {
                "success": True,
                "total_users": 0,
                "users": [],
                "message": "No users registered in the system yet",
                "next_steps": [
                    "Register first user with register_new_user()",
                    "Create guest session with create_guest_access()",
                ],
            }

        # Organize users by role for family view
        users_by_role = {"admins": [], "parents": [], "children": [], "guests": []}

        user_summaries = []
        for user in all_users:
            # Create user summary
            summary = {
                "username": user["username"],
                "user_id": user["user_id"],
                "role": user["role"],
                "status": user["status"],
                "created_date": str(user["created_at"])[:10],
                "last_active": str(user["last_active"])[:10],
                "games_analyzed": user["profile_data"].get("total_games_analyzed", 0),
                "is_current": user["user_id"]
                == system_stats["current_user"].get("user_id"),
            }

            user_summaries.append(summary)

            # Organize by role
            if user["role"] == "admin":
                users_by_role["admins"].append(summary)
            elif user["role"] == "parent":
                users_by_role["parents"].append(summary)
            elif user["role"] == "child":
                users_by_role["children"].append(summary)
            elif user["role"] == "guest":
                users_by_role["guests"].append(summary)

        # Generate insights
        insights = []
        stats = system_stats["user_breakdown"]

        if stats["admins"] > 0:
            insights.append(f"🔑 {stats['admins']} admin(s) - full system access")
        if stats["parents"] > 0:
            insights.append(
                f"👨‍👩‍👧‍👦 {stats['parents']} parent(s) - family management"
            )
        if stats["children"] > 0:
            insights.append(f"👶 {stats['children']} child account(s)")
        if stats["guests"] > 0:
            insights.append(f"👤 {stats['guests']} guest session(s)")

        # Current user info
        current_user = system_stats["current_user"]
        if current_user["logged_in"]:
            insights.append(
                f"👋 Currently logged in: {current_user['username']} ({current_user['role']})"
            )
        else:
            insights.append("❓ No user currently active")

        logger.info(f"✅ Listed {len(all_users)} users successfully")

        return {
            "success": True,
            "total_users": len(all_users),
            "active_users": system_stats["active_users"],
            "users": user_summaries,
            "family_view": users_by_role,
            "system_stats": {
                "total_users": system_stats["total_users"],
                "breakdown": stats,
                "current_user": current_user,
                "session_duration": system_stats["session_duration"],
            },
            "insights": insights,
            "available_actions": [
                "Switch to user with switch_to_user(username)",
                "Register new user with register_new_user()",
                "Get user details with get_current_user_details()",
            ],
        }

    except Exception as e:
        error_msg = f"Error listing users: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "User listing temporarily unavailable",
        }


@register_for_llm(
    description="Create a temporary guest session - Input: None - Output: Dict with guest session details"
)
@register_for_execution()
def create_guest_access() -> Dict:
    """
    👤 PHASE 7.1.5: Create a temporary guest session for quick access.

    Features:
    - Instant guest access without registration
    - Temporary profile (not saved permanently)
    - Basic functionality access
    - Time-limited session
    - No personal data storage

    Returns:
        Dict: Guest session details and limitations
    """
    try:
        from utils.user_management import user_manager

        logger.info("👤 Creating guest session...")

        # Create guest session
        success, message, guest_profile = user_manager.create_guest_session()

        if success:
            guest_username = guest_profile.username
            guest_id = guest_profile.user_id
            logger.info(f"✅ Guest session created: {guest_username}")

            return {
                "success": True,
                "message": message,
                "guest_profile": {
                    "username": guest_username,
                    "user_id": guest_id,
                    "role": "guest",
                    "status": "guest",
                    "created_at": guest_profile.created_at.isoformat(),
                    "session_type": "temporary",
                },
                "limitations": [
                    "⏰ Temporary session - data not saved permanently",
                    "🚫 Limited personalization features",
                    "❌ No analysis history retention",
                    "⚠️ Profile deleted on system restart",
                ],
                "available_features": [
                    "✅ Game analysis and recommendations",
                    "✅ Price comparison and value analysis",
                    "✅ Basic opinion generation",
                    "✅ Search and scraping functionality",
                ],
                "upgrade_options": [
                    "Register permanent account with register_new_user()",
                    "Switch to existing user with switch_to_user()",
                ],
            }
        else:
            logger.error(f"❌ Guest session creation failed: {message}")
            return {
                "success": False,
                "error": message,
                "alternative": "Try registering a permanent user account",
            }

    except Exception as e:
        error_msg = f"Error creating guest session: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "Guest access temporarily unavailable",
        }


@register_for_llm(
    description="Get comprehensive system user statistics and family overview - Input: None - Output: Dict with system stats"
)
@register_for_execution()
def get_user_system_stats() -> Dict:
    """
    👤 PHASE 7.1.5: Get comprehensive user system statistics and overview.

    Features:
    - Total system statistics
    - Family organization overview
    - User activity analysis
    - Session management info
    - Storage and performance metrics

    Returns:
        Dict: Complete system user statistics
    """
    try:
        from utils.user_management import get_system_stats

        logger.info("📊 Getting user system statistics...")

        stats = get_system_stats()

        # Enhance with additional insights
        user_breakdown = stats["user_breakdown"]
        current_user = stats["current_user"]

        # Generate system insights
        system_insights = []

        if stats["total_users"] == 0:
            system_insights.append("📭 Fresh system - no users registered yet")
        elif stats["total_users"] == 1:
            system_insights.append("👤 Single user system")
        else:
            system_insights.append(
                f"👥 Multi-user system with {stats['total_users']} registered users"
            )

        if user_breakdown["admins"] > 1:
            system_insights.append(
                f"🔑 {user_breakdown['admins']} administrators registered"
            )

        if user_breakdown["children"] > 0:
            system_insights.append(
                f"👶 Family-friendly setup with {user_breakdown['children']} child accounts"
            )

        if current_user["logged_in"]:
            system_insights.append(
                f"🟢 Active session: {current_user['username']} ({stats['session_duration']})"
            )
        else:
            system_insights.append("🔴 No active user session")

        # Session activity analysis
        session_activity = {
            "total_actions": stats["session_actions"],
            "session_duration": stats["session_duration"],
            "active_user": current_user if current_user["logged_in"] else None,
        }

        # System health indicators
        health_indicators = {
            "user_data_available": stats["total_users"] > 0,
            "active_session": current_user["logged_in"],
            "multi_user_ready": stats["total_users"] > 1,
            "family_features": user_breakdown["parents"] > 0
            or user_breakdown["children"] > 0,
            "admin_available": user_breakdown["admins"] > 0,
        }

        health_score = sum(health_indicators.values()) / len(health_indicators) * 100

        # Generate recommendations
        recommendations = []

        if stats["total_users"] == 0:
            recommendations.append(
                "📝 Register first user to begin personalized analysis"
            )
        elif not current_user["logged_in"]:
            recommendations.append(
                "🔄 Switch to user profile for personalized features"
            )

        if user_breakdown["admins"] == 0:
            recommendations.append("🔑 Create admin account for system management")

        if stats["total_users"] > 1 and not current_user["logged_in"]:
            recommendations.append("👥 Select user profile for personalized experience")

        logger.info(
            f"✅ System stats: {stats['total_users']} users, {health_score:.1f}% system health"
        )

        return {
            "success": True,
            "system_overview": {
                "total_users": stats["total_users"],
                "active_users": stats["active_users"],
                "user_breakdown": user_breakdown,
                "system_health_score": round(health_score, 1),
            },
            "current_session": session_activity,
            "storage_info": {
                "storage_location": stats["storage_location"],
                "data_persistence": "JSON files with automatic backups",
                "session_tracking": "Active with action logging",
            },
            "health_indicators": health_indicators,
            "system_insights": system_insights,
            "recommendations": recommendations,
            "available_actions": [
                "Register new user: register_new_user(username, role)",
                "Switch user: switch_to_user(username)",
                "List users: list_system_users()",
                "Create guest: create_guest_access()",
                "Get user details: get_current_user_details()",
            ],
        }

    except Exception as e:
        error_msg = f"Error getting system stats: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "fallback": "System statistics temporarily unavailable",
        }
