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
            "eshop-sales": "eShop Sales",
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