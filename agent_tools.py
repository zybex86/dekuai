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
from utils.recommendation_engine import (
    RecommendationEngine,
    UserProfile,
    UserPreference,
    GameRecommendation,
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

    return insights[:4]  # Limit to 4 most important insights


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


# Initialize global recommendation engine
_recommendation_engine = RecommendationEngine()


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
