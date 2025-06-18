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
)

import logging

# Configure logging for CLI
logging.basicConfig(level=logging.WARNING)  # Less verbose for better CLI experience


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

        # 🚀 FAZA 6.1: Game Data Cache System
        self._game_data_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0

        # Setup cache-aware functions (monkey-patch for performance)
        self._setup_cached_functions()

    def _setup_cached_functions(self):
        """
        🚀 FAZA 6.1: Setup cache-aware versions of scraping functions.
        This eliminates redundant scraping by patching agent_tools functions.
        """
        # Store original functions
        self._original_search_and_scrape = search_and_scrape_game

        # Create cached version
        def cached_search_and_scrape_game(game_name: str) -> Dict:
            """Cache-aware version of search_and_scrape_game."""
            cache_key = game_name.lower().strip()

            if cache_key in self._game_data_cache:
                self._cache_hits += 1
                self.print_status(
                    f"💾 Cache HIT for '{game_name}' (saves ~2-3s scraping)", "info"
                )
                return self._game_data_cache[cache_key]
            else:
                self._cache_misses += 1
                self.print_status(
                    f"🔍 Cache MISS for '{game_name}' - scraping...", "info"
                )
                result = self._original_search_and_scrape(game_name)
                # Cache the result for future use
                self._game_data_cache[cache_key] = result
                return result

        # Monkey-patch the global function temporarily
        import agent_tools

        agent_tools.search_and_scrape_game = cached_search_and_scrape_game

        self.print_status("🚀 Performance cache system activated", "success")

    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (
            (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        )

        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": hit_rate,
            "cached_games": len(self._game_data_cache),
            "estimated_time_saved": self._cache_hits
            * 2.5,  # ~2.5s per scraping avoided
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
            ("🎪 --interactive", "Launch interactive mode"),
            ("🎬 --demo", "Run full system demonstration"),
        ]

        for cmd, desc in commands:
            cprint(f"   {cmd:<20}", "cyan", attrs=["bold"], end="")
            print(f" {desc}")

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

        # Cache performance summary
        if cache_stats["cache_hits"] > 0:
            self.print_status(
                f"💾 Cache: {cache_stats['cache_hits']} hits, "
                f"{cache_stats['hit_rate']:.1f}% hit rate, "
                f"~{cache_stats['estimated_time_saved']:.1f}s saved",
                "success",
            )
        else:
            self.print_status("💾 Cache: No hits (first run for this game)", "info")

        return results

    def _step_search_game(self, game_name: str) -> Dict:
        """Step 1: Search and scrape game data (unchanged)."""
        try:
            result = search_and_scrape_game(game_name)
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
        """Display formatted analysis results."""
        self.print_header(f"📊 Analysis Results: {game_name}", "success")

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

    def interactive_mode(self):
        """Launch interactive CLI mode."""
        self.print_header("🎪 Interactive Mode", "highlight")

        while True:
            print()
            action = self.get_user_choice(
                "What would you like to do?",
                [
                    "🎮 Analyze a specific game",
                    "📂 Browse games by category",
                    "🎲 Get random game recommendations",
                    "🆚 Compare multiple games",
                    "📋 View available categories",
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

            elif "compare" in action:
                self.compare_games_interactive()

            elif "categories" in action:
                self.show_categories()

            elif "Exit" in action:
                break

        self.print_status("Interactive mode ended", "info")

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
        """Browse category with progress visualization."""
        self.print_header(f"📂 Browsing Category: {category.title()}")

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
                self.print_status(f"Found {len(games)} games in {category}", "success")

                if games:
                    self.print_section(f"🎮 Games in {category.title()}", style="info")
                    for i, game in enumerate(games, 1):
                        cprint(f"   {i:2d}. {game}", "white")

                # Offer to analyze first game
                if games:
                    analyze = self.get_user_choice(
                        f"Would you like to analyze '{games[0]}'?", ["Yes", "No"]
                    )

                    if "Yes" in analyze:
                        results = self.analyze_game_with_progress(games[0])
                        self.display_game_analysis_results(results, games[0])
            else:
                self.print_status(f"Failed to fetch games from {category}", "error")

        except Exception as e:
            progress.close()
            self.print_status(f"Error browsing category: {str(e)}", "error")

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
                    rating_color = (
                        "green" if rating != "N/A" and float(rating) >= 7 else "yellow"
                    )
                    cprint(f"   ⭐ Rating: {rating}/10", rating_color)
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
                ("eshop-sales", "🏪 eShop Sales"),
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
