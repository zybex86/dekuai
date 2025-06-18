"""
Phase 1: Data Collection Module
Moduł zbierania danych - Faza 1

Core functionality for searching, scraping, and validating game data from DekuDeals.
Główna funkcjonalność do wyszukiwania, scrapowania i walidacji danych gier z DekuDeals.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
from bs4 import BeautifulSoup, Tag

# Core DekuDeals functionality
from deku_tools import search_deku_deals, scrape_game_details

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameDataCollector:
    """
    Podstawowy kolektor danych o grach z DekuDeals.

    Zapewnia ujednolicony interfejs do wyszukiwania i pobierania
    szczegółowych informacji o grach.
    """

    def __init__(self):
        """Inicjalizuje kolektor danych."""
        self.last_search_result = None
        self.search_history = []

    def search_game(self, game_name: str) -> Dict[str, Any]:
        """
        Wyszukuje grę na DekuDeals.

        Args:
            game_name (str): Nazwa gry do wyszukania

        Returns:
            Dict: Wynik wyszukiwania z URL lub błędem
        """
        try:
            if not game_name or not game_name.strip():
                return {
                    "success": False,
                    "error": "Game name cannot be empty",
                    "game_name": game_name,
                }

            logger.info(f"🔍 Searching for game: {game_name}")

            game_url = search_deku_deals(game_name.strip())

            result = {
                "success": bool(game_url),
                "game_name": game_name,
                "search_query": game_name.strip(),
                "timestamp": self._get_timestamp(),
            }

            if game_url:
                result["game_url"] = game_url
                logger.info(f"✅ Game found: {game_url}")
            else:
                result["error"] = "Game not found"
                logger.warning(f"❌ Game '{game_name}' not found")

            self.last_search_result = result
            self.search_history.append(result)

            return result

        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "game_name": game_name,
                "timestamp": self._get_timestamp(),
            }
            logger.error(f"❌ Search error: {e}")
            return error_result

    def collect_game_details(self, game_url: str) -> Dict[str, Any]:
        """
        Pobiera szczegółowe dane o grze z podanego URL.

        Args:
            game_url (str): URL gry na DekuDeals

        Returns:
            Dict: Szczegółowe dane gry lub błąd
        """
        try:
            if not game_url:
                return {"success": False, "error": "Game URL cannot be empty"}

            logger.info(f"📊 Collecting details from: {game_url}")

            game_details = scrape_game_details(game_url)

            if game_details:
                game_details["success"] = True
                game_details["source_url"] = game_url
                game_details["collection_timestamp"] = self._get_timestamp()

                logger.info(
                    f"✅ Details collected for: {game_details.get('title', 'Unknown')}"
                )
                return game_details
            else:
                error_result = {
                    "success": False,
                    "error": "Failed to collect game details",
                    "source_url": game_url,
                    "timestamp": self._get_timestamp(),
                }
                logger.error(f"❌ Failed to collect details from: {game_url}")
                return error_result

        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "source_url": game_url,
                "timestamp": self._get_timestamp(),
            }
            logger.error(f"❌ Collection error: {e}")
            return error_result

    def search_and_collect(self, game_name: str) -> Dict[str, Any]:
        """
        Wyszukuje grę i pobiera jej szczegółowe dane w jednym kroku.

        Args:
            game_name (str): Nazwa gry

        Returns:
            Dict: Kompletne dane gry lub błąd
        """
        # Krok 1: Wyszukiwanie
        search_result = self.search_game(game_name)

        if not search_result.get("success"):
            return search_result

        # Krok 2: Pobieranie szczegółów
        game_url = search_result.get("game_url")
        if not game_url:
            return search_result
        details_result = self.collect_game_details(game_url)

        if details_result.get("success"):
            # Dodaj metadata z wyszukiwania
            details_result["search_metadata"] = {
                "original_query": search_result.get("search_query"),
                "search_timestamp": search_result.get("timestamp"),
            }

        return details_result

    def validate_game_data(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
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

    def format_game_summary(self, game_data: Dict[str, Any]) -> str:
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

    def extract_key_metrics(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
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
            "has_basic_info": bool(
                game_data.get("developer") and game_data.get("genres")
            ),
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

    def get_search_history(self) -> List[Dict[str, Any]]:
        """
        Zwraca historię wyszukiwań.

        Returns:
            List[Dict]: Lista wyników wyszukiwań
        """
        return self.search_history.copy()

    def clear_history(self) -> None:
        """Czyści historię wyszukiwań."""
        self.search_history.clear()
        self.last_search_result = None
        logger.info("🧹 Search history cleared")

    def _get_timestamp(self) -> str:
        """Zwraca aktualny timestamp."""
        return datetime.now().isoformat()


# Utility functions for backward compatibility
def collect_game_data(game_name: str) -> Dict[str, Any]:
    """
    Funkcja utilitarna do prostego pobierania danych gry.

    Args:
        game_name (str): Nazwa gry

    Returns:
        Dict: Dane gry
    """
    collector = GameDataCollector()
    return collector.search_and_collect(game_name)


def search_and_scrape_game(game_name: Optional[str]) -> Dict[str, Any]:
    """
    Backward compatibility wrapper.

    Args:
        game_name (Optional[str]): Name of game to search for

    Returns:
        Dict: Complete game data or error message
    """
    if not game_name:
        return {"success": False, "error": "Game name cannot be empty"}

    collector = GameDataCollector()
    return collector.search_and_collect(game_name)


def validate_game_data(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """Backward compatibility wrapper for validation."""
    collector = GameDataCollector()
    return collector.validate_game_data(game_data)


def format_game_summary(game_data: Dict[str, Any]) -> str:
    """Backward compatibility wrapper for formatting."""
    collector = GameDataCollector()
    return collector.format_game_summary(game_data)


def extract_key_metrics(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """Backward compatibility wrapper for metrics extraction."""
    collector = GameDataCollector()
    return collector.extract_key_metrics(game_data)
