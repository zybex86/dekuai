"""
Batch Processing Manager for AutoGen DekuDeals Analysis System.

This module provides batch processing capabilities for analyzing multiple games
concurrently with intelligent resource management and progress tracking.

Author: AutoGen DekuDeals Team
Phase: 6.2 - Batch Processing & Scaling
"""

import asyncio
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Any, Dict, List, Optional, Callable

logger = logging.getLogger(__name__)


class BatchStatus(Enum):
    """Status of batch analysis operation."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Priority(Enum):
    """Task priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class BatchTask:
    """Individual game analysis task within a batch."""

    task_id: str
    game_name: str
    analysis_type: str = "comprehensive"
    priority: Priority = Priority.NORMAL
    status: BatchStatus = BatchStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def duration(self) -> Optional[float]:
        """Get task duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@dataclass
class BatchSession:
    """Batch analysis session containing multiple tasks."""

    batch_id: str
    batch_name: str
    tasks: List[BatchTask] = field(default_factory=list)
    status: BatchStatus = BatchStatus.PENDING
    max_concurrent: int = 3
    rate_limit: float = 1.0  # requests per second
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress_callback: Optional[Callable] = None

    @property
    def total_tasks(self) -> int:
        """Total number of tasks in batch."""
        return len(self.tasks)

    @property
    def completed_tasks(self) -> int:
        """Number of completed tasks."""
        return len([t for t in self.tasks if t.status == BatchStatus.COMPLETED])

    @property
    def failed_tasks(self) -> int:
        """Number of failed tasks."""
        return len([t for t in self.tasks if t.status == BatchStatus.FAILED])

    @property
    def progress_percentage(self) -> float:
        """Progress as percentage (0-100)."""
        if self.total_tasks == 0:
            return 0.0
        finished = self.completed_tasks + self.failed_tasks
        return (finished / self.total_tasks) * 100

    @property
    def duration(self) -> Optional[float]:
        """Get batch duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class BatchAnalysisManager:
    """
    Advanced batch processing manager for game analysis.

    Features:
    - Concurrent processing with configurable limits
    - Rate limiting to prevent server overload
    - Progress tracking with callbacks
    - Task prioritization and queue management
    - Error handling and retry mechanisms
    """

    def __init__(self, max_concurrent: int = 3, rate_limit: float = 1.0):
        """
        Initialize batch analysis manager.

        Args:
            max_concurrent: Maximum number of concurrent analysis tasks
            rate_limit: Maximum requests per second to prevent overload
        """
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit
        self.active_sessions: Dict[str, BatchSession] = {}
        self.completed_sessions: Dict[str, BatchSession] = {}
        self._lock = Lock()
        self._request_times = []

        logger.info(
            f"✅ BatchAnalysisManager initialized: "
            f"max_concurrent={max_concurrent}, rate_limit={rate_limit}/s"
        )

    def create_batch_session(
        self,
        game_names: List[str],
        analysis_type: str = "comprehensive",
        batch_name: Optional[str] = None,
        max_concurrent: Optional[int] = None,
        progress_callback: Optional[Callable] = None,
    ) -> str:
        """
        Create new batch analysis session.

        Args:
            game_names: List of game names to analyze
            analysis_type: Type of analysis (comprehensive, quick)
            batch_name: Optional custom name for the batch
            max_concurrent: Override default concurrency limit
            progress_callback: Function to call with progress updates

        Returns:
            str: Unique batch ID
        """
        batch_id = str(uuid.uuid4())[:8]
        if not batch_name:
            batch_name = (
                f"Batch_{len(game_names)}games_{datetime.now().strftime('%H%M%S')}"
            )

        # Create tasks
        tasks = []
        for i, game_name in enumerate(game_names):
            task = BatchTask(
                task_id=f"{batch_id}_task_{i+1}",
                game_name=game_name,
                analysis_type=analysis_type,
                priority=Priority.NORMAL,
            )
            tasks.append(task)

        # Create session
        session = BatchSession(
            batch_id=batch_id,
            batch_name=batch_name,
            tasks=tasks,
            max_concurrent=max_concurrent or self.max_concurrent,
            rate_limit=self.rate_limit,
            progress_callback=progress_callback,
        )

        with self._lock:
            self.active_sessions[batch_id] = session

        logger.info(
            f"🎯 Created batch session '{batch_name}' ({batch_id}): "
            f"{len(game_names)} games, {analysis_type} analysis"
        )

        return batch_id

    def start_batch_analysis(self, batch_id: str) -> bool:
        """
        Start batch analysis for given session.

        Args:
            batch_id: ID of batch session to start

        Returns:
            bool: True if started successfully, False otherwise
        """
        with self._lock:
            if batch_id not in self.active_sessions:
                logger.error(f"❌ Batch session {batch_id} not found")
                return False

            session = self.active_sessions[batch_id]
            if session.status != BatchStatus.PENDING:
                logger.error(f"❌ Batch {batch_id} already started or completed")
                return False

            session.status = BatchStatus.RUNNING
            session.start_time = datetime.now()

        logger.info(f"🚀 Starting batch analysis for session {batch_id}")

        # Run batch analysis in thread pool
        try:
            self._execute_batch_concurrent(session)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start batch {batch_id}: {e}")
            session.status = BatchStatus.FAILED
            return False

    def _execute_batch_concurrent(self, session: BatchSession) -> None:
        """Execute batch analysis with concurrent processing."""
        from agent_tools import generate_quick_game_opinion

        # Create analysis function based on type
        if session.tasks[0].analysis_type == "comprehensive":

            def analyze_game(game_name: str) -> Dict[str, Any]:
                # Import here to avoid circular import
                from enhanced_cli import EnhancedCLI

                cli = EnhancedCLI()
                return cli.analyze_game_with_progress(game_name, "comprehensive")

        else:  # quick

            def analyze_game(game_name: str) -> Dict[str, Any]:
                return generate_quick_game_opinion(game_name)

        # Process tasks with thread pool
        with ThreadPoolExecutor(max_workers=session.max_concurrent) as executor:
            # Submit all tasks
            future_to_task = {}
            for task in session.tasks:
                if session.status == BatchStatus.CANCELLED:
                    break

                # Rate limiting
                self._wait_for_rate_limit()

                future = executor.submit(self._execute_task, task, analyze_game)
                future_to_task[future] = task

            # Process completed tasks
            for future in as_completed(future_to_task):
                task = future_to_task[future]

                try:
                    result = future.result()
                    task.result = result
                    task.status = BatchStatus.COMPLETED
                    task.end_time = datetime.now()

                    logger.info(f"✅ Task completed: {task.game_name}")

                except Exception as e:
                    task.error = str(e)
                    task.status = BatchStatus.FAILED
                    task.end_time = datetime.now()

                    logger.error(f"❌ Task failed: {task.game_name} - {e}")

                # Call progress callback
                if session.progress_callback:
                    try:
                        session.progress_callback(session)
                    except Exception as e:
                        logger.warning(f"Progress callback error: {e}")

        # Finalize session
        session.end_time = datetime.now()
        session.status = (
            BatchStatus.COMPLETED if session.failed_tasks == 0 else BatchStatus.FAILED
        )

        # Move to completed sessions
        with self._lock:
            if session.batch_id in self.active_sessions:
                del self.active_sessions[session.batch_id]
            self.completed_sessions[session.batch_id] = session

        logger.info(
            f"🎉 Batch analysis completed: {session.batch_name} - "
            f"{session.completed_tasks}/{session.total_tasks} successful "
            f"({session.duration:.1f}s)"
        )

    def _execute_task(self, task: BatchTask, analyze_func: Callable) -> Dict[str, Any]:
        """Execute individual analysis task."""
        task.status = BatchStatus.RUNNING
        task.start_time = datetime.now()

        logger.info(f"🔄 Starting analysis: {task.game_name}")

        try:
            result = analyze_func(task.game_name)
            return result
        except Exception as e:
            logger.error(f"❌ Analysis failed for {task.game_name}: {e}")
            raise

    def _wait_for_rate_limit(self) -> None:
        """Wait to respect rate limiting."""
        current_time = time.time()

        # Clean old requests (older than 1 second)
        self._request_times = [t for t in self._request_times if current_time - t < 1.0]

        # Check if we need to wait
        if len(self._request_times) >= self.rate_limit:
            sleep_time = 1.0 - (current_time - self._request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Record this request
        self._request_times.append(current_time)

    def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of batch analysis."""
        with self._lock:
            session = self.active_sessions.get(batch_id) or self.completed_sessions.get(
                batch_id
            )

        if not session:
            return None

        # Count task statuses
        status_counts = {}
        for status in BatchStatus:
            status_counts[status.value] = len(
                [t for t in session.tasks if t.status == status]
            )

        return {
            "batch_id": session.batch_id,
            "batch_name": session.batch_name,
            "status": session.status.value,
            "progress_percentage": session.progress_percentage,
            "total_tasks": session.total_tasks,
            "completed_tasks": session.completed_tasks,
            "failed_tasks": session.failed_tasks,
            "duration": session.duration,
            "status_breakdown": status_counts,
            "start_time": (
                session.start_time.isoformat() if session.start_time else None
            ),
            "end_time": session.end_time.isoformat() if session.end_time else None,
        }

    def cancel_batch(self, batch_id: str) -> bool:
        """Cancel running batch analysis."""
        with self._lock:
            if batch_id not in self.active_sessions:
                return False

            session = self.active_sessions[batch_id]
            if session.status != BatchStatus.RUNNING:
                return False

            session.status = BatchStatus.CANCELLED
            session.end_time = datetime.now()

        logger.info(f"⏹️ Cancelled batch analysis: {batch_id}")
        return True

    def list_active_batches(self) -> List[Dict[str, Any]]:
        """List all active batch sessions."""
        with self._lock:
            return [
                {
                    "batch_id": session.batch_id,
                    "batch_name": session.batch_name,
                    "status": session.status.value,
                    "progress": session.progress_percentage,
                    "games": [t.game_name for t in session.tasks],
                }
                for session in self.active_sessions.values()
            ]

    def get_batch_results(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get complete results from batch analysis."""
        with self._lock:
            session = self.completed_sessions.get(batch_id)

        if not session:
            return None

        results = {
            "batch_id": session.batch_id,
            "batch_name": session.batch_name,
            "status": session.status.value,
            "duration": session.duration,
            "summary": {
                "total_games": session.total_tasks,
                "successful": session.completed_tasks,
                "failed": session.failed_tasks,
                "success_rate": (
                    (session.completed_tasks / session.total_tasks) * 100
                    if session.total_tasks > 0
                    else 0
                ),
            },
            "results": [],
        }

        for task in session.tasks:
            task_result = {
                "game_name": task.game_name,
                "status": task.status.value,
                "duration": task.duration,
                "result": task.result if task.status == BatchStatus.COMPLETED else None,
                "error": task.error if task.status == BatchStatus.FAILED else None,
            }
            results["results"].append(task_result)

        return results


# Global batch manager instance
_batch_manager = BatchAnalysisManager()


def get_batch_manager() -> BatchAnalysisManager:
    """Get global batch manager instance."""
    return _batch_manager


def create_batch_analysis(
    game_names: List[str],
    analysis_type: str = "comprehensive",
    batch_name: Optional[str] = None,
) -> str:
    """Convenience function to create and start batch analysis."""
    manager = get_batch_manager()
    batch_id = manager.create_batch_session(game_names, analysis_type, batch_name)
    manager.start_batch_analysis(batch_id)
    return batch_id
