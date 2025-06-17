"""
Phase 2: Value Analysis Integration
Punkt 2 Fazy 2: Integracja analizy wartości

Core value analysis module wrapping agent_tools value analysis functionality
Główny moduł analizy wartości opakowujący funkcjonalność z agent_tools
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Import value analysis functions from agent_tools
from agent_tools import (
    calculate_value_score as _calculate_value_score,
    calculate_advanced_value_analysis as _calculate_advanced_value_analysis,
)


def calculate_value_score(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Oblicza podstawowy score wartości za pieniądze.

    Core interface for basic value-for-money analysis.
    Główny interfejs dla podstawowej analizy wartości za pieniądze.

    Args:
        game_data (Dict[str, Any]): Dane gry z DekuDeals

    Returns:
        Dict: Analiza wartości z rekomendacjami cenowymi

    Example:
        >>> value_analysis = calculate_value_score(game_data)
        >>> print(value_analysis["value_metrics"]["recommendation"])
        >>> print(value_analysis["buy_timing"]["assessment"])
    """
    try:
        logger.info("💰 Core: Starting basic value analysis...")

        result = _calculate_value_score(game_data)

        if result.get("success", False):
            recommendation = result.get("value_metrics", {}).get(
                "recommendation", "Unknown"
            )
            timing = result.get("buy_timing", {}).get("assessment", "Unknown")
            logger.info(
                f"✅ Core: Value analysis complete - {recommendation} | Timing: {timing}"
            )
        else:
            logger.warning(
                f"⚠️ Core: Value analysis failed - {result.get('error', 'Unknown error')}"
            )

        return result

    except Exception as e:
        error_msg = f"Core value analysis error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.value_analysis.calculate_value_score",
        }


def calculate_advanced_value_analysis(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Przeprowadza zaawansowaną analizę wartości z algorytmami gatunkowymi.

    Core interface for advanced multi-dimensional value analysis.
    Główny interfejs dla zaawansowanej wielowymiarowej analizy wartości.

    Args:
        game_data (Dict[str, Any]): Dane gry z DekuDeals

    Returns:
        Dict: Kompleksowa analiza z genre factors, market position, age considerations

    Example:
        >>> advanced_analysis = calculate_advanced_value_analysis(game_data)
        >>> print(advanced_analysis["comprehensive_analysis"]["comprehensive_score"])
        >>> print(advanced_analysis["comprehensive_analysis"]["market_analysis"]["market_position"])
    """
    try:
        logger.info("🚀 Core: Starting advanced value analysis...")

        result = _calculate_advanced_value_analysis(game_data)

        if result.get("success", False):
            comp_analysis = result.get("comprehensive_analysis", {})
            score = comp_analysis.get("comprehensive_score", 0)
            recommendation = comp_analysis.get("advanced_recommendation", "Unknown")
            position = comp_analysis.get("market_analysis", {}).get(
                "market_position", "Unknown"
            )

            logger.info(
                f"✅ Core: Advanced analysis complete - Score: {score}, "
                f"Recommendation: {recommendation}, Position: {position}"
            )
        else:
            logger.warning(
                f"⚠️ Core: Advanced analysis failed - {result.get('error', 'Unknown error')}"
            )

        return result

    except Exception as e:
        error_msg = f"Core advanced analysis error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.value_analysis.calculate_advanced_value_analysis",
        }


def get_value_analysis_summary(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generuje kompletne podsumowanie analizy wartości (basic + advanced).

    Combines both basic and advanced value analysis for comprehensive overview.
    Łączy podstawową i zaawansowaną analizę wartości dla pełnego przeglądu.

    Args:
        game_data (Dict[str, Any]): Dane gry z DekuDeals

    Returns:
        Dict: Połączone wyniki obu analiz z metadanymi
    """
    try:
        logger.info("📊 Core: Generating complete value analysis summary...")

        # Przeprowadź obie analizy
        basic_result = calculate_value_score(game_data)
        advanced_result = calculate_advanced_value_analysis(game_data)

        # Sprawdź powodzenie
        basic_success = basic_result.get("success", False)
        advanced_success = advanced_result.get("success", False)

        summary = {
            "success": basic_success or advanced_success,
            "game_title": game_data.get("title", "Unknown"),
            "basic_analysis": basic_result,
            "advanced_analysis": advanced_result,
            "analysis_metadata": {
                "basic_analysis_success": basic_success,
                "advanced_analysis_success": advanced_success,
                "has_complete_analysis": basic_success and advanced_success,
            },
        }

        # Dodaj unified recommendations jeśli obie analizy się powiodły
        if basic_success and advanced_success:
            basic_rec = basic_result.get("value_metrics", {}).get("recommendation", "")
            advanced_rec = advanced_result.get("comprehensive_analysis", {}).get(
                "advanced_recommendation", ""
            )

            summary["unified_recommendation"] = {
                "basic_recommendation": basic_rec,
                "advanced_recommendation": advanced_rec,
                "consensus": _determine_consensus_recommendation(
                    basic_rec, advanced_rec
                ),
            }

        logger.info(
            f"✅ Core: Value analysis summary complete - Both analyses: {basic_success and advanced_success}"
        )
        return summary

    except Exception as e:
        error_msg = f"Core value summary error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.value_analysis.get_value_analysis_summary",
        }


def _determine_consensus_recommendation(basic_rec: str, advanced_rec: str) -> str:
    """Określa consensus recommendation na podstawie obu analiz."""
    # Mapowanie na siłę rekomendacji
    strength_map = {
        "STRONG BUY": 5,
        "BUY": 4,
        "HOLD": 3,
        "CONSIDER": 3,
        "WAIT FOR SALE": 2,
        "WAIT": 2,
        "SKIP": 1,
        "INSTANT BUY": 6,
    }

    basic_strength = strength_map.get(basic_rec, 3)
    advanced_strength = strength_map.get(advanced_rec, 3)

    # Średnia ważona (advanced ma większą wagę)
    weighted_strength = basic_strength * 0.4 + advanced_strength * 0.6

    # Mapowanie z powrotem na rekomendację
    if weighted_strength >= 5.5:
        return "STRONG BUY"
    elif weighted_strength >= 4.5:
        return "BUY"
    elif weighted_strength >= 2.5:
        return "CONSIDER"
    elif weighted_strength >= 1.5:
        return "WAIT FOR SALE"
    else:
        return "SKIP"
