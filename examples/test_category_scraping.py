"""
Test Category Scraping and Diverse Game Testing
Test scrapowania kategorii i testowania różnorodnych gier

This module tests the new category scraping tools that provide
diverse, unbiased game samples from DekuDeals for better testing.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_tools import (
    scrape_dekudeals_category,
    get_games_from_popular_categories,
    get_random_game_sample,
    generate_quick_game_opinion,
    compare_games_with_reviews,
)
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_category_scraping():
    """Test scraping games from different DekuDeals categories."""
    print("=" * 70)
    print("🎯 CATEGORY SCRAPING - TEST SINGLE CATEGORY")
    print("=" * 70)

    test_category = "hottest"  # Hottest Deals

    try:
        print(f"\n🔍 Testing category scraping for: {test_category}")
        print("-" * 50)

        # Scrape category
        result = scrape_dekudeals_category(
            test_category, max_games=10, include_details=False
        )

        if result.get("success", False):
            print("✅ CATEGORY SCRAPING SUCCESS!")
            print(f"📂 Category: {result['category_name']} ({result['category']})")
            print(f"🎮 Games Found: {result['games_found']}")
            print(f"🌐 URL: {result['category_url']}")

            # Display sample games
            games = result.get("games", [])
            game_titles = result.get("game_titles", [])

            if game_titles:
                print(f"\n🎮 Sample Games:")
                for i, title in enumerate(game_titles[:5], 1):
                    price_info = ""
                    if i <= len(games):
                        game = games[i - 1]
                        if game.get("current_price"):
                            price_info = f" - {game['current_price']}"
                        if game.get("discount"):
                            price_info += f" ({game['discount']})"

                    print(f"   {i}. {title}{price_info}")

                if len(game_titles) > 5:
                    print(f"   ... and {len(game_titles) - 5} more games")

            # Display metadata
            metadata = result.get("scraping_metadata", {})
            print(f"\n📊 Scraping Stats:")
            print(f"   Elements Found: {metadata.get('total_elements_found', 'N/A')}")
            print(f"   Games Processed: {metadata.get('games_processed', 'N/A')}")
            print(f"   Include Details: {metadata.get('include_details', False)}")

            return True
        else:
            print("❌ CATEGORY SCRAPING FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            available = result.get("available_categories", [])
            if available:
                print(f"Available categories: {', '.join(available[:5])}")
            return False

    except Exception as e:
        print(f"❌ Exception during category scraping test: {e}")
        return False


def test_multiple_categories():
    """Test collecting games from multiple categories."""
    print("\n" + "=" * 70)
    print("📋 MULTIPLE CATEGORIES - TEST COLLECTION")
    print("=" * 70)

    test_categories = ["hottest", "highest-rated", "recent-drops"]

    try:
        print(f"\n📂 Testing multiple categories: {', '.join(test_categories)}")
        print("-" * 50)

        # Collect from multiple categories
        result = get_games_from_popular_categories(
            max_games_per_category=5, categories=test_categories
        )

        if result.get("success", False):
            print("✅ MULTIPLE CATEGORIES SUCCESS!")
            print(f"📊 Categories Processed: {result['categories_processed']}")
            print(f"🎮 Total Unique Games: {result['total_unique_games']}")

            # Display categories
            games_by_category = result.get("games_by_category", {})
            for category, info in games_by_category.items():
                category_name = info.get("category_name", category)
                count = info.get("count", 0)
                print(f"\n📂 {category_name}: {count} games")

                category_games = info.get("games", [])
                for i, game in enumerate(category_games[:3], 1):
                    title = game.get("title", "Unknown")
                    price = game.get("current_price", "")
                    price_str = f" - {price}" if price else ""
                    print(f"   {i}. {title}{price_str}")

                if len(category_games) > 3:
                    print(f"   ... and {len(category_games) - 3} more")

            # Display failed categories
            failed = result.get("failed_categories", [])
            if failed:
                print(f"\n⚠️ Failed Categories: {', '.join(failed)}")

            # Show unique titles sample
            all_titles = result.get("all_unique_titles", [])
            if all_titles:
                print(f"\n🎲 All Unique Games Sample:")
                for i, title in enumerate(all_titles[:10], 1):
                    print(f"   {i}. {title}")
                if len(all_titles) > 10:
                    print(f"   ... and {len(all_titles) - 10} more")

            return True
        else:
            print("❌ MULTIPLE CATEGORIES FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Exception during multiple categories test: {e}")
        return False


def test_random_sample():
    """Test getting random game sample."""
    print("\n" + "=" * 70)
    print("🎲 RANDOM SAMPLE - TEST DIVERSE SELECTION")
    print("=" * 70)

    sample_size = 6
    category_preference = "mixed"

    try:
        print(
            f"\n🎲 Testing random sample: {sample_size} games ({category_preference})"
        )
        print("-" * 50)

        # Get random sample
        result = get_random_game_sample(sample_size, category_preference)

        if result.get("success", False):
            print("✅ RANDOM SAMPLE SUCCESS!")
            print(f"🎯 Requested: {result['sample_size_requested']} games")
            print(f"🎮 Actual: {result['sample_size_actual']} games")
            print(f"📂 Preference: {result['category_preference']}")
            print(f"🏷️ Categories Used: {', '.join(result['categories_used'])}")

            # Display selected games
            selected_games = result.get("selected_games", [])
            if selected_games:
                print(f"\n🎮 Random Sample Games:")
                for i, game in enumerate(selected_games, 1):
                    print(f"   {i}. {game}")

            # Display metadata
            metadata = result.get("sampling_metadata", {})
            print(f"\n📊 Sampling Stats:")
            print(f"   Available Games: {metadata.get('total_games_available', 'N/A')}")
            print(
                f"   Source Categories: {', '.join(metadata.get('source_categories', []))}"
            )

            return True
        else:
            print("❌ RANDOM SAMPLE FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Exception during random sample test: {e}")
        return False


def test_diverse_game_analysis():
    """Test analyzing diverse games from categories."""
    print("\n" + "=" * 70)
    print("🔬 DIVERSE ANALYSIS - TEST WITH RANDOM GAMES")
    print("=" * 70)

    try:
        print(f"\n🔬 Testing analysis with diverse games...")
        print("-" * 50)

        # Get random sample for analysis
        sample_result = get_random_game_sample(3, "mixed")

        if not sample_result.get("success", False):
            print("❌ Failed to get random sample for analysis")
            return False

        selected_games = sample_result.get("selected_games", [])
        if not selected_games:
            print("❌ No games in random sample")
            return False

        print(f"🎮 Analyzing games: {', '.join(selected_games)}")

        # Test quick opinions for each game
        analysis_results = []
        for i, game_name in enumerate(selected_games, 1):
            try:
                print(f"\n📝 {i}. Analyzing: {game_name}")
                opinion = generate_quick_game_opinion(game_name)

                if opinion.get("success", False):
                    summary = opinion.get("quick_summary", {})
                    rating = summary.get("rating", "N/A")
                    recommendation = summary.get("recommendation", "N/A")

                    print(f"   Rating: {rating} | Rec: {recommendation}")
                    analysis_results.append(opinion)
                else:
                    print(f"   ❌ Analysis failed for {game_name}")

            except Exception as e:
                print(f"   ❌ Error analyzing {game_name}: {e}")

        # Test comparison if we have multiple successful analyses
        if len(analysis_results) >= 2:
            print(
                f"\n🆚 Comparing {len(analysis_results)} successfully analyzed games..."
            )

            successful_games = [
                result["game_title"]
                for result in analysis_results
                if result.get("success", False)
            ]

            if len(successful_games) >= 2:
                comparison = compare_games_with_reviews(successful_games[:3], "overall")

                if comparison.get("success", False):
                    winner = comparison.get("winner", {})
                    if winner:
                        winner_title = winner.get("game_title", "Unknown")
                        winner_rating = winner.get("quick_summary", {}).get(
                            "rating", "N/A"
                        )
                        print(f"   🏆 Winner: {winner_title} ({winner_rating})")

                    games_compared = comparison.get("games_compared", 0)
                    print(f"   📊 Compared: {games_compared} games")
                else:
                    print(f"   ⚠️ Comparison failed")

        print(f"\n✅ Diverse analysis completed!")
        print(
            f"📊 Successfully analyzed: {len(analysis_results)}/{len(selected_games)} games"
        )

        return len(analysis_results) > 0

    except Exception as e:
        print(f"❌ Exception during diverse analysis test: {e}")
        return False


def test_available_categories():
    """Test availability of different categories."""
    print("\n" + "=" * 70)
    print("📂 CATEGORIES AVAILABILITY - TEST ALL CATEGORIES")
    print("=" * 70)

    # Test invalid category to get list of available ones
    result = scrape_dekudeals_category("invalid_category", max_games=1)

    if not result.get("success", False):
        available_categories = result.get("available_categories", [])
        if available_categories:
            print(f"📂 Available Categories ({len(available_categories)}):")

            # Group categories for better display
            deal_categories = [
                "hottest",
                "recent-drops",
                "eshop-sales",
                "deepest-discounts",
                "bang-for-your-buck",
                "ending-soon",
            ]
            quality_categories = ["highest-rated", "staff-picks", "most-wanted"]
            trend_categories = [
                "trending",
                "recently-released",
                "upcoming-releases",
                "newest-listings",
            ]

            print(f"\n💰 Deal Categories:")
            for cat in deal_categories:
                if cat in available_categories:
                    # Map to display name
                    display_name = cat.replace("-", " ").title()
                    print(f"   • {cat} ({display_name})")

            print(f"\n⭐ Quality Categories:")
            for cat in quality_categories:
                if cat in available_categories:
                    display_name = cat.replace("-", " ").title()
                    print(f"   • {cat} ({display_name})")

            print(f"\n📈 Trending Categories:")
            for cat in trend_categories:
                if cat in available_categories:
                    display_name = cat.replace("-", " ").title()
                    print(f"   • {cat} ({display_name})")

            # Show any remaining categories
            shown_categories = deal_categories + quality_categories + trend_categories
            remaining = [
                cat for cat in available_categories if cat not in shown_categories
            ]
            if remaining:
                print(f"\n🔗 Other Categories:")
                for cat in remaining:
                    display_name = cat.replace("-", " ").title()
                    print(f"   • {cat} ({display_name})")

            print(f"\n💡 Usage examples:")
            print(f"   scrape_dekudeals_category('hottest', max_games=10)")
            print(f"   get_random_game_sample(5, 'deals')")
            print(
                f"   get_games_from_popular_categories(8, ['hottest', 'highest-rated'])"
            )

            return True

    print("❌ Could not retrieve available categories")
    return False


def run_category_scraping_tests():
    """Run all category scraping tests."""
    print("🚀 STARTING CATEGORY SCRAPING TESTS")
    print("Testing diverse game collection from DekuDeals categories...")
    print("=" * 70)

    results = []

    # Test 1: Single Category Scraping
    test1_result = test_category_scraping()
    results.append(("Category Scraping", test1_result))

    # Test 2: Multiple Categories
    test2_result = test_multiple_categories()
    results.append(("Multiple Categories", test2_result))

    # Test 3: Random Sample
    test3_result = test_random_sample()
    results.append(("Random Sample", test3_result))

    # Test 4: Diverse Analysis
    test4_result = test_diverse_game_analysis()
    results.append(("Diverse Analysis", test4_result))

    # Test 5: Available Categories
    test5_result = test_available_categories()
    results.append(("Available Categories", test5_result))

    # Summary
    print("\n" + "=" * 70)
    print("📊 CATEGORY SCRAPING - TEST RESULTS SUMMARY")
    print("=" * 70)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL CATEGORY SCRAPING TESTS PASSED!")
        print("✅ Diverse game collection system is fully functional!")
        print("🎮 Tests can now use unbiased, diverse game samples from DekuDeals!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = run_category_scraping_tests()

    print("\n" + "=" * 70)
    print("🏁 CATEGORY SCRAPING TESTING COMPLETE")
    print("=" * 70)

    if success:
        print("✅ Category scraping implementation is ready!")
        print("🎯 Benefits of the new system:")
        print("   • Unbiased game selection from real DekuDeals data")
        print("   • Diverse testing with games from different categories")
        print("   • Random sampling for objective analysis")
        print("   • Support for 13 different game categories")
        print("   • Better testing coverage beyond manually selected games")
    else:
        print("❌ Category scraping needs additional work.")
        print("🔧 Check the error messages above and fix any issues.")

    print(f"\n🎮 Ready to test with diverse, real-world game data!")
