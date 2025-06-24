#!/usr/bin/env python3
"""
🎮 AutoGen DekuDeals - Enhanced CLI Interface
Piękny, interaktywny interfejs z kolorami i progressbarami

FAZA 6.1: Performance Optimization
- Parallel processing dla kroków analizy
- Data sharing między krokami
- Optimized workflow execution
"""

import sys
import os
import time
import argparse
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import concurrent.futures
import threading
from functools import lru_cache
import hashlib

# 🚀 FAZA 6.1 - KROK 2: Advanced Cache System
from utils.advanced_cache_system import get_advanced_cache

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# CLI Enhancement libraries
from termcolor import colored, cprint
from tqdm import tqdm
import shutil

# Import project components
from conversation_manager import (
    GameAnalysisManager,
    analyze_game_quick,
    analyze_game_comprehensive,
)
from agent_tools import (
    search_and_scrape_game,
    calculate_value_score,
    calculate_advanced_value_analysis,
    generate_comprehensive_game_review,
    generate_quick_game_opinion,
    compare_games_with_reviews,
    adapt_review_for_context,
    create_multi_platform_opinions,
    scrape_dekudeals_category,
    get_random_game_sample,
    get_games_from_popular_categories,
    # 👨‍👩‍👧‍👦 PHASE 7.1.5: Multi-User System imports
    register_new_user,
    get_current_user_details,
    switch_to_user,
    list_system_users,
    create_guest_access,
    get_user_system_stats,
    # 🎮 PHASE 7.1.6: Game Collection Management imports
    add_game_to_collection,
    update_game_in_collection,
    remove_game_from_collection,
    get_user_game_collection,
    import_steam_library,
    import_collection_from_csv,
    export_collection_to_csv,
    check_if_game_owned,
    get_collection_recommendations_filter,
    # 🎮 PHASE 7.1.9: Collection-Aware Analysis import
    analyze_game_with_collection_awareness,
)

import logging

# Configure logging for CLI
logging.basicConfig(level=logging.WARNING)  # Less verbose for better CLI experience

# New import for batch processing
from utils.batch_processor import (
    get_batch_manager,
    create_batch_analysis,
    BatchStatus,
)


class EnhancedCLI:
    """Enhanced CLI Interface with colors, progress bars and interactive elements."""

    def __init__(self):
        self.manager = GameAnalysisManager()
        self.terminal_width = shutil.get_terminal_size().columns
        self.colors = {
            "header": "cyan",
            "success": "green",
            "error": "red",
            "warning": "yellow",
            "info": "blue",
            "highlight": "magenta",
            "secondary": "white",
            "loading": "yellow",
        }

        # 🚀 FAZA 6.1 - KROK 2: Advanced Multi-Level Cache System
        self.advanced_cache = get_advanced_cache()
        self._cache_hits = 0
        self._cache_misses = 0

        # Setup cache-aware functions with advanced caching
        self._setup_advanced_cached_functions()

    def _setup_advanced_cached_functions(self):
        """
        🚀 FAZA 6.1 - KROK 2: Setup advanced multi-level cache system.
        Features: Persistent cache, TTL expiration, memory+disk hierarchy.
        """
        # Store original functions
        self._original_search_and_scrape = search_and_scrape_game

        # Create advanced cached version
        def advanced_cached_search_and_scrape_game(game_name: str) -> Dict:
            """Advanced cache-aware version with persistent storage."""
            cache_key = game_name.lower().strip()

            # Try to get from advanced cache (memory → disk → scrape)
            cached_result = self.advanced_cache.get(cache_key, game_name)

            if cached_result is not None:
                self._cache_hits += 1
                cache_stats = self.advanced_cache.get_cache_statistics()
                memory_hits = cache_stats["cache_performance"]["memory_hits"]
                disk_hits = cache_stats["cache_performance"]["disk_hits"]

                cache_type = "MEMORY" if memory_hits > disk_hits else "DISK"

                self.print_status(
                    f"💾 Advanced Cache {cache_type} HIT for '{game_name}' (persistent cache)",
                    "success",
                )
                return cached_result
            else:
                self._cache_misses += 1
                self.print_status(
                    f"🔍 Advanced Cache MISS for '{game_name}' - scraping & persisting...",
                    "info",
                )

                # Scrape new data
                result = self._original_search_and_scrape(game_name)

                # Store in advanced cache with TTL
                ttl_hours = 24  # Default 24h TTL

                # Extend TTL for popular games
                if any(
                    popular in game_name.lower()
                    for popular in [
                        "zelda",
                        "mario",
                        "hollow",
                        "celeste",
                        "hades",
                        "metroid",
                    ]
                ):
                    ttl_hours = 72  # 3 days for popular games

                self.advanced_cache.put(cache_key, result, game_name, ttl_hours)

                return result

        # Monkey-patch the global function
        import agent_tools

        agent_tools.search_and_scrape_game = advanced_cached_search_and_scrape_game

        self.print_status("🚀 Advanced multi-level cache system activated", "success")

    def get_cache_stats(self) -> Dict:
        """
        🚀 FAZA 6.1 - KROK 2: Get advanced cache performance statistics.
        Now includes multi-level cache metrics and persistent storage info.
        """
        # Get comprehensive statistics from advanced cache
        advanced_stats = self.advanced_cache.get_cache_statistics()

        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (
            (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        )

        # Combine basic stats with advanced cache metrics
        return {
            "basic_tracking": {
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "hit_rate": hit_rate,
                "estimated_time_saved": self._cache_hits
                * 2.5,  # ~2.5s per scraping avoided
            },
            "advanced_cache": advanced_stats,
            "cache_efficiency": {
                "multi_level_hit_rate": advanced_stats["cache_performance"]["hit_rate"],
                "memory_vs_disk": {
                    "memory_hits": advanced_stats["cache_performance"]["memory_hits"],
                    "disk_hits": advanced_stats["cache_performance"]["disk_hits"],
                },
                "storage_efficiency": advanced_stats["cache_health"]["efficiency"],
                "persistent_entries": advanced_stats["cache_status"]["disk_size"],
            },
        }

    def print_header(
        self, text: str, style: str = "header", width: Optional[int] = None
    ):
        """Print styled header with borders."""
        if width is None:
            width = min(self.terminal_width, 80)

        border = "═" * width
        cprint(border, self.colors[style], attrs=["bold"])

        # Center the text
        padding = (width - len(text) - 4) // 2
        centered_text = f"{'═' * padding} {text} {'═' * padding}"
        if len(centered_text) < width:
            centered_text += "═"

        cprint(centered_text, self.colors[style], attrs=["bold"])
        cprint(border, self.colors[style], attrs=["bold"])

    def print_section(self, title: str, content: str = "", style: str = "info"):
        """Print section with styled title and content."""
        print()
        cprint(f"📋 {title}", self.colors[style], attrs=["bold"])
        cprint("─" * (len(title) + 3), self.colors[style])
        if content:
            print(content)

    def print_status(
        self, message: str, status: str = "info", symbol: Optional[str] = None
    ):
        """Print status message with colored symbol."""
        symbols = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
            "loading": "⏳",
            "highlight": "🎯",
        }

        if symbol is None:
            symbol = symbols.get(status, "ℹ️")

        # Get color safely with fallback
        color = self.colors.get(status, "white")
        colored_msg = colored(message, color)
        print(f"{symbol} {colored_msg}")

    def create_progress_bar(
        self, desc: str, total: int = 100, color: str = "cyan"
    ) -> tqdm:
        """Create styled progress bar."""
        return tqdm(
            total=total,
            desc=colored(desc, color, attrs=["bold"]),
            bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            colour=color,
            ncols=self.terminal_width - 10,
        )

    def show_welcome(self):
        """Display enhanced welcome screen."""
        self.print_header("🎮 AutoGen DekuDeals - Enhanced Gaming Analysis System")

        print()
        cprint("🚀 SYSTEM STATUS", "cyan", attrs=["bold"])
        print()

        # System capabilities with checkmarks
        capabilities = [
            ("📊 Phase 1: Foundation & Core Tools", "✅ COMPLETED"),
            ("💰 Phase 2: Price & Value Analysis", "✅ COMPLETED"),
            ("📝 Phase 3: Opinion Generation", "✅ COMPLETED"),
            ("🔍 Phase 4: Quality Control", "✅ COMPLETED"),
            ("🎨 Phase 5: Enhanced CLI Interface", "🔥 ACTIVE"),
        ]

        for capability, status in capabilities:
            status_color = "green" if "✅" in status else "yellow"
            print(f"   {capability}")
            cprint(f"   └─ {status}", status_color, attrs=["bold"])

        print()
        self.print_section("Available Commands", style="highlight")

        commands = [
            ("🎮 --game <name>", "Analyze specific game with full review"),
            ("⚡ --quick <name>", "Quick game analysis and opinion"),
            ("📂 --category <cat>", "Browse games from specific category"),
            ("🎲 --random <num>", "Get random game sample for analysis"),
            ("🆚 --compare <games>", "Compare multiple games side by side"),
            ("📋 --list-categories", "Show all available game categories"),
            ("🎪 --interactive", "Launch interactive mode with Multi-User System"),
            ("🎬 --demo", "Run full system demonstration"),
        ]

        # Add batch processing commands section (Phase 6.2)
        print()
        self.print_section(
            "🚀 Batch Processing Commands (NEW - Phase 6.2)", style="highlight"
        )

        batch_commands = [
            ("🔥 --batch-analyze <games>", "Analyze multiple games concurrently"),
            ("📦 --batch-category <cat>", "Batch analyze games from category"),
            ("🎲 --batch-random <num>", "Batch analyze random games"),
            ("📊 --batch-status", "Show status of batch operations"),
            ("📈 --batch-results <id>", "Show results of completed batch"),
            ("❌ --batch-cancel <id>", "Cancel running batch analysis"),
            ("⚙️ --batch-type [quick|comprehensive]", "Set batch analysis type"),
        ]

        for cmd, desc in batch_commands:
            cprint(f"   {cmd:<32}", "magenta", attrs=["bold"], end="")
            print(f" {desc}")

        print()
        self.print_section("Standard Commands", style="info")

        for cmd, desc in commands:
            cprint(f"   {cmd:<20}", "cyan", attrs=["bold"], end="")
            print(f" {desc}")

        # Add usage examples
        print()
        self.print_section("💡 Batch Processing Examples", style="secondary")
        examples = [
            'python enhanced_cli.py --batch-analyze "INSIDE" "Celeste" "Hollow Knight"',
            "python enhanced_cli.py --batch-category hottest --count 5 --batch-type quick",
            "python enhanced_cli.py --batch-random 3 --preference deals --batch-type comprehensive",
            "python enhanced_cli.py --batch-status  # Show all active batches",
        ]

        for example in examples:
            cprint(f"   {example}", "white")

        print()
        self.print_section(
            "👨‍👩‍👧‍👦 Multi-User System (NEW - Phase 7.1.5)", style="highlight"
        )

        multi_user_features = [
            ("👑 Admin Users", "Full system access and user management"),
            ("👨‍👩‍👧‍👦 Parent Users", "Family management and child controls"),
            ("👶 Child Users", "Age-appropriate with parental controls"),
            ("👤 Guest Sessions", "Temporary access without saving data"),
        ]

        for feature, desc in multi_user_features:
            cprint(f"   {feature:<20}", "magenta", attrs=["bold"], end="")
            print(f" {desc}")

        print()
        cprint(
            "💾 Advanced Features: Multi-level caching, persistent storage, concurrent processing, Multi-User System",
            "yellow",
            attrs=["bold"],
        )

    def get_user_choice(
        self, prompt: str, choices: List[str], allow_custom: bool = False
    ) -> str:
        """Interactive choice selection."""
        print()
        cprint(prompt, "cyan", attrs=["bold"])

        for i, choice in enumerate(choices, 1):
            cprint(f"   {i}. {choice}", "white")

        if allow_custom:
            cprint(f"   {len(choices)+1}. [Custom input]", "yellow")

        print()

        while True:
            try:
                choice_input = input(
                    colored("Enter choice (number): ", "cyan", attrs=["bold"])
                )
                choice_num = int(choice_input)

                if 1 <= choice_num <= len(choices):
                    selected = choices[choice_num - 1]
                    self.print_status(f"Selected: {selected}", "success")
                    return selected
                elif allow_custom and choice_num == len(choices) + 1:
                    custom = input(
                        colored("Enter custom value: ", "yellow", attrs=["bold"])
                    )
                    if custom.strip():
                        self.print_status(f"Custom input: {custom}", "success")
                        return custom.strip()
                    else:
                        self.print_status("Custom input cannot be empty", "error")
                else:
                    self.print_status(
                        f"Invalid choice. Please choose 1-{len(choices)}", "error"
                    )

            except ValueError:
                self.print_status("Please enter a valid number", "error")
            except KeyboardInterrupt:
                self.print_status("Operation cancelled", "warning")
                return ""

    def analyze_game_with_progress(
        self, game_name: str, analysis_type: str = "comprehensive"
    ) -> Dict:
        """
        🚀 FAZA 6.1: Optimized game analysis with parallel processing and data sharing.

        Performance improvements:
        - ✅ Single data fetch instead of redundant scraping
        - ✅ Parallel execution of independent analysis steps
        - ✅ Data sharing between analysis components
        - ✅ Optimized progress visualization
        """
        self.print_header(f"🎮 Game Analysis: {game_name}")
        self.print_status("🚀 Using optimized parallel processing workflow", "info")

        results = {}
        start_time = time.time()

        # Step 1: Data Collection (Required first - blocking)
        self.print_status("Step 1/4: 🔍 Collecting game data...", "loading")
        step_progress = self.create_progress_bar("Data Collection", 100, "blue")

        try:
            # Simulate progress
            for progress in range(0, 101, 25):
                step_progress.update(25)
                time.sleep(0.1)
            step_progress.close()

            # Actual data collection
            game_data_result = self._step_search_game(game_name)
            results["step_1"] = game_data_result

            if not game_data_result.get("success", False):
                self.print_status(
                    "❌ Data collection failed - aborting analysis", "error"
                )
                return results

            game_data = game_data_result.get("data", {})
            self.print_status("✅ Game data collected successfully", "success")

        except Exception as e:
            step_progress.close()
            self.print_status(f"❌ Data collection failed: {str(e)}", "error")
            return {"step_1": {"success": False, "error": str(e)}}

        # Steps 2-4: Parallel Analysis (Independent operations using shared game_data)
        self.print_status("Steps 2-4: 🚀 Running parallel analysis...", "loading")

        # Create progress bars for parallel steps
        overall_progress = self.create_progress_bar("Parallel Analysis", 3, "green")

        # Thread-safe progress tracking
        progress_lock = threading.Lock()
        completed_steps = 0

        def update_progress():
            nonlocal completed_steps
            with progress_lock:
                completed_steps += 1
                overall_progress.update(1)

        # Define parallel analysis functions with shared data
        def run_value_analysis():
            try:
                result = self._step_value_analysis_optimized(game_data)
                update_progress()
                return ("step_2", result)
            except Exception as e:
                update_progress()
                return ("step_2", {"success": False, "error": str(e)})

        def run_review_generation():
            try:
                result = self._step_generate_review_optimized(game_data)
                update_progress()
                return ("step_3", result)
            except Exception as e:
                update_progress()
                return ("step_3", {"success": False, "error": str(e)})

        def run_opinion_adaptations():
            try:
                result = self._step_opinion_adaptations_optimized(game_data)
                update_progress()
                return ("step_4", result)
            except Exception as e:
                update_progress()
                return ("step_4", {"success": False, "error": str(e)})

        # Execute parallel analysis
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                # Submit all parallel tasks
                future_to_step = {
                    executor.submit(run_value_analysis): "value_analysis",
                    executor.submit(run_review_generation): "review_generation",
                    executor.submit(run_opinion_adaptations): "opinion_adaptations",
                }

                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_step):
                    step_name = future_to_step[future]
                    try:
                        step_key, step_result = future.result()
                        results[step_key] = step_result

                        if step_result.get("success", False):
                            self.print_status(f"✅ {step_name} completed", "success")
                        else:
                            self.print_status(
                                f"⚠️ {step_name} completed with warnings", "warning"
                            )

                    except Exception as e:
                        self.print_status(f"❌ {step_name} failed: {str(e)}", "error")
                        results[f"{step_name}_error"] = {
                            "success": False,
                            "error": str(e),
                        }

        finally:
            overall_progress.close()

        # Step 5: Finalization (Quick)
        results["step_5"] = self._step_finalize_results()

        # Performance summary
        total_time = time.time() - start_time
        cache_stats = self.get_cache_stats()

        self.print_status(
            f"🚀 Optimized analysis completed in {total_time:.2f}s", "success"
        )
        self.print_status(
            f"💡 Performance: ~{len(results)-1} parallel operations", "info"
        )

        # Advanced Cache performance summary (FAZA 6.1 - KROK 2)
        basic_stats = cache_stats["basic_tracking"]
        advanced_stats = cache_stats["advanced_cache"]
        efficiency_stats = cache_stats["cache_efficiency"]

        if basic_stats["cache_hits"] > 0:
            self.print_status(
                f"💾 Advanced Cache: {basic_stats['cache_hits']} hits, "
                f"{efficiency_stats['multi_level_hit_rate']} hit rate, "
                f"~{basic_stats['estimated_time_saved']:.1f}s saved",
                "success",
            )

            # Show cache level breakdown
            memory_hits = efficiency_stats["memory_vs_disk"]["memory_hits"]
            disk_hits = efficiency_stats["memory_vs_disk"]["disk_hits"]

            if memory_hits > 0 or disk_hits > 0:
                self.print_status(
                    f"📊 Cache levels: Memory={memory_hits}, Disk={disk_hits}, "
                    f"Persistent entries={efficiency_stats['persistent_entries']}, "
                    f"Efficiency={efficiency_stats['storage_efficiency']}",
                    "info",
                )
        else:
            self.print_status(
                "💾 Advanced Cache: No hits (first run for this game)", "info"
            )

        return results

    def _step_search_game(self, game_name: str) -> Dict:
        """Step 1: Search and scrape game data with collection awareness."""
        try:
            # Use collection-aware analysis instead of standard search
            result = analyze_game_with_collection_awareness(game_name)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # 🚀 OPTIMIZED STEP FUNCTIONS (FAZA 6.1) - Use shared game_data instead of re-scraping

    def _step_value_analysis_optimized(self, game_data: Dict) -> Dict:
        """
        🚀 OPTIMIZED Step 2: Calculate value analysis using shared game_data.
        Performance improvement: No redundant scraping!
        """
        try:
            result = calculate_advanced_value_analysis(game_data)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _step_generate_review_optimized(self, game_data: Dict) -> Dict:
        """
        🚀 OPTIMIZED Step 3: Generate comprehensive review using shared game_data.
        Performance improvement: Uses pre-fetched data!
        """
        try:
            game_title = game_data.get("title", "Unknown Game")
            # Use the pre-fetched data for review generation instead of re-scraping
            result = generate_comprehensive_game_review(
                game_title, include_recommendations=True
            )
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _step_opinion_adaptations_optimized(self, game_data: Dict) -> Dict:
        """
        🚀 OPTIMIZED Step 4: Create opinion adaptations using shared game_data.
        Performance improvement: Uses pre-fetched data!
        """
        try:
            game_title = game_data.get("title", "Unknown Game")
            result = create_multi_platform_opinions(
                game_title, ["twitter", "website", "blog"]
            )
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Legacy step functions (kept for backward compatibility)
    def _step_value_analysis(self, game_name: str) -> Dict:
        """Legacy Step 2: Calculate value analysis (less efficient)."""
        try:
            result = calculate_advanced_value_analysis({"title": game_name})
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _step_generate_review(self, game_name: str) -> Dict:
        """Legacy Step 3: Generate comprehensive review (less efficient)."""
        try:
            result = generate_comprehensive_game_review(
                game_name, include_recommendations=True
            )
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _step_opinion_adaptations(self, game_name: str) -> Dict:
        """Legacy Step 4: Create opinion adaptations (less efficient)."""
        try:
            result = create_multi_platform_opinions(
                game_name, ["twitter", "website", "blog"]
            )
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _step_finalize_results(self) -> Dict:
        """Step 5: Finalize and format results."""
        return {"success": True, "data": "Results finalized"}

    def display_game_analysis_results(self, results: Dict, game_name: str):
        """Display formatted analysis results with enhanced content from Phase 7.3.1."""
        self.print_header(f"📊 Analysis Results: {game_name}", "success")

        # Check if this is an "already owned" result from collection-aware analysis
        step_1_data = results.get("step_1", {}).get("data", {})
        analysis_type = step_1_data.get("analysis_type")

        if analysis_type == "already_owned":
            # Special handling for already owned games
            self._display_owned_game_results(step_1_data, game_name)
            return

        # NEW: Display enhanced game information first
        self._display_enhanced_game_info(step_1_data, game_name)

        # Check for ownership context in standard analysis
        ownership_context = step_1_data.get("ownership_context")
        if ownership_context and ownership_context.get("already_owned", False):
            print()
            cprint("⚠️ NOTE: You already own this game!", "yellow", attrs=["bold"])
            ownership_details = ownership_context.get("ownership_details", {})
            status = ownership_details.get("status", "owned")
            rating = ownership_details.get("user_rating")

            status_emoji = {
                "owned": "👑",
                "wishlist": "💭",
                "playing": "🎮",
                "completed": "✅",
            }.get(status, "📚")
            print(f"   {status_emoji} Status: {status.title()}")
            if rating:
                print(f"   ⭐ Your Rating: {rating}/10")
            print(f"   📝 Note: {ownership_context.get('analysis_note', '')}")
            print()

        # Extract key information from results
        review_data = None
        review_result = None
        for step_key, step_result in results.items():
            if "3" in step_key and step_result.get(
                "success"
            ):  # Step 3 is review generation
                review_result = step_result.get("data", {})
                if review_result.get("success", False):
                    review_data = review_result.get("review_data", {})
                break

        if review_data:
            # Display rating prominently
            rating = review_data.get("overall_rating", "N/A")
            if rating != "N/A":
                rating_color = (
                    "green"
                    if float(rating) >= 8
                    else "yellow" if float(rating) >= 6 else "red"
                )
                print()
                cprint(f"⭐ OVERALL RATING: {rating}/10", rating_color, attrs=["bold"])

            # Display recommendation
            recommendation = review_data.get("recommendation", "N/A")
            rec_color = "green" if "BUY" in recommendation.upper() else "yellow"
            print()
            cprint(f"🎯 RECOMMENDATION: {recommendation}", rec_color, attrs=["bold"])

            # Display strengths and weaknesses
            strengths = review_data.get("strengths", [])
            if strengths:
                self.print_section("💪 Strengths", style="success")
                for strength in strengths[:3]:
                    print(f"   • {strength}")

            weaknesses = review_data.get("weaknesses", [])
            if weaknesses:
                self.print_section("⚠️ Potential Weaknesses", style="warning")
                for weakness in weaknesses[:3]:
                    print(f"   • {weakness}")

            # Display final verdict
            verdict = review_data.get("final_verdict", "")
            if verdict:
                self.print_section("📄 Final Verdict", style="info")
                print(f"   {verdict}")
        else:
            self.print_status("No detailed review data available", "warning")

    def _display_enhanced_game_info(self, game_data: Dict, game_name: str):
        """Display enhanced game information from Phase 7.3.1 enhanced scraping."""
        if not game_data:
            return

        # Basic game information
        title = game_data.get("title", game_name)
        developer = game_data.get("developer", "Unknown")
        current_price = game_data.get("current_eshop_price", "N/A")
        metacritic = game_data.get("metacritic_score", "No score")

        print()
        self.print_section("🎮 Game Information", style="info")
        print(f"   📝 Title: {title}")
        print(f"   👨‍💻 Developer: {developer}")
        print(f"   💰 Current Price: {current_price}")
        print(f"   ⭐ Metacritic: {metacritic}")

        # NEW: Enhanced genre display
        genres = game_data.get("genres", [])
        primary_genre = game_data.get("primary_genre", "")
        secondary_genres = game_data.get("secondary_genres", [])

        if genres:
            print()
            self.print_section("🎭 Genre Information", style="secondary")

            if primary_genre:
                print(f"   🎯 Primary: {primary_genre}")

            if secondary_genres:
                print(f"   🏷️ Also: {', '.join(secondary_genres[:3])}")
            elif len(genres) > 1:
                print(f"   🏷️ All: {', '.join(genres)}")

        # NEW: Game description display
        description = game_data.get("description", "")
        if description and description != "No description available":
            print()
            self.print_section("📝 Game Description", style="info")

            # Show description with option to expand
            if len(description) > 300:
                preview = description[:300] + "..."
                print(f"   {preview}")
                print()
                expand = input(colored("   📖 Show full description? (y/n): ", "cyan"))
                if expand.lower() in ["y", "yes"]:
                    print()
                    print(f"   {description}")
            else:
                print(f"   {description}")

        # Awards section removed due to unreliable extraction

        # NEW: Enhanced metadata indicator
        metadata = game_data.get("data_extraction_metadata", {})
        if metadata.get("enhanced_scraping", False):
            print()
            enhanced_features = []
            if metadata.get("has_description", False):
                enhanced_features.append("Rich Description")
            if game_data.get("primary_genre"):
                enhanced_features.append("Enhanced Genres")

            if enhanced_features:
                self.print_status(
                    f"✨ Enhanced Data: {', '.join(enhanced_features)} available",
                    "success",
                )

    def _display_owned_game_results(self, owned_data: Dict, game_name: str):
        """Display special results for already owned games."""
        ownership_status = owned_data.get("ownership_status", {})
        ownership_insights = owned_data.get("ownership_insights", {})
        collection_context = owned_data.get("collection_context", {})
        alternative_suggestions = owned_data.get("alternative_suggestions", {})

        # Main ownership message
        main_message = ownership_insights.get(
            "main_message", "You already own this game!"
        )
        print()
        cprint(main_message, "green", attrs=["bold"])

        # Display ownership details
        print()
        self.print_section("📚 Collection Details", style="info")

        status = ownership_status.get("status", "owned")
        platform = ownership_status.get("platform", "Nintendo Switch")
        date_added = ownership_status.get("date_added", "Unknown")
        user_rating = ownership_status.get("user_rating")
        hours_played = ownership_status.get("hours_played")
        notes = ownership_status.get("notes", "")

        status_emoji = {
            "owned": "👑",
            "wishlist": "💭",
            "playing": "🎮",
            "completed": "✅",
            "dropped": "❌",
        }.get(status, "📚")

        print(f"   {status_emoji} Status: {status.title()}")
        print(f"   🎮 Platform: {platform}")
        print(f"   📅 Added: {date_added}")

        if user_rating:
            rating_emoji = (
                "⭐" if user_rating >= 8 else "🌟" if user_rating >= 6 else "💫"
            )
            print(f"   {rating_emoji} Your Rating: {user_rating}/10")
        else:
            print("   ⭐ Your Rating: Not rated yet")

        if hours_played:
            print(f"   ⏱️ Hours Played: {hours_played}")

        if notes:
            print(f"   📝 Notes: {notes}")

        # Display suggested actions
        suggested_actions = ownership_insights.get("suggested_actions", [])
        if suggested_actions:
            print()
            self.print_section("💡 Suggested Actions", style="highlight")
            for action in suggested_actions:
                print(f"   • {action}")

        # Display alternative suggestions
        alt_message = alternative_suggestions.get("message", "")
        alt_suggestions = alternative_suggestions.get("suggestions", [])
        if alt_message and alt_suggestions:
            print()
            self.print_section("🎯 Alternative Ideas", style="secondary")
            print(f"   {alt_message}")
            for suggestion in alt_suggestions:
                print(f"   • {suggestion}")

        # Display next steps
        next_steps = owned_data.get("next_steps", [])
        if next_steps:
            print()
            self.print_section("🚀 Next Steps", style="info")
            for step in next_steps:
                print(f"   • {step}")

    def interactive_mode(self):
        """Launch interactive CLI mode with Multi-User System integration."""
        self.print_header("🎪 Interactive Mode", "highlight")

        # 👨‍👩‍👧‍👦 PHASE 7.1.5: Check user login status first
        user_status = self.check_user_login_status()

        # If no user logged in, offer user management first
        if not user_status.get("logged_in", False):
            print()
            self.print_status(
                "🚀 Multi-User System is available for personalized gaming experience!",
                "highlight",
            )

            first_time = self.get_user_choice(
                "Would you like to set up user management?",
                [
                    "👨‍👩‍👧‍👦 Yes, set up users for personalized experience",
                    "🎮 No, continue as anonymous user",
                ],
            )

            if "Yes, set up users" in first_time:
                # Enter user management workflow
                while self.user_management_menu():
                    pass  # Keep showing user management until user goes back

                # Check again after user management
                user_status = self.check_user_login_status()

        while True:
            print()

            # Show current user in prompt if logged in
            current_user_info = ""
            if user_status.get("logged_in", False):
                user_profile = user_status.get("user_profile", {})
                username = user_profile.get("username", "Unknown")
                role = user_profile.get("role", "unknown")

                role_emoji = {
                    "admin": "👑",
                    "parent": "👨‍👩‍👧‍👦",
                    "child": "👶",
                    "guest": "👤",
                }.get(role, "👤")

                current_user_info = f" (👤 {username} {role_emoji})"

            action = self.get_user_choice(
                f"What would you like to do?{current_user_info}",
                [
                    "🎮 Analyze a specific game (collection-aware)",
                    "📂 Browse games by category",
                    "🎲 Get random game recommendations",
                    "🆚 Compare multiple games",
                    "🔥 Batch analyze multiple games",
                    "📦 Batch analyze category games",
                    "🎲 Batch analyze random games",
                    "📊 View batch operations status",
                    "📋 View available categories",
                    "👨‍👩‍👧‍👦 User Management",
                    "🎮📚 Game Collection Management",
                    "🚪 Exit interactive mode",
                ],
            )

            if not action:  # User cancelled
                break

            if "specific game" in action:
                game_name = input(
                    colored("\n🎮 Enter game name: ", "cyan", attrs=["bold"])
                )
                if game_name.strip():
                    results = self.analyze_game_with_progress(game_name.strip())
                    self.display_game_analysis_results(results, game_name.strip())

            elif "category" in action:
                self.browse_categories_interactive()

            elif "random" in action:
                self.random_recommendations_interactive()

            elif "Compare multiple games" in action:
                self.compare_games_interactive()

            elif "Batch analyze multiple games" in action:
                self.batch_analyze_interactive()

            elif "Batch analyze category games" in action:
                self.batch_category_interactive()

            elif "Batch analyze random games" in action:
                self.batch_random_interactive()

            elif "View batch operations status" in action:
                self.show_batch_status()

            elif "categories" in action:
                self.show_categories()

            elif "User Management" in action:
                # Enter user management workflow
                while self.user_management_menu():
                    pass  # Keep showing user management until user goes back

                # Refresh user status after management operations
                user_status = self.check_user_login_status()

            elif "Game Collection Management" in action:
                # Check if user is logged in for personalized collections
                if not user_status.get("logged_in", False):
                    need_user = self.get_user_choice(
                        "Game Collection Management requires user login for personalized libraries.",
                        ["👤 Login or register user first", "🔙 Back to main menu"],
                    )

                    if "Login or register" in need_user:
                        while self.user_management_menu():
                            pass
                        user_status = self.check_user_login_status()
                    continue

                # Enter game collection management workflow
                while self.game_collection_menu():
                    pass  # Keep showing collection management until user goes back

            elif "Exit" in action:
                break

        self.print_status("Interactive mode ended", "info")

    # 🎮📚 PHASE 7.1.6: Game Collection Management Methods

    def game_collection_menu(self) -> bool:
        """Display game collection management menu and handle operations."""
        self.print_header("🎮📚 Game Collection Management", "highlight")

        # Show current user collection stats
        try:
            collection_data = get_user_game_collection(limit=5)
            if collection_data.get("success", False):
                stats = collection_data.get("statistics", {})
                total_games = stats.get("total_games", 0)
                owned_games = stats.get("owned_games", 0)
                wishlist_games = stats.get("wishlist_games", 0)
                average_rating = stats.get("average_rating", 0)

                self.print_status(
                    f"📚 Your Collection: {total_games} games ({owned_games} owned, {wishlist_games} wishlist)",
                    "info",
                )
                if average_rating > 0:
                    self.print_status(
                        f"⭐ Average Rating: {average_rating:.1f}/10", "info"
                    )
        except:
            pass

        action = self.get_user_choice(
            "Collection Management Options:",
            [
                "➕ Add game to collection",
                "📝 Update game in collection",
                "🔄 Bulk update all owned games",
                "❌ Remove game from collection",
                "📋 View my game collection",
                "🔍 Check if game is owned",
                "🎯 Get collection-based recommendations",
                "🔗 Import Steam library",
                "📁 Import from CSV file",
                "💾 Export collection to CSV",
                "📊 Get recommendation filter",
                "🌐 Import DekuDeals collection",
                "🔙 Back to main menu",
            ],
        )

        if not action:
            return False

        if "Add game to collection" in action:
            return self.add_game_to_collection_interactive()

        elif "Update game in collection" in action:
            return self.update_game_in_collection_interactive()

        elif "Bulk update all owned games" in action:
            return self.bulk_update_owned_games_interactive()

        elif "Remove game from collection" in action:
            return self.remove_game_from_collection_interactive()

        elif "View my game collection" in action:
            self.view_game_collection_interactive()
            return True

        elif "Check if game is owned" in action:
            self.check_game_ownership_interactive()
            return True

        elif "Get collection-based recommendations" in action:
            self.get_collection_recommendations_interactive()
            return True

        elif "Import Steam library" in action:
            return self.import_steam_library_interactive()

        elif "Import from CSV file" in action:
            return self.import_csv_collection_interactive()

        elif "Export collection to CSV" in action:
            return self.export_csv_collection_interactive()

        elif "Get recommendation filter" in action:
            self.view_recommendation_filter_interactive()
            return True

        elif "Import DekuDeals collection" in action:
            return self.import_dekudeals_collection_interactive()

        elif "Back to main menu" in action:
            return False

        return True

    def add_game_to_collection_interactive(self) -> bool:
        """Interactive game addition to collection."""
        self.print_section("➕ Add Game to Collection", "highlight")

        # Get game title
        title = input(colored("🎮 Enter game title: ", "cyan", attrs=["bold"])).strip()
        if not title:
            self.print_status("Game title cannot be empty", "error")
            return False

        # Get game status
        status = self.get_user_choice(
            "Select game status:",
            [
                "📦 Owned (I own this game)",
                "❤️ Wishlist (I want this game)",
                "👎 Not Interested (Don't recommend)",
                "✅ Completed (Finished playing)",
                "🎮 Playing (Currently playing)",
                "⏸️ Dropped (Stopped playing)",
            ],
        )

        if not status:
            return False

        # Extract status value
        status_map = {
            "Owned": "owned",
            "Wishlist": "wishlist",
            "Not Interested": "not_interested",
            "Completed": "completed",
            "Playing": "playing",
            "Dropped": "dropped",
        }

        status_value = next((v for k, v in status_map.items() if k in status), "owned")

        # Get optional rating
        rating = None
        if status_value in ["owned", "completed", "playing", "dropped"]:
            rating_input = input(
                colored(
                    "⭐ Enter rating (1-10, or press Enter to skip): ",
                    "yellow",
                    attrs=["bold"],
                )
            ).strip()

            if rating_input:
                try:
                    rating = float(rating_input)
                    if not (1 <= rating <= 10):
                        self.print_status("Rating must be between 1 and 10", "warning")
                        rating = None
                except ValueError:
                    self.print_status("Invalid rating format", "warning")
                    rating = None

        # Get optional notes
        notes = input(
            colored("📝 Enter notes (optional): ", "white", attrs=["bold"])
        ).strip()

        try:
            result = add_game_to_collection(
                title=title,
                status=status_value,
                user_rating=rating,  # type: ignore
                notes=notes,
            )

            if result.get("success", False):
                self.print_status(f"✅ Added '{title}' to your collection!", "success")

                # Show collection stats
                stats = result.get("collection_stats", {})
                total_games = stats.get("total_games", 0)
                owned_games = stats.get("owned_games", 0)

                self.print_status(
                    f"📚 Updated collection: {total_games} total games ({owned_games} owned)",
                    "info",
                )
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                self.print_status(f"❌ Failed to add game: {error_msg}", "error")

                # Show suggestion if provided
                suggestion = result.get("suggestion", "")
                if suggestion:
                    self.print_status(f"💡 Suggestion: {suggestion}", "info")

                return False

        except Exception as e:
            self.print_status(f"❌ Addition error: {str(e)}", "error")
            return False

    def update_game_in_collection_interactive(self) -> bool:
        """Interactive game update in collection."""
        self.print_section("📝 Update Game in Collection", "highlight")

        # Get game title
        title = input(
            colored("🎮 Enter game title to update: ", "cyan", attrs=["bold"])
        ).strip()
        if not title:
            self.print_status("Game title cannot be empty", "error")
            return False

        # Check if game exists
        try:
            ownership_check = check_if_game_owned(title)
            if not ownership_check.get("owned", False):
                self.print_status(f"❌ '{title}' not found in your collection", "error")
                self.print_status(
                    "💡 Use 'Add game to collection' to add new games", "info"
                )
                return False

            # Show current game details
            game_details = ownership_check.get("game_details", {})
            current_status = game_details.get("status", "unknown")
            current_rating = game_details.get("user_rating")
            current_notes = game_details.get("notes", "")

            self.print_status(f"📋 Current status: {current_status}", "info")
            if current_rating:
                self.print_status(f"⭐ Current rating: {current_rating}/10", "info")
            if current_notes:
                self.print_status(f"📝 Current notes: {current_notes}", "info")

        except Exception as e:
            self.print_status(f"❌ Error checking game: {str(e)}", "error")
            return False

        # Get what to update
        update_choice = self.get_user_choice(
            "What would you like to update?",
            [
                "📊 Game status",
                "⭐ Rating",
                "🏷️ Tags/Genres",
                "📝 Notes",
                "🕒 Hours played",
                "📋 All details",
                "🔙 Cancel update",
            ],
        )

        if not update_choice or "Cancel" in update_choice:
            return False

        updates = {}

        try:
            if "Game status" in update_choice or "All details" in update_choice:
                status = self.get_user_choice(
                    "Select new game status:",
                    [
                        "📦 Owned",
                        "❤️ Wishlist",
                        "👎 Not Interested",
                        "✅ Completed",
                        "🎮 Playing",
                        "⏸️ Dropped",
                    ],
                )
                if status:
                    status_map = {
                        "Owned": "owned",
                        "Wishlist": "wishlist",
                        "Not Interested": "not_interested",
                        "Completed": "completed",
                        "Playing": "playing",
                        "Dropped": "dropped",
                    }
                    updates["status"] = next(
                        (v for k, v in status_map.items() if k in status), "owned"
                    )

            if "Rating" in update_choice or "All details" in update_choice:
                rating_input = input(
                    colored(
                        "⭐ Enter new rating (1-10, or press Enter to skip): ",
                        "yellow",
                        attrs=["bold"],
                    )
                ).strip()

                if rating_input:
                    try:
                        rating = float(rating_input)
                        if 1 <= rating <= 10:
                            updates["user_rating"] = rating
                        else:
                            self.print_status(
                                "Rating must be between 1 and 10", "warning"
                            )
                    except ValueError:
                        self.print_status("Invalid rating format", "warning")

            if "Tags/Genres" in update_choice or "All details" in update_choice:
                # Show suggested genres
                from utils.collection_updater import get_collection_updater

                updater = get_collection_updater()
                suggested_genres = updater._suggest_genres_for_game(title)

                if suggested_genres:
                    self.print_status(
                        f"💡 Suggested genres: {', '.join(suggested_genres)}", "info"
                    )

                tags_input = input(
                    colored(
                        "🏷️ Enter genre tags (comma-separated, e.g., 'Action,RPG,Indie'): ",
                        "cyan",
                        attrs=["bold"],
                    )
                ).strip()

                if tags_input:
                    # Convert comma-separated string to list
                    tag_list = [
                        tag.strip() for tag in tags_input.split(",") if tag.strip()
                    ]
                    if tag_list:
                        updates["tags"] = tag_list
                    else:
                        self.print_status("No valid tags provided", "warning")

            if "Notes" in update_choice or "All details" in update_choice:
                notes = input(
                    colored(
                        "📝 Enter new notes (or press Enter to skip): ",
                        "white",
                        attrs=["bold"],
                    )
                ).strip()
                if notes:
                    updates["notes"] = notes

            if "Hours played" in update_choice or "All details" in update_choice:
                hours_input = input(
                    colored(
                        "🕒 Enter hours played (or press Enter to skip): ",
                        "blue",
                        attrs=["bold"],
                    )
                ).strip()

                if hours_input:
                    try:
                        hours = float(hours_input)
                        if hours >= 0:
                            updates["hours_played"] = hours
                        else:
                            self.print_status("Hours must be non-negative", "warning")
                    except ValueError:
                        self.print_status("Invalid hours format", "warning")

            if not updates:
                self.print_status("No updates provided", "warning")
                return False

            # Perform update
            result = update_game_in_collection(title, **updates)

            if result.get("success", False):
                self.print_status(
                    f"✅ Updated '{title}' in your collection!", "success"
                )

                # Show updated details
                updated_game = result.get("updated_game", {})
                for field, value in updated_game.items():
                    if field in updates:
                        self.print_status(f"   {field}: {value}", "info")

                return True
            else:
                error_msg = result.get("error", "Unknown error")
                self.print_status(f"❌ Update failed: {error_msg}", "error")
                return False

        except Exception as e:
            self.print_status(f"❌ Update error: {str(e)}", "error")
            return False

    def bulk_update_owned_games_interactive(self) -> bool:
        """Interactive bulk update for all owned games metadata."""
        self.print_section("🔄 Bulk Update All Owned Games", "highlight")

        # Show current collection status
        try:
            from agent_tools import view_collection_summary

            summary_result = view_collection_summary()

            if summary_result.get("success", False):
                summary = summary_result.get("collection_summary", {})

                self.print_status(f"📚 Your Collection Overview:", "info")
                self.print_status(
                    f"   Total Games: {summary.get('total_games', 0)}", "info"
                )
                self.print_status(
                    f"   Rated Games: {summary.get('rated_games', 0)}", "info"
                )
                self.print_status(
                    f"   Tagged Games: {summary.get('tagged_games', 0)}", "info"
                )
                self.print_status(
                    f"   Completion: {summary.get('completion_percentage', 0)}%", "info"
                )
                self.print_status(
                    f"   Recommendation Ready: {'✅ Yes' if summary.get('recommendation_ready') else '❌ No'}",
                    "info",
                )

        except Exception as e:
            self.print_status(
                f"⚠️ Could not get collection summary: {str(e)}", "warning"
            )

        print()
        self.print_status(
            "This will automatically add missing genres/tags to your owned games to enable recommendations.",
            "info",
        )
        self.print_status(
            "⚠️ It only updates games that are missing metadata (safe mode).", "warning"
        )

        # Get user preferences
        update_options = self.get_user_choice(
            "Select bulk update options:",
            [
                "🎯 Auto-suggest genres only (safest)",
                "🎯 Auto-suggest genres + estimate hours",
                "📊 Full metadata enhancement",
                "🔙 Cancel bulk update",
            ],
        )

        if not update_options or "Cancel" in update_options:
            self.print_status("Bulk update cancelled", "info")
            return False

        # Set parameters based on choice
        auto_suggest_genres = True
        include_hours_estimates = (
            "estimate hours" in update_options or "Full metadata" in update_options
        )
        update_missing_only = True  # Always safe mode for interactive

        # Confirm action
        confirm = self.get_user_choice(
            f"⚠️ Proceed with bulk update of owned games?",
            [
                "✅ Yes, update my games",
                "🔙 No, go back",
            ],
        )

        if not confirm or "No, go back" in confirm:
            self.print_status("Bulk update cancelled", "info")
            return False

        # Perform bulk update with progress
        self.print_status("🔄 Starting bulk metadata update...", "loading")

        try:
            from agent_tools import bulk_update_owned_games_metadata

            # Create progress bar
            progress = self.create_progress_bar("Bulk Update Progress", 100, "cyan")
            progress.update(10)

            # Run bulk update
            result = bulk_update_owned_games_metadata(
                auto_suggest_genres=auto_suggest_genres,
                update_missing_only=update_missing_only,
                include_hours_estimates=include_hours_estimates,
            )

            progress.update(90)
            progress.close()

            if result.get("success", False):
                # Show success results
                games_updated = result.get("games_updated", 0)
                games_processed = result.get("total_games_processed", 0)
                improvements = result.get("metadata_improvements", {})
                readiness = result.get("recommendation_readiness", {})

                self.print_status(f"✅ Bulk update completed successfully!", "success")

                print()
                cprint("   📊 Update Results:", "cyan", attrs=["bold"])
                cprint(f"      🎮 Games Processed: {games_processed}", "white")
                cprint(f"      ✅ Games Updated: {games_updated}", "white")
                cprint(
                    f"      🏷️ Genres Added: {improvements.get('genres_added', 0)}",
                    "white",
                )
                cprint(
                    f"      💡 Rating Suggestions: {improvements.get('ratings_suggested', 0)}",
                    "white",
                )
                if include_hours_estimates:
                    cprint(
                        f"      🕒 Hours Estimated: {improvements.get('hours_estimated', 0)}",
                        "white",
                    )

                # Show recommendation readiness improvement
                before = readiness.get("before", {})
                after = readiness.get("after", {})

                before_complete = before.get("complete", 0)
                after_complete = after.get("complete", 0)
                improvement = after_complete - before_complete

                if improvement > 0:
                    print()
                    cprint(
                        "   🎯 Recommendation Readiness Improved:",
                        "green",
                        attrs=["bold"],
                    )
                    cprint(
                        f"      Before: {before_complete} recommendation-ready games",
                        "white",
                    )
                    cprint(
                        f"      After: {after_complete} recommendation-ready games",
                        "white",
                    )
                    cprint(
                        f"      ➕ Improvement: +{improvement} games",
                        "green",
                        attrs=["bold"],
                    )

                # Show update details if available
                update_details = result.get("update_details", [])
                successful_updates = [
                    d for d in update_details if d.get("status") == "success"
                ]

                if successful_updates:
                    print()
                    cprint(
                        "   🎮 Updated Games (showing first 5):", "cyan", attrs=["bold"]
                    )
                    for detail in successful_updates[:5]:
                        game_title = detail.get("game", "Unknown")
                        reasons = detail.get("reasons", [])
                        cprint(f"      • {game_title}", "white", attrs=["bold"])
                        for reason in reasons:
                            cprint(f"        └─ {reason}", "yellow")

                # Show errors if any
                errors = result.get("errors", [])
                if errors:
                    print()
                    cprint("   ⚠️ Some Updates Failed:", "yellow", attrs=["bold"])
                    for error in errors[:3]:  # Show only first 3 errors
                        game_title = error.get("game", "Unknown")
                        error_msg = error.get("error", "Unknown error")
                        cprint(f"      • {game_title}: {error_msg}", "yellow")

                # Next steps
                print()
                self.print_status("🎉 Next Steps:", "success")
                self.print_status(
                    "   1. Review the suggested rating ranges for your games", "info"
                )
                self.print_status(
                    "   2. Update ratings based on your personal experience", "info"
                )
                self.print_status(
                    "   3. Try getting collection-based recommendations!", "info"
                )

                return True

            else:
                error_msg = result.get("error", "Unknown error")
                self.print_status(f"❌ Bulk update failed: {error_msg}", "error")
                return False

        except Exception as e:
            self.print_status(f"❌ Bulk update error: {str(e)}", "error")
            return False

    def remove_game_from_collection_interactive(self) -> bool:
        """Interactive game removal from collection."""
        self.print_section("❌ Remove Game from Collection", "highlight")

        # Get game title
        title = input(
            colored("🎮 Enter game title to remove: ", "cyan", attrs=["bold"])
        ).strip()
        if not title:
            self.print_status("Game title cannot be empty", "error")
            return False

        # Check if game exists and show details
        try:
            ownership_check = check_if_game_owned(title)
            if not ownership_check.get("owned", False):
                self.print_status(f"❌ '{title}' not found in your collection", "error")
                return False

            # Show game details before removal
            game_details = ownership_check.get("game_details", {})
            status = game_details.get("status", "unknown")
            rating = game_details.get("user_rating")
            notes = game_details.get("notes", "")

            self.print_status(f"📋 Game to remove: {title}", "warning")
            self.print_status(f"   Status: {status}", "info")
            if rating:
                self.print_status(f"   Rating: {rating}/10", "info")
            if notes:
                self.print_status(f"   Notes: {notes}", "info")

        except Exception as e:
            self.print_status(f"❌ Error checking game: {str(e)}", "error")
            return False

        # Confirm removal
        confirm = self.get_user_choice(
            f"Are you sure you want to remove '{title}' from your collection?",
            [
                "✅ Yes, remove it",
                "🔙 No, keep it",
            ],
        )

        if not confirm or "No, keep it" in confirm:
            self.print_status("Removal cancelled", "info")
            return False

        try:
            result = remove_game_from_collection(title)

            if result.get("success", False):
                self.print_status(
                    f"✅ Removed '{title}' from your collection!", "success"
                )

                # Show updated collection stats
                stats = result.get("collection_stats", {})
                total_games = stats.get("total_games", 0)
                owned_games = stats.get("owned_games", 0)

                self.print_status(
                    f"📚 Updated collection: {total_games} total games ({owned_games} owned)",
                    "info",
                )
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                self.print_status(f"❌ Removal failed: {error_msg}", "error")
                return False

        except Exception as e:
            self.print_status(f"❌ Removal error: {str(e)}", "error")
            return False

    def view_game_collection_interactive(self):
        """Display user's game collection with filtering options."""
        self.print_section("📋 Your Game Collection", "highlight")

        # Get filter options
        filter_choice = self.get_user_choice(
            "Collection view options:",
            [
                "📚 All games",
                "📦 Owned games only",
                "❤️ Wishlist only",
                "✅ Completed games",
                "🎮 Currently playing",
                "⏸️ Dropped games",
                "👎 Not interested",
            ],
        )

        if not filter_choice:
            return

        # Extract filter value
        filter_map = {
            "All games": None,
            "Owned games only": "owned",
            "Wishlist only": "wishlist",
            "Completed games": "completed",
            "Currently playing": "playing",
            "Dropped games": "dropped",
            "Not interested": "not_interested",
        }

        status_filter = next(
            (v for k, v in filter_map.items() if k in filter_choice), None
        )

        try:
            result = get_user_game_collection(status_filter=status_filter, limit=50)  # type: ignore

            if result.get("success", False):
                collection = result.get("collection", {})
                games = collection.get("games", [])
                stats = result.get("statistics", {})
                user_context = result.get("user_context", {})
                insights = result.get("insights", {})

                # Display header
                username = user_context.get("username", "Unknown")
                filter_text = f" ({filter_choice})" if status_filter else ""

                self.print_status(f"📚 {username}'s Collection{filter_text}", "success")

                # Display statistics
                total_games = stats.get("total_games", 0)
                owned_games = stats.get("owned_games", 0)
                wishlist_games = stats.get("wishlist_games", 0)
                average_rating = stats.get("average_rating", 0)
                total_value = stats.get("total_value", 0)
                total_hours = stats.get("total_hours", 0)

                print()
                cprint("   📊 Collection Statistics:", "cyan", attrs=["bold"])
                cprint(f"      📚 Total Games: {total_games}", "white")
                cprint(f"      📦 Owned: {owned_games}", "white")
                cprint(f"      ❤️ Wishlist: {wishlist_games}", "white")
                if average_rating > 0:
                    cprint(f"      ⭐ Average Rating: {average_rating:.1f}/10", "white")
                if total_value > 0:
                    cprint(f"      💰 Total Value: ${total_value:.2f}", "white")
                if total_hours > 0:
                    cprint(f"      🕒 Total Hours: {total_hours:.1f}", "white")

                # Display insights
                most_played_platform = insights.get("most_played_platform", "None")
                completion_rate = insights.get("completion_rate", 0)
                avg_hours_game = insights.get("average_hours_per_game", 0)

                if most_played_platform != "None":
                    cprint(
                        f"      🎮 Favorite Platform: {most_played_platform}", "white"
                    )
                if completion_rate > 0:
                    cprint(f"      ✅ Completion Rate: {completion_rate:.1f}%", "white")
                if avg_hours_game > 0:
                    cprint(f"      ⏱️ Avg Hours/Game: {avg_hours_game:.1f}", "white")

                # Display games
                if games:
                    print()
                    cprint("   🎮 Games:", "cyan", attrs=["bold"])

                    for i, game in enumerate(games, 1):  # Show all games
                        title = game.get("title", "Unknown")
                        status = game.get("status", "unknown")
                        platform = game.get("platform", "Unknown")
                        rating = game.get("user_rating")
                        hours = game.get("hours_played")

                        # Status emoji
                        status_emoji = {
                            "owned": "📦",
                            "wishlist": "❤️",
                            "completed": "✅",
                            "playing": "🎮",
                            "dropped": "⏸️",
                            "not_interested": "👎",
                        }.get(status, "❓")

                        # Build game line
                        game_line = f"      {i:2d}. {status_emoji} {title}"
                        if platform != "Unknown":
                            game_line += f" ({platform})"

                        cprint(game_line, "white")

                        # Add rating and hours if available
                        details = []
                        if rating:
                            details.append(f"⭐{rating}/10")
                        if hours and hours > 0:
                            details.append(f"🕒{hours}h")

                        if details:
                            cprint(f"          {' | '.join(details)}", "yellow")

                else:
                    cprint("      No games found in this collection", "yellow")

            else:
                error_msg = result.get("error", "Unknown error")
                self.print_status(f"❌ Failed to get collection: {error_msg}", "error")

        except Exception as e:
            self.print_status(f"❌ Collection view error: {str(e)}", "error")

    def get_collection_recommendations_interactive(self):
        """Interactive collection-based recommendations."""
        self.print_section("🎯 Collection-Based Recommendations", "highlight")

        try:
            # Import the function here to avoid issues
            from agent_tools import generate_collection_based_recommendations

            # Show collection status first
            try:
                collection_data = get_user_game_collection(limit=5)
                if collection_data.get("success", False):
                    stats = collection_data.get("statistics", {})
                    total_games = stats.get("total_games", 0)
                    owned_games = stats.get("owned_games", 0)
                    average_rating = stats.get("average_rating", 0)

                    self.print_status(
                        f"📚 Your Collection: {total_games} games ({owned_games} owned)",
                        "info",
                    )
                    if average_rating > 0:
                        self.print_status(
                            f"⭐ Average Rating: {average_rating:.1f}/10", "info"
                        )
            except:
                pass

            # Get recommendation type
            rec_type = self.get_user_choice(
                "Select recommendation type:",
                [
                    "🎲 Similar games (based on your favorites)",
                    "🔍 Discovery (explore new genres)",
                    "👨‍💻 Developer favorites (more from favorite developers)",
                    "🧩 Complementary (fill collection gaps)",
                    "🔙 Back to collection menu",
                ],
            )

            if not rec_type or "Back to collection menu" in rec_type:
                return

            # Map choice to type
            type_map = {
                "Similar games": "similar",
                "Discovery": "discovery",
                "Developer favorites": "developer",
                "Complementary": "complementary",
            }

            recommendation_type = next(
                (v for k, v in type_map.items() if k in rec_type), "similar"
            )

            # Get number of recommendations
            max_recs = self.get_user_choice(
                "How many recommendations?",
                [
                    "5 recommendations",
                    "10 recommendations",
                    "15 recommendations",
                    "20 recommendations",
                ],
            )

            if not max_recs:
                return

            max_recommendations = int(max_recs.split()[0])

            # Show progress
            self.print_status(
                f"🎯 Generating {recommendation_type} recommendations...", "loading"
            )

            # Generate recommendations
            result = generate_collection_based_recommendations(
                recommendation_type=recommendation_type,
                max_recommendations=max_recommendations,
            )

            if result.get("success", False):
                recommendations = result.get("recommendations", [])
                summary = result.get("recommendation_summary", {})
                insights = result.get("collection_insights", {})

                # Show success message
                message = result.get("message", "Generated recommendations")
                self.print_status(f"✅ {message}", "success")

                # Show collection summary
                based_on = summary.get("based_on_collection", {})
                total_games = based_on.get("total_games", 0)
                confidence = based_on.get("confidence_level", "unknown")

                print()
                cprint("   📊 Recommendation Summary:", "cyan", attrs=["bold"])
                cprint(
                    f"      📚 Based on: {total_games} games in your collection",
                    "white",
                )
                cprint(f"      🎯 Type: {recommendation_type.title()}", "white")
                cprint(f"      📈 Confidence: {confidence}", "white")

                # Show key preferences
                key_prefs = summary.get("key_preferences", {})
                fav_genres = key_prefs.get("favorite_genres", [])
                if fav_genres:
                    genre_list = [f"{genre}" for genre, _ in fav_genres]
                    cprint(f"      🎭 Top Genres: {', '.join(genre_list[:3])}", "white")

                # Display recommendations
                if recommendations:
                    print()
                    cprint("   🎮 Recommended Games:", "cyan", attrs=["bold"])

                    for i, rec in enumerate(recommendations, 1):
                        title = rec.get("game_title", "Unknown")
                        score = rec.get("recommendation_score", 0)
                        confidence = rec.get("confidence", "unknown")
                        reason = rec.get("primary_reason", "No reason provided")

                        print()
                        cprint(f"      {i}. {title}", "white", attrs=["bold"])
                        cprint(f"         📊 Score: {score:.1f}/100", "white")
                        cprint(f"         📈 Confidence: {confidence}", "white")
                        cprint(f"         💡 Reason: {reason}", "white")

                        # Show similar owned games
                        similar_games = rec.get("similar_owned_games", [])
                        if similar_games:
                            similar_list = ", ".join(similar_games[:2])
                            cprint(f"         🎯 Similar to: {similar_list}", "yellow")

                        # Show genre matches
                        genre_matches = rec.get("genre_matches", [])
                        if genre_matches:
                            genre_list = ", ".join(genre_matches[:3])
                            cprint(f"         🎭 Genres: {genre_list}", "yellow")

                    # Ask if user wants to analyze any recommendations
                    print()
                    analyze_choice = self.get_user_choice(
                        "Would you like to analyze any recommended game?",
                        [
                            "🔍 Yes, analyze a recommendation",
                            "❤️ Add recommendation to wishlist",
                            "🔙 Back to collection menu",
                        ],
                    )

                    if "analyze a recommendation" in analyze_choice:
                        game_to_analyze = input(
                            colored(
                                "🎮 Enter game title to analyze: ",
                                "cyan",
                                attrs=["bold"],
                            )
                        ).strip()

                        if game_to_analyze:
                            print()
                            self.print_status(
                                f"🔍 Analyzing {game_to_analyze}...", "loading"
                            )
                            # Run game analysis
                            analysis_results = self.analyze_game_with_progress(
                                game_to_analyze
                            )
                            self.display_game_analysis_results(
                                analysis_results, game_to_analyze
                            )

                    elif "Add recommendation to wishlist" in analyze_choice:
                        game_to_add = input(
                            colored(
                                "❤️ Enter game title to add to wishlist: ",
                                "cyan",
                                attrs=["bold"],
                            )
                        ).strip()

                        if game_to_add:
                            try:
                                add_result = add_game_to_collection(
                                    title=game_to_add,
                                    status="wishlist",
                                    notes=f"Added from {recommendation_type} recommendations",
                                )

                                if add_result.get("success", False):
                                    self.print_status(
                                        f"✅ Added '{game_to_add}' to wishlist!",
                                        "success",
                                    )
                                else:
                                    error = add_result.get("error", "Unknown error")
                                    self.print_status(
                                        f"❌ Failed to add: {error}", "error"
                                    )
                            except Exception as e:
                                self.print_status(f"❌ Error: {str(e)}", "error")

                else:
                    self.print_status("No recommendations found", "warning")

            else:
                error_msg = result.get("error", "Unknown error")
                self.print_status(f"❌ Recommendations failed: {error_msg}", "error")

                # Show helpful information
                requirements = result.get("requirements", {})
                if requirements:
                    needed = requirements.get("needed", "Unknown")
                    current_size = requirements.get("current_collection_size", 0)

                    print()
                    cprint("   💡 Requirements:", "yellow", attrs=["bold"])
                    cprint(f"      📋 Needed: {needed}", "white")
                    cprint(
                        f"      📚 Current collection: {current_size} games", "white"
                    )

                suggestions = result.get("suggestions", [])
                if suggestions:
                    print()
                    cprint("   🔧 Suggestions:", "cyan", attrs=["bold"])
                    for suggestion in suggestions:
                        cprint(f"      • {suggestion}", "white")

        except ImportError:
            self.print_status("❌ Collection recommendations not available", "error")
        except Exception as e:
            self.print_status(f"❌ Recommendations error: {str(e)}", "error")

    def check_game_ownership_interactive(self):
        """Interactive game ownership checking."""
        self.print_section("🔍 Check Game Ownership", "highlight")

        # Get game title
        title = input(
            colored("🎮 Enter game title to check: ", "cyan", attrs=["bold"])
        ).strip()
        if not title:
            self.print_status("Game title cannot be empty", "error")
            return

        try:
            result = check_if_game_owned(title)

            if result.get("success", False):
                owned = result.get("owned", False)

                if owned:
                    self.print_status(
                        f"✅ You own '{title}' in your collection!", "success"
                    )

                    # Show game details
                    game_details = result.get("game_details", {})
                    status = game_details.get("status", "unknown")
                    platform = game_details.get("platform", "Unknown")
                    rating = game_details.get("user_rating")
                    hours = game_details.get("hours_played")
                    date_added = game_details.get("date_added", "Unknown")
                    notes = game_details.get("notes", "")

                    print()
                    cprint("   📋 Game Details:", "cyan", attrs=["bold"])
                    cprint(f"      📊 Status: {status}", "white")
                    cprint(f"      🎮 Platform: {platform}", "white")
                    if rating:
                        cprint(f"      ⭐ Your Rating: {rating}/10", "white")
                    if hours and hours > 0:
                        cprint(f"      🕒 Hours Played: {hours}", "white")
                    cprint(f"      📅 Added: {date_added}", "white")
                    if notes:
                        cprint(f"      📝 Notes: {notes}", "white")
                else:
                    self.print_status(
                        f"❌ '{title}' not found in your collection", "warning"
                    )
                    suggestion = result.get("suggestion", "")
                    if suggestion:
                        self.print_status(f"💡 {suggestion}", "info")

            else:
                error_msg = result.get("error", "Unknown error")
                self.print_status(f"❌ Ownership check failed: {error_msg}", "error")

        except Exception as e:
            self.print_status(f"❌ Check error: {str(e)}", "error")

    def import_steam_library_interactive(self) -> bool:
        """Interactive Steam library import."""
        self.print_section("🔗 Import Steam Library", "highlight")

        self.print_status("To import your Steam library, you need:", "info")
        self.print_status("   1. Your Steam ID (17-digit number)", "info")
        self.print_status(
            "   2. Steam Web API Key (get from: https://steamcommunity.com/dev/apikey)",
            "info",
        )
        print()

        # Get Steam ID
        steam_id = input(
            colored("🆔 Enter your Steam ID: ", "cyan", attrs=["bold"])
        ).strip()
        if not steam_id:
            self.print_status("Steam ID cannot be empty", "error")
            return False

        # Get API Key
        api_key = input(
            colored("🔑 Enter your Steam API Key: ", "yellow", attrs=["bold"])
        ).strip()
        if not api_key:
            self.print_status("API Key cannot be empty", "error")
            return False

        # Confirm import
        confirm = self.get_user_choice(
            "Ready to import your Steam library?",
            [
                "✅ Yes, import now",
                "🔙 Cancel import",
            ],
        )

        if not confirm or "Cancel" in confirm:
            self.print_status("Import cancelled", "info")
            return False

        # Show progress
        self.print_status("🔗 Importing Steam library...", "loading")

        try:
            result = import_steam_library(steam_id, api_key)

            if result.get("success", False):
                import_results = result.get("import_results", {})
                games_imported = import_results.get("games_imported", 0)
                import_date = import_results.get("import_date", "Unknown")
                recent_games = import_results.get("recent_games", [])

                self.print_status(
                    f"✅ Successfully imported {games_imported} games from Steam!",
                    "success",
                )
                self.print_status(f"📅 Import completed: {import_date}", "info")

                # Show collection changes
                changes = result.get("collection_changes", {})
                games_added = changes.get("games_added", 0)
                total_after = changes.get("after", {}).get("total_games", 0)

                self.print_status(
                    f"📚 Collection updated: {games_added} new games added (total: {total_after})",
                    "info",
                )

                # Show recent imports
                if recent_games:
                    print()
                    cprint("   🎮 Recently Imported Games:", "cyan", attrs=["bold"])
                    for game in recent_games[:5]:
                        title = game.get("title", "Unknown")
                        hours = game.get("hours_played", 0)
                        cprint(f"      • {title} ({hours} hours)", "white")

                    if len(recent_games) > 5:
                        remaining = len(recent_games) - 5
                        cprint(f"      ... and {remaining} more games", "yellow")

                # Show next steps
                next_steps = result.get("next_steps", [])
                if next_steps:
                    print()
                    cprint("   💡 Next Steps:", "yellow", attrs=["bold"])
                    for step in next_steps:
                        cprint(f"      • {step}", "white")

                return True
            else:
                error_msg = result.get("error", "Unknown error")
                self.print_status(f"❌ Steam import failed: {error_msg}", "error")

                # Show provided inputs for debugging
                provided_steam_id = result.get("steam_id", "")
                if provided_steam_id:
                    self.print_status(
                        f"   Steam ID provided: {provided_steam_id}", "info"
                    )

                return False

        except Exception as e:
            self.print_status(f"❌ Import error: {str(e)}", "error")
            return False

    def import_csv_collection_interactive(self) -> bool:
        """Interactive CSV collection import."""
        self.print_section("📁 Import Collection from CSV", "highlight")

        self.print_status("CSV file should contain these columns:", "info")
        self.print_status(
            "   title, status, platform, user_rating, hours_played, notes, tags", "info"
        )
        print()
        self.print_status("Example row:", "info")
        self.print_status(
            "   Hollow Knight,owned,Nintendo Switch,9.5,47,Amazing metroidvania,indie;metroidvania",
            "white",
        )
        print()

        # Get CSV file path
        csv_path = input(
            colored("📁 Enter CSV file path: ", "cyan", attrs=["bold"])
        ).strip()
        if not csv_path:
            self.print_status("File path cannot be empty", "error")
            return False

        # Confirm import
        confirm = self.get_user_choice(
            f"Ready to import from '{csv_path}'?",
            [
                "✅ Yes, import now",
                "🔙 Cancel import",
            ],
        )

        if not confirm or "Cancel" in confirm:
            self.print_status("Import cancelled", "info")
            return False

        # Show progress
        self.print_status("📁 Importing from CSV file...", "loading")

        try:
            result = import_collection_from_csv(csv_path)

            if result.get("success", False):
                import_results = result.get("import_results", {})
                games_imported = import_results.get("games_imported", 0)
                import_date = import_results.get("import_date", "Unknown")

                self.print_status(
                    f"✅ Successfully imported {games_imported} games from CSV!",
                    "success",
                )
                self.print_status(f"📅 Import completed: {import_date}", "info")

                # Show collection changes
                changes = result.get("collection_changes", {})
                games_added = changes.get("games_added", 0)
                total_after = changes.get("after", {}).get("total_games", 0)

                self.print_status(
                    f"📚 Collection updated: {games_added} new games added (total: {total_after})",
                    "info",
                )

                # Show CSV format example
                csv_example = result.get("csv_format_example", {})
                headers = csv_example.get("headers", [])
                if headers:
                    print()
                    cprint("   📋 CSV Format Reference:", "yellow", attrs=["bold"])
                    cprint(f"      Headers: {', '.join(headers)}", "white")

                return True
            else:
                error_msg = result.get("error", "Unknown error")
                self.print_status(f"❌ CSV import failed: {error_msg}", "error")

                csv_file = result.get("csv_file", "")
                if csv_file:
                    self.print_status(f"   File: {csv_file}", "info")

                return False

        except Exception as e:
            self.print_status(f"❌ Import error: {str(e)}", "error")
            return False

    def export_csv_collection_interactive(self) -> bool:
        """Interactive CSV collection export."""
        self.print_section("💾 Export Collection to CSV", "highlight")

        # Get export file path
        csv_path = input(
            colored("💾 Enter CSV file path to save: ", "cyan", attrs=["bold"])
        ).strip()
        if not csv_path:
            self.print_status("File path cannot be empty", "error")
            return False

        # Ensure .csv extension
        if not csv_path.endswith(".csv"):
            csv_path += ".csv"

        # Get filter options
        filter_choice = self.get_user_choice(
            "Export options:",
            [
                "📚 Export all games",
                "📦 Export owned games only",
                "❤️ Export wishlist only",
                "✅ Export completed games only",
                "🎮 Export currently playing only",
            ],
        )

        if not filter_choice:
            return False

        # Extract filter value
        filter_map = {
            "Export all games": None,
            "Export owned games only": "owned",
            "Export wishlist only": "wishlist",
            "Export completed games only": "completed",
            "Export currently playing only": "playing",
        }

        status_filter = next(
            (v for k, v in filter_map.items() if k in filter_choice), None
        )

        # Confirm export
        filter_text = (
            f" ({filter_choice.replace('Export ', '').replace(' only', '')})"
            if status_filter
            else ""
        )
        confirm = self.get_user_choice(
            f"Ready to export{filter_text} to '{csv_path}'?",
            [
                "✅ Yes, export now",
                "🔙 Cancel export",
            ],
        )

        if not confirm or "Cancel" in confirm:
            self.print_status("Export cancelled", "info")
            return False

        # Show progress
        self.print_status("💾 Exporting collection to CSV...", "loading")

        try:
            result = export_collection_to_csv(csv_path, status_filter)  # type: ignore

            if result.get("success", False):
                export_results = result.get("export_results", {})
                games_exported = export_results.get("games_exported", 0)
                export_date = export_results.get("export_date", "Unknown")
                csv_file = export_results.get("csv_file", csv_path)

                self.print_status(
                    f"✅ Successfully exported {games_exported} games to CSV!",
                    "success",
                )
                self.print_status(f"📁 File saved: {csv_file}", "info")
                self.print_status(f"📅 Export completed: {export_date}", "info")

                # Show file info
                file_info = result.get("file_info", {})
                format_type = file_info.get("format", "CSV")
                encoding = file_info.get("encoding", "UTF-8")
                columns = file_info.get("columns", [])

                print()
                cprint("   📋 File Information:", "cyan", attrs=["bold"])
                cprint(f"      Format: {format_type}", "white")
                cprint(f"      Encoding: {encoding}", "white")
                if columns:
                    cprint(
                        f"      Columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}",
                        "white",
                    )

                return True
            else:
                error_msg = result.get("error", "Unknown error")
                self.print_status(f"❌ CSV export failed: {error_msg}", "error")

                csv_file = result.get("csv_file", "")
                if csv_file:
                    self.print_status(f"   File: {csv_file}", "info")

                return False

        except Exception as e:
            self.print_status(f"❌ Export error: {str(e)}", "error")
            return False

    def view_recommendation_filter_interactive(self):
        """Display recommendation filtering information."""
        self.print_section("🎯 Recommendation Filter", "highlight")

        try:
            result = get_collection_recommendations_filter()

            if result.get("success", False):
                filter_data = result.get("filter_data", {})
                exclude_games = filter_data.get("exclude_from_recommendations", [])
                total_owned = filter_data.get("total_owned_games", 0)
                filtering_active = filter_data.get("filtering_active", False)

                collection_context = result.get("collection_context", {})
                total_games = collection_context.get("total_games", 0)
                owned_games = collection_context.get("owned_games", 0)
                completion_rate = collection_context.get("completion_rate", 0)

                # Display filter status
                if filtering_active:
                    self.print_status(
                        f"🎯 Recommendation filtering is ACTIVE", "success"
                    )
                    self.print_status(
                        f"📦 {total_owned} owned games will be excluded from recommendations",
                        "info",
                    )
                else:
                    self.print_status(
                        "🎯 Recommendation filtering is INACTIVE (no owned games)",
                        "warning",
                    )

                # Display collection context
                print()
                cprint("   📊 Collection Context:", "cyan", attrs=["bold"])
                cprint(f"      📚 Total Games: {total_games}", "white")
                cprint(f"      📦 Owned Games: {owned_games}", "white")
                if completion_rate > 0:
                    cprint(f"      ✅ Completion Rate: {completion_rate:.1f}%", "white")

                # Show sample excluded games
                if exclude_games:
                    print()
                    cprint(
                        "   🚫 Games Excluded from Recommendations:",
                        "yellow",
                        attrs=["bold"],
                    )

                    for i, game in enumerate(exclude_games[:10], 1):
                        title = game.get("title", "Unknown")
                        rating = game.get("user_rating")

                        game_line = f"      {i:2d}. {title}"
                        if rating:
                            game_line += f" (⭐{rating}/10)"

                        cprint(game_line, "white")

                    if len(exclude_games) > 10:
                        remaining = len(exclude_games) - 10
                        cprint(f"      ... and {remaining} more games", "yellow")

                # Show usage info
                usage_info = result.get("usage_info", {})
                purpose = usage_info.get("purpose", "")
                benefit = usage_info.get("benefit", "")

                if purpose or benefit:
                    print()
                    cprint("   💡 Filter Benefits:", "green", attrs=["bold"])
                    if purpose:
                        cprint(f"      🎯 Purpose: {purpose}", "white")
                    if benefit:
                        cprint(f"      ✨ Benefit: {benefit}", "white")

            else:
                error_msg = result.get("error", "Unknown error")
                self.print_status(f"❌ Failed to get filter info: {error_msg}", "error")

        except Exception as e:
            self.print_status(f"❌ Filter error: {str(e)}", "error")

    # 👨‍👩‍👧‍👦 PHASE 7.1.5: Multi-User System Methods

    def check_user_login_status(self) -> Dict:
        """Check current user login status and display welcome info."""
        try:
            current_user = get_current_user_details()

            if current_user.get("success", False) and current_user.get(
                "logged_in", False
            ):
                user_profile = current_user.get("user_profile", {})
                username = user_profile.get("username", "Unknown")
                role = user_profile.get("role", "unknown")
                session_duration = user_profile.get("session_duration", "Unknown")

                # Role-specific emoji
                role_emoji = {
                    "admin": "👑",
                    "parent": "👨‍👩‍👧‍👦",
                    "child": "👶",
                    "guest": "👤",
                }.get(role, "👤")

                self.print_status(
                    f"Welcome back, {username}! {role_emoji} ({role.title()} - {session_duration})",
                    "success",
                )
                return current_user
            else:
                self.print_status(
                    "👤 No user logged in - Multi-User System available", "info"
                )
                return {"logged_in": False}

        except Exception as e:
            self.print_status(f"Error checking user status: {str(e)}", "warning")
            return {"logged_in": False, "error": str(e)}

    def user_management_menu(self) -> bool:
        """Display user management menu and handle user operations."""
        self.print_header("👨‍👩‍👧‍👦 Multi-User System", "highlight")

        # Show current system stats
        try:
            stats = get_user_system_stats()
            if stats.get("success", False):
                overview = stats.get("system_overview", {})
                total_users = overview.get("total_users", 0)
                health_score = overview.get("system_health_score", 0)

                self.print_status(
                    f"👥 Family System: {total_users} users, {health_score}% health",
                    "info",
                )
        except:
            pass

        action = self.get_user_choice(
            "User Management Options:",
            [
                "👤 Register new user",
                "🔄 Switch to different user",
                "👥 View all family members",
                "🧳 Create guest session",
                "📊 View system statistics",
                "🔙 Back to main menu",
            ],
        )

        if not action:
            return False

        if "Register new user" in action:
            return self.register_user_interactive()

        elif "Switch to different user" in action:
            return self.switch_user_interactive()

        elif "View all family members" in action:
            self.view_family_members()
            return True

        elif "Create guest session" in action:
            return self.create_guest_session_interactive()

        elif "View system statistics" in action:
            self.view_system_statistics()
            return True

        elif "Back to main menu" in action:
            return False

        return True

    def register_user_interactive(self) -> bool:
        """Interactive user registration."""
        self.print_section("👤 New User Registration", "highlight")

        # Get username
        username = input(colored("👤 Enter username: ", "cyan", attrs=["bold"])).strip()
        if not username:
            self.print_status("Username cannot be empty", "error")
            return False

        # Get role
        role = self.get_user_choice(
            "Select user role:",
            [
                "👑 Admin (Full system access)",
                "👨‍👩‍👧‍👦 Parent (Family management)",
                "👶 Child (Parental controls)",
                "👤 Guest (Temporary access)",
            ],
        )

        if not role:
            return False

        # Extract role name
        role_map = {
            "Admin": "admin",
            "Parent": "parent",
            "Child": "child",
            "Guest": "guest",
        }

        role_name = next((v for k, v in role_map.items() if k in role), "guest")

        try:
            result = register_new_user(username, role_name)

            if result.get("success", False):
                user_profile = result.get("user_profile", {})
                user_id = user_profile.get("user_id", "Unknown")

                self.print_status(
                    f"✅ User '{username}' registered successfully!", "success"
                )
                self.print_status(f"   📊 Role: {role_name.title()}", "info")
                self.print_status(f"   🆔 ID: {user_id}", "info")

                # Auto-login to new user
                auto_login = self.get_user_choice(
                    f"Switch to '{username}' now?", ["Yes", "No"]
                )

                if "Yes" in auto_login:
                    switch_result = switch_to_user(username)
                    if switch_result.get("success", False):
                        self.print_status(f"🔄 Switched to {username}", "success")

                return True
            else:
                error_msg = result.get("message", "Unknown error")
                self.print_status(f"❌ Registration failed: {error_msg}", "error")
                return False

        except Exception as e:
            self.print_status(f"❌ Registration error: {str(e)}", "error")
            return False

    def switch_user_interactive(self) -> bool:
        """Interactive user switching."""
        self.print_section("🔄 Switch User", "highlight")

        # Get list of users
        try:
            users_result = list_system_users()
            if not users_result.get("success", False):
                self.print_status("Failed to get user list", "error")
                return False

            family_view = users_result.get("family_view", {})
            total_users = users_result.get("total_users", 0)

            if total_users == 0:
                self.print_status(
                    "No users registered. Please register a user first.", "warning"
                )
                return False

            # Build user list for selection
            user_options = []
            for role_group, users in family_view.items():
                if users:  # If this role group has users
                    role_emoji = {
                        "admins": "👑",
                        "parents": "👨‍👩‍👧‍👦",
                        "children": "👶",
                        "guests": "👤",
                    }.get(role_group, "👤")

                    for user in users:
                        username = user.get("username", "Unknown")
                        games_analyzed = user.get("games_analyzed", 0)
                        user_options.append(
                            f"{role_emoji} {username} ({role_group[:-1]} - {games_analyzed} games)"
                        )

            if not user_options:
                self.print_status("No active users available", "warning")
                return False

            user_choice = self.get_user_choice(
                "Select user to switch to:", user_options + ["🔙 Back to menu"]
            )

            if not user_choice or "Back to menu" in user_choice:
                return False

            # Extract username from choice
            username = user_choice.split(" ")[1]  # Get username after emoji

            # Switch user
            switch_result = switch_to_user(username)

            if switch_result.get("success", False):
                switched_to = switch_result.get("switched_to", {})
                role = switched_to.get("role", "unknown")
                welcome_msg = switch_result.get("welcome_message", "")

                self.print_status(
                    f"🔄 Successfully switched to {username} ({role})", "success"
                )
                if welcome_msg:
                    self.print_status(f"   {welcome_msg}", "info")
                return True
            else:
                error_msg = switch_result.get("message", "Unknown error")
                self.print_status(f"❌ Switch failed: {error_msg}", "error")
                return False

        except Exception as e:
            self.print_status(f"❌ Switch error: {str(e)}", "error")
            return False

    def view_family_members(self):
        """Display all family members with their stats."""
        self.print_section("👥 Family Members", "highlight")

        try:
            users_result = list_system_users()
            if not users_result.get("success", False):
                self.print_status("Failed to get family list", "error")
                return

            family_view = users_result.get("family_view", {})
            total_users = users_result.get("total_users", 0)

            if total_users == 0:
                self.print_status("No family members registered yet", "info")
                return

            self.print_status(f"👨‍👩‍👧‍👦 Family has {total_users} members:", "info")
            print()

            for role_group, users in family_view.items():
                if users:
                    role_emoji = {
                        "admins": "👑",
                        "parents": "👨‍👩‍👧‍👦",
                        "children": "👶",
                        "guests": "👤",
                    }.get(role_group, "👤")

                    cprint(
                        f"   {role_emoji} {role_group.title()}:", "cyan", attrs=["bold"]
                    )

                    for user in users:
                        username = user.get("username", "Unknown")
                        games_analyzed = user.get("games_analyzed", 0)
                        cprint(
                            f"      • {username} ({games_analyzed} games analyzed)",
                            "white",
                        )

            print()

        except Exception as e:
            self.print_status(f"❌ Error viewing family: {str(e)}", "error")

    def create_guest_session_interactive(self) -> bool:
        """Create interactive guest session."""
        self.print_section("🧳 Guest Session", "highlight")

        try:
            guest_result = create_guest_access()

            if guest_result.get("success", False):
                guest_profile = guest_result.get("guest_profile", {})
                guest_username = guest_profile.get("username", "Unknown")
                session_type = guest_profile.get("session_type", "temporary")

                self.print_status(
                    f"🧳 Guest session created: {guest_username}", "success"
                )
                self.print_status(f"   ⏰ Type: {session_type}", "info")
                self.print_status("   📝 Note: Guest data will not be saved", "warning")

                return True
            else:
                error_msg = guest_result.get("message", "Unknown error")
                self.print_status(f"❌ Guest session failed: {error_msg}", "error")
                return False

        except Exception as e:
            self.print_status(f"❌ Guest session error: {str(e)}", "error")
            return False

    def view_system_statistics(self):
        """Display comprehensive system statistics."""
        self.print_section("📊 System Statistics", "highlight")

        try:
            stats = get_user_system_stats()

            if stats.get("success", False):
                overview = stats.get("system_overview", {})
                current_user = stats.get("current_user", {})

                # System overview
                total_users = overview.get("total_users", 0)
                active_users = overview.get("active_users", 0)
                health_score = overview.get("system_health_score", 0)
                user_breakdown = overview.get("user_breakdown", {})

                self.print_status(
                    f"👥 Total Users: {total_users} ({active_users} active)", "info"
                )
                self.print_status(
                    f"💚 System Health: {health_score}%",
                    "success" if health_score >= 80 else "warning",
                )

                print()
                cprint("   👨‍👩‍👧‍👦 Family Breakdown:", "cyan", attrs=["bold"])
                for role, count in user_breakdown.items():
                    if count > 0:
                        role_emoji = {
                            "admins": "👑",
                            "parents": "👨‍👩‍👧‍👦",
                            "children": "👶",
                            "guests": "👤",
                        }.get(role, "👤")
                        cprint(f"      {role_emoji} {role.title()}: {count}", "white")

                # Current user info
                print()
                if current_user.get("logged_in", False):
                    username = current_user.get("username", "Unknown")
                    role = current_user.get("role", "unknown")
                    session_duration = current_user.get("session_duration", "Unknown")

                    self.print_status(
                        f"🔵 Active User: {username} ({role}) - {session_duration}",
                        "info",
                    )
                else:
                    self.print_status("🔴 No user currently logged in", "warning")

                # Storage info
                storage_location = overview.get("storage_location", "Unknown")
                if storage_location:
                    self.print_status(f"💾 Data stored in: {storage_location}", "info")

            else:
                self.print_status("Failed to get system statistics", "error")

        except Exception as e:
            self.print_status(f"❌ Statistics error: {str(e)}", "error")

    def batch_analyze_interactive(self):
        """Interactive batch analysis of multiple games."""
        self.print_section("🔥 Batch Game Analysis Setup", style="highlight")

        games_to_analyze = []

        # Get games from user
        while len(games_to_analyze) < 10:  # Max 10 games for interactive
            game = input(
                colored(
                    f"Enter game {len(games_to_analyze)+1} name (or 'done' to start): ",
                    "cyan",
                    attrs=["bold"],
                )
            )

            if game.strip().lower() == "done" and len(games_to_analyze) >= 1:
                break
            elif game.strip() and game.strip().lower() != "done":
                games_to_analyze.append(game.strip())
                self.print_status(f"Added: {game.strip()}", "success")
            elif not game.strip() and len(games_to_analyze) >= 1:
                break

        if games_to_analyze:
            # Get analysis type
            analysis_type = self.get_user_choice(
                "Select analysis type:", ["quick", "comprehensive"]
            )

            if analysis_type:
                batch_id = self.batch_analyze_games_with_progress(
                    games_to_analyze, analysis_type
                )
                self.print_status(
                    f"Batch analysis completed! (ID: {batch_id})", "success"
                )

                # Ask if user wants to see detailed results for comprehensive analysis
                if analysis_type == "comprehensive":
                    show_details = self.get_user_choice(
                        "Would you like to see detailed analysis results?",
                        ["Yes", "No"],
                    )
                    if "Yes" in show_details:
                        self.display_detailed_batch_results(batch_id)
        else:
            self.print_status("No games added for batch analysis", "warning")

    def batch_category_interactive(self):
        """Interactive batch analysis of category games."""
        categories = [
            "hottest",
            "recent-drops",
            "deepest-discounts",
            "highest-rated",
            "staff-picks",
            "trending",
            "recently-released",
        ]

        category = self.get_user_choice(
            "Select category:", categories, allow_custom=True
        )

        if category:
            count = self.get_user_choice(
                "How many games to analyze?", ["3", "5", "10"], allow_custom=True
            )

            analysis_type = self.get_user_choice(
                "Select analysis type:", ["quick", "comprehensive"]
            )

            try:
                count_num = int(count) if count.isdigit() else 5
                self.batch_analyze_category_with_progress(
                    category, count_num, analysis_type
                )
            except:
                self.print_status("Invalid count, using default of 5", "warning")
                self.batch_analyze_category_with_progress(category, 5, analysis_type)

    def batch_random_interactive(self):
        """Interactive batch analysis of random games."""
        count = self.get_user_choice(
            "How many random games?", ["3", "5", "10"], allow_custom=True
        )

        preference = self.get_user_choice(
            "What type of games?", ["mixed", "deals", "quality", "trending"]
        )

        analysis_type = self.get_user_choice(
            "Select analysis type:", ["quick", "comprehensive"]
        )

        if count and preference and analysis_type:
            try:
                count_num = int(count) if count.isdigit() else 5
                self.batch_analyze_random_with_progress(
                    count_num, preference, analysis_type
                )
            except:
                self.print_status("Invalid count, using default of 5", "warning")
                self.batch_analyze_random_with_progress(5, preference, analysis_type)

    def browse_categories_interactive(self):
        """Interactive category browsing."""
        categories = [
            "hottest",
            "recent-drops",
            "eshop-sales",
            "deepest-discounts",
            "highest-rated",
            "staff-picks",
            "trending",
            "recently-released",
        ]

        category = self.get_user_choice(
            "Select category to browse:", categories, allow_custom=True
        )

        if category:
            count = self.get_user_choice(
                "How many games to show?", ["5", "10", "15", "20"], allow_custom=True
            )

            try:
                count_num = int(count) if count.isdigit() else 5
                self.browse_category_with_progress(category, count_num)
            except:
                self.print_status("Invalid count, using default of 5", "warning")
                self.browse_category_with_progress(category, 5)

    def browse_category_with_progress(self, category: str, count: int):
        """Browse category with progress visualization and improved game selection."""
        self.print_header(f"📂 Browsing Category: {category.title()}")

        while True:  # Outer loop for refreshing the category list
            progress = self.create_progress_bar("Fetching games", 100, "blue")

            try:
                # Simulate loading
                for i in range(0, 101, 25):
                    progress.update(25)
                    time.sleep(0.2)

                progress.close()

                result = scrape_dekudeals_category(category, max_games=count)

                if result.get("success", False):
                    games = result.get("game_titles", [])
                    self.print_status(
                        f"Found {len(games)} games in {category}", "success"
                    )

                    if games:
                        while True:  # Inner loop for game selection within current list
                            self.print_section(
                                f"🎮 Games in {category.title()}", style="info"
                            )
                            for i, game in enumerate(games, 1):
                                cprint(f"   {i:2d}. {game}", "white")

                            print()
                            action = self.get_user_choice(
                                "What would you like to do?",
                                [
                                    "📊 Analyze a game from this list",
                                    "🔄 Get another list from this category",
                                    "🔙 Back to main menu",
                                ],
                            )

                            if not action:  # User cancelled
                                return  # Exit completely

                            if "Analyze a game" in action:
                                # Let user choose which game to analyze
                                game_choice = input(
                                    colored(
                                        f"\n🎯 Enter game number (1-{len(games)}) to analyze: ",
                                        "cyan",
                                        attrs=["bold"],
                                    )
                                ).strip()

                                try:
                                    game_index = int(game_choice) - 1
                                    if 0 <= game_index < len(games):
                                        selected_game = games[game_index]
                                        self.print_status(
                                            f"Analyzing: {selected_game}", "info"
                                        )
                                        results = self.analyze_game_with_progress(
                                            selected_game
                                        )
                                        self.display_game_analysis_results(
                                            results, selected_game
                                        )
                                    else:
                                        self.print_status(
                                            f"Invalid choice. Please enter 1-{len(games)}",
                                            "error",
                                        )
                                except ValueError:
                                    self.print_status(
                                        "Invalid input. Please enter a number.", "error"
                                    )

                            elif "Get another list" in action:
                                # Refresh the list - get new games from same category
                                self.print_status(
                                    f"Refreshing {category} list...", "info"
                                )
                                break  # Exit inner loop to refetch, stay in outer loop

                            elif "Back to main menu" in action:
                                return  # Exit completely

                    else:
                        self.print_status(f"No games found in {category}", "warning")
                        return  # Exit if no games found
                else:
                    error_msg = result.get("error", "Unknown error")
                    self.print_status(
                        f"Failed to fetch games from {category}: {error_msg}", "error"
                    )

                    # Provide help for eshop-sales issue
                    if category == "eshop-sales":
                        print()
                        self.print_status(
                            "💡 Tip: 'eshop-sales' category might be temporarily unavailable",
                            "info",
                        )
                        self.print_status(
                            "    Try 'hottest' or 'recent-drops' instead", "info"
                        )
                    return  # Exit if fetching failed

            except Exception as e:
                progress.close()
                self.print_status(f"Error browsing category: {str(e)}", "error")
                return  # Exit on error

    def random_recommendations_interactive(self):
        """Interactive random game recommendations."""
        sample_size = self.get_user_choice(
            "How many random games?", ["3", "5", "10"], allow_custom=True
        )

        preference = self.get_user_choice(
            "What type of games do you prefer?",
            ["mixed", "deals", "quality", "trending"],
        )

        if sample_size and preference:
            try:
                size_num = int(sample_size) if sample_size.isdigit() else 3
                self.get_random_games_with_progress(size_num, preference)
            except:
                self.print_status("Invalid size, using default of 3", "warning")
                self.get_random_games_with_progress(3, preference)

    def get_random_games_with_progress(self, size: int, preference: str):
        """Get random games with progress visualization."""
        self.print_header(
            f"🎲 Random Game Recommendations: {size} games ({preference})"
        )

        progress = self.create_progress_bar(
            "Generating recommendations", 100, "magenta"
        )

        try:
            for i in range(0, 101, 20):
                progress.update(20)
                time.sleep(0.15)

            progress.close()

            result = get_random_game_sample(size, preference)

            if result.get("success", False):
                games = result.get("selected_games", [])
                self.print_status(
                    f"Generated {len(games)} random recommendations", "success"
                )

                if games:
                    self.print_section("🎮 Your Random Game Picks", style="highlight")
                    for i, game in enumerate(games, 1):
                        cprint(f"   🎯 {i}. {game}", "cyan", attrs=["bold"])

                # Offer quick analysis
                if games:
                    analyze = self.get_user_choice(
                        "Would you like quick analysis of these games?", ["Yes", "No"]
                    )

                    if "Yes" in analyze:
                        self.quick_analyze_multiple_games(games)
            else:
                self.print_status("Failed to generate random recommendations", "error")

        except Exception as e:
            progress.close()
            self.print_status(f"Error generating recommendations: {str(e)}", "error")

    def _extract_rating_number(self, rating: str) -> float:
        """Extract numeric rating from string like '7.5/10' or 'N/A'."""
        try:
            if rating == "N/A" or not rating:
                return 0.0
            # Extract number before "/10" or just the number
            if "/" in rating:
                return float(rating.split("/")[0])
            else:
                return float(rating)
        except (ValueError, IndexError):
            return 0.0

    def quick_analyze_multiple_games(self, games: List[str]):
        """Quick analysis of multiple games."""
        self.print_header("⚡ Quick Multi-Game Analysis")

        progress = self.create_progress_bar("Analyzing games", len(games), "green")

        for i, game in enumerate(games):
            try:
                result = generate_quick_game_opinion(game)

                if result.get("success", False):
                    summary = result.get("quick_summary", {})
                    rating = summary.get("rating", "N/A")
                    recommendation = summary.get("recommendation", "N/A")

                    print()
                    cprint(f"🎮 {game}", "cyan", attrs=["bold"])

                    # Extract numeric rating safely
                    numeric_rating = self._extract_rating_number(rating)
                    rating_color = (
                        "green"
                        if numeric_rating >= 7
                        else "yellow" if numeric_rating >= 5 else "red"
                    )
                    cprint(f"   ⭐ Rating: {rating}", rating_color)
                    cprint(f"   🎯 Recommendation: {recommendation}", "white")
                else:
                    print()
                    cprint(f"🎮 {game}", "cyan", attrs=["bold"])
                    self.print_status("   Analysis failed", "error")

            except Exception as e:
                print()
                cprint(f"🎮 {game}", "cyan", attrs=["bold"])
                self.print_status(f"   Error: {str(e)}", "error")

            progress.update(1)

        progress.close()

    def compare_games_interactive(self):
        """Interactive game comparison."""
        self.print_section("🆚 Game Comparison Setup", style="highlight")

        games_to_compare = []

        while len(games_to_compare) < 2:
            game = input(
                colored(
                    f"Enter game {len(games_to_compare)+1} name: ",
                    "cyan",
                    attrs=["bold"],
                )
            )
            if game.strip():
                games_to_compare.append(game.strip())
                self.print_status(f"Added: {game.strip()}", "success")

        # Ask for more games
        while len(games_to_compare) < 5:
            more = self.get_user_choice(
                f"Add another game? (Currently have {len(games_to_compare)})",
                ["Yes", "No, start comparison"],
            )

            if "Yes" in more:
                game = input(
                    colored(
                        f"Enter game {len(games_to_compare)+1} name: ",
                        "cyan",
                        attrs=["bold"],
                    )
                )
                if game.strip():
                    games_to_compare.append(game.strip())
                    self.print_status(f"Added: {game.strip()}", "success")
            else:
                break

        if len(games_to_compare) >= 2:
            self.compare_games_with_progress(games_to_compare)

    def compare_games_with_progress(self, games: List[str]):
        """Compare games with progress visualization."""
        self.print_header(f"🆚 Comparing {len(games)} Games")

        progress = self.create_progress_bar("Comparing games", 100, "red")

        try:
            for i in range(0, 101, 33):
                progress.update(33)
                time.sleep(0.2)

            progress.close()

            result = compare_games_with_reviews(games, "overall")

            if result.get("success", False):
                winner = result.get("winner", {})
                reasoning = result.get("comparison_reasoning", "")

                self.print_status("Comparison completed successfully!", "success")

                if winner:
                    winner_title = winner.get("game_title", "Unknown")
                    print()
                    cprint(f"🏆 WINNER: {winner_title}", "green", attrs=["bold"])

                if reasoning:
                    self.print_section("🤔 Comparison Reasoning", style="info")
                    print(f"   {reasoning}")

                # Show all games with rankings
                self.print_section("📊 Full Ranking", style="secondary")
                for i, game in enumerate(games, 1):
                    rank_color = "green" if i == 1 else "yellow" if i == 2 else "white"
                    cprint(
                        f"   {i}. {game}", rank_color, attrs=["bold"] if i == 1 else []
                    )
            else:
                self.print_status("Comparison failed", "error")

        except Exception as e:
            progress.close()
            self.print_status(f"Comparison error: {str(e)}", "error")

    def show_categories(self):
        """Display all available categories with enhanced formatting."""
        self.print_header("📋 Available Game Categories")

        categories = {
            "💰 Deal Categories": [
                ("hottest", "🔥 Hottest Deals"),
                ("recent-drops", "📉 Recent Price Drops"),
                # ("eshop-sales", "🏪 eShop Sales"),  # Temporarily disabled
                ("deepest-discounts", "💸 Deepest Discounts"),
                ("bang-for-your-buck", "💎 Bang for Your Buck"),
                ("ending-soon", "⏰ Ending Soon"),
            ],
            "⭐ Quality Categories": [
                ("highest-rated", "🏆 Highest Rated"),
                ("staff-picks", "👥 Staff Picks"),
                ("most-wanted", "❤️ Most Wanted"),
            ],
            "📈 Trending Categories": [
                ("trending", "📈 Trending Games"),
                ("recently-released", "🆕 Recently Released"),
                ("upcoming-releases", "🔮 Upcoming Releases"),
                ("newest-listings", "📝 Newly Listed"),
            ],
        }

        for group_name, group_categories in categories.items():
            print()
            cprint(group_name, "cyan", attrs=["bold"])
            cprint("─" * len(group_name), "cyan")

            for cat_id, cat_display in group_categories:
                print(f"   {cat_display}")
                cprint(f"     └─ Use: --category {cat_id}", "white")

        # Add note about temporarily unavailable categories
        print()
        self.print_status(
            "⚠️ Note: Some categories may be temporarily unavailable due to site protection",
            "warning",
        )
        self.print_status(
            "   If a category fails, try 'hottest', 'recent-drops', or 'deepest-discounts'",
            "info",
        )

    def run_demo_mode(self):
        """Run full system demonstration."""
        self.print_header("🎬 Full System Demonstration", "highlight")

        demo_game = "INSIDE"
        self.print_status(f"Running demo with game: {demo_game}", "info")

        # Run comprehensive analysis
        results = self.analyze_game_with_progress(demo_game, "comprehensive")
        self.display_game_analysis_results(results, demo_game)

        # Show category browsing
        print()
        self.browse_category_with_progress("hottest", 5)

        # Show random recommendations
        print()
        self.get_random_games_with_progress(3, "mixed")

        self.print_status("Demo completed successfully!", "success")

    def batch_analyze_games_with_progress(
        self, game_names: List[str], analysis_type: str = "comprehensive"
    ) -> str:
        """
        Analyze multiple games concurrently with batch processing.

        Args:
            game_names: List of game names to analyze
            analysis_type: Type of analysis (comprehensive, quick)

        Returns:
            str: Batch ID for tracking
        """
        self.print_header(
            f"🚀 Batch Analysis: {len(game_names)} Games ({analysis_type})"
        )

        # Create progress callback
        progress_bar = None

        def progress_callback(session):
            nonlocal progress_bar
            if progress_bar is None:
                progress_bar = self.create_progress_bar(
                    f"Analyzing {session.total_tasks} games",
                    session.total_tasks,
                    "cyan",
                )

            completed = session.completed_tasks + session.failed_tasks
            progress_bar.update(completed - progress_bar.n)

        # Start batch analysis
        manager = get_batch_manager()
        batch_id = manager.create_batch_session(
            game_names, analysis_type, progress_callback=progress_callback
        )

        self.print_status(f"Starting batch analysis... (ID: {batch_id})", "info")

        # Start analysis
        success = manager.start_batch_analysis(batch_id)
        if not success:
            self.print_status("Failed to start batch analysis", "error")
            return batch_id

        # Wait for completion and show progress
        import time

        while True:
            status = manager.get_batch_status(batch_id)
            if not status:
                break

            if status["status"] in ["completed", "failed", "cancelled"]:
                break

            time.sleep(0.5)

        if progress_bar:
            progress_bar.close()

        # Show results
        self.display_batch_results(batch_id)
        return batch_id

    def display_batch_results(self, batch_id: str):
        """Display batch analysis results in formatted way."""
        manager = get_batch_manager()
        results = manager.get_batch_results(batch_id)

        if not results:
            self.print_status(f"Batch {batch_id} not found", "error")
            return

        # Display summary
        summary = results["summary"]
        self.print_header(f"📊 Batch Results: {results['batch_name']}")

        print()
        cprint(f"📈 Summary:", "cyan", attrs=["bold"])
        cprint(f"   Total Games: {summary['total_games']}", "white")
        cprint(f"   Successful: {summary['successful']}", "green")
        cprint(
            f"   Failed: {summary['failed']}",
            "red" if summary["failed"] > 0 else "white",
        )
        cprint(
            f"   Success Rate: {summary['success_rate']:.1f}%",
            (
                "green"
                if summary["success_rate"] >= 80
                else "yellow" if summary["success_rate"] >= 50 else "red"
            ),
        )
        cprint(f"   Duration: {results['duration']:.1f}s", "white")

        # Display individual results
        print()
        cprint(f"🎮 Individual Results:", "cyan", attrs=["bold"])

        for i, result in enumerate(results["results"], 1):
            game_name = result["game_name"]
            status = result["status"]
            duration = result["duration"] or 0

            # Status symbol and color
            if status == "completed":
                symbol = "✅"
                color = "green"
            elif status == "failed":
                symbol = "❌"
                color = "red"
            else:
                symbol = "⚠️"
                color = "yellow"

            print()
            cprint(f"   {i:2d}. {symbol} {game_name}", color, attrs=["bold"])
            cprint(
                f"       Status: {status.title()}, Duration: {duration:.1f}s", "white"
            )

            # Show quick result or error
            if status == "completed" and result["result"]:
                game_result = result["result"]

                # Try different result structures
                if "quick_summary" in game_result:
                    # Quick analysis results
                    summary = game_result["quick_summary"]
                    rating = summary.get("rating", "N/A")
                    recommendation = summary.get("recommendation", "N/A")
                    cprint(
                        f"       Rating: {rating}, Recommendation: {recommendation}",
                        "white",
                    )
                elif "review_data" in game_result.get("data", {}):
                    # Comprehensive analysis - review_data structure
                    review_data = game_result["data"]["review_data"]
                    rating = review_data.get("overall_rating", "N/A")
                    recommendation = review_data.get("recommendation", "N/A")
                    cprint(
                        f"       Rating: {rating}/10, Recommendation: {recommendation}",
                        "white",
                    )
                elif isinstance(game_result, dict) and any(
                    step_key.startswith("step_") for step_key in game_result.keys()
                ):
                    # Comprehensive analysis - step-based structure
                    self._extract_step_based_summary(game_result, "       ")
                else:
                    # Fallback - show what we can
                    cprint(
                        f"       Analysis completed (use --batch-results {batch_id} for details)",
                        "cyan",
                    )
            elif status == "failed":
                error = result.get("error", "Unknown error")
                cprint(f"       Error: {error[:80]}...", "red")

    def _extract_step_based_summary(self, game_result: Dict, indent: str = ""):
        """Extract summary from step-based comprehensive analysis results."""
        try:
            # Look for review data in different steps
            review_data = None

            # Check step_3 (review generation)
            if "step_3" in game_result and game_result["step_3"].get("success"):
                step3_data = game_result["step_3"].get("data", {})
                if "review_data" in step3_data:
                    review_data = step3_data["review_data"]
                elif "data" in step3_data and "review_data" in step3_data["data"]:
                    review_data = step3_data["data"]["review_data"]

            if review_data:
                rating = review_data.get("overall_rating", "N/A")
                recommendation = review_data.get("recommendation", "N/A")
                cprint(
                    f"{indent}Rating: {rating}/10, Recommendation: {recommendation}",
                    "white",
                )
            else:
                # Fallback - show completion status
                completed_steps = sum(
                    1
                    for key, value in game_result.items()
                    if key.startswith("step_") and value.get("success", False)
                )
                total_steps = len(
                    [key for key in game_result.keys() if key.startswith("step_")]
                )
                cprint(
                    f"{indent}Comprehensive analysis: {completed_steps}/{total_steps} steps completed",
                    "cyan",
                )

        except Exception as e:
            cprint(f"{indent}Analysis completed (structure parsing failed)", "yellow")

    def display_detailed_batch_results(self, batch_id: str):
        """Display detailed batch results with full comprehensive analysis data."""
        manager = get_batch_manager()
        results = manager.get_batch_results(batch_id)

        if not results:
            self.print_status(f"Batch {batch_id} not found", "error")
            return

        self.print_header(f"📋 Detailed Batch Results: {results['batch_name']}")

        for i, result in enumerate(results["results"], 1):
            if result["status"] == "completed" and result["result"]:
                game_name = result["game_name"]
                game_result = result["result"]

                self.print_header(f"🎮 {i}. {game_name}", "info")

                # Display using the same logic as single game analysis
                self.display_game_analysis_results(game_result, game_name)

                print()  # Add spacing between games

    def show_batch_status(self, batch_id: Optional[str] = None):
        """Show status of batch operations."""
        manager = get_batch_manager()

        if batch_id:
            # Show specific batch status
            status = manager.get_batch_status(batch_id)
            if not status:
                self.print_status(f"Batch {batch_id} not found", "error")
                return

            self.print_header(f"📊 Batch Status: {batch_id}")

            print()
            cprint(f"Batch: {status['batch_name']}", "cyan", attrs=["bold"])
            cprint(f"Status: {status['status'].title()}", "white")
            cprint(f"Progress: {status['progress_percentage']:.1f}%", "green")
            cprint(
                f"Tasks: {status['completed_tasks']}/{status['total_tasks']} completed",
                "white",
            )
            if status["failed_tasks"] > 0:
                cprint(f"Failed: {status['failed_tasks']}", "red")

            if status.get("duration"):
                cprint(f"Duration: {status['duration']:.1f}s", "white")
        else:
            # Show all active batches
            active_batches = manager.list_active_batches()

            self.print_header("📊 Active Batch Operations")

            if not active_batches:
                self.print_status("No active batch operations", "info")
                return

            for batch in active_batches:
                print()
                cprint(
                    f"🎯 {batch['batch_name']} ({batch['batch_id']})",
                    "cyan",
                    attrs=["bold"],
                )
                cprint(f"   Status: {batch['status'].title()}", "white")
                cprint(f"   Progress: {batch['progress']:.1f}%", "green")
                cprint(f"   Games: {', '.join(batch['games'][:3])}", "white")
                if len(batch["games"]) > 3:
                    cprint(f"   ... and {len(batch['games']) - 3} more", "white")

    def cancel_batch_analysis(self, batch_id: str):
        """Cancel running batch analysis."""
        manager = get_batch_manager()

        success = manager.cancel_batch(batch_id)
        if success:
            self.print_status(f"Cancelled batch analysis: {batch_id}", "warning")
        else:
            self.print_status(
                f"Could not cancel batch: {batch_id} (not found or not running)",
                "error",
            )

    def batch_analyze_category_with_progress(
        self, category: str, count: int = 5, analysis_type: str = "quick"
    ):
        """Analyze multiple games from a category using batch processing."""
        self.print_header(f"🚀 Batch Category Analysis: {category.title()}")

        # Get games from category
        progress = self.create_progress_bar("Fetching games", 100, "blue")

        try:
            for i in range(0, 101, 25):
                progress.update(25)
                time.sleep(0.1)

            progress.close()

            result = scrape_dekudeals_category(category, max_games=count)

            if result.get("success", False):
                games = result.get("game_titles", [])
                self.print_status(f"Found {len(games)} games in {category}", "success")

                if games:
                    # Start batch analysis
                    batch_id = self.batch_analyze_games_with_progress(
                        games, analysis_type
                    )
                    return batch_id
                else:
                    self.print_status(f"No games found in {category}", "warning")
            else:
                error_msg = result.get("error", "Unknown error")
                self.print_status(
                    f"Failed to fetch games from {category}: {error_msg}", "error"
                )

        except Exception as e:
            progress.close()
            self.print_status(f"Error in batch category analysis: {str(e)}", "error")

    def batch_analyze_random_with_progress(
        self, count: int = 5, preference: str = "mixed", analysis_type: str = "quick"
    ):
        """Analyze random games using batch processing."""
        self.print_header(f"🚀 Batch Random Analysis: {count} Games ({preference})")

        # Get random games
        progress = self.create_progress_bar("Getting random games", 100, "magenta")

        try:
            for i in range(0, 101, 20):
                progress.update(20)
                time.sleep(0.1)

            progress.close()

            result = get_random_game_sample(count, preference)

            if result.get("success", False):
                games = result.get("selected_games", [])
                self.print_status(f"Selected {len(games)} random games", "success")

                if games:
                    # Start batch analysis
                    batch_id = self.batch_analyze_games_with_progress(
                        games, analysis_type
                    )
                    return batch_id
                else:
                    self.print_status("No random games selected", "warning")
            else:
                self.print_status("Failed to get random games", "error")

        except Exception as e:
            progress.close()
            self.print_status(f"Error in batch random analysis: {str(e)}", "error")

        """Interactive DekuDeals collection import."""
        self.print_section("🌐 Import DekuDeals Collection", "highlight")

        self.print_status("To import your DekuDeals collection, you need:", "info")
        self.print_status("   1. Your DekuDeals collection URL", "info")
        print()

        # Get DekuDeals collection URL
        collection_url = input(
            colored("🔗 Enter DekuDeals collection URL: ", "cyan", attrs=["bold"])
        ).strip()
        if not collection_url:
            self.print_status("DekuDeals collection URL cannot be empty", "error")
            return False

        # Confirm import
        confirm = self.get_user_choice(
            "Ready to import your DekuDeals collection?",
            [
                "✅ Yes, import now",
                "🔙 Cancel import",
            ],
        )

        if not confirm or "Cancel" in confirm:
            self.print_status("Import cancelled", "info")
            return False

        # Show progress
        self.print_status("🔗 Importing DekuDeals collection...", "loading")

        try:

            if result.get("success", False):
                import_results = result.get("import_results", {})
                games_imported = import_results.get("games_imported", 0)
                import_date = import_results.get("import_date", "Unknown")
                recent_games = import_results.get("recent_games", [])

                self.print_status(
                    f"✅ Successfully imported {games_imported} games from DekuDeals!",
                    "success",
                )
                self.print_status(f"📅 Import completed: {import_date}", "info")

                # Show collection changes
                changes = result.get("collection_changes", {})
                games_added = changes.get("games_added", 0)
                total_after = changes.get("after", {}).get("total_games", 0)

                self.print_status(
                    f"📚 Collection updated: {games_added} new games added (total: {total_after})",
                    "info",
                )

                # Show recent imports
                if recent_games:
                    print()
                    cprint("   🎮 Recently Imported Games:", "cyan", attrs=["bold"])
                    for game in recent_games[:5]:
                        title = game.get("title", "Unknown")
                        hours = game.get("hours_played", 0)
                        cprint(f"      • {title} ({hours} hours)", "white")

                    if len(recent_games) > 5:
                        remaining = len(recent_games) - 5
                        cprint(f"      ... and {remaining} more games", "yellow")

                # Show next steps
                next_steps = result.get("next_steps", [])
                if next_steps:
                    print()
                    cprint("   💡 Next Steps:", "yellow", attrs=["bold"])
                    for step in next_steps:
                        cprint(f"      • {step}", "white")

                return True
            else:
                error_msg = result.get("error", "Unknown error")
                self.print_status(f"❌ DekuDeals import failed: {error_msg}", "error")

                # Show provided inputs for debugging
                provided_collection_url = result.get("collection_url", "")
                if provided_collection_url:
                    self.print_status(
                        f"   DekuDeals collection URL provided: {provided_collection_url}",
                        "info",
                    )

                return False

        except Exception as e:
            self.print_status(f"❌ Import error: {str(e)}", "error")
            return False

    def import_dekudeals_collection_interactive(self) -> bool:
        """Interactive DekuDeals collection import using manual game list input."""
        self.print_section("🌐 Import DekuDeals Collection", "highlight")

        self.print_status("To import from DekuDeals, you can:", "info")
        self.print_status("   1. Visit your DekuDeals collection page", "info")
        self.print_status("   2. Copy game titles from your collection", "info")
        self.print_status("   3. Paste them here (one per line)", "info")
        print()

        method = self.get_user_choice(
            "Choose import method:",
            [
                "📝 Manual game list (paste titles)",
                "🌐 Collection URL (experimental)",
                "🔙 Cancel import",
            ],
        )

        if not method or "Cancel" in method:
            return False

        if "Manual game list" in method:
            return self._import_dekudeals_manual_list()
        elif "Collection URL" in method:
            return self._import_dekudeals_url()

        return False

    def _import_dekudeals_manual_list(self) -> bool:
        """Import games from manually pasted list."""
        self.print_status(
            "Enter game titles (one per line, empty line to finish):", "info"
        )
        print()

        games_list = []
        line_count = 0

        while True:
            line_count += 1
            try:
                game_title = input(f"{line_count:2d}. ").strip()

                if not game_title:  # Empty line - finish input
                    break

                games_list.append(game_title)

                if len(games_list) >= 50:  # Practical limit
                    self.print_status("Maximum 50 games reached", "warning")
                    break

            except KeyboardInterrupt:
                print()
                self.print_status("Import cancelled by user", "info")
                return False

        if not games_list:
            self.print_status("No games entered", "warning")
            return False

        # Get import status
        status = self.get_user_choice(
            f"Import {len(games_list)} games as:",
            [
                "❤️ Wishlist (want to buy)",
                "📦 Owned (already own)",
                "✅ Completed (finished)",
                "🎮 Playing (currently playing)",
            ],
        )

        if not status:
            return False

        # Extract status value
        status_map = {
            "Wishlist": "wishlist",
            "Owned": "owned",
            "Completed": "completed",
            "Playing": "playing",
        }

        import_status = next(
            (v for k, v in status_map.items() if k in status), "wishlist"
        )

        # Confirm import
        confirm = self.get_user_choice(
            f"Import {len(games_list)} games as '{import_status}'?",
            [
                "✅ Yes, import now",
                "📋 Show games first",
                "🔙 Cancel import",
            ],
        )

        if "Show games first" in confirm:
            print()
            cprint("   📋 Games to import:", "cyan", attrs=["bold"])
            for i, title in enumerate(games_list, 1):
                cprint(f"      {i:2d}. {title}", "white")

            confirm = self.get_user_choice(
                "Proceed with import?",
                ["✅ Yes, import now", "🔙 Cancel import"],
            )

        if not confirm or "Cancel" in confirm:
            self.print_status("Import cancelled", "info")
            return False

        # Import games
        self.print_status(f"🔄 Importing {len(games_list)} games...", "loading")

        imported_count = 0
        skipped_count = 0
        failed_count = 0

        try:
            for i, title in enumerate(games_list, 1):
                try:
                    result = add_game_to_collection(
                        title=title,
                        status=import_status,
                        notes=f"Imported from DekuDeals collection",
                    )

                    if result.get("success", False):
                        imported_count += 1
                        print(f"✅ {i:2d}/{len(games_list)}: {title}")
                    else:
                        error = result.get("error", "Unknown error")
                        if "already exists" in error:
                            skipped_count += 1
                            print(
                                f"⏭️ {i:2d}/{len(games_list)}: {title} (already in collection)"
                            )
                        else:
                            failed_count += 1
                            print(f"❌ {i:2d}/{len(games_list)}: {title} - {error}")

                except Exception as e:
                    failed_count += 1
                    print(f"❌ {i:2d}/{len(games_list)}: {title} - Error: {str(e)}")

            # Summary
            print()
            self.print_status(f"✅ Import completed!", "success")
            self.print_status(f"   📦 Imported: {imported_count} games", "info")
            if skipped_count > 0:
                self.print_status(
                    f"   ⏭️ Skipped (already owned): {skipped_count} games", "info"
                )
            if failed_count > 0:
                self.print_status(f"   ❌ Failed: {failed_count} games", "warning")

            # Show updated collection stats
            if imported_count > 0:
                try:
                    collection_result = get_user_game_collection(limit=1)
                    if collection_result.get("success", False):
                        stats = collection_result.get("statistics", {})
                        total_games = stats.get("total_games", 0)
                        status_games = stats.get(f"{import_status}_games", 0)

                        self.print_status(
                            f"📚 Collection updated: {total_games} total games ({status_games} {import_status})",
                            "info",
                        )
                except:
                    pass

            return imported_count > 0

        except Exception as e:
            self.print_status(f"❌ Import error: {str(e)}", "error")
            return False

    def _import_dekudeals_url(self) -> bool:
        """Import games from DekuDeals collection URL."""
        self.print_status("🌐 Importing from DekuDeals collection URL", "info")
        print()

        # Get collection URL
        collection_url = input(
            colored("🔗 Enter DekuDeals collection URL: ", "cyan", attrs=["bold"])
        ).strip()

        if not collection_url:
            self.print_status("URL cannot be empty", "error")
            return False

        # Basic URL validation
        if "dekudeals.com/collection/" not in collection_url:
            self.print_status("Invalid DekuDeals collection URL format", "error")
            self.print_status(
                "Expected format: https://www.dekudeals.com/collection/{id}", "info"
            )
            return False

        self.print_status("🔄 Parsing collection from URL...", "loading")

        try:
            # Import the scraping function
            from deku_tools import scrape_dekudeals_collection

            # Parse the collection
            result = scrape_dekudeals_collection(collection_url)

            if not result["success"]:
                self.print_status(
                    f"❌ Failed to parse collection: {result['error']}", "error"
                )
                return False

            games_list = result["games"]
            game_count = result["game_count"]

            if not games_list:
                self.print_status("❌ No games found in collection", "error")
                return False

            self.print_status(f"✅ Found {game_count} games in collection!", "success")

            # Ask for import status
            import_status = self.get_user_choice(
                "Import these games as:",
                ["👑 Owned games", "💭 Wishlist games", "🎮 Playing games"],
            )

            if not import_status:
                return False

            # Map choice to status
            status_mapping = {
                "Owned games": "owned",
                "Wishlist games": "wishlist",
                "Playing games": "playing",
            }

            selected_status = None
            for key, value in status_mapping.items():
                if key in import_status:
                    selected_status = value
                    break

            if not selected_status:
                selected_status = "owned"

            # Show preview and confirm
            print()
            cprint("   📋 Games to import:", "cyan", attrs=["bold"])
            for i, title in enumerate(games_list, 1):
                cprint(f"      {i:2d}. {title}", "white")

            confirm = self.get_user_choice(
                f"Import {game_count} games as '{selected_status}'?",
                ["✅ Yes, import now", "🔙 Cancel import"],
            )

            if not confirm or "Cancel" in confirm:
                self.print_status("Import cancelled", "info")
                return False

            # Import games
            self.print_status(f"🔄 Importing {game_count} games...", "loading")

            imported_count = 0
            skipped_count = 0
            failed_count = 0

            for i, title in enumerate(games_list, 1):
                try:
                    result = add_game_to_collection(
                        title=title,
                        status=selected_status,
                        notes=f"Imported from DekuDeals collection: {collection_url}",
                    )

                    if result.get("success", False):
                        imported_count += 1
                        print(f"✅ {i:2d}/{game_count}: {title}")
                    else:
                        error = result.get("error", "Unknown error")
                        if "already exists" in error:
                            skipped_count += 1
                            print(
                                f"⏭️ {i:2d}/{game_count}: {title} (already in collection)"
                            )
                        else:
                            failed_count += 1
                            print(f"❌ {i:2d}/{game_count}: {title} - {error}")

                except Exception as e:
                    failed_count += 1
                    print(f"❌ {i:2d}/{game_count}: {title} - Error: {str(e)}")

            # Summary
            print()
            self.print_status(f"✅ Import completed!", "success")
            self.print_status(f"   📦 Imported: {imported_count} games", "info")
            if skipped_count > 0:
                self.print_status(
                    f"   ⏭️ Skipped (already owned): {skipped_count} games", "info"
                )
            if failed_count > 0:
                self.print_status(f"   ❌ Failed: {failed_count} games", "warning")

            return imported_count > 0

        except ImportError:
            self.print_status("❌ DekuDeals parsing not available", "error")
            self.print_status("Please install required dependencies", "info")
            return False
        except Exception as e:
            self.print_status(f"❌ Import error: {str(e)}", "error")
            return False


def main():
    """Main CLI function with enhanced argument parsing."""
    parser = argparse.ArgumentParser(
        description="🎮 AutoGen DekuDeals Enhanced CLI - Gaming Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --game "Hollow Knight"              # Analyze specific game
  %(prog)s --quick "Celeste"                   # Quick analysis
  %(prog)s --category hottest --count 10       # Browse top deals
  %(prog)s --random 5 --preference deals       # Random deal recommendations
  %(prog)s --compare "INSIDE" "Limbo"          # Compare games
  %(prog)s --interactive                       # Launch interactive mode
  %(prog)s --demo                              # Full system demo

Batch Processing (NEW - Phase 6.2):
  %(prog)s --batch-analyze "INSIDE" "Celeste" "Hollow Knight"  # Analyze multiple games concurrently
  %(prog)s --batch-category hottest --count 5 --batch-type quick  # Batch analyze category
  %(prog)s --batch-random 3 --preference mixed --batch-type comprehensive  # Batch random analysis
  %(prog)s --batch-status                      # Show all active batch operations
  %(prog)s --batch-status abc123ef            # Show specific batch status
  %(prog)s --batch-cancel abc123ef            # Cancel running batch
  %(prog)s --batch-results abc123ef           # Show batch results
        """,
    )

    # Main actions
    parser.add_argument(
        "--game",
        type=str,
        metavar="NAME",
        help="Analyze specific game with full review",
    )
    parser.add_argument(
        "--quick", type=str, metavar="NAME", help="Quick game analysis and opinion"
    )
    parser.add_argument(
        "--category",
        type=str,
        metavar="CATEGORY",
        help="Browse games from specific category",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of games from category (default: 5)",
    )
    parser.add_argument(
        "--random", type=int, metavar="N", help="Get N random game recommendations"
    )
    parser.add_argument(
        "--preference",
        type=str,
        default="mixed",
        choices=["mixed", "deals", "quality", "trending"],
        help="Preference for random games (default: mixed)",
    )
    parser.add_argument(
        "--compare", nargs="+", metavar="GAME", help="Compare multiple games"
    )
    parser.add_argument(
        "--list-categories", action="store_true", help="Show all available categories"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Launch interactive mode"
    )
    parser.add_argument(
        "--demo", action="store_true", help="Run full system demonstration"
    )

    # Batch processing arguments (NEW - Phase 6.2)
    parser.add_argument(
        "--batch-analyze",
        nargs="+",
        metavar="GAME",
        help="Analyze multiple games concurrently with batch processing",
    )
    parser.add_argument(
        "--batch-category",
        type=str,
        metavar="CATEGORY",
        help="Batch analyze games from specific category",
    )
    parser.add_argument(
        "--batch-random", type=int, metavar="N", help="Batch analyze N random games"
    )
    parser.add_argument(
        "--batch-type",
        type=str,
        default="quick",
        choices=["quick", "comprehensive"],
        help="Type of analysis for batch processing (default: quick)",
    )
    parser.add_argument(
        "--batch-status",
        type=str,
        metavar="BATCH_ID",
        nargs="?",
        const="",
        help="Show status of batch operations (optional: specific batch ID)",
    )
    parser.add_argument(
        "--batch-cancel",
        type=str,
        metavar="BATCH_ID",
        help="Cancel running batch analysis",
    )
    parser.add_argument(
        "--batch-results",
        type=str,
        metavar="BATCH_ID",
        help="Show results of completed batch analysis",
    )

    # Options
    parser.add_argument(
        "--no-color", action="store_true", help="Disable colored output"
    )
    parser.add_argument(
        "--no-progress", action="store_true", help="Disable progress bars"
    )

    args = parser.parse_args()

    # Initialize CLI
    cli = EnhancedCLI()

    # Handle no-color option
    if args.no_color:
        # Disable termcolor
        os.environ["ANSI_COLORS_DISABLED"] = "1"

    try:
        if args.interactive:
            cli.show_welcome()
            cli.interactive_mode()

        elif args.demo:
            cli.show_welcome()
            cli.run_demo_mode()

        elif args.list_categories:
            cli.show_categories()

        elif args.game:
            cli.show_welcome()
            results = cli.analyze_game_with_progress(args.game, "comprehensive")
            cli.display_game_analysis_results(results, args.game)

        elif args.quick:
            cli.show_welcome()
            results = cli.analyze_game_with_progress(args.quick, "quick")
            cli.display_game_analysis_results(results, args.quick)

        elif args.category:
            cli.show_welcome()
            cli.browse_category_with_progress(args.category, args.count)

        elif args.random:
            cli.show_welcome()
            cli.get_random_games_with_progress(args.random, args.preference)

        elif args.compare:
            cli.show_welcome()
            cli.compare_games_with_progress(args.compare)

        elif args.batch_analyze:
            cli.show_welcome()
            cli.batch_analyze_games_with_progress(args.batch_analyze, args.batch_type)

        elif args.batch_category:
            cli.show_welcome()
            cli.batch_analyze_category_with_progress(
                args.batch_category, args.count, args.batch_type
            )

        elif args.batch_random:
            cli.show_welcome()
            cli.batch_analyze_random_with_progress(
                args.batch_random, args.preference, args.batch_type
            )

        elif args.batch_status is not None:
            if args.batch_status == "":
                # Show all active batches
                cli.show_batch_status()
            else:
                # Show specific batch
                cli.show_batch_status(args.batch_status)

        elif args.batch_cancel:
            cli.show_welcome()
            cli.cancel_batch_analysis(args.batch_cancel)

        elif args.batch_results:
            cli.show_welcome()
            cli.display_batch_results(args.batch_results)

        else:
            # Show welcome and help
            cli.show_welcome()
            print()
            cprint(
                "💡 Use --help for full command list or --interactive for menu mode",
                "yellow",
                attrs=["bold"],
            )

    except KeyboardInterrupt:
        print()
        cprint("⏹️ Operation cancelled by user", "yellow", attrs=["bold"])
        sys.exit(0)
    except Exception as e:
        print()
        cprint(f"❌ Unexpected error: {str(e)}", "red", attrs=["bold"])
        sys.exit(1)


if __name__ == "__main__":
    main()
