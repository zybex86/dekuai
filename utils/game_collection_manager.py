#!/usr/bin/env python3

"""
Game Collection Manager - Personal Game Library System
====================================================

Manages personal game collections with import/export functionality.
Supports multiple import sources and integrates with Multi-User system.

Features:
- Personal game library tracking (owned/wishlist/not_interested)
- Steam library import (via Steam Web API)
- CSV import/export functionality
- Manual game addition/removal
- Collection-aware recommendations
- Multi-user collection management
- Integration with Smart User Profiler for enhanced personalization

Author: AutoGen DekuDeals Team
Version: 1.0.0
"""

import csv
import json
import logging
import requests
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from urllib.parse import quote

# Import Multi-User system
from .user_management import UserManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameStatus(Enum):
    """Game ownership status options."""

    OWNED = "owned"
    WISHLIST = "wishlist"
    NOT_INTERESTED = "not_interested"
    COMPLETED = "completed"
    PLAYING = "playing"
    DROPPED = "dropped"


class ImportSource(Enum):
    """Supported import sources."""

    STEAM = "steam"
    CSV = "csv"
    MANUAL = "manual"
    DEKUDEALS = "dekudeals"
    JSON = "json"


@dataclass
class GameEntry:
    """Individual game entry in collection."""

    title: str
    status: GameStatus
    platform: str = "Nintendo Switch"
    date_added: datetime = field(default_factory=datetime.now)
    user_rating: Optional[float] = None  # 1-10 scale
    hours_played: Optional[int] = None
    purchase_price: Optional[float] = None
    current_price: Optional[float] = None
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    import_source: ImportSource = ImportSource.MANUAL
    steam_id: Optional[str] = None
    dekudeals_url: Optional[str] = None
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data["date_added"] = self.date_added.isoformat()
        data["last_updated"] = self.last_updated.isoformat()
        # Convert enums to values
        data["status"] = self.status.value
        data["import_source"] = self.import_source.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameEntry":
        """Create GameEntry from dictionary."""
        # Convert datetime strings back to objects
        if isinstance(data["date_added"], str):
            data["date_added"] = datetime.fromisoformat(data["date_added"])
        if isinstance(data["last_updated"], str):
            data["last_updated"] = datetime.fromisoformat(data["last_updated"])

        # Convert enum values back to enums
        if isinstance(data["status"], str):
            data["status"] = GameStatus(data["status"])
        if isinstance(data["import_source"], str):
            data["import_source"] = ImportSource(data["import_source"])

        return cls(**data)


@dataclass
class CollectionStats:
    """Collection statistics and analytics."""

    total_games: int = 0
    owned_games: int = 0
    wishlist_games: int = 0
    completed_games: int = 0
    total_value: float = 0.0
    average_rating: float = 0.0
    total_hours: int = 0
    favorite_genres: List[str] = field(default_factory=list)
    platforms: Dict[str, int] = field(default_factory=dict)
    import_sources: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


class GameCollectionManager:
    """Manages personal game collections with import/export functionality."""

    def __init__(self, collections_dir: str = "game_collections"):
        """Initialize the Game Collection Manager."""
        self.collections_dir = Path(collections_dir)
        self.collections_dir.mkdir(exist_ok=True)

        # Initialize Multi-User system
        self.user_manager = UserManager()

        # Collection storage per user
        self.user_collections: Dict[str, Dict[str, GameEntry]] = {}
        self.collection_stats: Dict[str, CollectionStats] = {}

        # Load existing collections
        self._load_all_collections()

        logger.info("✅ Game Collection Manager initialized")

    def _get_current_user_id(self) -> str:
        """Get current user ID from Multi-User system."""
        try:
            current_user = self.user_manager.get_current_user()
            if current_user:
                return current_user.user_id
        except Exception as e:
            logger.debug(f"Could not get current user: {e}")
        return "default_user"

    def _get_collection_file(self, user_id: str) -> Path:
        """Get collection file path for user."""
        return self.collections_dir / f"{user_id}_collection.json"

    def _load_all_collections(self):
        """Load all user collections from storage."""
        try:
            for collection_file in self.collections_dir.glob("*_collection.json"):
                user_id = collection_file.stem.replace("_collection", "")
                self._load_user_collection(user_id)
        except Exception as e:
            logger.error(f"Error loading collections: {e}")

    def _load_user_collection(self, user_id: str):
        """Load specific user's collection."""
        collection_file = self._get_collection_file(user_id)

        if collection_file.exists():
            try:
                with open(collection_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Load games
                games = {}
                for game_id, game_data in data.get("games", {}).items():
                    games[game_id] = GameEntry.from_dict(game_data)

                self.user_collections[user_id] = games

                # Load stats
                stats_data = data.get("stats", {})
                if stats_data:
                    # Convert datetime if present
                    if "last_updated" in stats_data and isinstance(
                        stats_data["last_updated"], str
                    ):
                        stats_data["last_updated"] = datetime.fromisoformat(
                            stats_data["last_updated"]
                        )
                    self.collection_stats[user_id] = CollectionStats(**stats_data)
                else:
                    self.collection_stats[user_id] = CollectionStats()

                logger.info(
                    f"✅ Loaded collection for user {user_id}: {len(games)} games"
                )

            except Exception as e:
                logger.error(f"Error loading collection for {user_id}: {e}")
                self.user_collections[user_id] = {}
                self.collection_stats[user_id] = CollectionStats()
        else:
            self.user_collections[user_id] = {}
            self.collection_stats[user_id] = CollectionStats()

    def _save_user_collection(self, user_id: str):
        """Save specific user's collection."""
        collection_file = self._get_collection_file(user_id)

        try:
            # Update stats before saving
            self._update_collection_stats(user_id)

            # Prepare data for JSON serialization
            games_data = {}
            for game_id, game_entry in self.user_collections.get(user_id, {}).items():
                games_data[game_id] = game_entry.to_dict()

            # Prepare stats data
            stats = self.collection_stats.get(user_id, CollectionStats())
            stats_data = asdict(stats)
            stats_data["last_updated"] = stats.last_updated.isoformat()

            data = {
                "games": games_data,
                "stats": stats_data,
                "metadata": {
                    "user_id": user_id,
                    "last_saved": datetime.now().isoformat(),
                    "version": "1.0.0",
                },
            }

            with open(collection_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Saved collection for user {user_id}")

        except Exception as e:
            logger.error(f"Error saving collection for {user_id}: {e}")

    def _update_collection_stats(self, user_id: str):
        """Update collection statistics for user."""
        games = self.user_collections.get(user_id, {})

        if not games:
            self.collection_stats[user_id] = CollectionStats()
            return

        stats = CollectionStats()
        stats.total_games = len(games)

        total_rating = 0
        rated_games = 0
        platforms = {}
        import_sources = {}

        for game in games.values():
            # Count by status
            if game.status == GameStatus.OWNED:
                stats.owned_games += 1
            elif game.status == GameStatus.WISHLIST:
                stats.wishlist_games += 1
            elif game.status == GameStatus.COMPLETED:
                stats.completed_games += 1

            # Rating calculation
            if game.user_rating:
                total_rating += game.user_rating
                rated_games += 1

            # Platform tracking
            platforms[game.platform] = platforms.get(game.platform, 0) + 1

            # Import source tracking
            source = game.import_source.value
            import_sources[source] = import_sources.get(source, 0) + 1

            # Value calculation
            if game.purchase_price:
                stats.total_value += game.purchase_price
            elif game.current_price:
                stats.total_value += game.current_price

            # Hours played
            if game.hours_played:
                stats.total_hours += game.hours_played

        # Calculate averages
        if rated_games > 0:
            stats.average_rating = round(total_rating / rated_games, 2)

        stats.platforms = platforms
        stats.import_sources = import_sources
        stats.last_updated = datetime.now()

        self.collection_stats[user_id] = stats

    def add_game(
        self,
        title: str,
        status: GameStatus = GameStatus.OWNED,
        user_rating: Optional[float] = None,
        **kwargs,
    ) -> bool:
        """Add a game to current user's collection."""
        user_id = self._get_current_user_id()

        # Initialize user collection if needed
        if user_id not in self.user_collections:
            self.user_collections[user_id] = {}

        # Create game ID (normalized title)
        game_id = self._normalize_title(title)

        # Check if game already exists
        if game_id in self.user_collections[user_id]:
            logger.warning(f"Game '{title}' already exists in collection")
            return False

        # Create game entry
        game_entry = GameEntry(
            title=title, status=status, user_rating=user_rating, **kwargs
        )

        # Add to collection
        self.user_collections[user_id][game_id] = game_entry

        # Save collection
        self._save_user_collection(user_id)

        logger.info(f"✅ Added '{title}' to collection with status: {status.value}")
        return True

    def update_game(self, title: str, **updates) -> bool:
        """Update a game in current user's collection."""
        user_id = self._get_current_user_id()
        game_id = self._normalize_title(title)

        if (
            user_id not in self.user_collections
            or game_id not in self.user_collections[user_id]
        ):
            logger.warning(f"Game '{title}' not found in collection")
            return False

        game_entry = self.user_collections[user_id][game_id]

        # Update fields
        for field, value in updates.items():
            if hasattr(game_entry, field):
                if field == "status" and isinstance(value, str):
                    value = GameStatus(value)
                setattr(game_entry, field, value)

        game_entry.last_updated = datetime.now()

        # Save collection
        self._save_user_collection(user_id)

        logger.info(f"✅ Updated '{title}' in collection")
        return True

    def remove_game(self, title: str) -> bool:
        """Remove a game from current user's collection."""
        user_id = self._get_current_user_id()
        game_id = self._normalize_title(title)

        if (
            user_id not in self.user_collections
            or game_id not in self.user_collections[user_id]
        ):
            logger.warning(f"Game '{title}' not found in collection")
            return False

        del self.user_collections[user_id][game_id]

        # Save collection
        self._save_user_collection(user_id)

        logger.info(f"✅ Removed '{title}' from collection")
        return True

    def get_game(self, title: str) -> Optional[GameEntry]:
        """Get a game from current user's collection."""
        user_id = self._get_current_user_id()
        game_id = self._normalize_title(title)

        if (
            user_id in self.user_collections
            and game_id in self.user_collections[user_id]
        ):
            return self.user_collections[user_id][game_id]
        return None

    def is_game_owned(self, title: str) -> bool:
        """Check if current user owns a game."""
        game = self.get_game(title)
        return game is not None and game.status == GameStatus.OWNED

    def get_collection(
        self, status_filter: Optional[GameStatus] = None
    ) -> List[GameEntry]:
        """Get current user's collection, optionally filtered by status."""
        user_id = self._get_current_user_id()
        games = self.user_collections.get(user_id, {}).values()

        if status_filter:
            games = [g for g in games if g.status == status_filter]

        return list(games)

    def get_collection_stats(self) -> CollectionStats:
        """Get current user's collection statistics."""
        user_id = self._get_current_user_id()
        return self.collection_stats.get(user_id, CollectionStats())

    def _normalize_title(self, title: str) -> str:
        """Normalize game title for consistent storage."""
        return (
            title.lower().strip().replace(" ", "_").replace(":", "").replace("-", "_")
        )

    def import_from_steam(self, steam_id: str, api_key: str) -> Tuple[bool, str, int]:
        """Import games from Steam library."""
        try:
            logger.info(f"🔄 Starting Steam import for Steam ID: {steam_id}")

            # Get Steam library
            url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
            params = {
                "key": api_key,
                "steamid": steam_id,
                "format": "json",
                "include_appinfo": True,
                "include_played_free_games": True,
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            games_data = data.get("response", {}).get("games", [])

            if not games_data:
                return False, "No games found in Steam library", 0

            # Import games
            imported_count = 0
            user_id = self._get_current_user_id()

            if user_id not in self.user_collections:
                self.user_collections[user_id] = {}

            for game_data in games_data:
                title = game_data.get("name", "Unknown Game")
                playtime_minutes = game_data.get("playtime_forever", 0)
                app_id = str(game_data.get("appid"))

                # Skip if already exists
                game_id = self._normalize_title(title)
                if game_id in self.user_collections[user_id]:
                    continue

                # Create game entry
                game_entry = GameEntry(
                    title=title,
                    status=GameStatus.OWNED,
                    platform="Steam",
                    hours_played=(
                        playtime_minutes // 60 if playtime_minutes > 0 else None
                    ),
                    steam_id=app_id,
                    import_source=ImportSource.STEAM,
                    notes=f"Imported from Steam. Playtime: {playtime_minutes} minutes",
                )

                self.user_collections[user_id][game_id] = game_entry
                imported_count += 1

                # Rate limiting
                time.sleep(0.1)

            # Save collection
            self._save_user_collection(user_id)

            message = f"Successfully imported {imported_count} games from Steam"
            logger.info(f"✅ {message}")
            return True, message, imported_count

        except requests.RequestException as e:
            error_msg = f"Steam API error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, 0
        except Exception as e:
            error_msg = f"Import error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, 0

    def import_from_csv(self, csv_file_path: str) -> Tuple[bool, str, int]:
        """Import games from CSV file."""
        try:
            logger.info(f"🔄 Starting CSV import from: {csv_file_path}")

            imported_count = 0
            user_id = self._get_current_user_id()

            if user_id not in self.user_collections:
                self.user_collections[user_id] = {}

            with open(csv_file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    title = row.get("title", "").strip()
                    if not title:
                        continue

                    # Skip if already exists
                    game_id = self._normalize_title(title)
                    if game_id in self.user_collections[user_id]:
                        continue

                    # Parse status
                    status_str = row.get("status", "owned").lower()
                    try:
                        status = GameStatus(status_str)
                    except ValueError:
                        status = GameStatus.OWNED

                    # Parse rating
                    rating = None
                    rating_str = row.get("rating", "").strip()
                    if rating_str:
                        try:
                            rating = float(rating_str)
                            if not (1 <= rating <= 10):
                                rating = None
                        except ValueError:
                            pass

                    # Parse hours
                    hours = None
                    hours_str = row.get("hours_played", "").strip()
                    if hours_str:
                        try:
                            hours = int(float(hours_str))
                        except ValueError:
                            pass

                    # Create game entry
                    game_entry = GameEntry(
                        title=title,
                        status=status,
                        platform=row.get("platform", "Nintendo Switch"),
                        user_rating=rating,
                        hours_played=hours,
                        notes=row.get("notes", ""),
                        tags=row.get("tags", "").split(",") if row.get("tags") else [],
                        import_source=ImportSource.CSV,
                    )

                    self.user_collections[user_id][game_id] = game_entry
                    imported_count += 1

            # Save collection
            self._save_user_collection(user_id)

            message = f"Successfully imported {imported_count} games from CSV"
            logger.info(f"✅ {message}")
            return True, message, imported_count

        except FileNotFoundError:
            error_msg = f"CSV file not found: {csv_file_path}"
            logger.error(error_msg)
            return False, error_msg, 0
        except Exception as e:
            error_msg = f"CSV import error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, 0

    def export_to_csv(
        self, csv_file_path: str, status_filter: Optional[GameStatus] = None
    ) -> Tuple[bool, str]:
        """Export current user's collection to CSV file."""
        try:
            logger.info(f"🔄 Starting CSV export to: {csv_file_path}")

            games = self.get_collection(status_filter)

            if not games:
                return False, "No games to export"

            fieldnames = [
                "title",
                "status",
                "platform",
                "user_rating",
                "hours_played",
                "purchase_price",
                "current_price",
                "notes",
                "tags",
                "date_added",
                "import_source",
            ]

            with open(csv_file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for game in games:
                    writer.writerow(
                        {
                            "title": game.title,
                            "status": game.status.value,
                            "platform": game.platform,
                            "user_rating": game.user_rating or "",
                            "hours_played": game.hours_played or "",
                            "purchase_price": game.purchase_price or "",
                            "current_price": game.current_price or "",
                            "notes": game.notes,
                            "tags": ",".join(game.tags),
                            "date_added": game.date_added.strftime("%Y-%m-%d"),
                            "import_source": game.import_source.value,
                        }
                    )

            message = f"Successfully exported {len(games)} games to CSV"
            logger.info(f"✅ {message}")
            return True, message

        except Exception as e:
            error_msg = f"CSV export error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def get_recommendations_filter(self) -> Set[str]:
        """Get set of game titles to exclude from recommendations (owned games)."""
        owned_games = self.get_collection(GameStatus.OWNED)
        return {self._normalize_title(game.title) for game in owned_games}

    def suggest_similar_games(self, limit: int = 5) -> List[str]:
        """Suggest games similar to user's favorites based on ratings."""
        favorites = []

        for game in self.get_collection():
            if game.user_rating and game.user_rating >= 8.0:
                favorites.append(game.title)

        # This would integrate with recommendation engine
        # For now, return the favorites as basis for similarity
        return favorites[:limit]


# Global instance
_game_collection_manager = None


def get_game_collection_manager() -> GameCollectionManager:
    """Get global Game Collection Manager instance."""
    global _game_collection_manager
    if _game_collection_manager is None:
        _game_collection_manager = GameCollectionManager()
    return _game_collection_manager


if __name__ == "__main__":
    # Example usage
    manager = GameCollectionManager()

    # Add some test games
    manager.add_game("Hollow Knight", GameStatus.OWNED, user_rating=9.5)
    manager.add_game("Celeste", GameStatus.OWNED, user_rating=9.0)
    manager.add_game("Hades", GameStatus.WISHLIST)

    # Get stats
    stats = manager.get_collection_stats()
    print(f"Collection: {stats.total_games} games, {stats.owned_games} owned")
    print(f"Average rating: {stats.average_rating}")
