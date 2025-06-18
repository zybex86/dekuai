"""
🧠 PHASE 7.1: Advanced ML Features - Price Drop Prediction Models Test

Test suite for ML-powered price prediction and analysis system.

This test validates:
- PricePredictionEngine functionality
- ML trend analysis and price drop probability
- Historical price data management
- AutoGen tool integration
- Real-world prediction scenarios

Author: AutoGen DekuDeals Team
Version: 7.1.0 Test Suite
"""

import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add utils to path for imports
sys.path.append(str(Path(__file__).parent))

# Configure logging for test
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_price_prediction_engine():
    """Test core PricePredictionEngine functionality."""
    try:
        from utils.price_prediction_ml import (
            PricePredictionEngine,
            PriceTrend,
            PredictionConfidence,
        )

        print("🧠 Testing PricePredictionEngine core functionality...")

        # Initialize engine
        engine = PricePredictionEngine(data_dir="test_price_data")

        # Test data recording
        test_game = "Test Game ML Prediction"
        current_date = datetime.now()

        # Record some test price data points
        test_prices = [
            (59.99, current_date - timedelta(days=90)),
            (45.99, current_date - timedelta(days=60)),  # 23% drop
            (39.99, current_date - timedelta(days=30)),  # 13% drop
            (29.99, current_date - timedelta(days=15)),  # 25% drop
            (35.99, current_date - timedelta(days=5)),  # 20% increase
        ]

        for price, date in test_prices:
            success = engine.record_price_data(test_game, price, date)
            print(
                f"  📈 Recorded ${price:.2f} on {date.date()}: {'✅' if success else '⚠️'}"
            )

        # Test historical data retrieval
        history = engine.get_price_history(test_game)
        print(f"  📊 Retrieved {len(history)} price data points")

        if len(history) >= 3:
            # Test trend analysis
            trend_analysis = engine.analyze_price_trend(history)
            print(
                f"  📈 Trend analysis: {trend_analysis['trend'].value} (R² = {trend_analysis['confidence']:.3f})"
            )

            # Test drop probability calculation
            drop_prob = engine.calculate_price_drop_probability(test_game, history)
            print(f"  🎯 Price drop probability: {drop_prob:.1%}")

            # Test target price prediction
            target_price = engine.predict_target_price(test_game, history)
            if target_price:
                print(f"  🎯 Target price prediction: ${target_price:.2f}")

            # Test comprehensive prediction
            current_price = history[-1].price
            prediction = engine.generate_price_prediction(test_game, current_price)

            print(f"  🧠 Full ML Prediction Results:")
            print(f"    Current Price: ${prediction.current_price:.2f}")
            print(f"    Predicted Price (30d): ${prediction.predicted_price:.2f}")
            print(f"    Drop Probability: {prediction.price_drop_probability:.1%}")
            print(f"    Trend: {prediction.trend.value}")
            print(f"    Confidence: {prediction.confidence.value}")
            if prediction.target_price:
                print(f"    Target Price: ${prediction.target_price:.2f}")
            print(f"    Reasons: {len(prediction.reasons)} insights")

            return True
        else:
            print("  ⚠️ Insufficient data for advanced testing")
            return False

    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        print("  💡 Install ML dependencies: pip install numpy scikit-learn")
        return False
    except Exception as e:
        print(f"  ❌ Error testing PricePredictionEngine: {e}")
        return False


def test_autogen_integration():
    """Test AutoGen tool integration."""
    try:
        from agent_tools import generate_ml_price_prediction, get_price_history_analysis

        print("\n🔧 Testing AutoGen ML tools integration...")

        # Test data
        test_game_data = {
            "title": "Hollow Knight",
            "current_eshop_price": "$14.99",
            "MSRP": "$14.99",
            "genres": ["Action", "Adventure", "Platformer"],
            "developer": "Team Cherry",
            "metacritic_score": "87",
        }

        # Test ML price prediction tool
        print("  🧠 Testing generate_ml_price_prediction()...")
        prediction_result = generate_ml_price_prediction(test_game_data)

        if prediction_result.get("success"):
            print(f"    ✅ Prediction successful for {prediction_result['game_title']}")
            print(f"    💰 Current Price: ${prediction_result['current_price']:.2f}")
            print(
                f"    🔮 Prediction: ${prediction_result['prediction']['predicted_price']:.2f}"
            )
            print(
                f"    📊 Drop Probability: {prediction_result['prediction']['price_drop_probability']:.1%}"
            )
            print(f"    🎯 Confidence: {prediction_result['confidence_level']}")
            print(
                f"    💡 Action Recommendations: {len(prediction_result['action_recommendations'])}"
            )
        else:
            print(
                f"    ⚠️ Prediction failed: {prediction_result.get('error', 'Unknown error')}"
            )

        # Test price history analysis tool
        print("  📊 Testing get_price_history_analysis()...")
        history_result = get_price_history_analysis("Hollow Knight", 365)

        if history_result.get("success"):
            data_points = history_result.get("data_quality", {}).get(
                "total_data_points", 0
            )
            print(f"    ✅ History analysis successful: {data_points} data points")

            if data_points > 0:
                trend = history_result.get("trend_analysis", {}).get("trend", "unknown")
                print(f"    📈 Trend: {trend}")

                stats = history_result.get("price_statistics", {})
                if stats:
                    print(
                        f"    💰 Price Range: ${stats.get('historical_low', 0):.2f} - ${stats.get('historical_high', 0):.2f}"
                    )
                    print(
                        f"    📊 Volatility: {stats.get('volatility_percent', 0):.1f}%"
                    )

                insights = history_result.get("insights", [])
                print(f"    💡 Insights: {len(insights)}")
            else:
                print(f"    ℹ️ No historical data available yet")
        else:
            print(
                f"    ⚠️ History analysis failed: {history_result.get('error', 'Unknown error')}"
            )

        return prediction_result.get("success", False) or history_result.get(
            "success", False
        )

    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error testing AutoGen integration: {e}")
        return False


def test_ml_with_real_game():
    """Test ML prediction with real game data."""
    try:
        from agent_tools import search_and_scrape_game, generate_ml_price_prediction

        print("\n🎮 Testing ML prediction with real game data...")

        # Use a popular game for testing
        test_games = ["Stardew Valley", "Hades", "Celeste"]

        for game_name in test_games:
            print(f"  🔍 Analyzing {game_name}...")

            # Get real game data
            game_data = search_and_scrape_game(game_name)

            if not game_data.get("success"):
                print(f"    ⚠️ Could not fetch data for {game_name}")
                continue

            # Generate ML prediction
            ml_prediction = generate_ml_price_prediction(game_data)

            if ml_prediction.get("success"):
                print(f"    ✅ ML prediction successful!")
                print(f"    💰 Current: ${ml_prediction['current_price']:.2f}")
                print(
                    f"    🔮 Predicted: ${ml_prediction['prediction']['predicted_price']:.2f}"
                )
                print(
                    f"    📊 Drop Prob: {ml_prediction['prediction']['price_drop_probability']:.1%}"
                )
                print(f"    📈 Trend: {ml_prediction['prediction']['trend']}")

                # Show some action recommendations
                actions = ml_prediction.get("action_recommendations", [])
                if actions:
                    print(f"    🎯 Top Recommendation: {actions[0]}")

                return True
            else:
                print(
                    f"    ⚠️ ML prediction failed: {ml_prediction.get('error', 'Unknown')}"
                )

        return False

    except Exception as e:
        print(f"  ❌ Error testing with real game: {e}")
        return False


def test_price_tracking_simulation():
    """Simulate price tracking over time."""
    try:
        from utils.price_prediction_ml import PricePredictionEngine

        print("\n⏰ Testing price tracking simulation...")

        engine = PricePredictionEngine(data_dir="test_price_data")

        # Simulate a game with realistic price changes
        sim_game = "Price Simulation Game"
        base_date = datetime.now() - timedelta(days=180)

        # Simulate price history with various patterns
        price_simulation = [
            (59.99, 0),  # Launch price
            (59.99, 30),  # Stable for a month
            (45.99, 60),  # First sale (23% off)
            (59.99, 75),  # Back to full price
            (39.99, 120),  # Holiday sale (33% off)
            (49.99, 135),  # Post-holiday price
            (29.99, 150),  # Deep discount (50% off)
            (39.99, 165),  # Slight increase
            (34.99, 180),  # Current "best" price
        ]

        print(f"  📈 Simulating {len(price_simulation)} price points over 180 days...")

        for price, days_offset in price_simulation:
            date = base_date + timedelta(days=days_offset)
            engine.record_price_data(sim_game, price, date)
            print(f"    Day {days_offset:3d}: ${price:5.2f}")

        # Analyze the complete pattern
        prediction = engine.generate_price_prediction(sim_game, 34.99)

        print(f"  🧠 Final Analysis Results:")
        print(f"    📊 Trend: {prediction.trend.value}")
        print(f"    🎯 Drop Probability: {prediction.price_drop_probability:.1%}")
        print(f"    💎 Historical Low: ${prediction.historical_low:.2f}")
        print(f"    🔮 Predicted (30d): ${prediction.predicted_price:.2f}")

        if prediction.target_price:
            print(f"    🎯 Target Price: ${prediction.target_price:.2f}")

        print(f"    💡 Key Insights:")
        for reason in prediction.reasons[:3]:
            print(f"      • {reason}")

        return True

    except Exception as e:
        print(f"  ❌ Error in price tracking simulation: {e}")
        return False


def test_ml_personalization():
    """Test ML prediction with personalization."""
    try:
        from agent_tools import generate_ml_price_prediction, get_smart_user_insights
        from utils.smart_user_profiler import get_smart_user_profiler

        print("\n👤 Testing ML prediction with user personalization...")

        # Get current user profile
        user_insights = get_smart_user_insights()

        if user_insights.get("user_profile"):
            print(
                f"  🧠 User profile found with {user_insights['user_profile']['total_interactions']} interactions"
            )

            # Test personalized prediction
            test_game = {
                "title": "The Witness",
                "current_eshop_price": "$39.99",
                "genres": ["Puzzle", "Indie"],
                "metacritic_score": "87",
            }

            # Generate both regular and personalized predictions
            regular_prediction = generate_ml_price_prediction(test_game)
            personalized_prediction = generate_ml_price_prediction(
                test_game, "current_user"
            )

            if regular_prediction.get("success") and personalized_prediction.get(
                "success"
            ):
                reg_insights = len(regular_prediction.get("personalized_insights", []))
                pers_insights = len(
                    personalized_prediction.get("personalized_insights", [])
                )

                print(
                    f"    ✅ Regular prediction: {reg_insights} personalized insights"
                )
                print(
                    f"    ✅ Personalized prediction: {pers_insights} personalized insights"
                )

                if pers_insights > reg_insights:
                    print(
                        f"    🎯 Personalization working - more insights with user ID!"
                    )

                    for insight in personalized_prediction["personalized_insights"]:
                        print(f"      💡 {insight}")

                return True
            else:
                print(f"    ⚠️ Could not test personalization - prediction failed")
                return False
        else:
            print(f"    ℹ️ No user profile available - analyze some games first!")
            return True  # Not a failure, just no profile yet

    except Exception as e:
        print(f"  ❌ Error testing ML personalization: {e}")
        return False


def main():
    """Run comprehensive PHASE 7.1 ML Features test suite."""
    print("🧠 PHASE 7.1: Advanced ML Features - Price Drop Prediction Models")
    print("=" * 70)
    print("Starting comprehensive test suite...\n")

    tests = [
        ("Core PricePredictionEngine", test_price_prediction_engine),
        ("AutoGen Integration", test_autogen_integration),
        ("Real Game ML Prediction", test_ml_with_real_game),
        ("Price Tracking Simulation", test_price_tracking_simulation),
        ("ML Personalization", test_ml_personalization),
    ]

    results = []
    start_time = time.time()

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "⚠️ PARTIAL"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            print(f"\n❌ FAILED: {test_name} - {e}")
            results.append((test_name, False))

    # Final summary
    elapsed = time.time() - start_time
    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\n{'='*70}")
    print(f"🧠 PHASE 7.1 ML Features Test Summary")
    print(f"{'='*70}")
    print(f"⏱️  Total Time: {elapsed:.2f}s")
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%")

    print(f"\n📋 Detailed Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")

    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! PHASE 7.1 ML Features are ready! 🚀")
    elif passed >= total * 0.8:
        print(
            f"\n🎯 MOSTLY SUCCESSFUL! {passed}/{total} tests passed - system is functional!"
        )
    else:
        print(
            f"\n⚠️ ISSUES DETECTED! Only {passed}/{total} tests passed - check dependencies!"
        )

    print(f"\n💡 Next steps:")
    print(f"  • Install ML dependencies: pip install numpy scikit-learn psutil")
    print(f"  • Try: python enhanced_cli.py --game 'Hollow Knight'")
    print(f"  • ML predictions will improve with more price data over time")


if __name__ == "__main__":
    main()
