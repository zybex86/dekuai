"""
Agent Tools for AutoGen DekuDeals Analysis
Narzędzia dla agentów AutoGen do analizy gier z DekuDeals
"""

import logging
from typing import Dict, Any, Optional, List
from deku_tools import search_deku_deals, scrape_game_details
from utils.price_calculator import (
    extract_price,
    extract_score,
    calculate_discount_percentage,
    calculate_price_difference,
    calculate_value_ratio,
    assess_buy_timing,
    generate_price_recommendation,
    get_price_analysis_summary,
)
from utils.advanced_value_algorithms import (
    calculate_comprehensive_value_analysis,
    calculate_genre_value_score,
    calculate_market_position_score,
    calculate_age_factor,
)

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
        logger.info(f"📊 Extracted prices: current={current_price}, MSRP={msrp}, lowest={lowest_price}")
        logger.info(f"⭐ Extracted scores: Metacritic={metacritic}, OpenCritic={opencritic}")
        
        # Calculate indicators using utility functions
        value_analysis = {
            "success": True,
            "game_title": game_data.get("title", "Unknown"),
            "price_data": {
                "current_price": current_price,
                "msrp": msrp,
                "lowest_historical": lowest_price,
                "price_vs_msrp": calculate_discount_percentage(current_price, msrp),
                "price_vs_lowest": calculate_price_difference(current_price, lowest_price),
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
                "value_score": calculate_value_ratio(current_price, metacritic, opencritic),
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
    opencritic: Optional[float]
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
            "UNKNOWN": "❓ Limited historical price data"
        }
        summary_parts.append(timing_messages.get(timing, "❓ Price timing unclear"))
    
    # Quality assessment
    if metacritic or opencritic:
        avg_score = (metacritic + opencritic) / 2 if metacritic and opencritic else (metacritic or opencritic)
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
            logger.error(f"❌ Comprehensive analysis failed: {comprehensive_result.get('error')}")
            return {"success": False, "error": comprehensive_result["error"], "analysis": "incomplete"}
        
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
            "confidence_level": _calculate_analysis_confidence(game_data, comprehensive_result),
        }
        
        # Log results
        score = comprehensive_result.get("comprehensive_score", 0)
        recommendation = comprehensive_result.get("advanced_recommendation", "Unknown")
        market_position = comprehensive_result.get("market_analysis", {}).get("market_position", "Unknown")
        
        logger.info(f"✅ Advanced analysis complete: Score={score}, Rec={recommendation}, Position={market_position}")
        
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
        insights.append("💎 This appears to be a hidden gem - exceptional quality at budget price")
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
        insights.append(f"💰 Excellent cost per hour (~{cost_per_hour:.1f}/hour) for {expected_hours}h+ of content")
    elif cost_per_hour and cost_per_hour > 5.0:
        insights.append(f"💸 High cost per hour (~{cost_per_hour:.1f}/hour) might not justify the price")
    
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
    
    return insights[:4]  # Limit to 4 most important insights


def _calculate_analysis_confidence(game_data: Dict[str, Any], comprehensive_result: Dict[str, Any]) -> str:
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
    has_historical = bool(extract_price(game_data.get("lowest_historical_price", "N/A")))
    has_metacritic = bool(extract_score(game_data.get("metacritic_score", "0")))
    has_opencritic = bool(extract_score(game_data.get("opencritic_score", "0")))
    has_genres = bool(game_data.get("genres", []))
    has_developer = bool(game_data.get("developer", ""))
    has_release_dates = bool(game_data.get("release_dates_parsed", {}))
    
    data_completeness = sum([
        has_price, has_msrp, has_historical, has_metacritic, 
        has_opencritic, has_genres, has_developer, has_release_dates
    ])
    
    # Check analysis success
    analysis_success = comprehensive_result.get("success", False)
    has_market_analysis = "market_analysis" in comprehensive_result
    has_genre_analysis = "genre_analysis" in comprehensive_result
    
    # Calculate confidence
    if data_completeness >= 7 and analysis_success and has_market_analysis and has_genre_analysis:
        return "HIGH"
    elif data_completeness >= 5 and analysis_success:
        return "MEDIUM"
    else:
        return "LOW"
