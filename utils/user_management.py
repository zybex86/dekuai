"""
User Management System for AutoGen DekuDeals
Enhanced user experience with multi-user support, persistent profiles, and family-friendly features.

This module provides:
- Username registration on first use
- User profile switching with persistent storage
- Family/shared device support
- User session management
"""

import json
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserStatus(Enum):
    """User account status options."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    GUEST = "guest"


class UserRole(Enum):
    """User role types for family management."""

    ADMIN = "admin"  # Full system access, can manage other users
    PARENT = "parent"  # Can manage child accounts, spending limits
    CHILD = "child"  # Limited access, parental controls
    GUEST = "guest"  # Temporary access, no profile saving


@dataclass
class UserPreferences:
    """User-specific preferences and settings."""

    preferred_language: str = "en"
    currency: str = "USD"
    budget_limit: Optional[float] = None
    parental_controls: bool = False
    notification_settings: Dict[str, bool] = None
    privacy_settings: Dict[str, bool] = None

    def __post_init__(self):
        if self.notification_settings is None:
            self.notification_settings = {
                "price_alerts": True,
                "new_games": True,
                "sale_notifications": True,
                "weekly_digest": False,
            }
        if self.privacy_settings is None:
            self.privacy_settings = {
                "share_profile": False,
                "public_reviews": False,
                "analytics_tracking": True,
            }


@dataclass
class UserProfile:
    """Complete user profile with metadata and preferences."""

    username: str
    user_id: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    last_active: datetime
    preferences: UserPreferences
    profile_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.profile_data is None:
            self.profile_data = {
                "total_games_analyzed": 0,
                "favorite_genres": [],
                "average_rating": 0.0,
                "total_savings": 0.0,
                "analysis_history": [],
            }


class UserManager:
    """
    Comprehensive user management system with persistent storage.

    Features:
    - Multi-user support with role-based access
    - Family-friendly controls and parental settings
    - Persistent user profiles and preferences
    - Session management and user switching
    - Guest mode for temporary access
    """

    def __init__(self, users_dir: str = "user_profiles"):
        """
        Initialize user management system.

        Args:
            users_dir: Directory for storing user profiles
        """
        self.users_dir = Path(users_dir)
        self.users_dir.mkdir(exist_ok=True)

        # Core user management files
        self.users_file = self.users_dir / "users.json"
        self.current_user_file = self.users_dir / "current_user.json"
        self.session_file = self.users_dir / "session.json"

        # Load existing users and session
        self.users = self._load_users()
        self.current_user = self._load_current_user()
        self.session_data = self._load_session()

        logger.info(f"UserManager initialized. {len(self.users)} users found.")

    def _load_users(self) -> Dict[str, UserProfile]:
        """Load all user profiles from storage."""
        if not self.users_file.exists():
            logger.info("No existing users file found. Starting fresh.")
            return {}

        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            users = {}
            for user_id, user_data in data.items():
                # Convert datetime strings back to datetime objects
                user_data["created_at"] = datetime.fromisoformat(
                    user_data["created_at"]
                )
                user_data["last_active"] = datetime.fromisoformat(
                    user_data["last_active"]
                )

                # Convert enums
                user_data["role"] = UserRole(user_data["role"])
                user_data["status"] = UserStatus(user_data["status"])

                # Reconstruct preferences
                if "preferences" in user_data:
                    user_data["preferences"] = UserPreferences(
                        **user_data["preferences"]
                    )
                else:
                    user_data["preferences"] = UserPreferences()

                users[user_id] = UserProfile(**user_data)

            logger.info(f"Loaded {len(users)} user profiles successfully.")
            return users

        except Exception as e:
            logger.error(f"Error loading users: {e}")
            return {}

    def _save_users(self) -> bool:
        """Save all user profiles to storage."""
        try:
            # Convert to serializable format
            data = {}
            for user_id, profile in self.users.items():
                user_data = asdict(profile)
                # Convert datetime objects to strings
                user_data["created_at"] = profile.created_at.isoformat()
                user_data["last_active"] = profile.last_active.isoformat()
                # Convert enums to strings
                user_data["role"] = profile.role.value
                user_data["status"] = profile.status.value
                data[user_id] = user_data

            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(self.users)} user profiles successfully.")
            return True

        except Exception as e:
            logger.error(f"Error saving users: {e}")
            return False

    def _load_current_user(self) -> Optional[str]:
        """Load currently active user ID."""
        if not self.current_user_file.exists():
            return None

        try:
            with open(self.current_user_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("current_user_id")
        except Exception as e:
            logger.error(f"Error loading current user: {e}")
            return None

    def _save_current_user(self, user_id: Optional[str]) -> bool:
        """Save currently active user ID."""
        try:
            data = {
                "current_user_id": user_id,
                "updated_at": datetime.now().isoformat(),
            }
            with open(self.current_user_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving current user: {e}")
            return False

    def _load_session(self) -> Dict[str, Any]:
        """Load session data."""
        if not self.session_file.exists():
            return {"started_at": datetime.now().isoformat(), "actions": []}

        try:
            with open(self.session_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return {"started_at": datetime.now().isoformat(), "actions": []}

    def _save_session(self) -> bool:
        """Save session data."""
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(self.session_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False

    def register_user(
        self,
        username: str,
        role: UserRole = UserRole.ADMIN,
        preferences: Optional[UserPreferences] = None,
    ) -> Tuple[bool, str, Optional[UserProfile]]:
        """
        Register a new user with the system.

        Args:
            username: Desired username (must be unique)
            role: User role (admin, parent, child, guest)
            preferences: User preferences (optional)

        Returns:
            Tuple of (success, message, user_profile)
        """
        # Validate username
        if not username or len(username.strip()) < 2:
            return False, "Username must be at least 2 characters long", None

        username = username.strip()

        # Check if username already exists
        for profile in self.users.values():
            if profile.username.lower() == username.lower():
                return False, f"Username '{username}' already exists", None

        # Generate unique user ID
        user_id = (
            f"user_{len(self.users) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # Create user profile
        if preferences is None:
            preferences = UserPreferences()

        profile = UserProfile(
            username=username,
            user_id=user_id,
            role=role,
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            last_active=datetime.now(),
            preferences=preferences,
        )

        # Save user
        self.users[user_id] = profile

        # If this is the first user, make them current
        if len(self.users) == 1:
            self.current_user = user_id
            self._save_current_user(user_id)

        # Save to storage
        if self._save_users():
            self._log_action(f"User registered: {username} (Role: {role.value})")
            logger.info(f"User '{username}' registered successfully with ID: {user_id}")
            return True, f"User '{username}' registered successfully!", profile
        else:
            # Rollback on save failure
            del self.users[user_id]
            return False, "Failed to save user profile", None

    def get_all_users(self) -> List[UserProfile]:
        """Get list of all registered users."""
        return list(self.users.values())

    def get_active_users(self) -> List[UserProfile]:
        """Get list of active users only."""
        return [
            profile
            for profile in self.users.values()
            if profile.status == UserStatus.ACTIVE
        ]

    def get_user_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by user ID."""
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[UserProfile]:
        """Get user profile by username."""
        for profile in self.users.values():
            if profile.username.lower() == username.lower():
                return profile
        return None

    def switch_user(
        self, user_identifier: str
    ) -> Tuple[bool, str, Optional[UserProfile]]:
        """
        Switch to a different user.

        Args:
            user_identifier: User ID or username

        Returns:
            Tuple of (success, message, user_profile)
        """
        # Try to find user by ID first, then by username
        profile = self.get_user_by_id(user_identifier)
        if not profile:
            profile = self.get_user_by_username(user_identifier)

        if not profile:
            return False, f"User '{user_identifier}' not found", None

        if profile.status != UserStatus.ACTIVE:
            return False, f"User '{profile.username}' is not active", None

        # Update last active and switch user
        profile.last_active = datetime.now()
        self.current_user = profile.user_id

        # Save changes
        self._save_users()
        self._save_current_user(profile.user_id)

        self._log_action(f"Switched to user: {profile.username}")
        logger.info(f"Switched to user: {profile.username} ({profile.user_id})")

        return True, f"Switched to user: {profile.username}", profile

    def get_current_user(self) -> Optional[UserProfile]:
        """Get currently active user profile."""
        if not self.current_user:
            return None
        return self.users.get(self.current_user)

    def get_current_user_info(self) -> Dict[str, Any]:
        """Get comprehensive current user information."""
        profile = self.get_current_user()
        if not profile:
            return {
                "logged_in": False,
                "message": "No user logged in",
                "suggestion": "Use register_user() to create an account or switch_user() to log in",
            }

        return {
            "logged_in": True,
            "user_id": profile.user_id,
            "username": profile.username,
            "role": profile.role.value,
            "status": profile.status.value,
            "created_at": profile.created_at.isoformat(),
            "last_active": profile.last_active.isoformat(),
            "preferences": asdict(profile.preferences),
            "profile_stats": profile.profile_data,
            "session_duration": self._get_session_duration(),
        }

    def update_user_preferences(self, preferences: UserPreferences) -> Tuple[bool, str]:
        """Update current user's preferences."""
        profile = self.get_current_user()
        if not profile:
            return False, "No user logged in"

        profile.preferences = preferences
        profile.last_active = datetime.now()

        if self._save_users():
            self._log_action("User preferences updated")
            return True, "Preferences updated successfully"
        else:
            return False, "Failed to save preferences"

    def deactivate_user(self, user_identifier: str) -> Tuple[bool, str]:
        """Deactivate a user account (admin only)."""
        current = self.get_current_user()
        if not current or current.role != UserRole.ADMIN:
            return False, "Admin access required"

        profile = self.get_user_by_id(user_identifier) or self.get_user_by_username(
            user_identifier
        )
        if not profile:
            return False, f"User '{user_identifier}' not found"

        if profile.user_id == current.user_id:
            return False, "Cannot deactivate your own account"

        profile.status = UserStatus.INACTIVE
        profile.last_active = datetime.now()

        if self._save_users():
            self._log_action(f"User deactivated: {profile.username}")
            return True, f"User '{profile.username}' deactivated"
        else:
            return False, "Failed to save changes"

    def create_guest_session(self) -> Tuple[bool, str, Optional[UserProfile]]:
        """Create a temporary guest session."""
        guest_username = f"Guest_{datetime.now().strftime('%H%M%S')}"

        profile = UserProfile(
            username=guest_username,
            user_id=f"guest_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            role=UserRole.GUEST,
            status=UserStatus.GUEST,
            created_at=datetime.now(),
            last_active=datetime.now(),
            preferences=UserPreferences(),
        )

        # Don't save guest users permanently
        self.current_user = profile.user_id
        self.users[profile.user_id] = profile  # Temporary storage

        self._log_action(f"Guest session created: {guest_username}")
        logger.info(f"Guest session created: {guest_username}")

        return True, f"Guest session created: {guest_username}", profile

    def get_family_users(self) -> Dict[str, List[UserProfile]]:
        """Get users organized by family roles."""
        family = {"admins": [], "parents": [], "children": [], "guests": []}

        for profile in self.users.values():
            if profile.role == UserRole.ADMIN:
                family["admins"].append(profile)
            elif profile.role == UserRole.PARENT:
                family["parents"].append(profile)
            elif profile.role == UserRole.CHILD:
                family["children"].append(profile)
            elif profile.role == UserRole.GUEST:
                family["guests"].append(profile)

        return family

    def _log_action(self, action: str):
        """Log user action to session."""
        self.session_data["actions"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "user_id": self.current_user,
                "action": action,
            }
        )
        self._save_session()

    def _get_session_duration(self) -> str:
        """Get current session duration."""
        try:
            started = datetime.fromisoformat(self.session_data["started_at"])
            duration = datetime.now() - started

            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60

            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "Unknown"

    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        active_users = self.get_active_users()
        family = self.get_family_users()

        return {
            "total_users": len(self.users),
            "active_users": len(active_users),
            "user_breakdown": {
                "admins": len(family["admins"]),
                "parents": len(family["parents"]),
                "children": len(family["children"]),
                "guests": len(family["guests"]),
            },
            "current_user": self.get_current_user_info(),
            "session_actions": len(self.session_data.get("actions", [])),
            "session_duration": self._get_session_duration(),
            "storage_location": str(self.users_dir.absolute()),
        }


# Global user manager instance
user_manager = UserManager()


# Convenience functions for easy access
def register_user(
    username: str, role: str = "admin", preferences: Optional[Dict] = None
) -> Tuple[bool, str, Optional[Dict]]:
    """
    Register a new user (convenience function).

    Args:
        username: Username
        role: User role (admin, parent, child, guest)
        preferences: User preferences dict

    Returns:
        Tuple of (success, message, user_data)
    """
    try:
        role_enum = UserRole(role.lower())
    except ValueError:
        return (
            False,
            f"Invalid role: {role}. Must be: admin, parent, child, guest",
            None,
        )

    prefs = None
    if preferences:
        prefs = UserPreferences(**preferences)

    success, message, profile = user_manager.register_user(username, role_enum, prefs)

    if success and profile:
        return success, message, asdict(profile)
    else:
        return success, message, None


def get_current_user_info() -> Dict[str, Any]:
    """Get current user information (convenience function)."""
    return user_manager.get_current_user_info()


def switch_user(user_identifier: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Switch to different user (convenience function).

    Args:
        user_identifier: User ID or username

    Returns:
        Tuple of (success, message, user_data)
    """
    success, message, profile = user_manager.switch_user(user_identifier)

    if success and profile:
        return success, message, asdict(profile)
    else:
        return success, message, None


def list_all_users() -> List[Dict[str, Any]]:
    """Get list of all users (convenience function)."""
    users = user_manager.get_all_users()
    return [asdict(user) for user in users]


def get_system_stats() -> Dict[str, Any]:
    """Get system statistics (convenience function)."""
    return user_manager.get_system_stats()


if __name__ == "__main__":
    # Demo usage
    print("🎮 AutoGen DekuDeals - User Management System Demo")
    print("=" * 50)

    # Show system stats
    stats = get_system_stats()
    print(f"Total users: {stats['total_users']}")
    print(
        f"Current user: {stats['current_user']['username'] if stats['current_user']['logged_in'] else 'None'}"
    )

    # If no users, demonstrate registration
    if stats["total_users"] == 0:
        print("\n📝 Registering demo users...")

        # Register main admin user
        success, msg, user = register_user("GameMaster", "admin")
        print(f"Admin: {msg}")

        # Register family members
        success, msg, user = register_user("Dad", "parent")
        print(f"Parent: {msg}")

        success, msg, user = register_user("Kid1", "child")
        print(f"Child: {msg}")

        # Show updated stats
        print(f"\n📊 Updated stats:")
        stats = get_system_stats()
        print(f"Total users: {stats['total_users']}")
        print(f"Active users: {stats['active_users']}")
        print(f"User breakdown: {stats['user_breakdown']}")

    print(f"\n👤 Current user info:")
    current = get_current_user_info()
    if current["logged_in"]:
        print(f"Username: {current['username']}")
        print(f"Role: {current['role']}")
        print(f"Session duration: {current['session_duration']}")
    else:
        print("No user logged in")
