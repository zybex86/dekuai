# ===================================================================
# 🎮 AutoGen DekuDeals - Usage Analytics System
# Comprehensive user behavior and usage pattern tracking
# ===================================================================

import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import logging
from collections import defaultdict, Counter
import threading

# ===================================================================
# Analytics Data Models
# ===================================================================


class EventType(Enum):
    """Types of user events to track"""

    GAME_ANALYSIS = "game_analysis"
    QUICK_ANALYSIS = "quick_analysis"
    BATCH_ANALYSIS = "batch_analysis"
    COMPARISON = "comparison"
    CATEGORY_BROWSE = "category_browse"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    ERROR = "error"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    CLI_COMMAND = "cli_command"
    INTERACTIVE_MODE = "interactive_mode"


class UserSegment(Enum):
    """User behavior segments"""

    POWER_USER = "power_user"  # High frequency, diverse usage
    CASUAL_USER = "casual_user"  # Occasional single analyses
    RESEARCHER = "researcher"  # Batch analyses, comparisons
    BARGAIN_HUNTER = "bargain_hunter"  # Focus on price analysis
    QUALITY_SEEKER = "quality_seeker"  # Focus on review quality
    NEW_USER = "new_user"  # Recent first-time users


@dataclass
class UsageEvent:
    """Single usage event"""

    event_id: str
    session_id: str
    user_id: str
    event_type: EventType
    timestamp: datetime
    game_name: Optional[str]
    command: Optional[str]
    parameters: Dict[str, Any]
    success: bool
    execution_time: float
    error_message: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class UserSession:
    """User session data"""

    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_events: int
    unique_games: Set[str]
    commands_used: Set[str]
    total_execution_time: float
    errors_count: int
    session_duration: Optional[float]  # minutes
    user_segment: Optional[UserSegment]


@dataclass
class UsageStatistics:
    """Usage statistics summary"""

    period: str
    total_users: int
    total_sessions: int
    total_events: int
    unique_games_analyzed: int
    avg_session_duration: float
    most_popular_games: List[Dict[str, Any]]
    most_used_commands: List[Dict[str, Any]]
    user_segments: Dict[str, int]
    error_rate: float
    cache_hit_rate: float
    peak_usage_hours: List[int]
    growth_metrics: Dict[str, float]


@dataclass
class UserProfile:
    """Detailed user behavior profile"""

    user_id: str
    first_seen: datetime
    last_seen: datetime
    total_sessions: int
    total_events: int
    favorite_games: List[str]
    preferred_commands: List[str]
    avg_session_duration: float
    user_segment: UserSegment
    behavior_patterns: Dict[str, Any]
    preferences: Dict[str, Any]


# ===================================================================
# Usage Analytics System
# ===================================================================


class UsageAnalytics:
    """
    Comprehensive usage analytics and user behavior tracking system

    Features:
    - Real-time event tracking
    - User session management
    - Behavior pattern analysis
    - User segmentation
    - Usage statistics and reporting
    - Trend analysis and insights
    """

    def __init__(self, data_dir: str = "analytics_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Storage files
        self.events_file = self.data_dir / "usage_events.json"
        self.sessions_file = self.data_dir / "user_sessions.json"
        self.profiles_file = self.data_dir / "user_profiles.json"
        self.statistics_file = self.data_dir / "usage_statistics.json"

        # In-memory storage
        self.events: List[UsageEvent] = []
        self.sessions: Dict[str, UserSession] = {}
        self.user_profiles: Dict[str, UserProfile] = {}

        # Current session tracking
        self.current_session_id: Optional[str] = None
        self.current_user_id: str = self._generate_user_id()

        # Configuration
        self.max_events_in_memory = 50000
        self.session_timeout_minutes = 30

        # Thread safety
        self._lock = threading.Lock()

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Load existing data
        self._load_existing_data()

        # Start new session
        self._start_session()

    def _generate_user_id(self) -> str:
        """Generate or retrieve persistent user ID"""
        user_id_file = self.data_dir / "user_id.txt"

        if user_id_file.exists():
            try:
                return user_id_file.read_text().strip()
            except:
                pass

        # Generate new user ID
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        try:
            user_id_file.write_text(user_id)
        except:
            pass

        return user_id

    def _load_existing_data(self):
        """Load existing analytics data"""
        try:
            # Load events (last 30 days)
            if self.events_file.exists():
                with open(self.events_file, "r") as f:
                    data = json.load(f)
                    cutoff = datetime.now() - timedelta(days=30)
                    for item in data.get("events", []):
                        timestamp = datetime.fromisoformat(item["timestamp"])
                        if timestamp > cutoff:
                            event = UsageEvent(
                                event_id=item["event_id"],
                                session_id=item["session_id"],
                                user_id=item["user_id"],
                                event_type=EventType(item["event_type"]),
                                timestamp=timestamp,
                                game_name=item.get("game_name"),
                                command=item.get("command"),
                                parameters=item.get("parameters", {}),
                                success=item["success"],
                                execution_time=item["execution_time"],
                                error_message=item.get("error_message"),
                                metadata=item.get("metadata", {}),
                            )
                            self.events.append(event)

            # Load sessions
            if self.sessions_file.exists():
                with open(self.sessions_file, "r") as f:
                    data = json.load(f)
                    for session_id, session_data in data.get("sessions", {}).items():
                        session = UserSession(
                            session_id=session_data["session_id"],
                            user_id=session_data["user_id"],
                            start_time=datetime.fromisoformat(
                                session_data["start_time"]
                            ),
                            end_time=(
                                datetime.fromisoformat(session_data["end_time"])
                                if session_data.get("end_time")
                                else None
                            ),
                            total_events=session_data["total_events"],
                            unique_games=set(session_data["unique_games"]),
                            commands_used=set(session_data["commands_used"]),
                            total_execution_time=session_data["total_execution_time"],
                            errors_count=session_data["errors_count"],
                            session_duration=session_data.get("session_duration"),
                            user_segment=(
                                UserSegment(session_data["user_segment"])
                                if session_data.get("user_segment")
                                else None
                            ),
                        )
                        self.sessions[session_id] = session

            # Load user profiles
            if self.profiles_file.exists():
                with open(self.profiles_file, "r") as f:
                    data = json.load(f)
                    for user_id, profile_data in data.get("profiles", {}).items():
                        profile = UserProfile(
                            user_id=profile_data["user_id"],
                            first_seen=datetime.fromisoformat(
                                profile_data["first_seen"]
                            ),
                            last_seen=datetime.fromisoformat(profile_data["last_seen"]),
                            total_sessions=profile_data["total_sessions"],
                            total_events=profile_data["total_events"],
                            favorite_games=profile_data["favorite_games"],
                            preferred_commands=profile_data["preferred_commands"],
                            avg_session_duration=profile_data["avg_session_duration"],
                            user_segment=UserSegment(profile_data["user_segment"]),
                            behavior_patterns=profile_data.get("behavior_patterns", {}),
                            preferences=profile_data.get("preferences", {}),
                        )
                        self.user_profiles[user_id] = profile

        except Exception as e:
            self.logger.warning(f"Could not load existing analytics data: {e}")

    def _start_session(self):
        """Start a new user session"""
        self.current_session_id = f"session_{uuid.uuid4().hex[:8]}"

        session = UserSession(
            session_id=self.current_session_id,
            user_id=self.current_user_id,
            start_time=datetime.now(),
            end_time=None,
            total_events=0,
            unique_games=set(),
            commands_used=set(),
            total_execution_time=0.0,
            errors_count=0,
            session_duration=None,
            user_segment=None,
        )

        self.sessions[self.current_session_id] = session

        # Track session start event
        self.track_event(
            event_type=EventType.SESSION_START, success=True, execution_time=0.0
        )

    def track_event(
        self,
        event_type: EventType,
        success: bool = True,
        execution_time: float = 0.0,
        game_name: Optional[str] = None,
        command: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Track a usage event"""

        if not self.current_session_id:
            self._start_session()

        event_id = f"event_{uuid.uuid4().hex[:8]}"

        event = UsageEvent(
            event_id=event_id,
            session_id=self.current_session_id,
            user_id=self.current_user_id,
            event_type=event_type,
            timestamp=datetime.now(),
            game_name=game_name,
            command=command,
            parameters=parameters or {},
            success=success,
            execution_time=execution_time,
            error_message=error_message,
            metadata=metadata or {},
        )

        with self._lock:
            self.events.append(event)

            # Update session
            if self.current_session_id in self.sessions:
                session = self.sessions[self.current_session_id]
                session.total_events += 1
                session.total_execution_time += execution_time

                if game_name:
                    session.unique_games.add(game_name)
                if command:
                    session.commands_used.add(command)
                if not success:
                    session.errors_count += 1

            # Keep only recent events in memory
            if len(self.events) > self.max_events_in_memory:
                cutoff = datetime.now() - timedelta(days=7)
                self.events = [e for e in self.events if e.timestamp > cutoff]

        # Update user profile
        self._update_user_profile(event)

        # Save periodically
        if len(self.events) % 1000 == 0:
            self._save_data()

        self.logger.debug(
            f"Tracked event: {event_type.value} for user {self.current_user_id}"
        )
        return event_id

    def _update_user_profile(self, event: UsageEvent):
        """Update user profile based on new event"""
        user_id = event.user_id

        if user_id not in self.user_profiles:
            # Create new profile
            profile = UserProfile(
                user_id=user_id,
                first_seen=event.timestamp,
                last_seen=event.timestamp,
                total_sessions=0,
                total_events=1,
                favorite_games=[],
                preferred_commands=[],
                avg_session_duration=0.0,
                user_segment=UserSegment.NEW_USER,
                behavior_patterns={},
                preferences={},
            )
            self.user_profiles[user_id] = profile
        else:
            profile = self.user_profiles[user_id]
            profile.last_seen = event.timestamp
            profile.total_events += 1

        # Update based on event type
        if event.game_name and event.game_name not in profile.favorite_games:
            profile.favorite_games.append(event.game_name)
            # Keep only top 10 games
            if len(profile.favorite_games) > 10:
                profile.favorite_games = profile.favorite_games[-10:]

        if event.command and event.command not in profile.preferred_commands:
            profile.preferred_commands.append(event.command)
            # Keep only top 10 commands
            if len(profile.preferred_commands) > 10:
                profile.preferred_commands = profile.preferred_commands[-10:]

        # Update user segment
        profile.user_segment = self._determine_user_segment(user_id)

    def _determine_user_segment(self, user_id: str) -> UserSegment:
        """Determine user segment based on behavior"""
        user_events = [e for e in self.events if e.user_id == user_id]

        if not user_events:
            return UserSegment.NEW_USER

        # Calculate metrics
        total_events = len(user_events)
        unique_games = len(set(e.game_name for e in user_events if e.game_name))
        batch_events = len(
            [e for e in user_events if e.event_type == EventType.BATCH_ANALYSIS]
        )
        comparison_events = len(
            [e for e in user_events if e.event_type == EventType.COMPARISON]
        )
        days_active = (
            max(e.timestamp for e in user_events)
            - min(e.timestamp for e in user_events)
        ).days + 1

        # Calculate rates
        events_per_day = total_events / max(days_active, 1)
        batch_rate = batch_events / total_events if total_events > 0 else 0
        comparison_rate = comparison_events / total_events if total_events > 0 else 0

        # Segment logic
        if days_active <= 3:
            return UserSegment.NEW_USER
        elif events_per_day >= 5 and unique_games >= 10:
            return UserSegment.POWER_USER
        elif batch_rate >= 0.3 or comparison_rate >= 0.2:
            return UserSegment.RESEARCHER
        elif events_per_day >= 2:
            # Analyze content patterns for bargain hunter vs quality seeker
            price_focus_events = len(
                [
                    e
                    for e in user_events
                    if e.parameters.get("analysis_type") == "price"
                    or "price" in str(e.parameters).lower()
                ]
            )

            if price_focus_events / total_events >= 0.4:
                return UserSegment.BARGAIN_HUNTER
            else:
                return UserSegment.QUALITY_SEEKER
        else:
            return UserSegment.CASUAL_USER

    def end_session(self):
        """End current session"""
        if not self.current_session_id or self.current_session_id not in self.sessions:
            return

        session = self.sessions[self.current_session_id]
        session.end_time = datetime.now()

        if session.start_time:
            session.session_duration = (
                session.end_time - session.start_time
            ).total_seconds() / 60.0

        # Determine session's user segment
        session.user_segment = self._determine_user_segment(self.current_user_id)

        # Update user profile
        if self.current_user_id in self.user_profiles:
            profile = self.user_profiles[self.current_user_id]
            profile.total_sessions += 1

            # Update average session duration
            all_sessions = [
                s
                for s in self.sessions.values()
                if s.user_id == self.current_user_id and s.session_duration
            ]
            if all_sessions:
                profile.avg_session_duration = sum(
                    s.session_duration for s in all_sessions
                ) / len(all_sessions)

        # Track session end event
        self.track_event(
            event_type=EventType.SESSION_END,
            success=True,
            execution_time=0.0,
            metadata={"session_duration": session.session_duration},
        )

        self.current_session_id = None
        self._save_data()

    def get_usage_statistics(self, period: str = "30d") -> UsageStatistics:
        """Generate comprehensive usage statistics"""
        # Parse period
        if period.endswith("d"):
            days = int(period[:-1])
            cutoff = datetime.now() - timedelta(days=days)
        elif period.endswith("h"):
            hours = int(period[:-1])
            cutoff = datetime.now() - timedelta(hours=hours)
        else:
            cutoff = datetime.now() - timedelta(days=30)  # Default 30 days

        # Filter data
        period_events = [e for e in self.events if e.timestamp >= cutoff]
        period_sessions = [s for s in self.sessions.values() if s.start_time >= cutoff]

        if not period_events:
            return UsageStatistics(
                period=period,
                total_users=0,
                total_sessions=0,
                total_events=0,
                unique_games_analyzed=0,
                avg_session_duration=0.0,
                most_popular_games=[],
                most_used_commands=[],
                user_segments={},
                error_rate=0.0,
                cache_hit_rate=0.0,
                peak_usage_hours=[],
                growth_metrics={},
            )

        # Calculate basic metrics
        unique_users = len(set(e.user_id for e in period_events))
        unique_games = len(set(e.game_name for e in period_events if e.game_name))
        success_events = [e for e in period_events if e.success]
        error_rate = (1 - len(success_events) / len(period_events)) * 100

        # Session metrics
        session_durations = [
            s.session_duration for s in period_sessions if s.session_duration
        ]
        avg_session_duration = (
            sum(session_durations) / len(session_durations)
            if session_durations
            else 0.0
        )

        # Popular games
        game_counts = Counter(e.game_name for e in period_events if e.game_name)
        most_popular_games = [
            {"game": game, "count": count}
            for game, count in game_counts.most_common(10)
        ]

        # Popular commands
        command_counts = Counter(e.command for e in period_events if e.command)
        most_used_commands = [
            {"command": cmd, "count": count}
            for cmd, count in command_counts.most_common(10)
        ]

        # User segments
        segment_counts = Counter()
        for session in period_sessions:
            if session.user_segment:
                segment_counts[session.user_segment.value] += 1
        user_segments = dict(segment_counts)

        # Cache metrics
        cache_hits = len(
            [e for e in period_events if e.event_type == EventType.CACHE_HIT]
        )
        cache_misses = len(
            [e for e in period_events if e.event_type == EventType.CACHE_MISS]
        )
        cache_hit_rate = (
            (cache_hits / (cache_hits + cache_misses)) * 100
            if (cache_hits + cache_misses) > 0
            else 0.0
        )

        # Peak usage hours
        hour_counts = Counter(e.timestamp.hour for e in period_events)
        peak_usage_hours = [hour for hour, count in hour_counts.most_common(3)]

        # Growth metrics
        growth_metrics = self._calculate_growth_metrics(period_events, period)

        return UsageStatistics(
            period=period,
            total_users=unique_users,
            total_sessions=len(period_sessions),
            total_events=len(period_events),
            unique_games_analyzed=unique_games,
            avg_session_duration=avg_session_duration,
            most_popular_games=most_popular_games,
            most_used_commands=most_used_commands,
            user_segments=user_segments,
            error_rate=error_rate,
            cache_hit_rate=cache_hit_rate,
            peak_usage_hours=peak_usage_hours,
            growth_metrics=growth_metrics,
        )

    def _calculate_growth_metrics(
        self, events: List[UsageEvent], period: str
    ) -> Dict[str, float]:
        """Calculate growth metrics"""
        if not events:
            return {}

        # Split period in half for comparison
        total_days = (
            30 if period == "30d" else int(period[:-1]) if period.endswith("d") else 30
        )
        mid_point = datetime.now() - timedelta(days=total_days // 2)

        first_half = [e for e in events if e.timestamp < mid_point]
        second_half = [e for e in events if e.timestamp >= mid_point]

        if not first_half:
            return {"user_growth": 0.0, "event_growth": 0.0}

        # Calculate growth rates
        users_first = len(set(e.user_id for e in first_half))
        users_second = len(set(e.user_id for e in second_half))
        user_growth = (
            ((users_second - users_first) / users_first) * 100
            if users_first > 0
            else 0.0
        )

        events_first = len(first_half)
        events_second = len(second_half)
        event_growth = (
            ((events_second - events_first) / events_first) * 100
            if events_first > 0
            else 0.0
        )

        return {"user_growth": user_growth, "event_growth": event_growth}

    def get_user_insights(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed user behavior insights"""
        target_user = user_id or self.current_user_id

        user_events = [e for e in self.events if e.user_id == target_user]
        user_sessions = [s for s in self.sessions.values() if s.user_id == target_user]

        if not user_events:
            return {"error": "No data found for user"}

        # Basic stats
        total_events = len(user_events)
        unique_games = len(set(e.game_name for e in user_events if e.game_name))
        first_activity = min(e.timestamp for e in user_events)
        last_activity = max(e.timestamp for e in user_events)
        days_active = (last_activity - first_activity).days + 1

        # Behavior patterns
        event_types = Counter(e.event_type.value for e in user_events)
        game_preferences = Counter(e.game_name for e in user_events if e.game_name)
        command_usage = Counter(e.command for e in user_events if e.command)

        # Time patterns
        hour_pattern = Counter(e.timestamp.hour for e in user_events)
        day_pattern = Counter(e.timestamp.strftime("%A") for e in user_events)

        # Session patterns
        session_durations = [
            s.session_duration for s in user_sessions if s.session_duration
        ]
        avg_session_duration = (
            sum(session_durations) / len(session_durations)
            if session_durations
            else 0.0
        )

        # User profile
        profile = self.user_profiles.get(target_user)

        return {
            "user_id": target_user,
            "profile": asdict(profile) if profile else None,
            "activity_summary": {
                "total_events": total_events,
                "unique_games": unique_games,
                "days_active": days_active,
                "events_per_day": total_events / max(days_active, 1),
                "first_activity": first_activity.isoformat(),
                "last_activity": last_activity.isoformat(),
            },
            "behavior_patterns": {
                "event_types": dict(event_types.most_common()),
                "favorite_games": dict(game_preferences.most_common(10)),
                "preferred_commands": dict(command_usage.most_common(10)),
            },
            "time_patterns": {
                "peak_hours": dict(hour_pattern.most_common(5)),
                "active_days": dict(day_pattern.most_common()),
            },
            "session_patterns": {
                "total_sessions": len(user_sessions),
                "avg_session_duration": avg_session_duration,
                "session_durations": session_durations[-10:],  # Last 10 sessions
            },
        }

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        return {
            "analytics_status": "active",
            "current_user": self.current_user_id,
            "current_session": self.current_session_id,
            "data_summary": {
                "total_events": len(self.events),
                "total_sessions": len(self.sessions),
                "total_users": len(self.user_profiles),
                "data_retention": "30 days",
                "last_update": datetime.now().isoformat(),
            },
            "recent_activity": {
                "events_last_hour": len(
                    [
                        e
                        for e in self.events
                        if e.timestamp > datetime.now() - timedelta(hours=1)
                    ]
                ),
                "events_last_day": len(
                    [
                        e
                        for e in self.events
                        if e.timestamp > datetime.now() - timedelta(days=1)
                    ]
                ),
                "active_users_today": len(
                    set(
                        e.user_id
                        for e in self.events
                        if e.timestamp > datetime.now() - timedelta(days=1)
                    )
                ),
            },
        }

    def _save_data(self):
        """Save analytics data to disk"""
        try:
            # Save events
            events_data = {"timestamp": datetime.now().isoformat(), "events": []}

            for event in self.events:
                events_data["events"].append(
                    {
                        "event_id": event.event_id,
                        "session_id": event.session_id,
                        "user_id": event.user_id,
                        "event_type": event.event_type.value,
                        "timestamp": event.timestamp.isoformat(),
                        "game_name": event.game_name,
                        "command": event.command,
                        "parameters": event.parameters,
                        "success": event.success,
                        "execution_time": event.execution_time,
                        "error_message": event.error_message,
                        "metadata": event.metadata,
                    }
                )

            with open(self.events_file, "w") as f:
                json.dump(events_data, f, indent=2)

            # Save sessions
            sessions_data = {"timestamp": datetime.now().isoformat(), "sessions": {}}

            for session_id, session in self.sessions.items():
                sessions_data["sessions"][session_id] = {
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "start_time": session.start_time.isoformat(),
                    "end_time": (
                        session.end_time.isoformat() if session.end_time else None
                    ),
                    "total_events": session.total_events,
                    "unique_games": list(session.unique_games),
                    "commands_used": list(session.commands_used),
                    "total_execution_time": session.total_execution_time,
                    "errors_count": session.errors_count,
                    "session_duration": session.session_duration,
                    "user_segment": (
                        session.user_segment.value if session.user_segment else None
                    ),
                }

            with open(self.sessions_file, "w") as f:
                json.dump(sessions_data, f, indent=2)

            # Save user profiles
            profiles_data = {"timestamp": datetime.now().isoformat(), "profiles": {}}

            for user_id, profile in self.user_profiles.items():
                profiles_data["profiles"][user_id] = {
                    "user_id": profile.user_id,
                    "first_seen": profile.first_seen.isoformat(),
                    "last_seen": profile.last_seen.isoformat(),
                    "total_sessions": profile.total_sessions,
                    "total_events": profile.total_events,
                    "favorite_games": profile.favorite_games,
                    "preferred_commands": profile.preferred_commands,
                    "avg_session_duration": profile.avg_session_duration,
                    "user_segment": profile.user_segment.value,
                    "behavior_patterns": profile.behavior_patterns,
                    "preferences": profile.preferences,
                }

            with open(self.profiles_file, "w") as f:
                json.dump(profiles_data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Could not save analytics data: {e}")


# ===================================================================
# Global Usage Analytics Instance
# ===================================================================

# Create a global instance for easy use
_global_analytics: Optional[UsageAnalytics] = None


def get_usage_analytics() -> UsageAnalytics:
    """Get or create global usage analytics instance"""
    global _global_analytics
    if _global_analytics is None:
        _global_analytics = UsageAnalytics()
    return _global_analytics


def track_usage(event_type: EventType, **kwargs):
    """Track usage event using global analytics"""
    return get_usage_analytics().track_event(event_type, **kwargs)


# ===================================================================
# Example Usage
# ===================================================================

if __name__ == "__main__":
    # Create analytics
    analytics = UsageAnalytics()

    # Track some sample events
    analytics.track_event(
        event_type=EventType.GAME_ANALYSIS,
        success=True,
        execution_time=2.5,
        game_name="Hollow Knight",
        command="analyze",
        parameters={"type": "comprehensive"},
    )

    analytics.track_event(
        event_type=EventType.BATCH_ANALYSIS,
        success=True,
        execution_time=15.2,
        command="batch_analyze",
        parameters={"games": ["INSIDE", "Celeste", "Moving Out"]},
    )

    # Get statistics
    stats = analytics.get_usage_statistics("7d")
    print("Usage Statistics:", json.dumps(asdict(stats), indent=2, default=str))

    # Get user insights
    insights = analytics.get_user_insights()
    print("\nUser Insights:", json.dumps(insights, indent=2, default=str))

    # End session
    analytics.end_session()
