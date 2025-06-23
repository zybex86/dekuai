"""
Collection Updater - Tool for managing and enriching game collections.

This module provides functionality to:
- View and browse game collections
- Update individual games with ratings, tags, and metadata
- Automatically save changes
- Validate collection readiness for recommendations
- Batch update multiple games
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import asdict

from utils.game_collection_manager import (
    GameCollectionManager,
    GameEntry,
    GameStatus,
    ImportSource,
)
from utils.user_management import UserManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollectionUpdater:
    """Tool for updating and enriching game collections."""

    def __init__(self):
        """Initialize the Collection Updater."""
        self.collection_manager = GameCollectionManager()
        self.user_manager = UserManager()

        # Common genres for quick selection
        self.common_genres = [
            "Action",
            "Adventure",
            "RPG",
            "Strategy",
            "Puzzle",
            "Platformer",
            "Indie",
            "Simulation",
            "Sports",
            "Racing",
            "Fighting",
            "Shooter",
            "Horror",
            "Survival",
            "Metroidvania",
            "Roguelike",
            "Visual Novel",
            "Tower Defense",
            "Card Game",
            "Party",
            "Music",
            "Educational",
        ]

        # Game-specific genre suggestions based on title patterns
        self.genre_suggestions = {
            "mario": ["Platformer", "Party", "Sports", "Racing"],
            "zelda": ["Action", "Adventure", "RPG"],
            "minecraft": ["Simulation", "Survival", "Indie"],
            "overcooked": ["Party", "Simulation", "Co-op"],
            "bastion": ["Action", "RPG", "Indie"],
            "trine": ["Platformer", "Adventure", "Co-op"],
            "steamworld": ["Strategy", "Indie", "Adventure"],
            "final fantasy": ["RPG", "Adventure"],
            "dragon quest": ["RPG", "Adventure", "Simulation"],
            "ace attorney": ["Visual Novel", "Adventure", "Mystery"],
            "rayman": ["Platformer", "Adventure"],
            "moonlighter": ["RPG", "Simulation", "Indie"],
            "iconoclasts": ["Platformer", "Adventure", "Indie"],
            "wargroove": ["Strategy", "Fantasy", "Indie"],
            "star ocean": ["RPG", "Adventure", "Sci-Fi"],
        }

        logger.info("✅ Collection Updater initialized")

    def get_current_user_collection(self) -> Tuple[str, List[GameEntry]]:
        """Get current user and their collection."""
        try:
            current_user = self.user_manager.get_current_user()
            user_id = current_user.user_id if current_user else "default_user"

            collection = self.collection_manager.get_collection()
            return user_id, collection

        except Exception as e:
            logger.error(f"Error getting collection: {e}")
            return "default_user", []

    def view_collection_summary(self) -> Dict[str, Any]:
        """Get a summary of the current collection."""
        user_id, collection = self.get_current_user_collection()
        stats = self.collection_manager.get_collection_stats()

        # Analyze collection readiness
        rated_games = len([g for g in collection if g.user_rating])
        tagged_games = len([g for g in collection if g.tags])
        complete_games = len([g for g in collection if g.user_rating and g.tags])

        # Calculate completion percentage
        total_games = len(collection)
        completion_pct = (complete_games / total_games * 100) if total_games > 0 else 0

        return {
            "user_id": user_id,
            "total_games": total_games,
            "owned_games": stats.owned_games,
            "wishlist_games": stats.wishlist_games,
            "completed_games": stats.completed_games,
            "average_rating": stats.average_rating,
            "rated_games": rated_games,
            "tagged_games": tagged_games,
            "complete_games": complete_games,
            "completion_percentage": round(completion_pct, 1),
            "recommendation_ready": complete_games
            >= 5,  # Need at least 5 complete entries
            "platforms": dict(stats.platforms),
            "import_sources": dict(stats.import_sources),
        }

    def list_games(
        self, status_filter: Optional[str] = None, limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """List games with their current metadata."""
        _, collection = self.get_current_user_collection()

        # Filter by status if specified
        if status_filter:
            try:
                status_enum = GameStatus(status_filter.lower())
                collection = [g for g in collection if g.status == status_enum]
            except ValueError:
                logger.warning(f"Invalid status filter: {status_filter}")

        # Sort by date added (newest first)
        collection.sort(key=lambda g: g.date_added, reverse=True)

        # Limit results
        collection = collection[:limit]

        games_list = []
        for game in collection:
            games_list.append(
                {
                    "title": game.title,
                    "status": game.status.value,
                    "user_rating": game.user_rating,
                    "tags": game.tags,
                    "platform": game.platform,
                    "hours_played": game.hours_played,
                    "purchase_price": game.purchase_price,
                    "notes": (
                        game.notes[:100] + "..."
                        if len(game.notes) > 100
                        else game.notes
                    ),
                    "last_updated": game.last_updated.strftime("%Y-%m-%d %H:%M"),
                    "completion_status": self._get_completion_status(game),
                }
            )

        return games_list

    def _get_completion_status(self, game: GameEntry) -> str:
        """Get completion status for a game."""
        has_rating = game.user_rating is not None
        has_tags = len(game.tags) > 0

        if has_rating and has_tags:
            return "Complete"
        elif has_rating or has_tags:
            return "Partial"
        else:
            return "Empty"

    def get_game_details(self, title: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific game."""
        game = self.collection_manager.get_game(title)
        if not game:
            return None

        # Get suggested genres based on title
        suggested_genres = self._suggest_genres_for_game(title)

        return {
            "title": game.title,
            "status": game.status.value,
            "platform": game.platform,
            "user_rating": game.user_rating,
            "tags": game.tags,
            "hours_played": game.hours_played,
            "purchase_price": game.purchase_price,
            "current_price": game.current_price,
            "notes": game.notes,
            "steam_id": game.steam_id,
            "dekudeals_url": game.dekudeals_url,
            "import_source": game.import_source.value,
            "date_added": game.date_added.strftime("%Y-%m-%d %H:%M"),
            "last_updated": game.last_updated.strftime("%Y-%m-%d %H:%M"),
            "suggested_genres": suggested_genres,
            "completion_status": self._get_completion_status(game),
        }

    def _suggest_genres_for_game(self, title: str) -> List[str]:
        """Suggest genres based on game title."""
        title_lower = title.lower()
        suggestions = []

        # Check title patterns
        for pattern, genres in self.genre_suggestions.items():
            if pattern in title_lower:
                suggestions.extend(genres)
                break

        # If no specific suggestions, provide common ones
        if not suggestions:
            suggestions = ["Action", "Adventure", "Indie", "Strategy"]

        return list(set(suggestions))  # Remove duplicates

    def update_game(self, title: str, updates: Dict[str, Any]) -> Tuple[bool, str]:
        """Update a game with new information."""
        try:
            # Validate rating if provided
            if "user_rating" in updates and updates["user_rating"] is not None:
                rating = float(updates["user_rating"])
                if not (1.0 <= rating <= 10.0):
                    return False, "Rating must be between 1.0 and 10.0"
                updates["user_rating"] = rating

            # Validate status if provided
            if "status" in updates:
                try:
                    GameStatus(updates["status"].lower())
                except ValueError:
                    return (
                        False,
                        f"Invalid status. Valid options: {[s.value for s in GameStatus]}",
                    )

            # Validate tags if provided
            if "tags" in updates:
                if isinstance(updates["tags"], str):
                    # Convert comma-separated string to list
                    updates["tags"] = [
                        tag.strip() for tag in updates["tags"].split(",") if tag.strip()
                    ]
                elif not isinstance(updates["tags"], list):
                    return False, "Tags must be a list or comma-separated string"

            # Validate hours_played if provided
            if "hours_played" in updates and updates["hours_played"] is not None:
                hours = int(updates["hours_played"])
                if hours < 0:
                    return False, "Hours played cannot be negative"
                updates["hours_played"] = hours

            # Update the game
            success = self.collection_manager.update_game(title, **updates)

            if success:
                return True, f"Successfully updated '{title}'"
            else:
                return False, f"Game '{title}' not found in collection"

        except Exception as e:
            return False, f"Error updating game: {str(e)}"

    def batch_update_ratings(
        self, ratings: Dict[str, float]
    ) -> Tuple[int, int, List[str]]:
        """Batch update ratings for multiple games."""
        success_count = 0
        error_count = 0
        errors = []

        for title, rating in ratings.items():
            try:
                success, message = self.update_game(title, {"user_rating": rating})
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"{title}: {message}")
            except Exception as e:
                error_count += 1
                errors.append(f"{title}: {str(e)}")

        return success_count, error_count, errors

    def batch_add_tags(
        self, game_tags: Dict[str, List[str]]
    ) -> Tuple[int, int, List[str]]:
        """Batch add tags to multiple games."""
        success_count = 0
        error_count = 0
        errors = []

        for title, tags in game_tags.items():
            try:
                success, message = self.update_game(title, {"tags": tags})
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"{title}: {message}")
            except Exception as e:
                error_count += 1
                errors.append(f"{title}: {str(e)}")

        return success_count, error_count, errors

    def auto_suggest_improvements(self) -> Dict[str, Any]:
        """Automatically suggest improvements for the collection."""
        _, collection = self.get_current_user_collection()

        suggestions = {
            "missing_ratings": [],
            "missing_tags": [],
            "suggested_tags": {},
            "priority_games": [],
            "completion_tips": [],
        }

        for game in collection:
            # Games missing ratings
            if game.user_rating is None:
                suggestions["missing_ratings"].append(game.title)

            # Games missing tags
            if not game.tags:
                suggestions["missing_tags"].append(game.title)
                # Suggest tags for this game
                suggested = self._suggest_genres_for_game(game.title)
                suggestions["suggested_tags"][game.title] = suggested

        # Priority games (popular titles that should be rated first)
        priority_keywords = [
            "mario",
            "zelda",
            "minecraft",
            "overcooked",
            "bastion",
            "final fantasy",
        ]
        for game in collection:
            if any(keyword in game.title.lower() for keyword in priority_keywords):
                if game.user_rating is None or not game.tags:
                    suggestions["priority_games"].append(game.title)

        # General completion tips
        total_games = len(collection)
        rated_games = len([g for g in collection if g.user_rating])
        tagged_games = len([g for g in collection if g.tags])

        if rated_games < 5:
            suggestions["completion_tips"].append(
                "Add ratings to at least 5 games to enable recommendations"
            )
        if tagged_games < 5:
            suggestions["completion_tips"].append(
                "Add genre tags to at least 5 games for better recommendations"
            )
        if total_games > 20 and rated_games < total_games * 0.3:
            suggestions["completion_tips"].append(
                "Rate at least 30% of your games for optimal recommendations"
            )

        return suggestions

    def validate_collection_for_recommendations(self) -> Dict[str, Any]:
        """Validate if collection is ready for recommendations."""
        try:
            from utils.collection_recommendation_engine import (
                get_collection_recommendation_engine,
            )

            engine = get_collection_recommendation_engine()
            insights = engine.get_collection_insights()

            readiness = insights.get("recommendations_readiness", {})
            summary = insights.get("collection_summary", {})
            genre_prefs = insights.get("genre_preferences", {})
            dev_prefs = insights.get("developer_preferences", {})

            return {
                "ready": all(readiness.values()),
                "readiness_details": readiness,
                "collection_size": summary.get("total_games", 0),
                "confidence_level": summary.get("confidence_level", "unknown"),
                "genre_preferences_found": len(genre_prefs.get("favorites", [])),
                "developer_preferences_found": len(dev_prefs.get("favorites", [])),
                "recommendations": {
                    "similar": (
                        "✅ Ready" if readiness.get("similar") else "❌ Not Ready"
                    ),
                    "discovery": (
                        "✅ Ready" if readiness.get("discovery") else "❌ Not Ready"
                    ),
                    "developer": (
                        "✅ Ready" if readiness.get("developer") else "❌ Not Ready"
                    ),
                    "complementary": (
                        "✅ Ready" if readiness.get("complementary") else "❌ Not Ready"
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Error validating collection: {e}")
            return {
                "ready": False,
                "error": str(e),
                "recommendations": {
                    "similar": "❌ Error",
                    "discovery": "❌ Error",
                    "developer": "❌ Error",
                    "complementary": "❌ Error",
                },
            }

    def export_collection_summary(self, format: str = "dict") -> Any:
        """Export collection summary in various formats."""
        summary = self.view_collection_summary()
        games = self.list_games(limit=1000)  # Get all games

        export_data = {
            "summary": summary,
            "games": games,
            "export_timestamp": datetime.now().isoformat(),
        }

        if format == "json":
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        else:
            return export_data


# Convenience functions
def get_collection_updater() -> CollectionUpdater:
    """Get singleton instance of CollectionUpdater."""
    if not hasattr(get_collection_updater, "_instance"):
        get_collection_updater._instance = CollectionUpdater()
    return get_collection_updater._instance


def quick_update_game(
    title: str, rating: Optional[float] = None, tags: Optional[List[str]] = None
) -> Tuple[bool, str]:
    """Quick function to update a game's rating and tags."""
    updater = get_collection_updater()
    updates = {}

    if rating is not None:
        updates["user_rating"] = rating
    if tags is not None:
        updates["tags"] = tags

    return updater.update_game(title, updates)


def quick_collection_status() -> Dict[str, Any]:
    """Quick function to get collection status."""
    updater = get_collection_updater()
    return updater.view_collection_summary()
