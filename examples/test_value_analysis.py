"""
Test Value Analysis - Phase 2 Point 1
Test analizy wartości - Faza 2 Punkt 1

This example tests the new calculate_value_score functionality.
Ten przykład testuje nową funkcjonalność calculate_value_score.
"""

import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_tools import search_and_scrape_game, calculate_value_score
import json


def test_value_analysis(game_name: str) -> None:
    """
    Testuje analizę wartości dla podanej gry.

    Args:
        game_name (str): Nazwa gry do przetestowania
    """
    print(f"🎮 Testing value analysis for: {game_name}")
    print("=" * 60)

    try:
        # Step 1: Get game data
        print("📡 Step 1: Collecting game data...")
        game_data = search_and_scrape_game(game_name)

        if not game_data.get("success", False):
            print(
                f"❌ Failed to get game data: {game_data.get('message', 'Unknown error')}"
            )
            return

        print(f"✅ Game data collected for: {game_data.get('title', 'Unknown')}")

        # Step 2: Analyze value
        print("💰 Step 2: Performing value analysis...")
        value_analysis = calculate_value_score(game_data)

        if not value_analysis.get("success", False):
            print(
                f"❌ Value analysis failed: {value_analysis.get('error', 'Unknown error')}"
            )
            return

        # Step 3: Display results
        print("✅ Value analysis completed!")
        print("\n" + "🔍 DETAILED RESULTS:")
        print("=" * 60)

        # Basic info
        title = value_analysis.get("game_title", "Unknown")
        print(f"🎮 Game: {title}")

        # Price data
        price_data = value_analysis.get("price_data", {})
        current = price_data.get("current_price")
        msrp = price_data.get("msrp")
        lowest = price_data.get("lowest_historical")
        discount = price_data.get("price_vs_msrp")
        difference = price_data.get("price_vs_lowest")

        print(f"💰 Current Price: {current}")
        print(f"💵 MSRP: {msrp}")
        print(f"📉 Historical Low: {lowest}")
        if discount is not None:
            print(f"🏷️ Discount vs MSRP: {discount:.1f}%")
        if difference is not None:
            print(f"📊 vs Historical Low: +{difference:.2f}")

        # Score data
        score_data = value_analysis.get("score_data", {})
        metacritic = score_data.get("metacritic")
        opencritic = score_data.get("opencritic")
        avg_score = score_data.get("average_score")

        print(f"⭐ Metacritic: {metacritic}")
        print(f"⭐ OpenCritic: {opencritic}")
        print(f"⭐ Average Score: {avg_score}")

        # Value metrics
        value_metrics = value_analysis.get("value_metrics", {})
        value_score = value_metrics.get("value_score")
        timing = value_metrics.get("buy_timing")
        recommendation = value_metrics.get("recommendation")

        print(f"💎 Value Score: {value_score}")
        print(f"⏰ Buy Timing: {timing}")
        print(f"🎯 Recommendation: {recommendation}")

        # Analysis summary
        summary = value_analysis.get("analysis_summary", "No summary available")
        print(f"\n📝 Summary: {summary}")

        print("\n" + "=" * 60)
        print("✅ Value analysis test completed successfully!")

    except Exception as e:
        print(f"❌ Error during value analysis test: {e}")


def test_multiple_games() -> None:
    """Testuje analizę wartości dla wielu gier."""
    test_games = [
        "Ace Attorney Investigations",  # Should be excellent value
        "The Legend of Zelda: Breath of the Wild",  # Premium game
        "Deltarune",  # Good indie value
        "Celeste",  # Good indie value
        "INSIDE",  # Good indie value
        "Moving Out",  # Good indie value
        "Mario & Luigi: Brothership",  # premium game
        "Baten Kaitos I & II HD Remaster",
    ]

    print("🧪 Phase 2 Point 1 - Value Analysis Testing")
    print("=" * 70)

    for i, game in enumerate(test_games, 1):
        print(f"\n🎯 Test {i}/{len(test_games)}: {game}")
        test_value_analysis(game)

        if i < len(test_games):
            print("\n" + "-" * 70)


def test_price_extraction() -> None:
    """Testuje funkcje wyciągania cen."""
    print("🧪 Testing price extraction functions...")

    from utils.price_calculator import extract_price, extract_score

    # Test price extraction
    price_tests = ["53,99 zł", "$19.99", ":289,80 zł", "N/A", "20.50"]

    print("💰 Price extraction tests:")
    for price_text in price_tests:
        result = extract_price(price_text)
        print(f"  '{price_text}' → {result}")

    # Test score extraction
    score_tests = ["92", "8.7", "Brak oceny", "95", "No score"]

    print("\n⭐ Score extraction tests:")
    for score_text in score_tests:
        result = extract_score(score_text)
        print(f"  '{score_text}' → {result}")


if __name__ == "__main__":
    print("🚀 Phase 2 Point 1 - calculate_value_score Implementation Test")
    print("=" * 80)

    # Test basic functionality first
    test_price_extraction()
    print("\n" + "=" * 80)

    # Test full value analysis
    test_multiple_games()

    print(f"\n🎉 Phase 2 Point 1 testing completed!")
    print("✅ calculate_value_score function implemented and tested!")
