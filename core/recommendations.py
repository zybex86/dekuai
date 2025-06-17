"""
Phase 2 Point 3: Recommendation System Integration
Punkt 3 Fazy 2: Integracja systemu rekomendacji

Core recommendations module wrapping agent_tools recommendation functionality
Główny moduł rekomendacji opakowujący funkcjonalność z agent_tools
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Import recommendation functions from agent_tools
from agent_tools import (
    generate_personalized_recommendations as _generate_personalized_recommendations,
    compare_games_for_user as _compare_games_for_user,
    get_recommendation_insights as _get_recommendation_insights,
)


def generate_personalized_recommendations(
    games_list: List[str],
    user_preference: str = "bargain_hunter",
    max_recommendations: int = 5,
) -> Dict[str, Any]:
    """
    Generuje spersonalizowane rekomendacje gier dla użytkownika.

    Core interface for personalized game recommendations.
    Główny interfejs dla spersonalizowanych rekomendacji gier.

    Args:
        games_list (List[str]): Lista nazw gier do analizy
        user_preference (str): Typ preferencji użytkownika
            Available: bargain_hunter, quality_seeker, indie_lover, aaa_gamer, casual_player
        max_recommendations (int): Maksymalna liczba rekomendacji

    Returns:
        Dict: Spersonalizowane rekomendacje z uzasadnieniami i metrykami

    Example:
        >>> recommendations = generate_personalized_recommendations(
        ...     ["Hollow Knight", "Celeste", "Dead Cells"],
        ...     user_preference="indie_lover",
        ...     max_recommendations=3
        ... )
        >>> print(recommendations["recommendations"][0]["game_title"])
    """
    try:
        logger.info(f"🎯 Core: Generating personalized recommendations...")
        logger.info(f"📋 Games: {len(games_list)}, Preference: {user_preference}")

        result = _generate_personalized_recommendations(
            games_list, user_preference, max_recommendations
        )

        if result.get("success", False):
            logger.info(
                f"✅ Core: Generated {len(result.get('recommendations', []))} recommendations"
            )
        else:
            logger.warning(
                f"⚠️ Core: Recommendation generation failed - {result.get('error', 'Unknown error')}"
            )

        return result

    except Exception as e:
        error_msg = f"Core recommendations error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.recommendations.generate_personalized_recommendations",
        }


def compare_games_for_user(
    game_names: List[str], user_preference: str = "bargain_hunter"
) -> Dict[str, Any]:
    """
    Porównuje gry pod kątem konkretnego użytkownika z rankingiem.

    Core interface for user-specific game comparison.
    Główny interfejs dla porównań gier specyficznych dla użytkownika.

    Args:
        game_names (List[str]): Lista nazw gier do porównania (minimum 2)
        user_preference (str): Typ preferencji użytkownika

    Returns:
        Dict: Porównanie gier z rankingiem i uzasadnieniami

    Example:
        >>> comparison = compare_games_for_user(
        ...     ["Zelda BOTW", "Hollow Knight", "Celeste"],
        ...     user_preference="quality_seeker"
        ... )
        >>> print(comparison["best_choice"]["game"])
    """
    try:
        logger.info(f"🆚 Core: Comparing {len(game_names)} games...")
        logger.info(f"👤 User preference: {user_preference}")

        if len(game_names) < 2:
            error_msg = "Core comparison requires at least 2 games"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg, "minimum_games_required": 2}

        result = _compare_games_for_user(game_names, user_preference)

        if result.get("success", False):
            logger.info(
                f"✅ Core: Comparison completed - Best: {result.get('best_choice', {}).get('game', 'Unknown')}"
            )
        else:
            logger.warning(
                f"⚠️ Core: Comparison failed - {result.get('error', 'Unknown error')}"
            )

        return result

    except Exception as e:
        error_msg = f"Core comparison error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.recommendations.compare_games_for_user",
        }


def get_recommendation_insights(
    game_name: str, user_preferences: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Analizuje jak gra pasuje do różnych typów użytkowników.

    Core interface for multi-user analysis of a single game.
    Główny interfejs dla analizy gry pod kątem różnych użytkowników.

    Args:
        game_name (str): Nazwa gry do analizy
        user_preferences (List[str], optional): Lista preferencji do sprawdzenia
            Default: ["bargain_hunter", "quality_seeker", "indie_lover", "aaa_gamer", "casual_player"]

    Returns:
        Dict: Analiza dopasowania do różnych profili użytkowników

    Example:
        >>> insights = get_recommendation_insights("Hollow Knight")
        >>> print(insights["best_fit_user"]["user_type"])
        >>> print(insights["overall_insights"])
    """
    try:
        logger.info(f"🔍 Core: Analyzing '{game_name}' for different user types...")

        if user_preferences:
            logger.info(f"📊 Custom preferences: {user_preferences}")
        else:
            logger.info("📊 Using default user preference profiles")

        result = _get_recommendation_insights(game_name, user_preferences)

        if result.get("success", False):
            best_fit = result.get("best_fit_user", {})
            logger.info(
                f"✅ Core: Analysis completed - Best fit: {best_fit.get('user_type', 'Unknown')} ({best_fit.get('score', 0):.1f}/100)"
            )
        else:
            logger.warning(
                f"⚠️ Core: Analysis failed - {result.get('error', 'Unknown error')}"
            )

        return result

    except Exception as e:
        error_msg = f"Core insights error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.recommendations.get_recommendation_insights",
        }


def get_available_user_preferences() -> List[str]:
    """
    Zwraca listę dostępnych preferencji użytkowników.

    Returns list of available user preference types.
    Zwraca listę dostępnych typów preferencji użytkowników.

    Returns:
        List[str]: Lista dostępnych preferencji
    """
    return [
        "bargain_hunter",  # Szuka najlepszych ofer
        "quality_seeker",  # Priorytet jakości nad ceną
        "indie_lover",  # Preferuje gry indie
        "aaa_gamer",  # Preferuje gry AAA
        "casual_player",  # Preferuje krótkie, łatwe gry
    ]


def get_user_preference_descriptions() -> Dict[str, str]:
    """
    Zwraca opisy preferencji użytkowników.

    Returns descriptions of user preference types.
    Zwraca opisy typów preferencji użytkowników.

    Returns:
        Dict[str, str]: Mapa preferencji na opisy
    """
    return {
        "bargain_hunter": "Szuka najlepszych ofert i promocji, budżet 0-30 zł",
        "quality_seeker": "Priorytet jakości nad ceną, minimum 85+ punktów, budżet 30-100 zł",
        "indie_lover": "Preferuje gry niezależne, unikalne doświadczenia, budżet 0-40 zł",
        "aaa_gamer": "Preferuje gry AAA od dużych studiów, budżet 50-200 zł",
        "casual_player": "Preferuje proste, łatwe gry na krótkie sesje, budżet 0-50 zł",
    }
