"""
Agent Tools for AutoGen DekuDeals Analysis
Narzędzia dla agentów AutoGen do analizy gier z DekuDeals
"""

import logging
from typing import Dict, Any, Optional
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
